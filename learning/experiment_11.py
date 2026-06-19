from playwright.sync_api import sync_playwright
from groq import Groq
import os
import json
from dotenv import load_dotenv
load_dotenv()

client= Groq(api_key=os.getenv("GROQ_API_KEY")) 

playwright = sync_playwright().start()
browser = playwright.chromium.launch(headless=False)
page = browser.new_page()

def navigate_to(url):
    page.goto(url)
    return {"status":"Success","message":f"Navigate to {url}"}

def click_element(selector):
    page.click(selector)
    return {"status":"Success","message":f"Clicked {selector}"}

def type_text(selector, text):
    page.fill(selector, text)
    return {"status":"Success", "message":f"Typed '{text}' into {selector}"}

def get_page_text():
    text = page.inner_text("body")
    return {"page_text": text}

tools=[
    {
        "type":"function",
        "function":{
            "name":"navigate_to",
            "description":"Navigate the browser to a specific URL",
            "parameters":{
                "type":"object",
                "properties":{
                    "url":{"type":"string", "description":"The URL to Navigate to"}
                },
                "required":["url"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"click_element",
            "description":"Click an element on the page using a CSS selector",
            "parameters":{
                "type":"object",
                "properties":{
                    "selector":{"type":"string", "description":"CSS selector e.g. #submit"}
                },
                "required":["selector"]
            }
        }        
    },
    {
        "type":"function",
        "function":{
            "name":"type_text",
            "description": "Type text into an input field using a CSS selector",
            "parameters": {
                "type":"object",
                "properties":{
                    "selector": {"type": "string", "description": "CSS selector e.g. #username"},
                    "text": {"type": "string", "description": "Text to type into the field"}
                },
                "required":["selector","text"]
            }
        }
    },
    {
        "type":"function",
        "function":{
            "name":"get_page_text",
            "description":"Get the visible text content of the current page to verify results",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[]
            }
        }
    }
]

def execute_tool(tool_name, arguments):
    if tool_name == "navigate_to":
        return navigate_to(arguments["url"])
    elif tool_name == "click_element":
        return click_element(arguments["selector"])
    elif tool_name == "type_text":
        return type_text(arguments["selector"],arguments["text"])
    elif tool_name == "get_page_text":
        return get_page_text()
    else:
        return {"error": f"Unknown tool:{tool_name}"}

def run_test_agent(test_case):
    messages = [
        {
            "role" : "system",
            "content" : """You are a QA automation agent. You will be given a test case with steps.
Execute each step using the available browser tools, one tool call at a time.
After completing all steps, report whether the test PASSED or FAILED based on what you observe.
Use the CSS selectors exactly as provided in the test case."""
        },
        {
            "role":"user",
            "content": test_case
        }
    ]

    max_steps = 10

    for step in range(max_steps):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=tools
            )
        except Exception as e:
            print(f"API call failed: {e}")
            return f"FAIL - Agent error: {e}"

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                print(f"step {step+1}: AI Calls {tool_name}({arguments})")
                result = execute_tool(tool_name, arguments)
                print(f" Result: {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id" : tool_call.id,
                    "content": json.dumps(result)
                })
        else:
            print(f"\nFinal Report:\n{message.content}")
            return message.content

known_selectors = """
Known Selectors for this application:
- Username field: #username
- Password field: #password
- Submit button: #submit
"""

test_cases = [
    {
        "id":"TC_001",
        "title":"Login with valid credentials",
        "steps": "Enter valid username 'student' and password 'Password123'. Click on the login button.",
        "expected_result": "User is redirected to the protected area."
    },
    {
        "id": "TC_002",
        "title": "Login with invalid username",
        "steps": "Enter invalid username 'invalid_user' and valid password 'Password123'. Click on the login button.",
        "expected_result": "Error message is shown."
    },
    {
        "id": "TC_003",
        "title": "Login with invalid password",
        "steps": "Enter valid username 'student' and invalid password 'invalid_password'. Click on the login button.",
        "expected_result": "Error message is shown."
    },
    {
        "id": "TC_004",
        "title": "Login with empty fields",
        "steps": "Enter empty username and password. Click on the login button.",
        "expected_result": "Error message is shown."
    },
    {
        "id": "TC_005",
        "title": "Login with valid username and empty password",
        "steps": "Enter valid username 'student' and empty password. Click on the login button.",
        "expected_result": "Error message is shown."
    }
]

application_url = "https://practicetestautomation.com/practice-test-login/"

results =[]

for tc in test_cases:
    print(f"\n{'='*50}")
    print(f"running {tc['id']}:{tc['title']}")
    print('='*50)

    full_test_case =f"""
        Test Case: {tc['title']}

        Application URL: {application_url}

        Steps: {tc['steps']}

        Expected Result: {tc['expected_result']}

        {known_selectors}

        Navigate to the application URL first, then perform the steps using the known selectors.
        Report PASS or FAIL based on whether the actual result matches the expected result.
        """
    
    report = run_test_agent(full_test_case)
    results.append({"id": tc["id"], "title": tc["title"], "report": report})

print(f"\n\n{'='*50}")
print("SUMMARY REPORT")
print('='*50)
for r in results:
    print(f"{r['id']} - {r['title']}")
    print(f"   {r['report']}\n")

browser.close()
playwright.stop()