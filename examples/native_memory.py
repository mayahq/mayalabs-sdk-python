# This function created will error out on first run since the runtime 
# is not configured with the Maya API key (as you'll see in the log'). 
# You can configure the API key by opening the function in the browser 
# and opening the nodes with red triangles on them.

import mayalabs
mayalabs.api_key = '< your API key here >'

script = """
1. trigger on receiving request
2. store {{info}} in native memory
3. send response back
"""

fn = mayalabs.Function.create(name = 'native_memory', script = script)
fn.deploy()

res = fn.call({
    'info': 'Dushyant follows a push-pull-legs workout routine at the gym'
})

print('Docs added to native memory. Doc IDs:', res)