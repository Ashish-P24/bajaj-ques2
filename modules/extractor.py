import os
import fitz  # PyMuPDF
import docx
import pandas as pd

def extract_text_from_file(file):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file)
    elif ext == ".docx":
        return extract_text_from_docx(file)
    elif ext in [".csv", ".xlsx"]:
        return extract_text_from_table(file, ext)
    else:
        return "❌ Unsupported file type"

def extract_text_from_pdf(file):
    try:
        file.file.seek(0)  # Ensure start of stream
        doc = fitz.open(stream=file.file.read(), filetype="pdf")
        return "\n".join([page.get_text() for page in doc])
    except Exception as e:
        return f"❌ Error reading PDF: {e}"

def extract_text_from_docx(file):
    try:
        file.file.seek(0)
        document = docx.Document(file.file)
        return "\n".join([para.text for para in document.paragraphs])
    except Exception as e:
        return f"❌ Error reading DOCX: {e}"

def extract_text_from_table(file, ext):
    try:
        file.file.seek(0)
        if ext == ".csv":
            df = pd.read_csv(file.file)
        elif ext == ".xlsx":
            df = pd.read_excel(file.file)
        else:
            return "❌ Unsupported table format"
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
