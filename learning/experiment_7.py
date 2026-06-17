import json
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client= Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_test_case_count():
    return {"Count": 42, "message":" $2 Test cases were in the history"}

tools1=[
    {
        "type":"function",
        "function":{
            "name":"get_test_case_count",
            "description":"Get total number of Test cases in the system",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
        }
    }
]

messages1=[
    {"role":"user",
     "content":"How many test case do we have?"
     }
]

response=client.chat.completions.create(
    model="llama-3.1-8b-instant",
    messages= messages1,
    tools=tools1
)

if response.choices[0].message.tool_calls:
    tool_call=response.choices[0].message.tool_calls[0]
    print(f"AI decided to call:{tool_call.function.name}")

    result=get_test_case_count()
    print(f"Function Returned:{result}")
else:
    print("AI responded without using the tool")
    print(response.choices[0].message.content)

print("\n=== Agent Loop ===")

message2=[
    {
        "role":"user", 
        "content":"How many test cases do we have"
    }
]

response2=client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=message2,
    tools=tools1
)

response2.choices[0].message.tool_calls[0]
print(f"AI wants to call:{tool_call.function.name}")

result= get_test_case_count()
print(f"Function Returned:{result}")

message2.append(response2.choices[0].message)
message2.append({
    "role":"tool",
    "tool_call_id":tool_call.id,
    "content":json.dumps(result)
})

final_response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=message2,
    tools=tools1
)

print(f"\nFinal Answer: {final_response.choices[0].message.content}")