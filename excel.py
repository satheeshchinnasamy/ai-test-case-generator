import pandas as pd
from io import BytesIO


def to_df(test_cases):
    df = pd.DataFrame(test_cases)
    df.columns = ["ID", "Title", "Precondition", "Steps", "Expected Result", "Type"]
    return df

def to_excel(df):
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def to_excel_with_comments(df):
    df = df.copy()
    df["Comments"] = ""
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer

def read_reviewed_excel(file):
    df = pd.read_excel(file)
    test_cases, comments = [], []
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