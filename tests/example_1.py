import pytest
import mayalabs
import os

mayalabs.api_key = os.environ.get("MAYA_API_KEY")

script = """
1. trigger on receive message
2. set {{payload}} to '{"num": 29}'
3. add 1 to {{payload.num}}
4. print {{payload.num}}
5. if {{payload.num}} is less than 36
    - 5.1. go to step 3
6. else if {{payload.num}} is more than 36
    - 6.1. print {{payload.num}}
7. respond back with {{payload}}
    """
def test_if_condition_with_loop():
    os.environ['MAYA_ENVIRONMENT'] = "development"
    func = mayalabs.Function.create(name='UniqueNewFunc01', script=script)
    func.deploy()
    output = func.call(payload={"trigger": "this"})
    print(output)
    assert True if output['num'] == 36 else False