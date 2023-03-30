import click
from .session import Session
from .function import Function
from .mayalabs import auth

def cli():
    """
    What
    """
    instruct()
    return

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
