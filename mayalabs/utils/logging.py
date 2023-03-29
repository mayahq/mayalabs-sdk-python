from colorama import Fore, Style

def format_error_log(arr):
    if not arr:
        return ''
    styled_strings = [f"{Fore.RED}{s}{Style.RESET_ALL}" for s in arr]
    return "\n".join(styled_strings)
