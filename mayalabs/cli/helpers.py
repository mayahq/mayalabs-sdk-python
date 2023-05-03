import os
import json
import getpass
from colorama import Fore, Style

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

def get_api_key(prompt_if_missing):
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

    if need_api_key and prompt_if_missing:
        print(Style.BRIGHT + Fore.BLUE + 'Paste your API key and press Enter.' + Style.RESET_ALL)
        api_key = getpass.getpass(prompt='You can get one from https://app.mayalabs.io/settings/developers: \n')
        file_json = {"MAYA_API_KEY": api_key}
        with open(MAYA_CACHE_FILE, "w+", encoding='UTF-8') as f:
            f.write(json.dumps(file_json))
            f.close()
    return api_key