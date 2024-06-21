def save_questions_to_file(questions, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for question in questions:
            f.write(question + "\n\n")