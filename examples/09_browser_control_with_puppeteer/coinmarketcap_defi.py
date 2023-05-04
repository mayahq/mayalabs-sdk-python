import mayalabs
import time

mayalabs.api_key = 'mayakey-$2a$10$Yt9iCQv1ydwhWXvgr3Lx4.VU.PCWvAR/AmeC.2zW9SScVmHzAYjD2'
mayalabs.api_base = 'https://api.dev.mayalabs.io'
mayalabs.log_level = 'debug'

def get_time():
    return int(round(time.time() * 1000))

script = """
1. trigger on receive
2. connect to browser at 'ws://100.96.1.191:3000'
3. go to website 'https://coinmarketcap.com'
4. click on element with text 'DeFi'
5. wait for 10 seconds
6. scrape "//tbody//tr//div[contains(@class, 'name-area')]/p//text()" as 'DeFi'
7. send back response
"""

function = mayalabs.Function(name="CMC")

function.update(script=script)
res = function.call()