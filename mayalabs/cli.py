import os
import json
import time
import argparse
import requests
from colorama import Fore, Style
import mayalabs
from .session import Session
from .function import Function
from .utils.name_gen import get_random_name
from .utils.defaults import default_api_base_url

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

def cli():
    """
    Main function for the mayalabs CLI.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("function_name", help="The function to execute")
    parser.add_argument("-c", "--command", help="The command to pass to function")
    parser.add_argument("-k", "--key", help="The API Key to use")
    args = parser.parse_args()
    command = args.command
    key = args.key
    function_name = args.function_name
    if function_name == "instruct" and not command:
        print("Please provide a command with the -c flag")
    elif function_name == "instruct" and command:
        instruct(command=command, from_scratch=True, session_id=None)
    elif function_name == "set" and not key:
        print("Please provide the API key with the -k flag")
    elif function_name == "set" and key:
        set_key(api_key=key)
    elif function_name == "whoami":
        whoami()

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
        print(Style.BRIGHT + Fore.BLUE + 'Please paste your API key.' + Style.RESET_ALL)
        api_key = input('You can get one from https://app.mayalabs.io/settings/developers: \n')
        file_json = {"MAYA_API_KEY": api_key}
        with open(MAYA_CACHE_FILE, "w+", encoding='UTF-8') as f:
            f.write(json.dumps(file_json))
            f.close()
    return api_key

def instruct(command, from_scratch, session_id):
    """
    Executes a command provided with the -c option.
    """
    mayalabs.api_key = get_api_key(prompt_if_missing=True)
    # to be used if testing using devapp
    # mayalabs.api_base = "https://api.dev.mayalabs.io"
    recipe = ""
    def on_message(message, task):
        nonlocal recipe
        recipe = message['recipe']

    if session_id is None:
        session = Session.new(script='')
        session_id = session._id
        print(Style.BRIGHT + Fore.CYAN + 'Generating...\n' + Style.RESET_ALL)
    else:
        session = Session.get(session_id=session_id)
        session_id = session._id
        print(Style.BRIGHT + Fore.CYAN + 'Modifying...\n' + Style.RESET_ALL)
    session.instruct(prompt=command, from_scratch=from_scratch, on_message=on_message)

    lines = recipe.split('\n')
    num_lines = len(lines)

    for i, line in enumerate(lines):
        print(line)
        if i < num_lines - 1:
            time.sleep(1)

    if from_scratch:
        print(Style.BRIGHT + Fore.GREEN + 'Generation successful.\n' + Style.RESET_ALL)
    else:
        print(Style.BRIGHT + Fore.GREEN + 'Modification successful.\n' + Style.RESET_ALL)

    show_post_instruct_options(recipe=recipe, session_id=session_id)


def show_post_instruct_options(recipe, session_id):
    """
    Show the actions available after instruct response is completed.
    """
    while True:
        print(Style.BRIGHT + '1.' + Style.RESET_ALL + ' Deploy as function')
        print(Style.BRIGHT + '2.' + Style.RESET_ALL + ' Modify')
        print(Style.BRIGHT + '3.' + Style.RESET_ALL + ' Save to .nl\n')
        choice = input(Style.BRIGHT + Fore.BLUE + 'Select an option and press Enter: ' + Style.RESET_ALL)

        if choice == "1":
            print(Style.BRIGHT + Fore.CYAN + 'Deploying as function...\n' + Style.RESET_ALL)
            random_name = "SDK:" + get_random_name()
            function = Function.create(name=random_name, script=recipe)
            function.deploy()
            exit()
        elif choice == "2":
            new_command = input(Style.BRIGHT + Fore.BLUE + 'How do you want to modify this program? ' + Style.RESET_ALL)
            instruct(command=new_command, from_scratch=False, session_id=session_id)
            break
        elif choice == "3":
            with open("output.nl", "w", encoding='utf-8') as output_file:
                output_file.write(recipe)
            print(Style.BRIGHT + Fore.CYAN + 'Saved to output.nl file.' + Style.RESET_ALL)
            exit()
        else:
            print(Style.BRIGHT + Fore.RED + 'Invalid choice. Please try again.' + Style.RESET_ALL)

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