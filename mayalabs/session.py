import requests
from requests import HTTPError
import sys
import aiohttp
import asyncio
import time, os, json, sys, hashlib
import concurrent.futures

from .utils.pac_engine import GenerateTask, InstructTask
from .worker import WorkerClient, Worker
from .utils.name_gen import get_random_name
from .utils.websocket import deploy_events
from .utils.log import log
from .utils.defaults import default_api_base_url, default_log_level
import asyncio
from time import sleep
from .mayalabs import authenticate
from colorama import init, Fore, Back, Style
from .exceptions import IntegrityException
from .utils.logging import format_error_log

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

hashseed = os.getenv('PYTHONHASHSEED')
if not hashseed:
    os.environ['PYTHONHASHSEED'] = '0'
    os.execv(sys.executable, [sys.executable] + sys.argv)

hash = hashlib.new('sha256')

class SessionClient:

    @staticmethod
    @authenticate
    def get_session(session_id, alias=None, api_key=None):
        """get the session object by providing session identifier

        Args:
            session_id (_type_): _description_
            alias (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        api_base = default_api_base_url()
        request = {
            'url': f"{api_base}/pac/v1/session/{session_id}",
            'method': "get",
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def create_session(from_script="", api_key=None) -> 'Session':
        api_base = default_api_base_url()
        request = {
            'url': f"{api_base}/pac/v1/session/new",
            'method': "post",
            'json': {
                'from_recipe': from_script
            },
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def list_sessions(api_key=None):
        api_base = default_api_base_url()
        request = {
            'url': f"{api_base}/pac/v1/sessions",
            'method': "get",
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def delete_session(session_id, api_key=None):
        api_base = default_api_base_url()
        request = {
            'url': f"{api_base}/pac/v1/session/{session_id}",
            'method': "delete",
            'json': {},
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def reset_session(session_id, api_key=None):
        api_base = default_api_base_url()
        request = {
            'url': f"{api_base}/pac/v1/session/clear",
            'method': "post",
            'json': {
                'session_id': session_id
            },
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def change_session(session_id, script, api_key=None):
        api_base = default_api_base_url()
        request = {
            'url': f"{api_base}/pac/v1/session/change",
            'method': "post",
            'json': {
                "session_id": session_id,
                "raw": script,
                "register_change": True

            },
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        if response.status_code == 200:
            change_response = response.json()
            change_status = change_response.get('change_status', {}).get('is_changed', False)
            return change_status
        else:
            raise HTTPError("Failed to update script")

    @authenticate
    async def deploy_session(session_id, workspace_id, api_key=None):
        data = {
            'session_id': session_id,
            'workspace_id' : workspace_id,
        }
        api_base = default_api_base_url()
        async with aiohttp.ClientSession(headers={'x-api-key': api_key}) as session:
            async with session.post(f'{api_base}/pac/v1/session/deploy', json=data) as response:
                response_json = await response.json()
                return response_json

class Session():
    def __init__(self, engine="pac-1"):
        self.id = None
        self.engine = engine
        self.script = ""
        self.worker : Worker = None
        self.steps = {}
        self.stitched_flow = []
        self.changed = None

    @classmethod
    def new(cls, script=None):
        # if not isinstance(script, str):
        #     error_log = [
        #         "Argument must be a string.",
        #         f"Received {type(script).__name__}, expected a string."]
        #     raise IntegrityException(format_error_log(error_log))
         
        response = SessionClient.create_session()
        session = cls()
        session.parse_obj(response['response'])
        return session
   
    @classmethod
    def get(cls, session_id=None):
        response = SessionClient.get_session(session_id=session_id)
        session = cls()
        session.parse_obj(response['response'])
        return session
    
    def instruct(self, prompt, from_scratch=True, on_message=None):
        # Implement this method
        task = InstructTask(self.id, instruction=prompt, from_scratch=from_scratch)
        if on_message is not None:
            task.on_message(on_message)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(task.execute())
        pass

    def generate(self):
        task = GenerateTask(self.id)
        asyncio.create_task(task.execute())
        pass

    async def generate_async(self):
        task = GenerateTask(self.id)
        await task.execute()
        res = SessionClient.get_session(session_id=self.id)
        self.parse_obj(res['response'])
        pass

    def check_worker_start(self):
        status = 0
        i = 0
        if (self.worker.status and self.worker.status != 'STARTED'):
            status = Fore.RED + 'PENDING' + Style.RESET_ALL
            log(
                Style.BRIGHT + Fore.CYAN + "Worker status:", status,
                prefix='mayalabs',
                prefix_color=Fore.BLACK
            )

        while self.worker.status and self.worker.status != "STARTED":
            i += 1
            # self.worker.update()
            worker_response = WorkerClient.get_worker(self.worker.id)
            if worker_response['results']:
                self.worker = Worker().parse_obj(worker_response['results'])
            time.sleep(2)

        started_status = Fore.GREEN + 'STARTED' + Style.RESET_ALL
        log(
            Style.BRIGHT + Fore.CYAN + 'Worker status:', started_status,
            prefix='mayalabs',
            prefix_color=Fore.BLACK
        )
        return

    def _deploy(self, worker_id=None, update=False):
        # Implement this method
        # print(worker_id)
        def run_asyncio_coroutine(coroutine):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(coroutine)
            loop.close()
            return result
        
        if worker_id is not None:
            try:
                self.worker = Worker.get_by_id(worker_id)
                log(Style.BRIGHT + Fore.CYAN + "Found worker: ", self.worker.name, prefix='mayalabs')
            except:
                raise Exception("Worker not found")
        elif self.worker is None:
            log(Style.BRIGHT + Fore.CYAN + "No worker found, creating new worker...", prefix='mayalabs')
            random_name = "SDK:" + get_random_name()
            self.worker = WorkerClient.create_worker(worker_name=random_name, alias=random_name)
        else:
            raise Exception("Error: Could not find worker")
        
        if self.worker:
            if self.worker.status != "STARTED":
                log(Style.BRIGHT + Fore.CYAN + "Starting worker: ", self.worker.name, prefix='mayalabs')
                self.worker.start()
            with concurrent.futures.ThreadPoolExecutor() as exec:
                result_2 = exec.submit(self.check_worker_start)
                if (self.changed or self.changed is None):
                    if self.changed:
                        log(Style.BRIGHT + Fore.CYAN + 'Script change detected. Regenerating changes...' + Style.RESET_ALL, prefix='mayalabs')
                    else:
                        log(Style.BRIGHT + Fore.CYAN + 'Generating program...' + Style.RESET_ALL, prefix='mayalabs')
                    future_1 = exec.submit(run_asyncio_coroutine, self.generate_async())
                    future_1.result()
                    log(Style.BRIGHT + Fore.CYAN + 'Generation successful.' + Style.RESET_ALL, prefix='mayalabs')
                else:
                    log(Style.BRIGHT + Fore.CYAN + 'No change in script. Skipped regeneration' + Style.RESET_ALL, prefix='mayalabs')
                result_2.result()
                # report all tasks done
            
            # loop = asyncio.get_event_loop()
            async def async_wrapper():
                if update:
                    deploy_task = asyncio.create_task(SessionClient.deploy_session(self.id, self.worker.id))
                    log_task = asyncio.create_task(self.worker.ws_client.start_listener(events=deploy_events, log_prefix=f'{self.worker.name}'))
                    def stop_log_task(future):
                        log_task.cancel()

                    deploy_task.add_done_callback(stop_log_task)
                    log(
                        Style.BRIGHT + Fore.CYAN + 'Deploying session to worker. Setting up dependencies...' + Style.RESET_ALL,
                        prefix = self.worker.name,
                        prefix_color = self.worker.prefix_color
                    )
                    await asyncio.gather(deploy_task, log_task)
                    log(
                        Style.BRIGHT + Fore.CYAN + 'Deploy successful.' + Style.RESET_ALL,
                        prefix = self.worker.name,
                        prefix_color = self.worker.prefix_color
                    )

                    return deploy_task.result()
                else:
                    log(Style.BRIGHT + Fore.LIGHTYELLOW_EX + 'Update set to false. Skipping deploy' + Style.RESET_ALL, prefix='mayalabs')
                    return
            
            response = asyncio.run(async_wrapper())
            problems = self.worker.get_flow_problems()

            modules_that_need_cfgs = response['data']['modulesThatNeedCfgProfiles']
            configure_url = self.worker.configure_url_base
            if len(modules_that_need_cfgs) > 0:
                log(
                    Fore.YELLOW + Style.BRIGHT + f'The following modules need authentication:' + Style.RESET_ALL,
                    prefix = self.worker.name,
                    prefix_color = self.worker.prefix_color
                )
                for module in modules_that_need_cfgs:
                    name = module['packageName']
                    log(
                        Fore.YELLOW + f'* {name}' + Style.RESET_ALL,
                        prefix = self.worker.name,
                        prefix_color= self.worker.prefix_color
                    )
                module_ids = ','.join([module['id'] for module in modules_that_need_cfgs])
                configure_url += f'&modules={module_ids}'



            if len(problems) > 0:
                log(
                    Fore.YELLOW + Style.BRIGHT + f'Found {len(problems)} missing requirement(s):' + Style.RESET_ALL,
                    prefix = self.worker.name,
                    prefix_color = self.worker.prefix_color
                )
                for p in problems:
                    # solve()  // hehe AGI
                    field_name, node_id, node_type = p['field_name'], p['node_id'], p['node_type']
                    # message = f'* Missing field {field_name} on node {node_id} (type: {node_type})'
                    message = f'* [{node_id}] Missing field {field_name} on node with type: {node_type}' if default_log_level()=="debug" else f'* Missing field {field_name} on node with type: {node_type}'
                    log(
                        Fore.YELLOW + message + Style.RESET_ALL,
                        prefix = self.worker.name,
                        prefix_color = self.worker.prefix_color
                    )
                configure_url += '&progIssues=1'

            link = None
            fixing_needed = False
            if len(modules_that_need_cfgs) > 0:
                link = configure_url
                fixing_needed = True
            elif len(problems) > 0:
                link = f'{self.worker.app_url}&progIssues=1'
                fixing_needed = True

            if fixing_needed:
                log(
                    Fore.YELLOW + 'Fix the above problems by going to this link:' + Style.RESET_ALL, 
                    "\x1B[3m" + link + Style.RESET_ALL,
                    prefix = self.worker.name,
                    prefix_color = self.worker.prefix_color
                )
            else:
                log(
                    Fore.GREEN + 'View/modify the program graph here:' + Style.RESET_ALL, 
                    "\x1B[3m" + self.worker.app_url + Style.RESET_ALL,
                    prefix = self.worker.name,
                    prefix_color = self.worker.prefix_color
                )
            # asyncio.run(async_wrapper())
            
        else:
            raise Exception("Error: Could not find worker") 

    def delete(self):
        # Implement this method
        response = SessionClient.delete_session(self.id)
        return response
    
    def change(self):
        # Implement this method
        change_response = SessionClient.change_session(session_id=self.id, script=self.script)
        self.changed = change_response
        return

    def parse_obj(self, obj):
        self.id = obj['session_id']
        self.script = obj['recipe']
        self.steps = obj['steps']
        self.stitched_flow = obj['stitched_flow']

    def update(self):
        response = SessionClient.get_session(self.id)
        self.parse_obj(response['response'])

    def to_string(self):
        pass

    def call(self, msg):
        call_task = asyncio.create_task(self.worker.call(msg))
        log_task = asyncio.create_task(self.worker.ws_client.create_listen_task())
        call_task.add_done_callback(log_task.cancel)

        tasks = asyncio.gather([call_task, log_task])
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(tasks)

        return response

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

