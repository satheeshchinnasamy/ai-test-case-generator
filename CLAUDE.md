# Memory — AI Test Generator Project

## Me
Satheesh — aspiring AI engineer. Goal: build a self-healing Playwright test automation agent as a product.

## Project
| Name | What |
|------|------|
| **ai-test-generator** | Active project — AI-powered QA tool with two components: (1) Streamlit test case generator, (2) autonomous browser testing agent |

→ Full details: memory/projects/ai-test-agent.md

## Key Files
| File | What it does |
|------|-------------|
| `app.py` | Streamlit UI — takes User Story input, calls Groq LLaMA 3.1 8b, returns JSON test cases, Excel export, history |
| `experiment_14.py` | Autonomous agent (Groq + MCP + retry logic, browser_snapshot for dynamic ref discovery) |
| `experiment_15.py` | LangGraph refactor of experiment_14 — same capability, 1/3 code, **already on Gemini** |
| `experiment_11.py` | End-to-end proof: AI-generated test cases → browser agent (Playwright sync, hardcoded selectors) |
| `history.json` | Stores all generated test case sessions (newline-delimited JSON) |
| `test_cases.json` | Static test case output file |

## Tech Stack
| Layer | Tech |
|-------|------|
| Frontend | Streamlit |
| LLM (generator) | Groq API — LLaMA 3.1 8b instant |
| LLM (agent) | Google Gemini 2.5 Flash Lite (switched from Groq in exp_15) |
| Browser control | Playwright MCP (`@playwright/mcp@latest`) |
| Agent framework | LangGraph + LangChain MCP adapters |
| Language | Python (async for agent, sync for Streamlit) |

→ Full stack: memory/context/tech-stack.md

## Current State (as of June 2026)
- ✅ `app.py` — working Streamlit test case generator
- ✅ `experiment_15.py` — working LangGraph agent with Gemini, runs hardcoded test case
- ❌ **Not connected** — app.py and experiment_15 are two separate things; no integration yet
- ❌ `requirements.txt` outdated — missing langchain, langgraph, google-genai, mcp packages
- ❌ No structured result storage — PASS/FAIL not saved anywhere

## Key Decisions Made
- Switched from Groq to **Gemini 2.5 Flash Lite** (rate limits on Groq free tier)
- Use **browser_snapshot + dynamic ref discovery** (not hardcoded CSS selectors) — more robust
- Use **LangGraph `create_react_agent`** over raw agentic loop — less code, same power
- MCP over direct Playwright — lets AI decide actions rather than scripting them
- **Windows-specific**: MCP server starts via `cmd /c npx` (not `npx` directly)

## Enhancement Roadmap (7-Step Product Vision)
| Step | What | Status |
|------|------|--------|
| 1 | US/AC → AI generates manual TCs | ✅ app.py |
| 2 | User reviews + comments → Agent revises → loop until approved | 🔨 build next |
| 3 | Upload approved TCs → Agent assesses automation feasibility | 🔨 to build |
| 4 | Agent navigates app via MCP → captures snapshots → generates POMs | 🔨 to build (parallel) |
| 5 | User picks TCs → Agent writes JS/Playwright POM + data-driven scripts | 🔨 to build |
| 6 | Agent pushes to branch → opens PR → human reviews → merge | 🔨 to build |
| 7 | Execute in test env → screenshots + results → report | 🔨 to build |

**Phase 1 test output stack: JS/Playwright + POM + Data Driven Framework**
Future: Java/Selenium, Python/Pytest

→ Full details: memory/projects/ai-test-agent.md

## Preferences
- Keep code clean and function-based (not class-heavy)
- Learn the "why" behind each tool before using it
- Experiment files stay in `learning/` folder; production code at root
