# 🧪 AI Test Case Generator

An AI-powered tool that generates structured test cases from User Stories instantly.

## Built With
- Python
- Streamlit
- Groq API (Llama 3)
- Pandas

## Features
- Input User Story Title, Description, and Acceptance Criteria
- AI generates minimum 8 test cases
- Covers Positive, Negative, and Edge Case scenarios
- Clean table display
- One-click Excel download

## How To Run

1. Clone this repository
2. Install dependencies
   pip install -r requirements.txt
3. Create a .env file and add your Groq API key
   GROQ_API_KEY=your_key_here
4. Run the app
   streamlit run app.py

## Version History

### v1.0 — Initial Build
- Basic User Story input
- AI test case generation
- Plain text output

### v2.0 — Structured Output
- Added Title, Description, Acceptance Criteria fields
- JSON structured AI response
- Table display
- Excel download
- Error handling
- Fixed Title and Type separation