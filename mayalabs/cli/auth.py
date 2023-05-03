import requests
import os
import json
from colorama import Fore, Style
from .helpers import get_api_key
from ..utils.defaults import default_api_base_url

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

def auth(subcommand):
    if subcommand == 'login':
        login()
    elif subcommand == 'logout':
        logout()
    elif subcommand == 'status':
        status()
    else:
        show_usage_guide()

def login():
    print('login handler here')

def logout():
    print('logout handler here')

def status():
    print('status handler here')

def show_usage_guide():
    print('USAGE')

def set_key(api_key):
    "Sets the API key provided using the -k option."
    file_json = {"MAYA_API_KEY": api_key}

    # Check if file exists
    if os.path.isfile(MAYA_CACHE_FILE):
        # Read existing data
        with open(MAYA_CACHE_FILE, "r", encoding='UTF-8') as f:
            data = json.load(f)
            f.close()
        # Update data
        data["MAYA_API_KEY"] = api_key
        # Write back to file
        with open(MAYA_CACHE_FILE, "w", encoding='UTF-8') as f:
            f.write(json.dumps(data))
            f.close()
    else:
        # Create new file
        with open(MAYA_CACHE_FILE, "w", encoding='UTF-8') as f:
            f.write(json.dumps(file_json))
            f.close()

def whoami():
    "Display information about the user."
    url = f"{default_api_base_url()}/app/v2/profiles/whoami"
    payload={}
    api_key = get_api_key(prompt_if_missing=False)
    if api_key:
        headers = { 'X-API-KEY': api_key }
        response = requests.request("GET", url, headers=headers, data=payload)
        response_dict = json.loads(response.text)
        name_value = response_dict["name"]
        print(name_value)
    else:
        print(Style.BRIGHT + Fore.RED + 'You have not provided an API key.' + Style.RESET_ALL)
        print("You can set the API key using mayalabs set -k '<YOUR_API_KEY>'")