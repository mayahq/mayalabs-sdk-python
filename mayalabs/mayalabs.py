import os
import click
from pathlib import Path
from .exceptions import AuthException
from .utils.logging import format_error_log
from .utils.auth import default_api_key


def return_error(err):
    raise err

def authenticate(func):
    def wrapped_function(*args, **kwargs):
        api_key = default_api_key()
        print("API KEY:", api_key)
        if not api_key:
            error_log = ['No API key provided.', 'Please provide an API key using mayalabs.api_key and try again.']
            raise AuthException(format_error_log(error_log))
        
        ret = func(*args, api_key=api_key, **kwargs)
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