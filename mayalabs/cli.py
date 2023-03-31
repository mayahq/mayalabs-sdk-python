import os
import platform
import argparse
from colorama import Fore, Style
from .session import Session
from .mayalabs import auth
from .function import Function
from .utils.name_gen import get_random_name

def cli():
    """
    Main function for the mayalabs CLI.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("function_name", help="The function to execute")
    parser.add_argument("-c", "--command", help="The command to pass to function")
    args = parser.parse_args()
    command = args.command
    function_name = args.function_name
    if function_name == "instruct" and not command:
        print("Please provide a command with the -c flag")
    elif function_name == "instruct" and command:
        instruct(command=command, from_scratch=True, session_id=None)


def instruct(command, from_scratch, session_id):
    """
    Executes a command provided with the -c option.
    """
    api_key = os.environ.get('MAYA_API_KEY')
    sys_platform = platform.system()
    if api_key is None:
        print(Style.BRIGHT + Fore.RED + 'You have not provided an API Key.' + Style.RESET_ALL)
        if sys_platform == 'Windows':
            print('You can set it by running the following in your PowerShell:\n')
            print(Style.BRIGHT + 'setx MAYA_API_KEY "YOUR_API_KEY"' + Style.RESET_ALL)
        else:
            print('You can set it by running the following in your terminal:\n')
            print(Style.BRIGHT + 'export MAYA_API_KEY="YOUR_API_KEY"' + Style.RESET_ALL)
        print(Style.DIM + r"Remember to escape '$' signs with a backslash (\)" + Style.RESET_ALL)
        exit()

    auth.api_key = api_key
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
    print(recipe)
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

# if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("function_name", help="The function to execute")
    # parser.add_argument("-c", "--command", help="The command to pass to function")
    # args = parser.parse_args()
    # command = args.command
    # instruct(command=command)
