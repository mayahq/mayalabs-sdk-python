from mayalabs import Session
from mayalabs import Worker, WorkerClient, SessionClient
from typing import Any, Dict
from .mayalabs import authenticate
from .utils.log import log
from colorama import Fore, Style
from .exceptions import IntegrityException
from .utils.logging import format_error_log
import random
import asyncio, os

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
    def exists(name):
        pass
        existing_worker = Worker.get_by_alias(alias=name)
        if existing_worker is None:
            return False
        
        return True

    @staticmethod
    def create(name, script):
        if os.environ.get("MAYA_ENVIRONMENT") == "development":
            log(Style.BRIGHT + Fore.YELLOW + 'DEVELOPMENT MODE' + Style.RESET_ALL, prefix='mayalabs')
            try:
                existing_worker = Worker.get_by_alias(alias=name)
                session_id = existing_worker.session_id if existing_worker.session_id else None
                log(Fore.YELLOW + f'Found existing [{existing_worker.alias}]. Reusing.' + Style.RESET_ALL, prefix='mayalabs')
            except Exception as err:
                session_id = None
                log(Fore.YELLOW + f'Creating new [{name}]' + Style.RESET_ALL, prefix='mayalabs')
                existing_worker = Worker.create(name=name, alias=name)
            try:
                if session_id is not None:
                    existing_session = Session.get(session_id=session_id)
                    existing_session.script = script
                else:
                    existing_session = Session.new(script=script)
            except Exception as err:
                raise err
            func = Function(
                name=name,
                script=script,
                init=False
            )
            try:
                existing_worker.attach_session(session_id=existing_session.id)
            except Exception as err:
                log(Fore.RED + f'Failed to attach session to worker [{existing_worker.alias}]' + Style.RESET_ALL, prefix='mayalabs')
                raise err
            func.worker = existing_worker
            func.session = existing_session
            return func
        else:
            func = Function(
                name=name,
                script=script,
                init=False
            )

            worker = None
            worker = Worker.create(name=name, alias=name)

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
        if not isinstance(payload, dict):
            error_log = [
                "Argument must be a dictionary.",
                f"Received {type(payload).__name__}, expected a dictionary."]
            raise IntegrityException(format_error_log(error_log))

        log(Fore.CYAN + 'Making sure the worker is online...' + Style.RESET_ALL, prefix='mayalabs')
        self.worker.start(wait=True)
        return self.worker.call(msg = { **payload, **kwargs }, session=self.session)
    
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