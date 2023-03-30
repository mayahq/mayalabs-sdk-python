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
            exit()

    session = Session.new(script='')
    print('Generating...\n')
    session.instruct(prompt=command, from_scratch=True, on_message=on_message)

# if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("function_name", help="The function to execute")
    # parser.add_argument("-c", "--command", help="The command to pass to function")
    # args = parser.parse_args()
    # command = args.command
    # instruct(command=command)
