## Maya Python SDK

For development

```
import src as mayalabs

script = """
1. inject default
2. print {{payload}}
"""
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
output = session.call({ 'payload' : "cool"})

# clear everything
session.delete()
worker.delete()

```
