def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return text

# Example usage
if __name__ == "__main__":
    txt_text = extract_text_from_txt("../data/txt/sample.txt")
    print(txt_text)
