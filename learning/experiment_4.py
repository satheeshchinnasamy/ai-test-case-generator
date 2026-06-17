import json

with open("test_output.txt","a") as f:
    f.write("Test Case ID: TC_001\n")
    f.write("Title: Valid Login\n")
    f.write("Type: Positive\n")
print("File written successfully")

with open("test_output.txt", "r") as f:
    content=f.read()
    print(content)

test_cases = [
    {"id":"TC_001", "title":"Valid login", "type":"positive"},
    {"id":"TC_002", "title":"Invalid login", "type":"positive"},
    {"id":"TC_003", "title":"Empty login", "type":"edgecases"},
]


with open("test_cases.json","w") as f:
    json.dump(test_cases, f, indent=2)

print("Json File written")

with open("test_cases.json", "r") as f:
    loaded=json.load(f)
    print(loaded)
    print(type(loaded))
    
