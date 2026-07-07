import os
import json
from groq import Groq
from google import genai as google_genai
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    gemini_client = google_genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    gemini_client = google_genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- Model routing: one model per task type ---
MODEL_GENERATE = {"provider": "groq", "model": "llama-3.1-8b-instant"}       # fast/cheap first-pass generation
MODEL_REVISE = {"provider": "groq", "model": "llama-3.3-70b-versatile"}      # stronger reasoning for applying scattered comments
MODEL_SUMMARIZE = {"provider": "gemini", "model": "gemini-2.5-flash-lite"}   # cheap, generous free tier — compaction/summarization


def call_llm(provider, model, system, user):
    if provider == "groq":
        response = groq_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content
    elif provider == "gemini":
        response = gemini_client.models.generate_content(
            model=model,
            contents=user,
            config={"system_instruction": system},
        )
        return response.text
    else:
        raise ValueError(f"Unknown provider: {provider}")


def _estimate_tokens(text):
    return len(text) // 4  # rough char/4 heuristic, fine for logging

def build_prompt(title, description, ac, num_cases=None, domain="General", doc_context=""):
    doc_section = f"\nAdditional context from document:\n{doc_context[:3000]}" if doc_context else ""
    count_instruction = (
        f"Generate exactly {num_cases} test cases for a {domain} application."
        if num_cases else
        f"Generate as many test cases as needed to fully cover the acceptance criteria above "
        f"for a {domain} application, including positive, negative, and edge cases. Do not pad "
        f"or artificially limit the count."
    )
    return f"""
Title:{title}
Description:{description}
Acceptance criteria:{ac}
{count_instruction}
{doc_section}
"""

def parse_response(raw):
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean)["test_cases"]

def _ensure_title_prefix(test_cases):
    for tc in test_cases:
        title = (tc.get("title") or "").strip()
        if title and not title.lower().startswith(("verify", "validate")):
            tc["title"] = f"Verify {title[0].lower() + title[1:]}"
    return test_cases

def generate_testcases(prompt):
    raw = call_llm(
        provider=MODEL_GENERATE["provider"],
        model=MODEL_GENERATE["model"],
        system="""You are a senior QA Engineer with 15 years of experience.
        When given a User story, generate test cases and return only JSON object.
        No Explanation. No extra text. No Markdown. Just pure JSON.

        Return exactly in this format:
        {
            "test_cases":[
                {
                    "id": "TC_001",
                    "title":"....",
                    "precondition":"...",
                    "steps":"...",
                    "expected_result":"...",
                    "type":"positive"
                }
            ]
        }

        Generate the number of test cases specified in the user prompt.
        STRICT RULES:
        - Title must describe WHAT is being tested only.
        - Title must always start with the word "Verify" or "Validate"
        - Title must NEVER start with or include Positive, Negative or Edge Case
        - Type field is the only place where Positive, Negative or Edge Case should appear""",
        user=prompt,
    )
    test_cases = parse_response(raw)
    return _ensure_title_prefix(test_cases)


# ---------------- Context compaction for the revision loop ----------------

def compact_revision_context(tcs_with_comments):
    """
    Splits test cases into 'changed' (has a real reviewer comment) and
    'unchanged' (no comment / 'No Changes'). Only 'changed' ones get sent
    to the LLM in full; 'unchanged' ones are sent as {id, title} stubs and
    spliced back in locally afterward. Keeps prompt size proportional to
    what actually changed, not total suite size.
    """
    changed, unchanged = [], []
    for tc in tcs_with_comments:
        comment = (tc.get("review_comment") or "").strip()
        if not comment or comment.lower() == "no changes":
            unchanged.append(tc)
        else:
            changed.append(tc)

    unchanged_compact = [{"id": tc["id"], "title": tc["title"]} for tc in unchanged]
    unchanged_lookup = {
        tc["id"]: {k: v for k, v in tc.items() if k != "review_comment"}
        for tc in unchanged
    }

    full_size = _estimate_tokens(json.dumps(tcs_with_comments))
    compact_size = _estimate_tokens(json.dumps(changed) + json.dumps(unchanged_compact))
    print(f"[context-compaction] full~{full_size} tok, compact~{compact_size} tok, saved~{full_size - compact_size}")

    return changed, unchanged_compact, unchanged_lookup


def _merge_revision_results(original_tcs, unchanged_lookup, llm_revised):
    """Reassembles the final list preserving original order: unchanged
    pass through untouched, changed ones get the LLM's version, removed
    ones (comment said 'remove', so LLM omitted them) are dropped, and
    any brand-new test cases the LLM appended go at the end."""
    llm_by_id = {tc["id"]: tc for tc in llm_revised}
    original_ids = [tc["id"] for tc in original_tcs]
    merged, seen = [], set()

    for tc_id in original_ids:
        if tc_id in llm_by_id:
            merged.append(llm_by_id[tc_id])
            seen.add(tc_id)
        elif tc_id in unchanged_lookup:
            merged.append(unchanged_lookup[tc_id])
            seen.add(tc_id)
        # else: removed by reviewer comment -> dropped silently

    for tc in llm_revised:
        if tc["id"] not in seen:
            merged.append(tc)

    return merged


def revise_testcases(title, description, ac, tcs_with_comments):
    changed, unchanged_compact, unchanged_lookup = compact_revision_context(tcs_with_comments)

    prompt = f"""
Title:{title}
Description:{description}
Acceptance criteria:{ac}

Test cases that are UNCHANGED (reference only — do NOT repeat these in your output):
{json.dumps(unchanged_compact, indent=2)}

Test cases WITH reviewer comments that need action:
{json.dumps(changed, indent=2)}

Instructions:
- Only return test cases from the "WITH reviewer comments" list, revised per their comment.
- If a comment says "remove", omit that test case entirely from your output.
- If a comment says "add [something]", add it as a new test case at the end.
- Do NOT return the unchanged test cases — they are merged back in automatically.
- Return ONLY JSON in the same format, without the review_comment field.
"""
    raw = call_llm(
        provider=MODEL_REVISE["provider"],
        model=MODEL_REVISE["model"],
        system="""You are a senior QA Engineer. Revise test cases based on reviewer comments.
        Return only a JSON object. No explanation. No markdown.
        Format:
        {"test_cases": [{"id": "TC_001", "title": "...", "precondition": "...", "steps": "...", "expected_result": "...", "type": "positive"}]}""",
        user=prompt,
    )
    llm_revised = parse_response(raw)
    merged = _merge_revision_results(tcs_with_comments, unchanged_lookup, llm_revised)
    return _ensure_title_prefix(merged)