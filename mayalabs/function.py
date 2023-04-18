from mayalabs import Session
from mayalabs import Worker, WorkerClient, SessionClient
from typing import Any, Dict
from .mayalabs import authenticate
from .utils.log import log
from colorama import Fore, Style
from .exceptions import IntegrityException
from .utils.logging import format_error_log
import concurrent.futures
import random
import asyncio, os

class Function:
    # @authenticate
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