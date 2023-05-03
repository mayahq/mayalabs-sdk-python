import os
import json
import getpass
from colorama import Fore, Style

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

def get_api_key(show_instructions):
    """
    Get the API key from the user or the cache file.
    """
    api_key = None
    need_api_key = True
    if os.path.exists(MAYA_CACHE_FILE):
        with open(MAYA_CACHE_FILE, "r+", encoding='UTF-8') as f:
            file_content = f.read()
            file_json = json.loads(file_content)
            if 'MAYA_API_KEY' in file_json:
                api_key = file_json['MAYA_API_KEY']
                need_api_key = False

    if need_api_key and show_instructions:
        print('API Key is missing. You can get one from https://app.mayalabs.io/settings/developers')
        print('Run mayalabs auth login to set it')
    return api_key

def print_usage_guide(command):
    print('I will be modified to print the usage instructions for:')
    print(command)