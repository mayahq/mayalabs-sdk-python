import os
import click
from pathlib import Path
from .exceptions import AuthException
from .utils.logging import format_error_log
from .utils.defaults import default_api_key


def return_error(err):
    raise err

def authenticate(func):
    def wrapped_function(*args, **kwargs):
        api_key = default_api_key()
        if not api_key:
            error_log = ["No API key provided.", "You can set your API key in code using 'mayalabs.api_key = <API-KEY>', or you can set the environment variable MAYA_API_KEY=<API-KEY>).", "You can generate API keys in the Maya web interface.", "See https://docs.mayalabs.io for details, or email humans@mayalabs.io if you have any questions."]
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