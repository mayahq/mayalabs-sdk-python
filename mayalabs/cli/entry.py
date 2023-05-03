import os
import sys
import mayalabs
from colorama import Style
from tabulate import tabulate
from .auth import auth
from .search import search
from .instruct import instruct
from .helpers import print_usage_guide

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

def cli():
    """
    Use Maya from the command line.
    """
    arguments = sys.argv[1:]
    # If testing using dev key
    mayalabs.api_base = 'https://api.dev.mayalabs.io'
    if len(arguments) == 0:
        print_usage_guide('mayalabs')
    elif len(arguments) >= 1:
        first_arg = arguments[0]
        second_arg = arguments[1] if len(arguments) > 1 else None
        if first_arg == 'instruct':
            instruct(command=second_arg, from_scratch=True, session_id=None)
        elif first_arg == 'search':
            search(query=second_arg)
        elif first_arg == 'auth':
            auth(subcommand=second_arg)
