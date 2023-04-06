import mayalabs

def default_api_base_url() -> str:
    if mayalabs.api_base is not None:
        return mayalabs.api_base
    else:
        return "https://api.mayalabs.io"
    
def default_api_ws_url() -> str:
    api_base = default_api_base_url()
    if api_base == "https://api.mayalabs.io":
        return "wss://paccomms.prod.mayalabs.io/socket"
    elif api_base == "https://api.dev.mayalabs.io":
        return "wss://paccomms.pac.dev.mayalabs.io/socket"
    else:
        raise Exception(
            f"Could not find a websocket URL associated with {api_base}. Make sure mayalabs.api_base is set to 'https://api.mayalabs.io'"
        )

def default_api_key() -> str:
    if mayalabs.api_key is not None:
        return mayalabs.api_key
    else:
        raise Exception(
            "No API key provided. You can set your API key in code using 'mayalabs.api_key = <API-KEY>', or you can set the environment variable MAYA_API_KEY=<API-KEY>). You can generate API keys in the Maya web interface. See https://docs.mayalabs.io for details, or email humans@mayalabs.io if you have any questions."
        )

def default_log_level() -> str:
    if mayalabs.log_level is not None:
        return mayalabs.log_level
    else:
        return "info"