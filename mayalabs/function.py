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
    def __init__(self, name, create=False, script=None, deploy=False):
        """Initailize remote Maya function. A Maya function is a managed compute, storage and network
        infrastructure on which business logic defined gets deployed and executed

        Args:
            name (str, required): unique name of the function, this should be unique for your profile.
            create (bool, optional): A True value attempts to create function of the provided name. It raises exception if a function of same name already exists. Defaults to False.
            script (str, optional): Step by step sequence of business logic to deploy and execute on the function. Defaults to None.
            deploy (bool, option): A True value would require providing a script and immediately attempts deploy of the business logic. Default to False. 
        """
        self.name : str = name
        self.worker : Worker = None
        self.session : Session = None
        self._get_or_create(name=self.name, create=create, script=script, deploy=deploy)

    @staticmethod
    def exists(name):
        pass
        existing_worker = Worker.get_by_alias(alias=name)
        if existing_worker is None:
            return False
        
        return True


    # @staticmethod
    def _get_or_create(self, name, create, script, deploy):
        if create:
            log(Fore.LIGHTRED_EX + f'it is not recommended to initialize Function with create=True in your production environments\nThe function name are unique within your profile and create=True may raise exception if an existing function of same name exists on your profile', prefix='[WARN]')
        try:
            existing_worker = Worker.get_by_alias(alias=name)
            session_id = existing_worker.session_id if existing_worker.session_id else None
            log(Fore.YELLOW + f'Found existing [{existing_worker.alias}]. Reusing.' + Style.RESET_ALL, prefix='mayalabs')
        except Exception as err:
            if create:
                session_id = None
                log(Fore.YELLOW + f'Creating new [{name}]' + Style.RESET_ALL, prefix='mayalabs')
                existing_worker = Worker.create(name=name, alias=name)
            else:
                log(Fore.RED + f'Could not find function [{name}] on your profile' + Style.RESET_ALL, prefix='mayalabs')
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
        # return func
        # else:
        #     func = Function(
        #         name=name,
        #         script=script,
        #         init=False
        #     )

        #     worker = None
        #     worker = Worker.create(name=name, alias=name)

        #     session = None
        #     try:
        #         session = Session.new(script=script)
        #         worker.attach_session(session_id=session.id)
        #     except:
        #         raise Exception('Failed to create a new session for the worker')
            
        #     func.worker = worker
        #     func.session = session

        #     return func
   
    # @authenticate
    # def init(self, api_key=None):
    #     """
    #     Initializes the function.
    #     Checks if the worker exists. If not, creates a new worker.
    #     Pass an api_key to override default and use a different profile.
    #     """
    #     if self.name is None:
    #         raise Exception("No name provided in the argument `name`")

    #     try:
    #         # check if the worker exists    
    #         if api_key is None:
    #             raise Exception("No api_key set, get your API Key from https://app.mayalabs.io/settings/developers/")
    #         else:
    #             self = self.get_or_create()

    #         if self.worker:
    #             if self.worker.session_id:
    #                 try:
    #                     self.session = Session.get(session_id=self.worker.session_id)
    #                     self.script = self.session.script
    #                 except Exception as e:
    #                     print("Session not found. Error:", e)
    #                     raise e
    #     except Exception as err:
    #         print("Worker not found.")
    #         raise err

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
                self.worker.start(wait=True)
        elif self.worker.status == "STOPPED" or self.worker.status == "PENDING":
            log(Fore.CYAN + 'Making sure the worker is online...' + Style.RESET_ALL, prefix='mayalabs')
            self.worker.start(wait=True)
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
    
    def delete(self):
        """
        Deletes the function by deleteing the associated session and the worker.
        """
        if self.session is not None:
            self.session.delete()
        if self.worker is not None:
            self.worker.delete()

    def update(self, script: str):
        """Updates the business logic on the function and deploys it. Such deployment is irreversible, use with caution.
        Args:
            script (str): Step by step sequence of business logic to deploy and execute on the function.
        """
        self.session.script = script
        self.session.change()
        self.session._deploy(worker_id=self.worker.id, update=True)