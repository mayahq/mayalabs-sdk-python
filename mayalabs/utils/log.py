from colorama import Fore, Style

prefix_length = 12

def log(*args, prefix='mayalabs', prefix_color=Fore.BLACK):
    final_prefix = f'|{prefix} |'
    if len(prefix) < prefix_length:
        final_prefix = f'|{prefix}' + (prefix_length - len(prefix)) * ' ' + ' |'
    elif len(prefix) > prefix_length:
        overshoot = len(prefix) - prefix_length
        num_chars = len(prefix) - overshoot - 2
        final_prefix = f'|{prefix[:num_chars]}..' + ' |'

    print(prefix_color + final_prefix + Style.RESET_ALL, *args)


# log('red', 'yo', prefix_color=Fore.RED)
# log('blue', 'yo', prefix_color=Fore.BLUE)
# log('green', 'yo', prefix_color=Fore.GREEN)
# log('magenta', 'yo', prefix_color=Fore.MAGENTA)
# log('black', 'yo', prefix_color=Fore.BLACK)
# log('yellow', 'yo', prefix_color=Fore.YELLOW)
# log('white', 'yo', prefix_color=Fore.WHITE)

# print('\nlight colors:')

# log('red', 'yo', prefix='Maya', prefix_color=Fore.LIGHTRED_EX)
# log('blue', 'yo', prefix='Maya', prefix_color=Fore.LIGHTBLUE_EX)
# log('green', 'yo', prefix='Maya', prefix_color=Fore.LIGHTGREEN_EX)
# log('magenta', 'yo', prefix='Maya', prefix_color=Fore.LIGHTMAGENTA_EX)
# log('black', 'yo', prefix='Maya', prefix_color=Fore.LIGHTBLACK_EX)
# log('yellow', 'yo', prefix='Maya', prefix_color=Fore.LIGHTYELLOW_EX)
# log('white', 'yo', prefix='Maya', prefix_color=Fore.LIGHTWHITE_EX)


# log('yo wtf', prefix='my stupid little runtime thats more than 20 chars')