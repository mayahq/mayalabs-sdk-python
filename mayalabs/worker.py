import os
import requests
import asyncio
import aiohttp
import json
from urllib.parse import urlparse
import traceback
from .utils.poll import poll
from .utils.websocket import WebsocketListener
import time
from .consts import api_base_url, api_ws_url
from .mayalabs import authenticate
from .utils.log import log
from colorama import init, Fore, Back, Style
from .exceptions import AuthException, IntegrityException
from .utils.logging import format_error_log

import random
# {'publishedSkillPacks': [], 'skillPacks': [], 'modules': [], 'externalModules': [], 'local': False, 'autoShutdownBehaviour': 'BY_LAST_USE', 'editorAutoDeploy': False, 'parent': None, 'alias': 'API_TEST', 'invalidNodes': [], 'createdAt': '2023-03-22T10:20:50.000Z', 'updatedAt': '2023-03-22T10:20:50.000Z', '_id': '641c89cb902176caaede0144', 'profileSlug': 'mayahq', 'name': 'TESTING API', 'status': 'STOPPED', 'deviceID': '5e0bbfe3717896af1cbb763b', 'deviceName': 'online-cpu', 'device': {'platform': 'cloud'}, 'thumbnail': 'https://maya-frontend-static.s3.ap-south-1.amazonaws.com/default.jpg', 'intents': [], 'url': 'https://rt-641c89cb902176caaede0144.mayahq.dev.mayalabs.io', 'deleted': False, 'createdBy': 'mayahq', 'updatedBy': 'mayahq', '__v': 0}

colors = [
    Fore.MAGENTA,
    Fore.GREEN,
    Fore.YELLOW
]

class Worker:
    def __init__(self) -> None:
        self.name : str = None
        self.alias : str = None
        self.id : str = None
        self.url : str = None
        self.status : str = None
        self.session_id : str = None
        self.ws_client : WebsocketListener = None
        self.prefix_color = random.choice(colors)

    def _init_from_api_response(self, response):
        self.name = response['name']
        self.alias = response['alias']
        self.id = response['_id']
        self.url = response['url']
        self.status = response['status']
        self.ws_client = WebsocketListener(
            url=self.url.replace('https', 'wss') + '/comms'
        )

    @staticmethod
    def get_by_id(id: str):
        worker_info = WorkerClient.get_worker(worker_id=id)
        worker = Worker()
        worker._init_from_api_response(worker_info['results'])
        return worker
        
    @staticmethod
    def get_by_alias(alias: str):
        return WorkerClient.get_worker_by_alias(alias)

    @staticmethod
    def search_by_name(name: str):
        return WorkerClient.search_worker_by_name(name=name)
    
    @staticmethod
    def create(name, alias):
        return WorkerClient.create_worker(worker_name=name, alias=alias)

    def start(self, wait = False):
        return WorkerClient.start_worker(worker_id=self.id, wait=wait)

    def stop(self):
        return WorkerClient.stop_worker(worker_id=self.id)

    def delete(self):
        return WorkerClient.delete_worker(worker_id=self.id)

    def clear(self):
        pass

    def update(self):
        if self.id is not None:
            response = WorkerClient.get_worker(worker_id=self.id)
            self.parse_obj(response['results'])
        else:
            raise Exception("Worker ID is not set")
        
    @authenticate
    def attach_session(self, session_id, api_key=None):
        request = {
            'url': f"{api_base_url}/app/v2/brains/linkSessionToRuntime",
            'method': "post",
            'json': {
                'workspaceId': self.id,
                'sessionId': session_id
            },
            'headers': {
                'x-api-key': api_key,
            },
        }

        requests.request(**request)

    def call(self, msg : dict):
        if self.id is None:
            raise Exception("Worker ID is not set")
        if self.url is None:
            self.update()

        # loop = asyncio.get_event_loop()

        async def async_wrapper():
            call_task = asyncio.create_task(WorkerClient.call_worker(worker_url=self.url, msg=msg))
            log_task = asyncio.create_task(self.ws_client.start_listener(log_prefix=self.name, prefix_color=self.prefix_color))

        
            def stop_log_task(future):
                log_task.cancel()

            call_task.add_done_callback(stop_log_task)

            log(Style.BRIGHT + Fore.CYAN + 'Executing program on worker.\n' + Style.RESET_ALL, prefix='mayalabs')
            await asyncio.gather(call_task, log_task)

            return call_task, log_task

        call_task, log_task = asyncio.run(async_wrapper())
        return call_task.result()

    @classmethod
    def parse_obj(cls, obj):
        worker = cls()
        worker.id = obj.get('_id', None)
        worker.url = obj.get('url', None)
        worker.status = obj.get('status', None)
        worker.name = obj.get('name', None)
        worker.alias = obj.get('alias', None)
        worker.session_id = obj.get('sessionId', None)
        worker_ws_url = worker.url.replace('https', 'wss') + '/comms'
        worker.ws_client = WebsocketListener(url=worker_ws_url)
        return worker
    
    @classmethod
    def new(cls, name, alias=None):
        worker = WorkerClient.create_worker(worker_name=name, alias=alias)
        return worker
    
    @property
    def app_url(self):
        url_data = urlparse(self.url)
        origin = url_data.netloc
        parts = origin.split('.')
        env = parts[2]

        app_subdomain = 'devapp' if env == 'dev' else 'app'
        return f'https://{app_subdomain}.mayalabs.io/edit?id={self.id}'



