import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    import streamlit as st
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def build_prompt(title, description, ac, num_cases=12, domain="General"):
    return f"""
Title:{title}
Description:{description}
Acceptance criteria:{ac}
Generate exactly {num_cases} test cases for a {domain} application.
"""

def parse_response(raw):
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean)["test_cases"]

def generate_testcases(prompt):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """You are a senior QA Engineer with 15 years of experience.
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
                - Title must NEVER start with or include Positive, Negative or Edge Case
                - Type field is the only place where Positive, Negative or Edge Case should appear"""
            },
            {"role": "user", "content": prompt}
        ]
    )
    return parse_response(response.choices[0].message.content)

def revise_testcases(title, description, ac, tcs_with_comments):
    prompt = f"""
Title:{title}
Description:{description}
Acceptance criteria:{ac}

Test cases with reviewer comments:
{json.dumps(tcs_with_comments, indent=2)}

Instructions:
- If review_comment is "No Changes", keep that test case exactly as-is
- If there is a comment, revise that test case accordingly
- If a comment says "remove", exclude that test case
- If a comment says "add [something]", add a new test case at the end
- Return ONLY revised test cases in the same JSON format, without the review_comment field
"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """You are a senior QA Engineer. Revise test cases based on reviewer comments.
                Return only a JSON object. No explanation. No markdown.
                Format:
                {"test_cases": [{"id": "TC_001", "title": "...", "precondition": "...", "steps": "...", "expected_result": "...", "type": "positive"}]}"""
            },
            {"role": "user", "content": prompt}
        ]
    )
    return parse_response(response.choices[0].message.content)