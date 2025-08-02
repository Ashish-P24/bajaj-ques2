import os
import fitz  # PyMuPDF
import docx
import pandas as pd

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path.name)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext == ".docx":
        return extract_text_from_docx(file_path)
    elif ext in [".csv", ".xlsx"]:
        return extract_text_from_table(file_path)
    else:
        return ""

def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    except Exception as e:
        return f"❌ Error reading PDF: {e}"

def extract_text_from_docx(file):
    try:
        document = docx.Document(file)
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        return f"❌ Error reading DOCX: {e}"

def extract_text_from_table(file):
    ext = os.path.splitext(file.name)[1].lower()
    try:
        if ext == ".csv":
            df = pd.read_csv(file)
        elif ext == ".xlsx":
            df = pd.read_excel(file)
        else:
            return ""
        return df.to_string(index=False)
    except Exception as e:
        return f"❌ Error reading table: {e}"

def chunk_text(text, max_length=400):
    sentences = text.split('. ')
    chunks = []
    current = ""

    for sentence in sentences:
        if len(current) + len(sentence) < max_length:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())

    return chunks
