import requests
import os
from .creds import api_key, api_base_url, api_ws_url
from .utils.pac_engine import GenerateTask, InstructTask
from .worker import WorkerClient, Worker
from .utils.name_gen import get_random_name
import asyncio
import time
from time import sleep
import concurrent.futures
class SessionClient:

    @staticmethod
    def get_session(session_id, alias=None):
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
    def create_session(from_script="") -> 'Session':
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
    def list_sessions():
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
    def delete_session(session_id):
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
    
    def deploy_session(session_id, workspace_id):
        request = {
            'url': f"{api_base_url}/pac/v1/session/deploy",
            'method': "post",
            'json': {
                'session_id': session_id,
                'workspace_id' : workspace_id,
            },
            'headers': {
                'x-api-key': api_key,
            }
        }
        response = requests.request(**request)
        try:
            return response.json()
        except:
            print('deploy error')
    
    def session_parse(obj):
        # requests = {
        #     'url': f"{self.pac_base_url}/pac/v1/session/parse",
        #     'method': "post",
        #     'json': {
                
        #     },
        #     'headers': {
        #         'x-api-key': self.api_key,
            
        # }
        pass

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

    async def generate(self):
        task = GenerateTask(self.id)
        asyncio.create_task(task.execute())
        pass

    def check_worker_start(self):
        status = 0
        while self.worker.status and self.worker.status != "STARTED":
            print("Checking - worker status:", self.worker.status)
            # self.worker.update()
            print("Waiting for worker to start...")
            worker_response = WorkerClient.get_worker(self.worker.id)
            if worker_response['results']:
                self.worker = Worker().parse_obj(worker_response['results'])
            time.sleep(2)
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
            response = WorkerClient.get_worker(worker_id)
            try:
                print(response['results'])
                self.worker = Worker().parse_obj(response['results'])
                print("Found worker: ", self.worker.name)
                print("Deploying...")
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
                print("Starting worker: ", self.worker.name, "...")
                self.worker.start()
            print("Generating program...")
            with concurrent.futures.ThreadPoolExecutor() as exec:

                future_1 = exec.submit(run_asyncio_coroutine, self.generate())
                result_2 = exec.submit(self.check_worker_start)
                result_1 = future_1.result()
                print("Program gneerated")
                result_2.result()
                # report all tasks done
                print("Deploying on worker:", self.worker.name, "...")
            
            response = SessionClient.deploy_session(self.id, self.worker.id)
            return response
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
        response = self.worker.call(msg) 
        return response

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

