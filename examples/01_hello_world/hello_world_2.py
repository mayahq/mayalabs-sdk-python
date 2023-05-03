# script to print Hello, World! on your developer console 
import mayalabs

script = """
1. trigger on receive message
2. set msg.{{payload}} to '{\"value\": \"Hello, World!\"}'
3. respond back with {{msg.payload}}
"""

function = mayalabs.Function(name="Hello_World_Demo")
function.update(script=script)

output = function.call(payload={})
print(output["value"])