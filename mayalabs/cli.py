import argparse
from .session import Session
from .mayalabs import auth

def cli():
    """
    Something
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
        instruct(command=command)


def instruct(command):
    """
    Executes a command provided with the -c option.
    """
    auth.api_key = "mayakey-$2a$10$QBppphtMME9aDjeVYi3Ije/m18tYBhcQsqFqeOm7qtiYQeEu1hTOW"

    def on_message(message):
        print(message['recipe'])
        if message['metadata']['status'] == 'complete':
            print('Recipe generation complete.')
            # show_post_instruct_options()

    session = Session.new(script='')
    print('Generating...\n')
    session.instruct(prompt=command, from_scratch=True, on_message=on_message)

def show_post_instruct_options():
    """
    Show the actions available after instruct response is completed.
    """
    while True:
        print("1. Deploy as function")
        print("2. Modify")
        print("3. Cancel")
        print("4. Save to .nl")
        choice = input("Select an option and press Enter: ")

        if choice == "1":
            # TODO: implement the Deploy as function option
            print("Deploying as function...")
            break
        elif choice == "2":
            # TODO: implement the Modify option
            print("Modifying...")
            break
        elif choice == "3":
            # TODO: implement the Cancel option
            print("Cancelling...")
            break
        elif choice == "4":
            # TODO: implement the Save to .nl option
            print("Saving to .nl...")
            break
        else:
            print("Invalid choice. Please try again.")

# if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("function_name", help="The function to execute")
    # parser.add_argument("-c", "--command", help="The command to pass to function")
    # args = parser.parse_args()
    # command = args.command
    # instruct(command=command)
