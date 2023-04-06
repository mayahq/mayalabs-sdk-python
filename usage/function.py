import mayalabs

mayalabs.api_key = "<API_KEY_HERE>"

script = """
1. inject default
2. print {{term}}
"""

function = mayalabs.Function(name="Function1", script=script)