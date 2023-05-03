import os
import sys
from colorama import Style
from tabulate import tabulate
from .auth import auth
from .search import search
from .instruct import instruct

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

def cli():
    """
    Use Maya from the command line.
    """
    arguments = sys.argv[1:]
    if len(arguments) == 0:
        print('Use Maya from the command line.')
        print(Style.BRIGHT + '\nUSAGE' + Style.RESET_ALL)
        print('mayalabs <command> <subcommand>')

        print(Style.BRIGHT + '\nCOMMANDS' + Style.RESET_ALL)
        table = [['auth:', 'Authenticate mayalabs'], ['instruct:', 'Instruct Maya'], ['search:', 'Search Maya']]
        print(tabulate(table, tablefmt='plain'))

        print(Style.BRIGHT + '\nEXAMPLES' + Style.RESET_ALL)
        print("$ mayalabs search 'comic book'")
        print("$ mayalabs instruct 'get data from gsheet'")

        print(Style.BRIGHT + '\nLEARN MORE' + Style.RESET_ALL)
        print('Read the manual at https://mayalabs.io/docs/cli\n')
    elif len(arguments) >= 1:
        first_arg = arguments[0]
        second_arg = arguments[1] if len(arguments) > 1 else None
        if first_arg == 'instruct':
            instruct(command=second_arg, from_scratch=True, session_id=None)
        elif first_arg == 'search':
            search(query=second_arg)
        elif first_arg == 'auth':
            auth(subcommand=second_arg)
