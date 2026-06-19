import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params=StdioServerParameters(
        command="cmd",
        args=["/c", "npx", "-y", "@playwright/mcp@latest", "--isolated"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = await session.call_tool(
                "browser_navigate",
                {"url":"https://practicetestautomation.com/practice-test-login/"}
            )
            print("Navigate Result: ")
            print(result)

            snapshot = await session.call_tool("browser_snapshot",{})
            print("\nPage Snapshot:")
            print(snapshot)

            type_user = await session.call_tool("browser_type",{
                "element":"Username fieldname",
                "target":"e37",
                "text":"student"
            })

            print("\nType Username Result:")
            print(type_user)

            type_pass = await session.call_tool("browser_type",{
                "element":"Password Field",
                "target":"e39",
                "text":"Password123"
            })
            print("\nType Password Result:")
            print(type_pass)

            click_submit = await session.call_tool("browser_click",{
                "element":"Submit Button",
                "target":"e40"
            })
            print("\nClick Submit Result:")
            print(click_submit)

            final_snapshot = await session.call_tool("browser_snapshot", {})
            print("\nFinal Snapshot:")
            print(final_snapshot)

asyncio.run(main())

