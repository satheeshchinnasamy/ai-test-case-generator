import asyncio
from dotenv import load_dotenv
#from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage


load_dotenv()

RELEVANT_TOOLS = ["browser_navigate", "browser_snapshot", "browser_type", "browser_click", "browser_fill_form"]

SYSTEM_PROMPT = """You are a QA automation agent. You have browser tools available.

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

async def main():
    client = MultiServerMCPClient({
        "playwright":{
            "command": "cmd",
            "args" : ["/c", "npx", "-y", "@playwright/mcp@latest", "--isolated"],
            "transport" : "stdio"
        }
    })

    async with client.session("playwright") as session:
        all_tools = await load_mcp_tools(session)
        tools = [t for t in all_tools if t.name in RELEVANT_TOOLS]
        print(f"Loaded {len(tools)} tools from MCP Server\n")

        #model = ChatGroq(model="llama-3.3-70b-versatile")
        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
        model_with_tools = model.bind_tools(tools)
        agent = create_react_agent(model_with_tools, tools)

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
    Report PASS or FAIL based on what you observe."""

        result = await agent.ainvoke({
            "messages" : [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=test_case)
            ]
        })

        final_message = result["messages"][-1].content
        print(f"\n{'='*50}")
        print(f"Final Result: {final_message}")
        print('='*50)

asyncio.run(main())

