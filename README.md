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

script = """
1. trigger on receive
2. send back response
"""

function = mayalabs.Function(name="Function1", script=script)

function.deploy()

output = function.call({ "term" : "alive"})

function.clear()
```
