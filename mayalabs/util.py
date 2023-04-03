import mayalabs

def default_api_key() -> str:
    if mayalabs.api_key is not None:
        return mayalabs.api_key
    else:
        raise Exception(
            "No API key provided. You can set your API key in code using 'openai.api_key = <API-KEY>', or you can set the environment variable OPENAI_API_KEY=<API-KEY>). If your API key is stored in a file, you can point the openai module at it with 'openai.api_key_path = <PATH>'. You can generate API keys in the OpenAI web interface. See https://onboard.openai.com for details, or email support@openai.com if you have any questions."
        )