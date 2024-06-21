from docx import Document

def extract_text_from_docx(docx_path):
    document = Document(docx_path)
    text = ""
    for paragraph in document.paragraphs:
        text += paragraph.text + "\n"
    return text

# Example usage
if __name__ == "__main__":
    docx_text = extract_text_from_docx("../data/docx/sample.docx")
    print(docx_text)
