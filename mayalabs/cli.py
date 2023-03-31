import argparse
from .session import Session
from .mayalabs import auth
from .function import Function

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
    auth.api_key = "mayakey-$2a$10$QBppphtMME9aDjeVYi3Ije/m18tYBhcQsqFqeOm7qtiYQeEu1hTOW"

    recipe = ""
    def on_message(message, task):
        nonlocal recipe
        recipe = message['recipe']

    if session_id is None:
        session = Session.new(script='')
        session_id = session._id
        print('Generating...\n')
    else:
        session = Session.get(session_id=session_id)
        session_id = session._id
        print('Modifying...\n')
    session.instruct(prompt=command, from_scratch=from_scratch, on_message=on_message)
    print(recipe)
    show_post_instruct_options(recipe=recipe, session_id=session_id)


def show_post_instruct_options(recipe, session_id):
    """
    Show the actions available after instruct response is completed.
    """
    while True:
        print("1. Deploy as function")
        print("2. Modify")
        print("3. Save to .nl\n")
        choice = input("Select an option and press Enter: ")

        if choice == "1":
            print("Deploying as function...")
            function = Function.create(name='Function69', script=recipe)
            function.deploy()
            print('Deployed.')
            exit()
        elif choice == "2":
            new_command = input("How do you want to modify this program? ")
            instruct(command=new_command, from_scratch=False, session_id=session_id)
            break
        elif choice == "3":
            print("Saving to .nl...")
            with open("output.nl", "w", encoding='utf-8') as output_file:
                output_file.write(recipe)
            print('Saved to output.nl file.')
            exit()
        else:
            print("Invalid choice. Please try again.")

# if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("function_name", help="The function to execute")
    # parser.add_argument("-c", "--command", help="The command to pass to function")
    # args = parser.parse_args()
    # command = args.command
    # instruct(command=command)
