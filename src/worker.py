import os
from pydantic import BaseModel
import requests
from poll import poll

class WorkspaceClient:
    def __init__(self, backend_base_url, api_key):
        self.backend_base_url = backend_base_url
        self.api_key = api_key

    def get_workspace(self, workspace_id, alias=None):
        request = {
            'url': f"{self.backend_base_url}/v2/brains/{workspace_id}",
            'method': "get",
            'json': {
                'workspaceId': workspace_id,
                'alias': alias
            },
            'headers': {
                'x-api-key': self.api_key,
            },
        }

        response = requests.request(**request)
        return response.json()

    def get_workspace_by_alias(self, alias):
        request = {
            'url': f"{self.backend_base_url}/v2/brains/getByAlias/{alias}",
            'method': "get",
            'headers': {
                'x-api-key': self.api_key,
            },
        }

        response = requests.request(**request)
        results = response.json().get('results', None)
        return results

    def search_workspace_by_name(self, name):
        request = {
            'url': f"{self.backend_base_url}/v2/brains/search?name={name}",
            'method': 'get',
            'headers': {
                'x-api-key': self.api_key
            }
        }

        response = requests.request(**request)
        data = response.json()
        return data[0] if len(data) > 0 else None

    def create_workspace(self, workspace_name, alias):
        create_request = {
            'url': f"{self.backend_base_url}/v2/brains",
            'method': "post",
            'json': {
                'name': workspace_name,
                'alias': alias,
                'default': False,
                'device': {
                    'platform': 'cloud'
                }
            },
            'headers': {
                'x-api-key': self.api_key,
            },
        }

        response = requests.request(**create_request)
        return response.json()

    def start_workspace(self, workspace_id, auto_shutdown_behaviour=None):
        start_request = {
            'url': f"{self.backend_base_url}/v2/brains/start",
            'method': 'post',
            'json': {
                '_id': workspace_id
            },
            'headers': {
                'x-api-key': self.api_key,
            }
        }

        if auto_shutdown_behaviour:
            start_request['json']['autoShutdownBehaviour'] = auto_shutdown_behaviour

        start_response = requests.request(**start_request)

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

    def delete_workspace(self, workspace_id):
        request = {
            'url': f"{self.backend_base_url}/v2/brains/{workspace_id}",
            'method': "delete",
            'json': {},
            'headers': {
                'x-api-key': self.api_key,
            },
        }

        response = requests.request(**request)
        return response.json
