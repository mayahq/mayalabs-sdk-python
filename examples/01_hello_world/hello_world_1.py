# script to print Hello, World! on Maya IDE/editor debug console
import mayalabs

script = """
1. trigger on receive message
    - 1.1. set {{msg.payload}} to 'Hello, World!'
    1.2. print {{msg.payload}}
    - 1.3. go to step 2
2. respond back with {{msg.payload}}
"""

function = mayalabs.Function(name="Hello_World_Demo")

function.update(script=script)

output = function.call(payload={})