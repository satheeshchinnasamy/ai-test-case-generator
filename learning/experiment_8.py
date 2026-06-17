import json
import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

client= Groq(api_key=os.getenv("GROQ_API_KEY"))

# --- TOOLS (functions) ---

def get_test_case_count():
    return {"count": 42, "messages":"42 Test cases in the system"}

def get_history():
    return{
        "sessions":[
            {"date":"2026-06-15", "title":"Eid Modernization", "count":12},
            {"date":"2026-06-16", "title":"Valid Login", "count":8}
        ],
        "total_sessions":2
    }
def generate_test_cases(user_story):
    return{
        "user story": user_story,
        "test_cases":["TC_01:Valid Login","TC_02:Invalid Login"],
        "Count":2
    }
# ---- Tool Definitions ----

tools=[
    {
        "type":"function",
        "function":{
            "name":"get_test_case_count",
            "description":"Get total number of test cases in the system",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_history",
            "description":"Get history of all past test case generation sessions",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"generate_test_cases",
            "description":"Generate test cases for a given user story",
            "parameters":{
                "type":"object",
                "properties":{
                    "user_story":{
                        "type":"string",
                        "description":"User Story to Generate the test cases for"
                    }
                },
                "required":["user_story"]
            }
        }
    }    
]

# ---- TOOL EXECUTOR ----

def execute_tool(tool_name, arguments):
    if tool_name =="get_test_case_count":
        return get_test_case_count()
    elif tool_name == "get_history":
        return get_history()
    elif tool_name == "generate_test_cases":
        return generate_test_cases(arguments["user_story"])
    else:
        return {"error":f"Unknown tool:{tool_name}"}
    
# --- AGENT LOOP ---

def run_agent(user_question):
    print(f"\nUser:{user_question}")
    print("-"*40)

    messages=[
        {
        "role":"user",
        "content":user_question       
        }
            ]
    response= client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        tools=tools
    )

    if response.choices[0].message.tool_calls:
        tool_call = response.choices[0].message.tool_calls[0]
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        print(f"AI choose tool:{tool_name}")
        print(f"Arguments:{arguments}")

        result = execute_tool(tool_name, arguments)
        print(f"Result:{result}")

        messages.append(response.choices[0].message)
        messages.append({
            "role":"tool",
            "tool_call_id":tool_call.id,
            "content":json.dumps(result)
        })

        final=client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=tools
        )

        print(f"Final Answer:{final.choices[0].message.content}" )
    else:
        print(f"Answer:{response.choices[0].message.content}")

# --- TEST WITH 3 DIFFERENT QUESTIONS ---
run_agent("How many test cases do we have?")
run_agent("Show me the history of past sessions")
run_agent("Generate test cases for user login feature")