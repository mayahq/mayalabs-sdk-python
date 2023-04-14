import os
import json
import time
import argparse
import getpass
import requests
from colorama import Fore, Style
import mayalabs
from .session import Session
from .function import Function
from .utils.name_gen import get_random_name
from .utils.defaults import default_api_base_url
from halo import Halo
from simple_term_menu import TerminalMenu

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
        print(Style.BRIGHT + Fore.BLUE + 'Please paste your API key and press Enter.' + Style.RESET_ALL)
        api_key = getpass.getpass(prompt='You can get one from https://app.mayalabs.io/settings/developers: \n')
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
    initial_spinner_text = 'Generating...'
    if not from_scratch:
        print('')
        initial_spinner_text = 'Modifying...'
    initial_spinner = Halo(text=initial_spinner_text, text_color='cyan', spinner='dots')
    line_spinner = Halo(spinner='dots')
    def on_message(message, task):
        initial_spinner.stop()
        line_spinner.stop()
        nonlocal recipe
        recipe = message['recipe']
        modified_recipe = remove_stars_and_newlines(recipe)
        if from_scratch:
            clear_terminal()
            print_user_command(command=command)

        if message['metadata']['delivery'] == 'stream':
            print(modified_recipe)
        else:
            lines = modified_recipe.split('\n')
            for line in lines:
                time.sleep(0.4)
                print(line)

        if message['metadata']['status'] == 'complete':
            line_spinner.stop()
            if from_scratch:
                clear_terminal()
                print_user_command(command=command)
            if from_scratch:
                print(modified_recipe)
                print(Style.BRIGHT + Fore.GREEN + '\nGeneration successful.\n' + Style.RESET_ALL)
            else:
                print(Style.BRIGHT + Fore.GREEN + '\nModification successful.\n' + Style.RESET_ALL)
        else:
            line_spinner.start()

    if session_id is None:
        session = Session.new(script='')
        session_id = session._id
    else:
        session = Session.get(session_id=session_id)
        session_id = session._id
    if from_scratch:
        clear_terminal()
        print_user_command(command=command)
    initial_spinner.start()
    session.instruct(prompt=command, from_scratch=from_scratch, on_message=on_message)
    show_post_instruct_options(recipe=recipe, session_id=session_id)

def show_post_instruct_options(recipe, session_id):
    """
    Show the actions available after instruct response is completed.
    """
    menu_entries = ["Deploy as function", "Modify", "Save to .nl"]
    menu_cursor_style = ("fg_cyan", "bold")
    terminal_menu = TerminalMenu(menu_entries=menu_entries, menu_cursor_style=menu_cursor_style)
    while True:
        menu_entry_index = terminal_menu.show()
        choice = str(menu_entry_index + 1)

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

def clear_terminal():
    os.system('cls' if os.name=='nt' else 'clear')

def remove_stars_and_newlines(string):
    """
    Removes the (*), trailing whitespace and newline characters from a multi-line string.
    """
    return string.replace("(*)", "").strip()

def print_user_command(command):
    """
    Prints the command entered by the user in a box.
    """
    box_height = 2
    header = ' Instruction '
    header_len = len(header)
    box_width = len(command) + 4

    # Calculate the number of blank lines above and below the command
    remaining_height = box_height - 2
    top_lines = remaining_height // 2
    bottom_lines = remaining_height - top_lines

    print("╭" + "─" + header + "─" * (box_width - header_len - 1) + "╮")
    for i in range(top_lines):
        print("│  " + " " * (box_width - 4) + "  │")
    print("│  " + command.center(box_width - 4) + "  │")
    for i in range(bottom_lines):
        print("│  " + " " * (box_width - 4) + "  │")
    print("╰" + "─" * box_width + "╯")



