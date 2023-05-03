# this examples create a loop to count from 26 to 36 at increments of 1
# and return the last counted number
import mayalabs

script = """
1. trigger on receive message
2. set {{msg.payload}} to '{"num": 29}'
3. add 1 to {{msg.payload.num}}
4. print {{msg.payload.num}}
5. if {{msg.payload.num}} is less than 36
    - 5.1. go to step 3
6. else if {{payload.num}} is more than 36
    - 6.1. print {{msg.payload.num}}
7. respond back with {{msg.payload}}
"""

mayalabs.log_level = "debug"

function = mayalabs.Function(name="Looping_With_Conditionals")
function.update(script=script)

output = function.call(payload={"num": 1})
print(output)