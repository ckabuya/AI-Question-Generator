from flask import Flask, request, render_template, send_file
import os
from werkzeug.utils import secure_filename
import spacy
import random

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

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

def generate_multiple_choice(sentences, key_concepts):
    questions = []
    for sentence in sentences:
        if len(key_concepts) > 3:
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

def generate_true_false(sentences):
    questions = []
    for sentence in sentences:
        if sentence.strip():
            question = {
                "question": sentence,
                "answer": random.choice(["True", "False"])
            }
            questions.append(question)
    return questions

def generate_short_answer(sentences, key_concepts):
    questions = []
    for sentence in sentences:
        if len(key_concepts) > 0:
            concept = random.choice(key_concepts)
            if concept in sentence:
                question = {
                    "question": sentence.replace(concept, "______"),
                    "answer": concept
                }
                questions.append(question)
    return questions

def generate_matching(sentences, key_concepts):
    questions = []
    if len(key_concepts) >= 4:
        pairs = random.sample(key_concepts, 4)
        question = {
            "question": "Match the terms to their definitions.",
            "pairs": [(pairs[i], pairs[i + 1]) for i in range(0, len(pairs), 2)]
        }
        questions.append(question)
    return questions

def format_multiple_choice_aiken(question):
    formatted_question = f"{question['question']}\n"
    choices = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, choice in enumerate(question['choices']):
        formatted_question += f"{choices[i]}. {choice}\n"
    correct_letter = choices[question['choices'].index(question['answer'])]
    formatted_question += f"ANSWER: {correct_letter}\n"
    return formatted_question

def format_true_false_aiken(question):
    formatted_question = f"{question['question']}\n"
    correct_answer = "A. True\nB. False\nANSWER: " + ("A" if question['answer'] == "True" else "B") + "\n"
    formatted_question += correct_answer
    return formatted_question

def format_multiple_choice_gift(question):
    formatted_question = f"::{question['question']} {{\n"
    for choice in question['choices']:
        if choice == question['answer']:
            formatted_question += f"   ={choice}\n"
        else:
            formatted_question += f"   ~{choice}\n"
    formatted_question += "}\n"
    return formatted_question

def format_true_false_gift(question):
    answer = "T" if question['answer'] == "True" else "F"
    formatted_question = f"::{question['question']} {{\n   {answer}\n}}\n"
    return formatted_question

def format_short_answer_gift(question):
    formatted_question = f"::{question['question']} {{\n   ={question['answer']}\n}}\n"
    return formatted_question

def format_matching_gift(question):
    formatted_question = f"::{question['question']} {{\n"
    for pair in question['pairs']:
        formatted_question += f"   {pair[0]} -> {pair[1]}\n"
    formatted_question += "}\n"
    return formatted_question

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        file = request.files['file']
        if file.filename == '':
            return 'No selected file'
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            with open(file_path, 'r') as f:
                text = f.read()

            sentences, key_concepts = process_text(text)
            mc_questions = generate_multiple_choice(sentences, key_concepts)
            tf_questions = generate_true_false(sentences)
            sa_questions = generate_short_answer(sentences, key_concepts)
            matching_questions = generate_matching(sentences, key_concepts)
            
            aiken_mc_questions = [format_multiple_choice_aiken(q) for q in mc_questions]
            aiken_tf_questions = [format_true_false_aiken(q) for q in tf_questions]
            gift_mc_questions = [format_multiple_choice_gift(q) for q in mc_questions]
            gift_tf_questions = [format_true_false_gift(q) for q in tf_questions]
            gift_sa_questions = [format_short_answer_gift(q) for q in sa_questions]
            gift_matching_questions = [format_matching_gift(q) for q in matching_questions]

            output_filename_aiken = 'questions_aiken.txt'
            output_path_aiken = os.path.join(app.config['UPLOAD_FOLDER'], output_filename_aiken)
            with open(output_path_aiken, 'w') as out_file:
                out_file.write("\n".join(aiken_mc_questions))
                out_file.write("\n".join(aiken_tf_questions))

            output_filename_gift = 'questions_gift.txt'
            output_path_gift = os.path.join(app.config['UPLOAD_FOLDER'], output_filename_gift)
            with open(output_path_gift, 'w') as out_file:
                out_file.write("\n".join(gift_mc_questions))
                out_file.write("\n".join(gift_tf_questions))
                out_file.write("\n".join(gift_sa_questions))
                out_file.write("\n".join(gift_matching_questions))

            return send_file(output_path_gift, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
