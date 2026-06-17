import json

bad_response = "This is not{json"
try:
    data=json.loads(bad_response)
    print("Parsed Successfully")
except json.JSONDecodeError as e:
    print(f"Json parsing failed: {e}")
    print("will ask AI to try again")

print("Programm continues running....")


test_case={"id":"TC_001","title":"Valid Login"}

try:
    print(test_case["type"])
except KeyError as e:
    print(f"key not found {e}")
    print("using default value instead")
    print(test_case.get("type", "positive"))