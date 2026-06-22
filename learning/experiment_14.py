import asyncio
import os
import json

from groq import Groq
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

RELEVANT_TOOLS = ["browser_navigate", "browser_snapshot", "browser_type", "browser_click", "browser_fill_form"]

async def get_groq_tools_from_mcp(session):
    mcp_tools = await session.list_tools()
    groq_tools = []
    for tool in mcp_tools.tools:
        if tool.name in RELEVANT_TOOLS:
            groq_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
    return groq_tools

def extract_mcp_text(mcp_result):
    texts = []
    for block in mcp_result.content:
        if hasattr(block, "text"):
            texts.append(block.text)
    return "\n".join(texts)

async def run_test_agent_mcp(test_case, session, groq_tools):
    messages = [
        {
            "role": "system",
            "content": """You are a QA automation agent. You have browser tools available.

When taking a snapshot, ALWAYS call browser_snapshot with NO arguments 
(empty {}) — do not provide a filename. This ensures you see the full 
page structure directly in the response.

Look for elements in the format [ref=eXX] in the snapshot output 
(e.g. [ref=e37]). Use that EXACT ref value (like "e37") as the target 
parameter for browser_type and browser_click — never use a description 
like "username field" as the target.

First navigate to the page, take a snapshot, identify the correct refs, 
then interact with the page. After completing the test steps, report 
whether the test PASSED or FAILED based on what you actually observe."""
        },
        {"role": "user", "content": test_case}
    ]

    max_steps = 15

    for step in range(max_steps):
        response = None
        last_error = None

        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=messages,
                    tools=groq_tools
                )
                break
            except Exception as e:
                last_error = e
                print(f"   Attempt {attempt+1} failed: {e}")

        if response is None:
            return f"FAIL - Agent error after retries: {last_error}"

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)

            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                print(f"Step {step+1}: AI Calls {tool_name}({arguments})")
                mcp_result = await session.call_tool(tool_name, arguments)
                result_text = extract_mcp_text(mcp_result)

                MAX_RESULT_LENGTH = 3000
                print(f"   Result: {result_text[:150]}...")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_text[:MAX_RESULT_LENGTH]
                })
        else:
            print(f"\nFinal Report:\n{message.content}")
            return message.content

    return "FAIL - Max steps reached without final answer"

async def main():
    server_params = StdioServerParameters(
        command="cmd",
        args=["/c", "npx", "-y", "@playwright/mcp@latest", "--isolated"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            groq_tools = await get_groq_tools_from_mcp(session)
            print(f"Loaded {len(groq_tools)} tools from MCP server\n")

            test_case = """
Test Case: Verify login with valid credentials

Application URL: https://practicetestautomation.com/practice-test-login/

Steps:
1. Navigate to the application URL
2. Take a snapshot to see the page elements and their refs
3. Type username "student" into the username field
4. Type password "Password123" into the password field
5. Click the submit button
6. Take a final snapshot to verify the result

Expected Result: Page shows "Logged In Successfully" with a congratulations message.
Report PASS or FAIL based on what you observe.
"""

            result = await run_test_agent_mcp(test_case, session, groq_tools)
            print(f"\n{'='*50}")
            print(f"Final result: {result}")
            print('='*50)

asyncio.run(main())