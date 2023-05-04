import mayalabs

script = """
1. trigger on receive
2. connect to browser at {{url}}
3. go to website 'https://google.com'
4. type {{query}} in field with xpath //*[@aria-label="Search"]
5. click button with xpath (//input[@aria-label="Google Search"])[2]
6. wait for 10 seconds
7. scrape '//h3[contains(text(), "Description")]/../span/text()' as 'description'
8. send response back
"""

fn = mayalabs.Function(name = 'google_result_scraper')
fn.update(script = script)

result = fn.call(payload={
    'url': 'ws://10.0.156.100:3000', # Points to Maya's internal browser service. You cannot access it from outside Maya.
    'query': 'lionel messi'
})

print(result)