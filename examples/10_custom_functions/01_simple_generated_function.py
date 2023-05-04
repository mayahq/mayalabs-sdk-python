import mayalabs

script = """
1. trigger on recieve
2. run a custom function to 'add 5 to every element of {{msg.payload.list}}'
3. send response back
"""

function = mayalabs.Function(name="Custom_Function_1")

function.update(script=script)