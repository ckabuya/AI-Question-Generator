import textract
import os
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document

def extract_text_from_pdf(file_path):
    try:
        text = extract_pdf_text(file_path)
        return text
    except Exception as e:
        print(f"Error extracting text from PDF {file_path}: {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        print(f"Error extracting text from DOCX {file_path}: {e}")
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except Exception as e:
        print(f"Error extracting text from TXT {file_path}: {e}")
        return ""

def extract_text_from_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_extension.lower() == '.docx':
        return extract_text_from_docx(file_path)
    elif file_extension.lower() == '.txt':
        return extract_text_from_txt(file_path)
    else:
        print(f"Unsupported file type: {file_extension}")
        return ""
