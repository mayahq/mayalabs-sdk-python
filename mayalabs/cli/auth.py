import requests
import os
import json
import getpass
from colorama import Fore, Style
from .helpers import get_api_key
from .helpers import print_usage_guide
from ..utils.defaults import default_api_base_url

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")


def auth(subcommand):
    if subcommand == "login":
        login()
    elif subcommand == "logout":
        logout()
    elif subcommand == "whoami":
        user_name = whoami()
        if user_name:
            print(f"Authenticated as {user_name}")
        else:
            print("Not logged in")
    else:
        print_usage_guide("auth")


def login():
    api_key = getpass.getpass(prompt="Please enter your API key: ")
    file_json = {"MAYA_API_KEY": api_key}
    if os.path.isfile(MAYA_CACHE_FILE):
        with open(MAYA_CACHE_FILE, "r", encoding="UTF-8") as f:
            data = json.load(f)
            f.close()
        data["MAYA_API_KEY"] = api_key
        with open(MAYA_CACHE_FILE, "w", encoding="UTF-8") as f:
            f.write(json.dumps(data))
            f.close()
    else:
        with open(MAYA_CACHE_FILE, "w", encoding="UTF-8") as f:
            f.write(json.dumps(file_json))
            f.close()
    user_name = whoami()
    if user_name:
        print(f"Authenticated as {user_name}")
    else:
        print("Invalid API Key")


def logout():
    user_name = whoami()
    if user_name:
        print(f"Logging out {user_name}")
    else:
        print("Not logged in")
        return
    if os.path.isfile(MAYA_CACHE_FILE):
        with open(MAYA_CACHE_FILE, "r", encoding="UTF-8") as f:
            data = json.load(f)
            f.close()
        del data["MAYA_API_KEY"]
        with open(MAYA_CACHE_FILE, "w", encoding="UTF-8") as f:
            f.write(json.dumps(data))
            f.close()
    print("Logged out")


def whoami():
    url = f"{default_api_base_url()}/app/v2/profiles/whoami"
    api_key = get_api_key(show_instructions=False)
    if api_key:
        headers = {"X-API-KEY": api_key}
        response = requests.request("GET", url, headers=headers, timeout=30)
        response_dict = json.loads(response.text)
        name_value = response_dict["name"]
        return name_value
    else:
        return None
