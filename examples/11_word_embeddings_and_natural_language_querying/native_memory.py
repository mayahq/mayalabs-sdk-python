# This function created will error out on first run since the runtime 
# is not configured with the Maya API key (as you'll see in the log'). 
# You can configure the API key by opening the function in the browser 
# and opening the nodes with red triangles on them.

import mayalabs

script = """
1. trigger on receiving request
2. store {{msg.payload.info}} in native memory
3. send response back
"""

fn = mayalabs.Function(name = 'Add_To_Native_Memory_1')
fn.update(script=script)

res = fn.call(payload={
    'info': 'Dushyant follows a push-pull-legs workout routine at the gym'
})

print('Docs added to native memory. Doc IDs:', res)

fn_ask = mayalabs.Function(name="Ask_From_Memory_1")

ask = """
1. trigger on receiving message
2. ask native memory 'What does Dushyant do?'
3. respond with {{msg.payload}}
"""

fn_ask.update(script=ask)

output = fn_ask.call(payload={
    "dummy": "trigger"
})

print(output)