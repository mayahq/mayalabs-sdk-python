def auth(subcommand):
    if subcommand == 'login':
        login()
    elif subcommand == 'logout':
        logout()
    elif subcommand == 'status':
        status()
    else:
        show_usage_guide()

def login():
    print('login handler here')

def logout():
    print('logout handler here')

def status():
    print('status handler here')

def show_usage_guide():
    print('USAGE')