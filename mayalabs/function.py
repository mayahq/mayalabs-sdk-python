from mayalabs import Session
from mayalabs import Worker, WorkerClient, SessionClient
from typing import Dict, Union
from .utils.log import log
from colorama import Fore, Style
from .exceptions import IntegrityException, NoDashboardException, WebBrowserException
from .utils.logging import format_error_log
from .utils.defaults import dashboard_nodes_list, default_log_level
from .utils.general import Views
import concurrent.futures
import webbrowser

class Function:
    def __init__(self, name, script=None, deploy=False):
        """Initailize remote Maya function. A Maya function is a managed compute, storage and network
        infrastructure on which business logic defined gets deployed and executed

        Args:
            name (str, required): unique name of the function, this should be unique for your profile.
            script (str, optional): Step by step sequence of business logic to deploy and execute on the function. Defaults to None.
            deploy (bool, option): A True value would require providing a script and immediately attempts deploy of the business logic. Default to False. 
        """
        self.name : str = name
        self.worker : Worker = None
        self.session : Session = None
        self.script: str = None
        self._get_or_create(name=self.name, script=script, deploy=deploy)

    @staticmethod
    def exists(name):
        pass
        existing_worker = Worker.get_by_alias(alias=name)
        if existing_worker is None:
            return False
        
        return True


    # @staticmethod
    def _get_or_create(self, name, script, deploy):
        try:
            existing_worker = Worker.create(name=name, alias=name)
            session_id = existing_worker.session_id if existing_worker.session_id else None
            if existing_worker._reuse:
                log(Style.BRIGHT + Fore.CYAN + f'Found existing [{existing_worker.alias}]. Reusing.' + Style.RESET_ALL, prefix='mayalabs')
            else:
                log(Style.BRIGHT + Fore.CYAN + f'Creating new [{name}]' + Style.RESET_ALL, prefix='mayalabs')
        except Exception as err:
                raise Exception(f'Could not find function [{name}] on your profile')
        try:
            if session_id is not None:
                existing_session = Session.get(session_id=session_id)
            else:
                existing_session = Session.new()
            if script is not None:
                    existing_session.script = script
                    if deploy:
                        self.deploy(update=True)
        except Exception as err:
            raise err
        try:
            existing_worker.attach_session(session_id=existing_session.id)
        except Exception as err:
            log(Fore.RED + f'Failed to attach session to worker [{existing_worker.alias}]' + Style.RESET_ALL, prefix='mayalabs')
            raise err
        self.worker = existing_worker
        self.session = existing_session
        self.session.worker = self.worker

    def deploy(self, update=False):
        """
        Deploys the function serverlessly.
        Creates a new session from script and deploys session to a worker.
        """
        if self.script is None:
            raise Exception("No script provided")

        if self.session is None:
            self.session = Session.new(script=self.script)

        if self.worker is None:
            self.worker = Worker.new(name=self.name, alias=self.name)

        self.session._deploy(worker_id=self.worker.id, update=update)

    def call(self, payload = {}, **kwargs) -> Dict:
        """
        Call the deployed function. 
        Arguments passed here are passed to the `msg` object in the script.
        A value like `msg['key']` can be accessed in the script by using {{key}}
        """
        if not isinstance(payload, dict):
            error_log = [
                "Argument must be a dictionary.",
                f"Received {type(payload).__name__}, expected a dictionary."]
            raise IntegrityException(format_error_log(error_log))

        # logic to check if a worker is awake before actually making a call
        if self.worker.status == "STARTED":
            worker_health = self.worker.get_health()
            if worker_health.status_code != 200:
                log(Fore.CYAN + 'Making sure the worker is online...' + Style.RESET_ALL, prefix='mayalabs')
                self.worker.start()
                with concurrent.futures.ThreadPoolExecutor() as exec:
                    worker_start_result = exec.submit(self.session.check_worker_start)
                worker_start_result.result()
        elif self.worker.status == "STOPPED" or self.worker.status == "PENDING":
            log(Fore.CYAN + 'Making sure the worker is online...' + Style.RESET_ALL, prefix='mayalabs')
            self.worker.start()
            with concurrent.futures.ThreadPoolExecutor() as exec:
                worker_start_result = exec.submit(self.session.check_worker_start)
            worker_start_result.result()
        # call worker with argument
        response = self.worker.call(msg = { **payload, **kwargs }, session=self.session)
        return response
    
    def __call__(self, payload = {}) -> Dict:
        """
        Call the deployed function. 
        Arguments passed here are passed to the `msg` object in the script.
        A value like `msg['key']` can be accessed in the script by using {{key}}
        """
        return self.call(payload=payload)
    
    def clear(self, session_only=False, worker_only=False):
        """This method clears the current function of programs and configurations set on it.
        Args:
            session_only (bool, optional): A True value clears only the session information i.e. your script shall be regenerated if an update is performed subsequently. Defaults to False.
            worker_only (bool, optional): A True value will clear the function of its deployment. i.e. a call() operation will be unresponsive without an update() operation preceding it. Defaults to False.

        Raises:
            e: JSONDecode exception if the service fails to respond successfully for cleaning either of session or worker
        """
        try:
            if session_only:
                SessionClient.reset_session(session_id=self.session.id)
            elif worker_only:
                WorkerClient.reset_worker(worker_id=self.worker.id)
            else:
                SessionClient.reset_session(session_id=self.session.id)
                WorkerClient.reset_worker(worker_id=self.worker.id)
        except Exception as e:
            raise e
    
    def delete(self):
        """
        Deletes the function by deleteing the associated session and the worker.
        """
        if self.session is not None:
            self.session.delete()
        if self.worker is not None:
            log(Fore.YELLOW + f'Deleting function [{self.worker.alias}]' + Style.RESET_ALL, prefix='mayalabs')
            try:
                self.worker.delete()
                log(Fore.YELLOW + f'Function [{self.worker.alias}] successfully deleted' + Style.RESET_ALL, prefix='mayalabs')
            except Exception as err:
                log(Fore.RED + f'Failed to delete function [{self.worker.alias}]' + Style.RESET_ALL, prefix='mayalabs')

    def update(self, script: str, override_lock=False):
        """Updates the business logic on the function and deploys it. Such deployment is irreversible, use with caution.
        Args:
            script (str): Step by step sequence of business logic to deploy and execute on the function.
            override_lock (bool, optional): A True value overrides lock state of function and updates it. Defaults to False.
        """
        self.session.script = script
        if override_lock:
            self.session.change()
            self.session._deploy(worker_id=self.worker.id, update=True)
        elif not self.worker.locked:
            log(Fore.YELLOW + f'Updating a function is irreversible.' + Style.RESET_ALL, prefix='mayalabs')
            log(Fore.YELLOW + f'Run function.lock() to prevent updates in production.' + Style.RESET_ALL, prefix='mayalabs')
            self.session.change()
            self.session._deploy(worker_id=self.worker.id, update=True)
        else:
            raise Exception(f"The function [{self.name}] is locked for updates. Unlock function using function.unlock() or set override_lock to True")
            
    def lock(self) -> bool:
        log(Style.BRIGHT + Fore.CYAN + f'Locking function [{self.worker.alias}] ...' + Style.RESET_ALL, prefix='mayalabs')
        lock_worker_response = WorkerClient.lock_worker(worker_id=self.worker.id)
        if lock_worker_response.status_code == 200:
            log(Style.BRIGHT + Fore.CYAN + f'[{self.worker.alias}] locked from deployment' + Style.RESET_ALL, prefix='mayalabs')
            self.worker.locked = True
            return True
        else:
            self.worker.locked = True
            return False
        
    def unlock(self) -> bool:
        log(Style.BRIGHT + Fore.CYAN + f'Unlocking function [{self.worker.alias}] ...' + Style.RESET_ALL, prefix='mayalabs')
        lock_worker_response = WorkerClient.lock_worker(worker_id=self.worker.id)
        if lock_worker_response.status_code == 200:
            log(Style.BRIGHT + Fore.CYAN + f'[{self.worker.alias}] unlocked for deployment' + Style.RESET_ALL, prefix='mayalabs')
            self.worker.locked = False
            return True
        else:
            self.worker.locked = True
            return False
        

    def show(self, view:Union[Views, str] = Views.dashboard, open_browser=True) -> str:
        """attempts to open the view of function program graph editor or dashboard in default web browser

        Args:
            view (Views, optional): Takes a string value from 'editor' or 'dashboard'. Attempts to open program graph or dashboard generated from the program in default web browser. Defaults to Views.dashboard. Raises exception if browser can't be found.
            open_browser (bool, optional): A true value attempts opening the 'editor' or 'dashboard' in the default web browser. Defaults to True.

        Raises:
            NoDashboardException: if no dashboard is present on the function this error is raised
            WebBrowserException: if there is error opening the default web browser

        Returns:
            str: Web URL to view program graph if view set to 'editor' and URl to view dashboard if view is set to 'dashboard'.
        """
        if isinstance(view, str):
            if view not in [e.value for e in Views]:
                raise ValueError(f"Invalid value for view. Allowed values: {[e.value for e in Views]}")
            view = Views(view)
            # print(Views.dashboard)
            # if view == Views.dashboard:
            #     view = Views.dashboard
            # elif view == Views.editor:
            #     view = Views.editor
            # else:
            #     raise ValueError(f"Invalid value for view. Allowed values: {[e.value for e in Views]}")
        if not isinstance(view, Views):
            raise ValueError(f"Invalid value for view. Allowed values: {[e.value for e in Views]}")

        if self.worker.status == "STARTED":
            worker_health = self.worker.get_health()
            if worker_health.status_code != 200:
                log(Fore.CYAN + 'Making sure the worker is online...' + Style.RESET_ALL, prefix='mayalabs')
                self.worker.start()
                with concurrent.futures.ThreadPoolExecutor() as exec:
                    worker_start_result = exec.submit(self.session.check_worker_start)
                worker_start_result.result()
        elif self.worker.status == "STOPPED" or self.worker.status == "PENDING":
            log(Fore.CYAN + 'Making sure the worker is online...' + Style.RESET_ALL, prefix='mayalabs')
            self.worker.start()
            with concurrent.futures.ThreadPoolExecutor() as exec:
                worker_start_result = exec.submit(self.session.check_worker_start)
            worker_start_result.result()
        
        flow = self.worker.get_flow()
        flow_problems = self.worker.get_flow_problems()
        has_dashboard = False
        if view == Views.dashboard:
            for flow_node in flow:
                if flow_node['type'] in dashboard_nodes_list:
                    has_dashboard = True
                    break
            if has_dashboard:
                if len(flow_problems) > 0:
                    dash_error_count = 0
                    for node in flow_problems:
                        if node['node_type'] in dashboard_nodes_list:
                            dash_error_count+=1
                            field_name, node_id, node_type = node['field_name'], node['node_id'], node['node_type']
                            # message = f'* Missing field {field_name} on node {node_id} (type: {node_type})'
                            message = f'* [{node_id}] Missing field {field_name} on node with type: {node_type}' if default_log_level()=="debug" else f'* Missing field {field_name} on node with type: {node_type}'
                            log(
                                Fore.YELLOW + message + Style.RESET_ALL,
                                prefix = self.worker.name,
                                prefix_color = self.worker.prefix_color
                            )
                    if dash_error_count < 1:
                        log(
                            Fore.GREEN + 'View the program dashboard here: ' + Style.RESET_ALL, 
                            "\x1B[3m" + self.worker.dash_url + Style.RESET_ALL,
                            prefix = self.worker.name,
                            prefix_color = self.worker.prefix_color
                        )

                        if open_browser:
                            try:
                                webbrowser.open(self.worker.dash_url, new=0, autoraise=True)
                            except Exception as e:
                                raise WebBrowserException(e)
                        return self.worker.dash_url
                else:
                    log(
                        Fore.GREEN + 'View the program dashboard here: ' + Style.RESET_ALL, 
                        "\x1B[3m" + self.worker.dash_url + Style.RESET_ALL,
                        prefix = self.worker.name,
                        prefix_color = self.worker.prefix_color
                    )
                    if open_browser:
                        try:
                            webbrowser.open(self.worker.dash_url, new=0, autoraise=True)
                        except Exception as e:
                            raise WebBrowserException(e)
                    return self.worker.dash_url
            else:
                raise NoDashboardException(Exception(f"function [{self.name}] does not have a dashboard output to show"))
        
        elif view == Views.editor:
            if open_browser:
                try:
                    webbrowser.open(self.worker.app_url, new=0, autoraise=True)
                except Exception as e:
                    raise WebBrowserException(e)
            return self.worker.app_url

     
    def set_config(self, type, data = {}):
        return self.worker.set_config(type, data)