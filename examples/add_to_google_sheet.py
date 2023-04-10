# This function has two requirements - 
# 1. You need to connect Maya to Google sheets. You can do so by
#    going to Settings > Integrations > Google Sheets > Configure
# 2. After deploying the function for the first time, you need to
#    open it and configure which sheet to use. The sheet URL is all
#    you need to specify the sheet.

import mayalabs

mayalabs.api_key = "< your api key here >"

script = """
1. trigger on receive
2. Add all data to google sheet
3. send response back
"""

function = mayalabs.Function.create(name="gsheet_write", script=script)
function.deploy()

function.call({
    'name': 'Dushyant',
    'age': 22
})