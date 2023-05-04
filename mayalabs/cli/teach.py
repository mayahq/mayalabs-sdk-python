import os
from .helpers import get_api_key
from .helpers import print_usage_guide


def teach(file_path):
    if not file_path:
        print_usage_guide("teach")
        return

    api_key = get_api_key(show_instructions=True)
    if not api_key:
        return

    if os.path.isfile(file_path):
        with open(file_path, "r") as f:
            contents = f.read()
        print(contents)
        # teach the contents of the file here
    else:
        print(f"The filepath {file_path} does not lead to a file.")
