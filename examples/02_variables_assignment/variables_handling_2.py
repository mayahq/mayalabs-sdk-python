# in this example a static configuration in step 2 is set with string value :
# "Wow, mate!"
import mayalabs

fn = mayalabs.Function(name="Handle_Variable_2")

script="""
1. inject default
2. print "Wow mate!"
"""

fn.update(script=script)

output = fn.call(payload={"trigger": 1})
print(output)