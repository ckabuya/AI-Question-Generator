import textract
import os

def extract_text_from_file(file_path):
    try:
        text = textract.process(file_path)
        return text.decode('utf-8')
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""
