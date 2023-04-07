import pytest
import mayalabs
import os

mayalabs.api_key = os.environ.get("MAYA_API_KEY")

example_object = {
  "id": 1,
  "name": "Alice",
  "position": "CEO",
  "subordinates": [
    {
      "id": 2,
      "name": "Bob",
      "position": "CTO",
      "subordinates": [
        {
          "id": 4,
          "name": "David",
          "position": "Lead Developer",
          "subordinates": []
        }
      ]
    },
    {
      "id": 3,
      "name": "Carol",
      "position": "CFO",
      "subordinates": []
    }
  ]
}

script = """
1. trigger on recieve
3. run a custom function to 'to take a deeply nested JSON object {{payload.data}} and flatten it then return'
4. send response back
"""
def test_custom_function_generate():
    os.environ['MAYA_ENVIRONMENT'] = "development"

    func = mayalabs.Function.create(name='UniqueNewFunc02', script=script)
    func.deploy()
    output = func.call(payload={"data": example_object})
    expected_return = ['id: 1', 'name: Alice', 'position: CEO', 'subordinates.0.id: 2', 'subordinates.0.name: Bob', 'subordinates.0.position: CTO', 'subordinates.0.subordinates.0.id: 4', 'subordinates.0.subordinates.0.name: David', 'subordinates.0.subordinates.0.position: Lead Developer', 'subordinates.1.id: 3', 'subordinates.1.name: Carol', 'subordinates.1.position: CFO']
    assert True if output == expected_return else False

