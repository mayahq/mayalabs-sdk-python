import requests
import sys
import aiohttp

from .utils.pac_engine import GenerateTask, InstructTask
from .worker import WorkerClient, Worker
from .utils.name_gen import get_random_name
from .utils.websocket import WebsocketListener, deploy_events
import asyncio
import time
from time import sleep
import concurrent.futures
from .consts import api_base_url, api_ws_url
from .mayalabs import authenticate
from colorama import init, Fore, Back, Style


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
        request = {
            'url': f"{api_base_url}/pac/v1/session/{session_id}",
            'method': "get",
            'json': {},
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def create_session(from_script="", api_key=None) -> 'Session':
        request = {
            'url': f"{api_base_url}/pac/v1/session/new",
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
        request = {
            'url': f"{api_base_url}/pac/v1/sessions",
            'method': "get",
            'json': {},
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def delete_session(session_id, api_key=None):
        request = {
            'url': f"{api_base_url}/pac/v1/session/{session_id}",
            'method': "delete",
            'json': {},
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        return response.json()
    
    # @authenticate
    # def deploy_session(session_id, workspace_id, api_key=None):
    #     request = {
    #         'url': f"{api_base_url}/pac/v1/session/deploy",
    #         'method': "post",
    #         'json': {
    #             'session_id': session_id,
    #             'workspace_id' : workspace_id,
    #         },
    #         'headers': {
    #             'x-api-key': api_key,
    #         }
    #     }
    #     response = requests.request(**request)
    #     try:
    #         return response.json()
    #     except:
    #         print('deploy error')

    @authenticate
    async def deploy_session(session_id, workspace_id, api_key=None):
        data = {
            'session_id': session_id,
            'workspace_id' : workspace_id,
        }
        async with aiohttp.ClientSession(headers={'x-api-key': api_key}) as session:
            async with session.post(f'{api_base_url}/pac/v1/session/deploy', json=data) as response:
                response_json = await response.json()
                return response_json
    
    # def session_parse(obj):
    #     # requests = {
    #     #     'url': f"{self.pac_base_url}/pac/v1/session/parse",
    #     #     'method': "post",
    #     #     'json': {
                
    #     #     },
    #     #     'headers': {
    #     #         'x-api-key': self.api_key,
            
    #     # }
    #     pass

class Session():
    def __init__(self, engine="pac-1"):
        self.id = None
        self.engine = engine
        self.script = ""
        self.worker : Worker = None

    @classmethod
    def new(cls, script=None):
        response = SessionClient.create_session(from_script=script)
        session = cls()
        session.parse_obj(response['response'])
        return session
    
    def instruct(self, prompt, from_scratch=True):
        # Implement this method
        task = InstructTask(self.id, prompt, from_scratch=from_scratch)
        task.execute(prompt)
        pass

    def generate(self):
        task = GenerateTask(self.id)
        asyncio.create_task(task.execute())
        pass

    async def generate_async(self):
        task = GenerateTask(self.id)
        await task.execute()
        pass

    def check_worker_start(self):
        status = 0
        i = 0
        while self.worker.status and self.worker.status != "STARTED":
            i += 1
            status = Fore.RED + 'PENDING' + Style.RESET_ALL
            print('[Maya]', "Checking - worker status:", status + (i%3)*'.', end='\r')
            # self.worker.update()
            worker_response = WorkerClient.get_worker(self.worker.id)
            if worker_response['results']:
                self.worker = Worker().parse_obj(worker_response['results'])
            time.sleep(2)

        started_status = Fore.GREEN + 'STARTED' + Style.RESET_ALL
        print('[Maya]', 'Checking - worker status:', started_status)
        return

    def deploy(self, worker_id=None):
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
                print('[Maya]', "Found worker: ", self.worker.name)
            except:
                raise Exception("Worker not found")
        elif self.worker is None:
            print("No worker found, creating new worker...")
            random_name = "SDK:" + get_random_name()
            self.worker = WorkerClient.create_worker(worker_name=random_name, alias=random_name)
        else:
            raise Exception("Error: Could not find worker")
        
        if self.worker:
            if self.worker.status != "STARTED":
                print('[Maya]', "Starting worker: ", self.worker.name)
                self.worker.start()
            print(f'[{self.worker.name}]', Style.BRIGHT + Fore.CYAN + 'Generating program.' + Style.RESET_ALL)
            with concurrent.futures.ThreadPoolExecutor() as exec:
                future_1 = exec.submit(run_asyncio_coroutine, self.generate_async())
                result_2 = exec.submit(self.check_worker_start)
                result_1 = future_1.result()
                print(f'[{self.worker.name}]', Style.BRIGHT + Fore.GREEN + 'Generation successful.' + Style.RESET_ALL)
                result_2.result()
                # report all tasks done
            
            loop = asyncio.get_event_loop()
            deploy_task = loop.create_task(SessionClient.deploy_session(self.id, self.worker.id))
            log_task = loop.create_task(self.worker.ws_client.start_listener(events=deploy_events, log_prefix=f'[{self.worker.name}]'))
            def stop_log_task(future):
                log_task.cancel()

            deploy_task.add_done_callback(stop_log_task)
            print(f'[{self.worker.name}]', Style.BRIGHT + Fore.CYAN + 'Deploying session to worker. Setting up dependencies.' + Style.RESET_ALL)
            loop.run_until_complete(
                asyncio.gather(deploy_task, log_task)
            )
            loop.close()
            print(f'[{self.worker.name}]', Style.BRIGHT + Fore.GREEN + 'Deploy successful.' + Style.RESET_ALL)

            return deploy_task.result()
        else:
            raise Exception("Error: Could not find worker") 

    def delete(self):
        # Implement this method
        response = SessionClient.delete_session(self.id)
        return print(response)

    def parse_obj(self, obj):
        self.id = obj['session_id']
        self.script = obj['recipe']

    def update(self):
        response = SessionClient.get_session(self.id)
        print(response)
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

        print('response:', response)

        return response

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

