import mayalabs

mayalabs.auth.api_key = "mayakey-$2a$10$QBppphtMME9aDjeVYi3Ije/m18tYBhcQsqFqeOm7qtiYQeEu1hTOW"

script = """
1. receive message {{payload}}
2. respond back with {{payload}}
"""

function = mayalabs.Function.create(name="Function1", script=script)

function.deploy()

output = function.call(term = "Hello, World")