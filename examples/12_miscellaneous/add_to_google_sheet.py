import mayalabs

script = """
1. trigger on receive
2. Add all data to google sheet
3. send response back
"""

function = mayalabs.Function(name="gsheet_write")
function.update(script=script)

function.call({
    'name': 'Dushyant',
    'age': 22
})