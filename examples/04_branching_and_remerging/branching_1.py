import mayalabs
mayalabs.api_key = "mayakey-$2a$10$mBaPxpG3wUkqWOEJtz4ssOj1TmsWOUvivzgrCYSbB/pp/tVDPjy8C"
mayalabs.api_base = "https://api.dev.mayalabs.io"
fn = mayalabs.Function(name="Branching_Simple_1")
fn.clear()
script = """
1. set {{msg.payload}} to 30
    - 1.1. add 31 to {{msg.payload}}
    1.2. print {{msg.payload}}
    - 1.3. add 45 to {{msg.payload}}
    1.4. print {{msg.payload}}
"""

fn.update(script=script)