import os
import json
import pandas as pd
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --- FUNCTIONS ---

def generate_testcases(title, description, ac):
    prompt = f"Title:{title}\nDescription:{description} \nAcceptance Criteria:{ac}\nGenerate exactly 5 test cases."
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages = [
            {
                "role" : "system",
                "content" : """You are a senior QA Engineer. Return only a JSON object. No explanation. No markdown.
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
            {"role" : "user", "content" : prompt}
        ]
    )
    raw = response.choices[0].message.content
    clean = raw.strip().replace("```json", "").replace("```", "").strip()
    return json.loads(clean)["test_cases"]

def save_excel_with_comments (test_cases, filename):
    df = pd.DataFrame(test_cases)
    df.columns = ["ID", "Title", "Precondition", "Steps", "Expected Result", "Type"]
    df["Comments"] = ""
    df.to_excel(filename, index=False)
    print(f"Saved: {filename}")

def read_excel_with_comments(filename):
    df = pd.read_excel(filename)
    # Convert each row back to a dict, separate comments
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
    return test_cases, comments

def build_revision_prompt(title, description, ac, test_cases, comments):
    # Pair each TC with its comment so the AI knows exactly what to change
    tcs_with_comments = []
    for tc, comment in zip(test_cases, comments):
        entry = dict(tc)
        entry["review_comment"] = comment if comment and comment != "nan" else "No Changes"
        tcs_with_comments.append(entry)
    
    return f"""
Title:{title}
Description:{description}
Acceptance criteria:{ac}

Test cases with reviewer comments:
{json.dumps(tcs_with_comments, indent=2)}

Instructions:
- Read the review_comment field for each test case
- If review_comment is "No changes", keep that test case exactly as-is
- If there is a comment, revise that test case accordingly
- If a comment says "remove", exclude that test case
- If a comment says "add [something]", add a new test case at the end
- Return ONLY the revised test cases in the same JSON format, without the review_comment field
"""

def revise_testcases(revision_prompt):
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
            {"role" : "user", "content" : revision_prompt}
        ]
    )
    raw = response.choices[0].message.content
    clean = raw.strip().replace("```json","").replace("```", "").strip()
    return json.loads(clean)["test_cases"]

# --- MAIN ---

def main():
    print("=== Excel-Based Test case Review Loop ===\n")

    # Step 1: Take user story input
    title = input("User Story Title: ")
    description = input("Description: ")
    ac = input("Acceptance Criteria: ")

    # Step 2: Saving to Excel
    print("\nGenerating Test Cases...")
    test_cases = generate_testcases(title, description, ac)
    output_file = "learning/tc_review.xlsx"
    save_excel_with_comments(test_cases, output_file)

    revision_count = 0

    while True:
        print(f"\n{'='*50}")
        print(f"Excel Saved: {output_file}")
        print("1. Open the Excel file")
        print("2. Fill in the 'Comments' column for any TC you want changed")
        print("3. Save and close the file")
        print(f"{'='*50}")
        print("\nOptions: [r] Upload Reviewed Excel [a] Approve & Finish")
        choice  = input("Your Choice: ").strip().lower()

        if choice == "a":
            print(f"\n✅ Approved after {revision_count} revision(s).")
            break
        elif choice == "r":
            upload_file = input("Path to reviewed Excel file (press Enter to use same file): ").strip()
            if not upload_file:
                upload_file = output_file
            print("\nReading your comments...")
            test_cases, comments = read_excel_with_comments(upload_file)
            has_comments = any(c and c != "nan" for c in comments)
            if not has_comments:
                print("No comments found in the Excel. Please add comments in the 'Comments' column.")
                continue

            print("Revising test cases based on your comments...")
            revision_prompt = build_revision_prompt(title, description, ac, test_cases, comments)
            test_cases = revise_testcases(revision_prompt)
            revision_count += 1

             # Save revised version back to Excel (with fresh Comments column)
            save_excel_with_comments(test_cases, output_file)
            print(f"✅ Revised! {len(test_cases)} test cases. Open Excel to review again.")
        else:
            print("Type 'r' to upload reviewed Excel or 'a' to approve.")

main()