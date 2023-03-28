from mayalabs import Session
from mayalabs import Worker, WorkerClient, SessionClient
from typing import Any, Dict
import asyncio

class Function:
    def __init__(self, name, script, api_key=None):
        self.name : str = name
        self.script : str = script
        self.worker : Worker = None
        self.session : Session = None
        self.init(api_key=api_key)

    def init(self, api_key=None):
        """
        Initializes the function.
        Checks if the worker exists. If not, creates a new worker.
        Pass an api_key to override default and use a different profile.
        """
        if self.name is None:
            raise Exception("No name provided in the argument `name`")
        if self.script is None:
            raise Exception("No script provided in the argument `script`")
        try:
            # check if the worker exists    
            if api_key is None:
                self.worker = WorkerClient().get_worker_by_alias(self.name)
            else:
                self.worker = WorkerClient().get_worker_by_alias(self.name, api_key=api_key)

            if self.worker:
                print("Worker found.")
                if self.worker.session_id:
                    try:
                        self.session = SessionClient().get_session(self.worker.session_id)
                    except Exception as e:
                        print("Session not found. Error:", e)
        except:
            print("Worker not found.")
            pass

    def deploy(self):
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

        self.worker = self.session.deploy(worker_id=self.worker.id)

    def call(self, **kwargs : Dict) -> Dict:
        """
        Call the deployed function. 
        Arguments passed here are passed to the `msg` object in the script.
        A value like `msg['key']` can be accessed in the script by using {{key}}
        """
        call_task = asyncio.create_task(self.worker.call(kwargs))
        log_task = asyncio.create_task(self.worker.ws_client.create_listen_task())
        call_task.add_done_callback(log_task.cancel)

        tasks = asyncio.gather([call_task, log_task])
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(tasks)

        print('response:', response)

        return response
    
    def __call__(self, **kwds: Dict) -> Dict:
        """
        Call the deployed function. 
        Arguments passed here are passed to the `msg` object in the script.
        A value like `msg['key']` can be accessed in the script by using {{key}}
        """
        return self.call(**kwds)