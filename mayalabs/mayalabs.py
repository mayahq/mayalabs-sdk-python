import os
import click
from pathlib import Path
from .exceptions import AuthException
from .utils.logging import format_error_log


def return_error(err):
    raise err

api_key = None

class Mayalabs():
    def __init__(self):
        self.api_key = None


auth = Mayalabs()

def authenticate(func):
    def wrapped_function(*args, **kwargs):
        if not auth.api_key:
            error_log = ['No API key provided.', 'Please provide an API key using mayalabs.auth.api_key and try again.']
            raise AuthException(format_error_log(error_log))
        
        ret = func(*args, api_key=auth.api_key, **kwargs)
        return ret
    return wrapped_function
# @click.group()
# @click.pass_context
# def cli(ctx):
#     ctx.obj = mayalabs()
#     ctx.obj.load_key()

# @cli.command()
# @click.option('--api_key', help='Your API key')
# @click.pass_obj
# def config(sdk, api_key):
#     sdk.set_key(api_key)
#     click.echo('API key configured.')