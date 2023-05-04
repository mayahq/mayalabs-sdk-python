import mayalabs

script = """
1. add a button with label 'Spawn Workers'
	- 1.1. spawn a worker 'Growth' to run 'fetch all the users who signed up and send to channel #growth on slack, every day at 8pm'
    - 1.2. spawn a worker 'Monitor' which runs 'fetch all the users who churned this week and send to channel #growth on slack, every week on Monday'
    - 1.3. spawn a worker 'Market' which runs 'fetch all users grouped by location and send to channel #marketing on slack'
"""

function = mayalabs.Function(name="Worker_Example_1")

function.update(script=script)