# this examples create a program that on being given a number responds if the number
# was either less than or equal to 18, less than 36 or greater than or equal to 36
import mayalabs

script = """
1. trigger on receive message
2. if {{msg.payload.num}} is less or equal to 18
    - 2.1 set {{msg.payload.response}} to "Number less than or equal to 18"
    2.2. print "Number less than or equal to 18"
3. if {{msg.payload.num}} is less than 36
    - 3.1 set {{msg.payload.response}} to "Number less than 36"
    3.2. print "Number less than 36"
4. set {{msg.payload.response}} to "Number greater than or equal to 36"
5. print "Number is greater than or equal to 36"
7. respond back with {{msg.payload}}
"""

function = mayalabs.Function(name="Conditionals")
function.update(script=script)

output = function.call(payload={"num": 1})
print(output)