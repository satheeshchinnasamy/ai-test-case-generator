import streamlit as st
from llm import build_prompt, generate_testcases, revise_testcases
from excel import to_df, to_excel_with_comments, read_reviewed_excel

st.title("🧪 AI Test Case Generator")
st.write("Fill in the User Story details and generate test cases instantly.")
st.divider()

us_title = st.text_input("User Story Title", placeholder="Example: User Login with Email and Password")
us_description = st.text_area("User Story Description", height=100,
    placeholder="Example: As a user, I want to login with my email and password so that I can access my account.")
us_ac = st.text_area("Acceptance Criteria", height=150,
    placeholder="1. User can login with valid email and password\n2. Error message shown for invalid credentials")

st.divider()

if st.button("🚀 Generate Test Cases"):
    if not us_title.strip():
        st.warning("Please enter the User Story Title.")
    elif not us_description.strip():
        st.warning("Please enter the User Story Description.")
    elif not us_ac.strip():
        st.warning("Please enter the Acceptance Criteria.")
    else:
        with st.spinner("Generating test cases..."):
            try:
                test_cases = generate_testcases(build_prompt(us_title, us_description, us_ac))
                st.success(f"✅ {len(test_cases)} test cases generated!")
                df = to_df(test_cases)
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    label="📥 Download for Review (with Comments column)",
                    data=to_excel_with_comments(df),
                    file_name=f"{us_title[:30]}_review.xlsx",
                    mime="application/vnd.ms-excel"
                )
            except Exception as e:
                st.error("⚠️ AI returned an unexpected format. Please try again.")
                st.code(str(e))

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
                try:
                    test_cases, comments = read_reviewed_excel(uploaded_file)
                    tcs_with_comments = [
                        {**tc, "review_comment": c if c and c != "nan" else "No Changes"}
                        for tc, c in zip(test_cases, comments)
                    ]
                    revised = revise_testcases(rev_title, rev_description, rev_ac, tcs_with_comments)
                    st.success(f"✅ Revised! {len(revised)} test cases.")
                    df_revised = to_df(revised)
                    st.dataframe(df_revised, use_container_width=True)
                    st.download_button(
                        label="📥 Download Revised TCs",
                        data=to_excel_with_comments(df_revised),
                        file_name=f"{rev_title[:30]}_revised.xlsx",
                        mime="application/vnd.ms-excel",
                        key="revised_download"
                    )
                except Exception as e:
                    st.error("⚠️ Something went wrong.")
                    st.code(str(e))