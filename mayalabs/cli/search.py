import json
import requests
from tabulate import tabulate
from .helpers import get_api_key

def search(query):
    api_key = get_api_key(prompt_if_missing=True)
    response = requests.request('GET', url=f'https://api.dev.mayalabs.io/pac/v1/session/suggest?q={query}&display_length=20&limit=20', headers={'X-API-KEY': api_key}, timeout=30)
    response_text = json.loads(response.text)
    table = []
    for i in range(len(response_text)):
        current_object = response_text[i]
        table.append([current_object['id'] ,current_object['main_text'], current_object['num_samples']])
    print(tabulate(table, headers=['ID', 'COMMAND', 'NUMBER OF SAMPLES'], tablefmt='plain'))