## Maya Labs Python SDK

A new way to program machines, using natural language.

WIP version : alpha - 0.0.1.

Requirements : Python and PIP >v3.6+ and <3.10

## Installation

```shell
pip install mayalabs

```

## Usage

```python
import mayalabs

mayalabs.api_key = <MAYA_API_KEY>

script = """
1. receive message {{payload}}
2. respond back with {{payload}}
"""

function = mayalabs.Function.create(name="Function1", script=script)

function.deploy()

output = function.call(term = "Hello, World")

# this will stop and delete your worker from profile. Comment out to view it on your worker dashboard.
function.clear()
```
