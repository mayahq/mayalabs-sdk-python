import click
from .session import Session
from .function import Function
from .mayalabs import auth

# @click.group
def cli():
    # instruct()
    print('inside cli')
    return

def instruct():
    """
    Executes a command provided with the -c option.
    """
    print('is this working?')
    auth.api_key = "mayakey-$2a$10$QBppphtMME9aDjeVYi3Ije/m18tYBhcQsqFqeOm7qtiYQeEu1hTOW"

    # deploy
    # script = """
    # 1. receive message {{payload}}
    # 2. respond back with {{payload}}
    # """
    # function = Function.create(name='Function1', script=script)
    # function.deploy()
    # end

    # def on_message(message):
    #     # print(f'Got message: {message}')
    #     print('Got message')

    # # instruct
    # session = Session.new(script='')
    # print(session)
    # prompt = 'get reddit results'
    # print(prompt)
    # result = session.instruct(prompt=prompt, from_scratch=True, on_message=on_message)
    # print(result)
    # end
    print('woooooooooooo')
    return
    
