import streamlit as st
from groq import Groq
import pandas as pd
import json
import os
from io import BytesIO
from dotenv import load_dotenv
import datetime

# --- SETUP ---
load_dotenv()

try:
    API_KEY=st.secrets["GROQ_API_KEY"]
except:
    API_KEY=os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

# --- FUNCTIONS ---

def build_prompt(title, description, ac, num_cases=12, domain="General" ):
    return f"""
Title:{title}
Description:{description}
Acceptance criteria:{ac}
Generate exactly {num_cases} test cases for a {domain} application.
"""

def parse_response(raw):
    clean=raw.strip().replace("```json","").replace("```","").strip()
    data=json.loads(clean)
    return data["test_cases"]

def generate_testcases(prompt):
    response=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role":"system",
                "content":""" You are senior QA Engineer with 15 years of experience.
                When given a User story, generate test cases and return only JSON object
                No Explanation. No extra text. No Markdown. Just pure Json.

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

                Generate the number of test cases specified in the user prompt
                STRICT RULES:
                - Title must describe WHAT is being tested only.
                - Title must NEVER start with or include Positive, Negative or Edge Case
                - Type field is the only place where Positive, Negative or Edge Case should appear"""
            },
            {
                "role":"user",
                "content":prompt
            }
        ]
    )
    return response.choices[0].message.content

def convert_to_excel(df):
    buffer=BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def convert_to_excel_with_comments(df):
    df["Comments"] = ""
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def revise_from_excel(file, title, description, ac):
    df = pd.read_excel(file)
    test_cases = []
    comments = []
    for _, row in df.iterrows():
        test_cases.append({
            "id": row["ID"],
            "title": row["Title"],
            "precondition": row["Precondition"],
            "steps": row["Steps"],
            "expected_result": row["Expected Result"],
            "type": row["Type"]
        })
        comments.append(str(row["Comments"]) if pd.notna(row["Comments"]) else "")
    tcs_with_comments = []
    for tc, comment in zip(test_cases, comments):
        entry = dict(tc)
        entry["review_comment"] = comment if comment and comment != "nan" else "No Changes"
        tcs_with_comments.append(entry)
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
                "role" : "system",
                "content" : """You are a senior QA Engineer. Revise test cases based on reviewer comments.
                Return only a JSON object. No explanation. No markdown.
                Format:
                {
                    "test_cases": [
                        {
                            "id": "TC_001",
                            "title": "...",
                            "precondition": "...",
                            "steps": "...",
                            "expected_result": "...",
                            "type": "positive"
                        }
                    ]
                }"""
            },
            {"role": "user", "content": prompt}
        ]
    )
    raw = response.choices[0].message.content
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean)["test_cases"]


def save_history(title, test_cases):
    import datetime
    record={
        "timestamp": str(datetime.datetime.now()),
        "us_title" : title,
        "test_cases" : test_cases
    }
    with open("history.json", "a") as f:
        f.write(json.dumps(record) + "\n")

def load_history():
    if not os.path.exists("history.json"):
        return[]
    records=[]
    with open("history.json", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# --- PAGE ---

st.title("🧪 AI Test Case Generator")
st.write("Fill in the User Story details and generate test cases instantly.")

st.divider()

# --- INPUTS ---

us_title = st.text_input("User Story Title",
              placeholder="Example: User Login with Email and Password")
us_description = st.text_area("User Story Description",
             height=100,
             placeholder="Example: As a user, I want to login with my email and password so that I can access my account.")
us_ac = st.text_area("Acceptance Criteria",
             height=150,
             placeholder="""Example:
1. User can login with valid email and password
2. Error message shown for invalid credentials
3. Account locks after 5 failed attempts""")

st.divider()

# --- BUTTON ---

if st.button("🚀 Generate Test Cases"):
    if not us_title.strip():
        st.warning("Please enter the User Story Title.")
    elif not us_description.strip():
        st.warning("Please enter the User Story Description.")
    elif not us_ac.strip():
        st.warning("Please enter the Acceptance Criteria.")
    else:
        with st.spinner("Generating test cases..."):
            prompt = build_prompt(us_title, us_description, us_ac)
            raw = generate_testcases(prompt)
        try:
            test_cases = parse_response(raw)
            st.success(f"✅ {len(test_cases)} test cases generated!")
            df = pd.DataFrame(test_cases)
            df.columns = ["ID", "Title", "Precondition", "Steps", "Expected Result", "Type"]
            st.dataframe(df, use_container_width=True)

            buffer = convert_to_excel_with_comments(df)
            st.download_button(
                label="📥 Download for Review (with Comments column)",
                data=buffer,
                file_name=f"{us_title[:30]}_review.xlsx",
                mime="application/vnd.ms-excel"
            )
        except Exception as e:
            st.error("⚠️ AI returned an unexpected format. Please try generating again.")
            st.code(raw)

st.divider()
st.subheader("📤 Upload Reviewed Excel")
st.write("Add comments in the Excel, save it, then upload here to revise.")

uploaded_file = st.file_uploader("Upload your reviewed Excel", type=["xlsx"])

if uploaded_file:
    rev_title = us_title if us_title.strip() else st.text_input("User Story Title (for revision)", key="rev_title")
    rev_description = us_description if us_description.strip() else st.text_area("Description (for revision)", key="rev_desc")
    rev_ac = us_ac if us_ac.strip() else st.text_area("Acceptance Criteria (for revision)", key="rev_ac")
    
    if st.button("🔄 Revise Based on Comments"):
        if not rev_title.strip():
            st.warning("Please enter the User Story Title.")
        else:
            with st.spinner("Reading comments and revising..."):
                revised = revise_from_excel(uploaded_file, rev_title, rev_description, rev_ac)

            st.success(f"✅ Revised! {len(revised)} test cases.")
            df_revised = pd.DataFrame(revised)
            df_revised.columns = ["ID", "Title", "Precondition", "Steps", "Expected Result", "Type"]
            st.dataframe(df_revised, use_container_width=True)

            save_history(rev_title, revised)

            buffer = convert_to_excel_with_comments(df_revised)
            st.download_button(
                label="📥 Download Revised TCs",
                data=buffer,
                file_name=f"{rev_title[:30]}_revised.xlsx",
                mime="application/vnd.ms-excel",
                key="revised_download"
            )