test_case={
    "id" : "TC_001",
    "title" : "Valid login",
    "type" : "Positive"
}

print(test_case)

print(test_case["id"])

test_case["title"]= "Valid login creds"

print(test_case)

test_case["priority"]="high"
print(test_case)