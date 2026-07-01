# Tech Stack

## Languages & Runtime
- Python 3.x (primary)
- async/await for agent (asyncio)
- Sync Playwright API for older experiments

## Frontend
- **Streamlit** — UI for test case generator (app.py)

## LLM APIs
| API | Used for | Model | Notes |
|-----|----------|-------|-------|
| Groq | Test case generation (app.py) | llama-3.1-8b-instant | Free tier, hits rate limits under heavy use |
| Groq | Agent (exp_14) | llama-3.3-70b-versatile | Rate limited after heavy testing |
| Google Gemini | Agent (exp_15) | gemini-2.5-flash-lite | Generous free tier, current choice |

## Agent Framework
- **LangGraph** — `create_react_agent` for the autonomous agent loop
- **LangChain** — `ChatGoogleGenerativeAI`, `MultiServerMCPClient`, `load_mcp_tools`
- **langchain-mcp-adapters** — bridges MCP tools into LangChain tool format

## Browser Automation
- **Playwright MCP** (`@playwright/mcp@latest`) — AI-controlled browser via MCP protocol
- Launched via: `cmd /c npx -y @playwright/mcp@latest --isolated` (Windows fix)
- Key tools used: `browser_navigate`, `browser_snapshot`, `browser_type`, `browser_click`
- `--isolated` flag: fresh browser context per run

## MCP (Model Context Protocol)
- Python `mcp` package — `ClientSession`, `StdioServerParameters`, `stdio_client`
- Used in exp_13/14 directly; abstracted in exp_15 via langchain-mcp-adapters

## Data & Storage
- `history.json` — newline-delimited JSON, one record per generation session
- `test_cases.json` — static output
- Excel export via `openpyxl` + `pandas`

## Environment
- `.env` file with API keys (`GROQ_API_KEY`, `GOOGLE_API_KEY`)
- `python-dotenv` for loading
- Streamlit secrets as fallback for cloud deploy

## Dependencies (requirements.txt — needs update)
Current:
```
streamlit
groq
pandas
openpyxl
python-dotenv
```

Missing (need to add):
```
langchain-groq
langchain-google-genai
langchain-mcp-adapters
langgraph
mcp
playwright
```

## Dev Environment
- Windows (important for MCP launch command)
- venv at `./venv`