class WorkerClient:
    @staticmethod
    @authenticate
    def get_worker(worker_id, alias=None, api_key=None) -> Worker:
        if alias:
            request = {
                'url': f"{api_base_url}/app/v2/brains/{worker_id}",
                'method': "get",
                'json': {
                    'workspaceId': worker_id,
                    'alias': alias
                },
                'headers': {
                    'x-api-key': api_key,
                },
            }
        else:
            request = {
                'url': f"{api_base_url}/app/v2/brains/{worker_id}",
                'method': "get",
                'json': {
                    'workspaceId': worker_id,
                },
                'headers': {
                    'x-api-key': api_key,
                },
            }

        response = requests.request(**request)
        return response.json()
    
    @staticmethod
    @authenticate
    def get_worker_by_alias(alias, api_key=None) -> Worker:
        request = {
            'url': f"{api_base_url}/app/v2/brains/getByAlias/{alias}",
            'method': "get",
            'headers': {
                'x-api-key': api_key,
            },
        }

        response = requests.request(**request)
        results = response.json().get('results', None)
        if results is None:
            return None
        else:
            worker = Worker.parse_obj(results)
            return worker
    
    @staticmethod
    @authenticate
    def search_worker_by_name(self, name, api_key=None) -> Worker:
        request = {
            'url': f"{api_base_url}/app/v2/brains/search?name={name}",
            'method': 'get',
            'headers': {
                'x-api-key': api_key
            }
        }

        response = requests.request(**request)
        data = response.json()
        if len(data) > 0:
            worker = Worker.parse_obj(data[0]['results'])
            return worker
        else:
            return None

    @staticmethod
    @authenticate
    def create_worker(worker_name, alias, api_key=None) -> Worker:      
        if not worker_name:
            error_log = ['No worker name provided.', 'Please provide a worker name and try again.']
            raise IntegrityException(format_error_log(error_log))

        create_request = {
            'url': f"{api_base_url}/app/v2/brains",
            'method': "post",
            'json': {
                'name': worker_name,
                'alias': alias,
                'default': False,
                'device': {
                    'platform': 'cloud'
                }
            },
            'headers': {
                'x-api-key': api_key,
            },
        }
        response = requests.request(**create_request)
        # print(response.json()['message'])
        if response.json()['message'] == "Error validating API key":
            error_log = ['Invalid API key.', 'Check if you are providing a valid API key and try again.']
            raise AuthException(format_error_log(error_log))

        worker = Worker.parse_obj(response.json()['results'])
        return worker
    
    @staticmethod
    @authenticate
    def start_worker(worker_id, auto_shutdown_behaviour=None, wait=False, api_key=None) -> Worker:
        start_request = {
            'url': f"{api_base_url}/app/v2/brains/start",
            'method': 'post',
            'json': {
                '_id': worker_id
            },
            'headers': {
                'x-api-key': api_key,
            }
        }

        if auto_shutdown_behaviour:
            start_request['json']['autoShutdownBehaviour'] = auto_shutdown_behaviour

        start_response = requests.request(**start_request)
        start_json = json.loads(start_response.text)

        worker = start_json['results']
        status = start_json['status']

        if status != 200:
            raise Exception('There was an error trying to start brain')
        
        if worker['status'] == 'STARTED':
            return start_json

        if wait:
            def start_confirmation_function():
                try:
                    health_state_response = requests.get(
                        f"{start_response.json()['results']['url']}/health?timesamp={int(time.time() * 1000)}",
                        timeout=2,
                        allow_redirects=True
                    )
                    return health_state_response.status_code == 200
                except requests.RequestException:
                    return False

            asyncio.run(poll(start_confirmation_function, 1000, 120000))
        return start_response.json()
    
    @staticmethod
    @authenticate
    def stop_worker(worker_id, wait=False, api_key=None) -> Worker:
        stop_request = {
            'url': f"{api_base_url}/app/v2/brains/stop",
            'method': 'post',
            'json': {
                '_id': worker_id
            },
            'headers': {
                'x-api-key': api_key,
            }
        }

        stop_response = requests.request(**stop_request)
        # if wait:
        #     def start_confirmation_function():
        #         try:
        #             health_state_response = requests.get(
        #                 f"{stop_response.json()['results']['url']}/health?timesamp={int(time.time() * 1000)}",
        #                 timeout=2,
        #                 allow_redirects=True
        #             )
        #             return health_state_response.status_code == 200
        #         except requests.RequestException:
        #             return False

        #     poll(start_confirmation_function, 1000, 120000)
        return stop_response.json()

    @staticmethod
    @authenticate
    def delete_worker(worker_id, api_key=None):
        request = {
            'url': f"{api_base_url}/app/v2/brains/{worker_id}",
            'method': "delete",
            'json': {},
            'headers': {
                'x-api-key': api_key,
            },
        }

        response = requests.request(**request)
        return response.json

    @staticmethod
    @authenticate
    async def call_worker(worker_url, msg, api_key=None):
        async with aiohttp.ClientSession(headers={ 'x-api-key': api_key }) as session:
            async with session.post(f"{worker_url}/send-maya-message", json=msg) as response:
                response_json = await response.json()
                return response_json
    
