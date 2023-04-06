from .session import Session
from .worker import Worker
from .worker import WorkerClient
from .session import SessionClient
from .function import Function
from .mayalabs import authenticate
import os

api_key = os.environ.get("MAYA_API_KEY")
api_base = os.environ.get("MAYA_API_BASE", "https://api.mayalabs.io")
log_level = os.environ.get("MAYA_LOG_LEVEL", "info")