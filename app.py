import streamlit as st
from groq import Groq
import pandas as pd
import json
from io import BytesIO
import os
from dotenv import load_dotenv
load_dotenv()

try:
    import streamlit as st
    API_KEY = st.secrets["GROQ_API_KEY"]
except:
    API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

# --- PAGE ---
st.title("🧪 AI Test Case Generator")
st.write("Fill in the User Story details and generate test cases instantly.")

st.divider()

# --- INPUT FIELDS ---
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
def build_prompt(title, description, ac, num_cases=7, domain="General"):
    return f"""
    User Story Title : {title}
    User Story Description : {description}
    Acceptance Criteria : {ac}
    Generate {num_cases} test cases for a {domain} application.
    """

if st.button("🚀 Generate Test Cases"):

    # Validation
    if not us_title.strip():
        st.warning("Please enter the User Story Title.")
    elif not us_description.strip():
        st.warning("Please enter the User Story Description.")
    elif not us_ac.strip():
        st.warning("Please enter the Acceptance Criteria.")

    else:
        with st.spinner("Generating test cases..."):

            prompt = build_prompt(us_title, us_description, us_ac)

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a senior QA engineer with 15 years of experience.
When given a User Story, generate test cases and return ONLY a JSON object.
No explanation. No extra text. No markdown. Just pure JSON.

Return exactly in this format:
{
  "test_cases": [
    {
      "id": "TC_001",
      "title": "...",
      "precondition": "...",
      "steps": "...",
      "expected_result": "...",
      "type": "Positive"
    }
  ]
}

Generate minimum 8 test cases covering positive, negative, and edge cases.
Type must be one of: Positive, Negative, Edge Case

STRICT RULES:
- Title must describe WHAT is being tested only. Example: "Verify valid login with correct credentials"
- Title must NEVER start with or include the words Positive, Negative or Edge Case
- Type field is the only place where Positive, Negative or Edge Case should appear"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

        # --- PARSE JSON RESPONSE ---
        raw = response.choices[0].message.content

        try:
            # Clean any accidental markdown like ```json
            clean = raw.strip().replace("```json", "").replace("```", "").strip()

            # Parse JSON
            data = json.loads(clean)
            test_cases = data["test_cases"]

            # --- SHOW AS TABLE ---
            st.success(f"✅ {len(test_cases)} Test cases generated!")
            df = pd.DataFrame(test_cases)
            df.columns = ["ID", "Title", "Precondition", "Steps", "Expected Result", "Type"]
            st.dataframe(df, use_container_width=True)

            # --- DOWNLOAD AS EXCEL ---
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="📥 Download Test Cases as Excel",
                data=buffer,
                file_name=f"{us_title[:30]}_test_cases.xlsx",
                mime="application/vnd.ms-excel"
            )

        except Exception as e:
            st.error("⚠️ AI returned an unexpected format. Please try generating again.")
            st.code(raw)