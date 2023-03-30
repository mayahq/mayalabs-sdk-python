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
#     print('here')
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-c", "--command", help="Name of the user")
#     args = parser.parse_args()
#     print(args)
#     name = args.command
#     print(f"Hello, {name}")
