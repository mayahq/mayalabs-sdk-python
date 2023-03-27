import os
import requests
from .utils.poll import poll
import time
from .consts import api_base_url, api_ws_url
from .mayalabs import authenticate

class Worker:
    def __init__(self) -> None:
        self.name : str = None
        self.alias : str = None
        self.id : str = None
        self.url : str = None
        self.status : str = None

    def start(self):
        return WorkerClient.start_worker(worker_id=self.id)

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

    def call(self, msg : dict):
        if self.id is None:
            raise Exception("Worker ID is not set")
        if self.url is None:
            self.update()
        try:
            response = WorkerClient.call_worker(worker_url=self.url, msg=msg)
            return response
        except Exception as e:
            raise Exception("Something went wrong while calling worker with message.")

    @classmethod
    def parse_obj(cls, obj):
        worker = cls()
        worker.id = obj.get('_id', None)
        worker.url = obj.get('url', None)
        worker.status = obj.get('status', None)
        worker.name = obj.get('name', None)
        worker.alias = obj.get('alias', None)
        return worker
    
    @classmethod
    def new(cls, name, alias=None):
        worker = WorkerClient.create_worker(worker_name=name, alias=alias)
        return worker



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
        print(create_request)
        response = requests.request(**create_request)
        print(response.json())
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

            poll(start_confirmation_function, 1000, 120000)
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
    def call_worker(worker_url, msg, api_key=None):
        request = {
            'url': f"{worker_url}/send-maya-message",
            'method': "post",
            'json': msg,
            'headers': {
                'x-api-key': api_key,
            },
            'timeout' : 30
        }

        response = requests.request(**request)
        return response.json()

    
    # def get_worker_health(self, worker_id):
    #     response = self.get_worker(worker_id)
    #     health_state_response = requests.get(
    #         f"{response['results']['url']}/health?timesamp={int(time.time() * 1000)}",
    #         timeout=2,
    #         allow_redirects=True
    #     )
    #     return health_state_response
