# in this example a dynamic variable is set with string value :
# "Write a 150 word summary of Charles Dickens' Great Expectation"
import mayalabs

fn = mayalabs.Function(name="Handle_Variable_1")

script="""
1. trigger on receive
2. set {{msg.payload.prompt}} to "Write a 150 word summary of Charles Dickens' Great Expectations"
3. get a creative response from a large language model
4. respond back
"""

fn.update(script=script)

output = fn.call(payload={"trigger": 1})
print(output)