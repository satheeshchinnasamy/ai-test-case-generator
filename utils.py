import docx
import pdfplumber

def extract_text_from_document(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".docx"):
        document = docx.Document(uploaded_file)
        return "\n".join([p.text for p in document.paragraphs if p.text.strip()])
    elif name.endswith(".pdf"):
        text=""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    return ""