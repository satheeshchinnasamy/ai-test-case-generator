# Project: AI-Powered QA Test Automation Agent

## Vision
A self-healing, AI-driven QA tool that:
1. Takes a User Story → generates test cases (done ✅)
2. Takes those test cases → runs them autonomously in a browser (done as prototype ✅)
3. Self-heals when tests fail — retries, adapts, re-reports (partially done ✅ exp_14/15)
4. Full product: Streamlit UI feeds test cases directly into the agent (not connected yet ❌)

## Journey So Far

### Learning Phase (experiments 1–9)
- Python fundamentals: dicts, list comprehensions, functions, file I/O, error handling
- OOP/classes, tool calling, multi-tool agents

### Agent Phase
| File | Milestone |
|------|-----------|
| `experiment_10.py` | Manual Playwright agent — hardcoded steps, no AI |
| `experiment_11.py` | AI test cases → browser agent (end-to-end proof of concept) |
| `experiment_12.py` | Learning async/await |
| `experiment_13.py` | MCP protocol basics — raw MCP calls, no AI |
| `experiment_14.py` | Self-correcting agent: Groq + MCP + retry logic + dynamic snapshot refs |
| `experiment_15.py` | LangGraph refactor — Gemini, create_react_agent, 1/3 the code |

### Key Bugs Solved
- Windows-specific: `npx` doesn't work directly → must use `cmd /c npx`
- Stateful MCP session bug — debugged against official docs
- Groq rate limits after heavy testing → switched to Gemini

## Architecture (current)

```
[app.py Streamlit UI]          [experiment_15.py Agent]
        |                               |
  User Story input              LangGraph ReAct loop
        |                               |
  Groq LLaMA 3.1 8b            Gemini 2.5 Flash Lite
        |                               |
  JSON test cases              Playwright MCP tools
        |                               |
  Excel download               PASS/FAIL verdict
        |
  history.json
```

**GAP: These two systems are not connected.**

## Architecture (target)

```
[Streamlit UI]
    |
  User Story → Generate Test Cases (Gemini or Groq)
    |
  Select test cases to run
    |
  [Agent Runner]
    |
  LangGraph agent → Playwright MCP → Browser
    |
  Structured results (PASS/FAIL + screenshots + error)
    |
  Report back in UI + save to DB/JSON
```

## Planned Enhancements (Full Product Vision)

### Step 1 — TC Generation (✅ mostly done in app.py)
- US + AC + Description → Agent generates manual test cases
- Currently: Groq LLaMA 3.1 8b, JSON output, Excel export, history

### Step 2 — Review Loop (✅ done)
- Generate TCs → download Excel with Comments column
- User fills Comments column per TC in Excel
- Upload Excel back → Agent reads comments → revises only commented TCs
- Download revised TCs → repeat until satisfied
- Key functions: `convert_to_excel_with_comments()`, `revise_from_excel()`
- Deployed live on Streamlit Community Cloud (public URL)

### Step 3 — Automation Feasibility Assessment (🔨 to build)
- User uploads approved TCs
- Agent assesses each TC: can it be automated? Why/why not?
- Output: feasibility score + reasoning per TC
- User reviews assessment before proceeding

### Step 4 — Page Object Discovery (🔨 to build, runs in parallel with 1–3)
- Agent gets scoped access to target web app
- Navigates screens via Playwright MCP
- Captures real DOM snapshots per screen
- Generates Page Object Model (POM) files (Java or JS)
- Human reviews and validates selectors
- Output: validated, reusable page objects → feed into Step 5
- Foundation: experiment_15.py MCP skills directly applicable

### Step 5 — Test Script Generation (🔨 to build)
- User selects which approved TCs to automate
- Agent compiles test scripts using validated page objects from Step 4
- **Phase 1 output: JS/Playwright — POM + Data Driven Framework**
- Future: add Java/Selenium, Python/Pytest, etc.
- Scripts call existing, human-validated page objects only
- Data driven: test data (credentials, inputs, expected results) in separate JSON/CSV files

### Step 6 — PR / Code Review (🔨 to build)
- Agent pushes generated scripts to a git branch
- Opens a Pull Request
- Human reviews code → merges
- Needs: GitHub API integration

### Step 7 — Execution + Reporting (🔨 to build)
- Execute in test environment using test IDs
- Capture screenshots + pass/fail results per step
- Generate structured test report
- Foundation: experiment_15.py agent loop + add structured output storage

## Current Blockers / Open Questions
- requirements.txt needs updating: add `langchain-groq`, `langchain-google-genai`, `langchain-mcp-adapters`, `langgraph`, `mcp`
- How to bridge async agent with Streamlit (which is sync) — needs `asyncio.run()` or thread
- Result storage format TBD (JSON file vs SQLite vs Streamlit session state)
