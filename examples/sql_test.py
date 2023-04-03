import os
import mayalabs

mayalabs.api_key = "<API_KEY_HERE>"


script = """
1. trigger on receiving (*)
2. query mysql with query 'SELECT * FROM BusinessPartners;' (*)
3. Show in a table with button 'Approve this' (*)
    - 3.1. print to screen {{payload.result}} (*)
    3.2 send a response back (*)
"""

function = mayalabs.Function(name="Function1", script=script)

function.deploy()

output = function.call()