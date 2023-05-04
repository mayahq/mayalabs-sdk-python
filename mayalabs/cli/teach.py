import os
import json
import requests
import mayalabs
from .helpers import get_api_key
from .helpers import print_usage_guide


def teach(file_path):
    if not file_path:
        print_usage_guide("teach")
        return

    api_key = get_api_key(show_instructions=True)
    if not api_key:
        return
    mayalabs.api_key = api_key

    if os.path.isfile(file_path):
        headers = {"X-API-KEY": api_key}
        files = {"files": open(file_path, "rb")}
        # Checking collision levels
        url = "https://api.dev.mayalabs.io/pac/v1/library/skill/verify"
        response = requests.post(url, headers=headers, files=files, timeout=30)
        response_text = json.loads(response.text)
        steps = response_text["reference"]["steps"]
        print(steps)

        max_collision = 0.0
        # find the max_collision from the nested data

        # Teaching
        # url = "https://api.dev.mayalabs.io/pac/v1/library/skill/teach"
        # response = requests.post(url, headers=headers, files=files, timeout=30)
        # response_text = json.loads(response.text)
        # print(response_text)
    else:
        print(f"{file_path} does not lead to a file.")
