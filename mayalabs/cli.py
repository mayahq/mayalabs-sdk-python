import argparse
from .session import Session
from .function import Function
from .mayalabs import auth

def cli():
    """
    Something
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="The command to execute")
    parser.add_argument("-c", "--command_name", help="Name of the user")
    args = parser.parse_args()
    print(args)
    name = args.command_name
    print(f"Hello, {name}")


def instruct():
    """
    Executes a command provided with the -c option.
    """
    auth.api_key = "mayakey-$2a$10$QBppphtMME9aDjeVYi3Ije/m18tYBhcQsqFqeOm7qtiYQeEu1hTOW"

    # deploy
    # script = """
    # 1. receive message {{payload}}
    # 2. respond back with {{payload}}
    # """
    # function = Function.create(name='Function1', script=script)
    # function.deploy()
    # end

    def on_message(message):
        print(message['recipe'])
        if message['metadata']['status'] == 'complete':
            exit()

    # # instruct
    session = Session.new(script='')
    prompt = 'create a 5 panel comic book of batman'
    print('Generating...\n')
    session.instruct(prompt=prompt, from_scratch=True, on_message=on_message)
    # end

# if __name__ == "__main__":
#     print('here')
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-c", "--command", help="Name of the user")
#     args = parser.parse_args()
#     print(args)
#     name = args.command
#     print(f"Hello, {name}")
