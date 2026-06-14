import streamlit as st
from groq import Groq
import pandas as pd
import json
import os
from io import BytesIO
from dotenv import load_dotenv

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
            prompt = build_prompt(us_title, us_description,us_ac)
            raw = generate_testcases(prompt)
        try:
            test_cases = parse_response(raw)
            st.success(f"✅ {len(test_cases)} Test cases generated!")
            df = pd.DataFrame(test_cases)
            df.columns = ["ID", "Title", "Precondition", "Steps", "Expected Result", "Type"]
            st.dataframe(df, use_container_width=True)

            buffer = convert_to_excel(df)
            st.download_button(
                label="📥 Download Test Cases as Excel",
                data=buffer,
                file_name=f"{us_title[:30]}_test_cases.xlsx",
                mime="application/vnd.ms-excel"
            )
        except Exception as e:
            st.error("⚠️ AI returned an unexpected format. Please try generating again.")
            st.code(raw)