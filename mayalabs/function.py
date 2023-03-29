from mayalabs import Session
from mayalabs import Worker, WorkerClient, SessionClient
from typing import Any, Dict
from .mayalabs import authenticate
from colorama import Fore, Style
import asyncio

class Function:
    # @authenticate
    def __init__(self, name, script = None, init = True):
        self.name : str = name
        self.script : str = script
        self.worker : Worker = None
        self.session : Session = None
        if init:
            self.init()

    @staticmethod
    def create(name, script):
        func = Function(
            name=name,
            script=script,
            init=False
        )

        worker = None
        try:
            worker = Worker.create(name=name, alias=name)
        except:
            raise Exception('Failed to create a worker for the function')

        session = None
        try:
            session = Session.new(script=script)
            worker.attach_session(session_id=session.id)
        except:
            raise Exception('Failed to create a new session for the worker')
        
        func.worker = worker
        func.session = session

        return func

    def init(self, api_key=None):
        """
        Initializes the function.
        Checks if the worker exists. If not, creates a new worker.
        Pass an api_key to override default and use a different profile.
        """
        if self.name is None:
            raise Exception("No name provided in the argument `name`")

        try:
            # check if the worker exists    
            if api_key is None:
                self.worker = WorkerClient().get_worker_by_alias(self.name)
            else:
                self.worker = WorkerClient().get_worker_by_alias(self.name, api_key=api_key)

            if self.worker:
                if self.worker.session_id:
                    try:
                        self.session = Session.get(session_id=self.worker.session_id)
                        self.script = self.session.script
                    except Exception as e:
                        print("Session not found. Error:", e)
                        raise e
        except Exception as err:
            print("Worker not found.")
            raise err

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

        self.session.deploy(worker_id=self.worker.id)

    def call(self, payload = {}, **kwargs) -> Dict:
        """
        Call the deployed function. 
        Arguments passed here are passed to the `msg` object in the script.
        A value like `msg['key']` can be accessed in the script by using {{key}}
        """
        print('[Maya]', Fore.CYAN + 'Making sure Function is online' + Style.RESET_ALL)
        self.worker.start(wait=True)
        return self.worker.call(msg = { **payload, **kwargs })
    
    def __call__(self, payload = {}) -> Dict:
        """
        Call the deployed function. 
        Arguments passed here are passed to the `msg` object in the script.
        A value like `msg['key']` can be accessed in the script by using {{key}}
        """
        return self.call(payload=payload)
    
    def clear(self):
        """
        Deletes the function by deleteing the associated session and the worker.
        """
        if self.session is not None:
            self.session.delete()
        if self.worker is not None:
            self.worker.delete()