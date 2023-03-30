import click
from .session import Session
from .mayalabs import auth

@click.command()
@click.argument('command_name')
@click.option('-c', '--command', type=str, required=True, help='The command to execute.')
def instruct(command_name, command):
    """
    Executes a command provided with the -c option.
    """
    # You can modify this function to do whatever you want with the command argument
    # print(f"Executing command '{command}' for '{command_name}'")
    auth.api_key = "mayakey-$2a$10$QBppphtMME9aDjeVYi3Ije/m18tYBhcQsqFqeOm7qtiYQeEu1hTOW"
    session = Session()
    session.instruct(prompt='get data', from_scratch=True)

if __name__ == '__main__':
    instruct()
