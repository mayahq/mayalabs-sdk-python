import pytest
import mayalabs
import os

mayalabs.api_key = os.environ.get("MAYA_API_KEY")

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
def test_web_scrape_type_click():
    os.environ['MAYA_ENVIRONMENT'] = "development"
    func = mayalabs.Function.create(name='UniqueNewFunc03', script=script)
    func.deploy()
    output = fn.call(payload={
            'url': 'wss://chrome.browserless.io?token=' + os.environ.get('BROWSERLESS_TOKEN', ''),
            'query': 'lionel messi'
        })
    try:
        assert True if len(output['scrapResults'].get('description')) > 0 else False
    except:
        assert False