import mayalabs

fn = mayalabs.Function(name="Branching_Simple_1")

script = """
1. set {{msg.payload}} to 20
    - 1.1. add '5' to {{msg.payload}}
    1.2. print {{msg.payload}}
    - 1.3. add '10' to {{msg.payload}}
    1.4. print {{msg.payload}}
"""

fn.update(script=script)