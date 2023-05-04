### Browser control with Puppeteer

The below program will go to Google, search for "Dr. Homi Bhabha" and give you the description that appears in the summary box to the right of the search results.

```python
import mayalabs
import time

mayalabs.api_key = '<YOUR API KEY>'

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
```

Most of the steps are self-explanatory. In step #6, we use an xpath to specify where we want to scrape the name of the coin from, and store the scrape results in key DeFi (i.e., the result can be found in `msg.payload.scrapeResults.DeFi`).

This script will give you all the coins that come under the DeFi category.

#### Adding functionality
You can add more instructions to the above script and update your function. Let's also scrape all the coins based on Solana, and then find which ones are common to the DeFi category. The below script will do just that - 

```python
import mayalabs
import time

mayalabs.api_key = '<YOUR API KEY>'

def get_time():
    return int(round(time.time() * 1000))

script = """
1. trigger on receive
2. connect to browser at 'ws://100.96.1.191:3000'
3. go to website 'https://coinmarketcap.com'
4. click on element with text 'DeFi'
5. wait for 10 seconds
6. scrape "//tbody//tr//div[contains(@class, 'name-area')]/p//text()" as 'DeFi'
7. click on element with text 'Solana'
8. wait for 10 seconds
9. scrape "//tbody//tr//div[contains(@class, 'name-area')]/p//text()" as 'Solana'
10. add a custom function to 'store the intersections of msg.payload.scrapeResults.DeFi and msg.payload.scrapeResults.Solana into msg.payload.finalResult'
11. send back response
"""

function = mayalabs.Function(name="CMC")

function.update(script=script)
res = function.call()
```

Steps #7, #8 and #9 are responsible for clicking on the Solana category, scraping the list of coins and storing them in `msg.payload.scrapeResults.Solana`. Step #10 will run a javascript function that checks which coins are in both the DeFi list and Solana list, which is our result.
