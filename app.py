from flask import Flask, request, render_template, send_file, flash, redirect
import os
from werkzeug.utils import secure_filename
import spacy
import random
from src.extract_text import extract_text_from_file

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_text(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    key_concepts = [chunk.text for chunk in doc.noun_chunks]
    return sentences, key_concepts

def generate_multiple_choice(sentences, key_concepts, num_questions):
    questions = []
    for sentence in sentences:
        if len(key_concepts) > 3 and len(questions) < num_questions:
            concept = random.choice(key_concepts)
            if concept in sentence:
                correct_answer = concept
                wrong_answers = random.sample([concept for concept in key_concepts if concept != correct_answer], 3)
                question = {
                    "question": sentence.replace(correct_answer, "______"),
                    "choices": wrong_answers + [correct_answer],
                    "answer": correct_answer
                }
                random.shuffle(question["choices"])
                questions.append(question)
    return questions

def generate_true_false(sentences, num_questions):
    questions = []
    for sentence in sentences:
        if sentence.strip() and len(questions) < num_questions:
            question = {
                "question": sentence,
                "answer": random.choice(["True", "False"])
            }
            questions.append(question)
    return questions

def generate_short_answer(sentences, key_concepts, num_questions):
    questions = []
    for sentence in sentences:
        if len(key_concepts) > 0 and len(questions) < num_questions:
            concept = random.choice(key_concepts)
            if concept in sentence:
                question = {
                    "question": sentence.replace(concept, "______"),
                    "answer": concept
                }
                questions.append(question)
    return questions

def generate_matching(sentences, key_concepts, num_questions):
    questions = []
    for _ in range(num_questions):
        if len(key_concepts) >= 4:
            pairs = random.sample(key_concepts, 4)
            question = {
                "question": "Match the terms to their definitions.",
                "pairs": [(pairs[i], pairs[i + 1]) for i in range(0, len(pairs), 2)]
            }
            questions.append(question)
    return questions

def format_multiple_choice_aiken(question):
    formatted_question = "{}\n".format(question['question'].replace('\n', ' '))
    choices = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, choice in enumerate(question['choices']):
        formatted_question += "{}. {}\n".format(choices[i], choice)
    correct_letter = choices[question['choices'].index(question['answer'])]
    formatted_question += "ANSWER: {}\n".format(correct_letter)
    return formatted_question

def format_true_false_aiken(question):
    formatted_question = "{}\n".format(question['question'].replace('\n', ' '))
    correct_answer = "A. True\nB. False\nANSWER: {}\n".format("A" if question['answer'] == "True" else "B")
    formatted_question += correct_answer
    return formatted_question

def format_multiple_choice_gift(question):
    formatted_question = "::{question} {{\n".format(question=question['question'])
    for choice in question['choices']:
        if choice == question['answer']:
            formatted_question += "   ={choice}\n".format(choice=choice)
        else:
            formatted_question += "   ~{choice}\n".format(choice=choice)
    formatted_question += "}\n"
    return formatted_question

def format_true_false_gift(question):
    answer = "T" if question['answer'] == "True" else "F"
    formatted_question = "::{question} {{\n   {answer}\n}}\n".format(question=question['question'], answer=answer)
    return formatted_question

def format_short_answer_gift(question):
    formatted_question = "::{question} {{\n   ={answer}\n}}\n".format(question=question['question'], answer=question['answer'])
    return formatted_question

def format_matching_gift(question):
    formatted_question = "::{question} {{\n".format(question=question['question'])
    for pair in question['pairs']:
        formatted_question += "   {term} -> {definition}\n".format(term=pair[0], definition=pair[1])
    formatted_question += "}\n"
    return formatted_question

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            text = extract_text_from_file(file_path)

            sentences, key_concepts = process_text(text)
            num_questions = int(request.form['num_questions'])
            question_types = request.form.getlist('question_types')
            
            mc_questions = generate_multiple_choice(sentences, key_concepts, num_questions) if 'mcq' in question_types else []
            tf_questions = generate_true_false(sentences, num_questions) if 'tf' in question_types else []
            sa_questions = generate_short_answer(sentences, key_concepts, num_questions) if 'sa' in question_types else []
            matching_questions = generate_matching(sentences, key_concepts, num_questions) if 'matching' in question_types else []
            
            format_choice = request.form['format']
            if format_choice == 'aiken':
                mc_questions_formatted = [format_multiple_choice_aiken(q) for q in mc_questions]
                tf_questions_formatted = [format_true_false_aiken(q) for q in tf_questions]
                output_filename = 'questions_aiken.txt'
            else:  # GIFT format
                mc_questions_formatted = [format_multiple_choice_gift(q) for q in mc_questions]
                tf_questions_formatted = [format_true_false_gift(q) for q in tf_questions]
                sa_questions_formatted = [format_short_answer_gift(q) for q in sa_questions]
                matching_questions_formatted = [format_matching_gift(q) for q in matching_questions]
                output_filename = 'questions_gift.txt'
                # Combine all GIFT questions into one list
                mc_questions_formatted.extend(tf_questions_formatted)
                mc_questions_formatted.extend(sa_questions_formatted)
                mc_questions_formatted.extend(matching_questions_formatted)
            
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            with open(output_path, 'w') as out_file:
                out_file.write("\n".join(mc_questions_formatted))
                if format_choice == 'aiken':
                    out_file.write("\n".join(tf_questions_formatted))

            return send_file(output_path, as_attachment=True)
        else:
            flash('Invalid file type. Only .txt, .pdf, and .docx files are allowed.')
            return redirect(request.url)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
