import click
import sys
from .session import Session
from .function import Function
from .mayalabs import auth

@click.command()
@click.argument('command_name')
@click.option('-c', '--command', type=str, required=True, help='The command to execute.')
def instruct(command_name, command):
    """
    Executes a command provided with the -c option.
    """
    auth.api_key = "mayakey-$2a$10$QBppphtMME9aDjeVYi3Ije/m18tYBhcQsqFqeOm7qtiYQeEu1hTOW"
    # session = Session()
    # Hardocoding prompt because Click is a piece of shit and is not able to parse a provided string if it has spaces. Fuck!
    # prompt = 'create a 5 panel comic book of batman'

    # from test
    script = """
    1. receive message {{payload}}
    2. respond back with {{payload}}
    """

    function = Function.create(name='Function01', script=script)
    function.deploy()
    sys.stdout.flush()
    # end
    
    # function.deploy()
    # session.instruct(prompt=prompt, from_scratch=True)

if __name__ == '__main__':
    instruct()
