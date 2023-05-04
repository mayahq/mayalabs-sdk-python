import os
import json
import getpass
from colorama import Fore, Style
from tabulate import tabulate

MAYA_CACHE_FILE = os.path.join(os.path.expanduser("~"), ".mayalabs")

guide = {
    "mayalabs": {
        "description": "Use Maya from the command line.",
        "usage": "mayalabs <command> <subcommand>",
        "commands_table": [
            ["auth:", "Authenticate mayalabs"],
            ["instruct:", "Instruct Maya"],
            ["search:", "Search Maya"],
        ],
        "examples": [
            "$ mayalabs search 'comic book'",
            "$ mayalabs instruct 'get data from gsheet'",
        ],
    },
    "auth": {
        "description": "Authenticate Maya.",
        "usage": "mayalabs auth <subcommand>",
        "commands_table": [
            ["login:", "Login to Maya"],
            ["whoami:", "Check authorized user"],
            ["logout:", "Logout of Maya"],
        ],
        "examples": ["$ mayalabs auth login", "$ mayalabs auth whoami"],
    },
    "search": {
        "description": "Search Maya.",
        "usage": "mayalabs search <query>",
        "commands_table": [],
        "examples": [
            "$ mayalabs search 'comic book'",
            "$ mayalabs search 'postgresql'",
        ],
    },
    "instruct": {
        "description": "Instruct Maya.",
        "usage": "mayalabs instruct <instruction>",
        "commands_table": [],
        "examples": [
            "$ mayalabs instruct 'send emails from gsheet'",
            "$ mayalabs instruct 'scrape wikipedia for Alan Turing'",
        ],
    },
}


def print_usage_guide(command):
    print(guide[command]["description"])
    print(Style.BRIGHT + "\nUSAGE" + Style.RESET_ALL)
    print(guide[command]["usage"])

    table = guide[command]["commands_table"]
    if len(table) >= 1:
        print(Style.BRIGHT + "\nCOMMANDS" + Style.RESET_ALL)
        print(tabulate(table, tablefmt="plain"))

    print(Style.BRIGHT + "\nEXAMPLES" + Style.RESET_ALL)
    for i in range(len(guide[command]["examples"])):
        print(guide[command]["examples"][i])

    print(Style.BRIGHT + "\nLEARN MORE" + Style.RESET_ALL)
    print("Read the manual at https://mayalabs.io/docs/cli\n")


def get_api_key(show_instructions):
    """
    Get the API key from the user or the cache file.
    """
    api_key = None
    need_api_key = True
    if os.path.exists(MAYA_CACHE_FILE):
        with open(MAYA_CACHE_FILE, "r+", encoding="UTF-8") as f:
            file_content = f.read()
            file_json = json.loads(file_content)
            if "MAYA_API_KEY" in file_json:
                api_key = file_json["MAYA_API_KEY"]
                need_api_key = False

    if need_api_key and show_instructions:
        print(
            "API Key is missing. You can get one from https://app.mayalabs.io/settings/developers"
        )
        print("Run mayalabs auth login to set it")
    return api_key
