## Maya Labs Python SDK

A new way to program machines, using natural language.

WIP version : alpha - 0.0.1.

## Installation
```shell
pip3 install mayalabs

```

## Usage

```python 
import mayalabs

script = """
1. inject default
2. print {{payload}}
"""

mayalabs.auth.api_key = <MAYA_API_KEY>

#create session
session = mayalabs.Session.new(script=script)

#create worker
worker = mayalabs.Worker.new(name="Test Worker")
worker.start()

# generate session
session.generate()

# wait for generate and start to end
session.deploy(worker_id=worker.id)

# soon
output = session.call({ 'payload' : 'cool'})

# clear everything
session.delete()
worker.delete()

```
