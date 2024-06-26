import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()
    return text

# Example usage
if __name__ == "__main__":
    pdf_text = extract_text_from_pdf("../data/pdfs/sample.pdf")
    print(pdf_text)
