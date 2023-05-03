import os
import sys
import shutil
import time
import getpass
import requests
from colorama import Fore, Style
import mayalabs
from ..session import Session
from ..function import Function
from ..utils.name_gen import get_random_name
from ..utils.defaults import default_api_base_url
from halo import Halo
from simple_term_menu import TerminalMenu
from .helpers import get_api_key
from .helpers import print_usage_guide

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

def instruct(command, from_scratch, session_id):
    """
    Executes a command provided with the -c option.
    """
    if not command:
        print_usage_guide('instruct')
        return

    api_key = get_api_key(show_instructions=True)
    if api_key:
        mayalabs.api_key = api_key
    else:
        return
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
            function = Function(name=random_name)
            function.update(script=recipe)
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
    max_width = shutil.get_terminal_size().columns

    command_lines = [command[i:i+max_width-8] for i in range(0, len(command), max_width-8)]

    header = ' Instruction '
    header_len = len(header)
    box_width = max(len(line) for line in command_lines) + 4

    print("╭" + "─" + header + "─" * (box_width - header_len - 1) + "╮")
    for line in command_lines:
        print("│  " + line.ljust(box_width - 4) + "  │")
    print("╰" + "─" * box_width + "╯")

    