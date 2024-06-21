from flask import Flask, request, render_template, send_file, flash, redirect, url_for
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
import spacy
import random
from src.extract_text import extract_text_from_file
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx'}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_text(text):
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    key_concepts = [chunk.text for chunk in doc.noun_chunks]
    return sentences, key_concepts

def char_filter(value):
    return chr(65 + value)

app.jinja_env.filters['char'] = char_filter

# Load environment variables from .env file
load_dotenv()

# Load the OpenAI API key from environment variables or another secure location
# Initialize OpenAI client
client_remote = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
#Initialize OpenAI client pointing to the local server
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
def generate_questions_with_gpt3(prompt, num_questions):
    chat_completion = client_remote.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="gpt-3.5-turbo-instruct",
        max_tokens=150,
        n=num_questions,
        stop=None,
        temperature=0.7,
    )
    questions = []
    for choice in chat_completion.choices:
        questions.append(choice.message['content'].strip())
    return questions

def generate_multiple_choice_with_gpt3(sentences, num_questions):
    prompt = "Generate multiple choice questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <question>\nA. <option1>\nB. <option2>\nC. <option3>\nD. <option4>\nAnswer: <correct_option>"
    return generate_questions_with_gpt3(prompt, num_questions)

def generate_true_false_with_gpt3(sentences, num_questions):
    prompt = "Generate true/false questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <question>\nAnswer: <True/False>"
    return generate_questions_with_gpt3(prompt, num_questions)

def generate_short_answer_with_gpt3(sentences, num_questions):
    prompt = "Generate short answer questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <question>\nAnswer: <answer>"
    return generate_questions_with_gpt3(prompt, num_questions)

def generate_matching_with_gpt3(sentences, num_questions):
    prompt = "Generate matching questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <term1> -> <definition1>\n<term2> -> <definition2>\n..."
    return generate_questions_with_gpt3(prompt, num_questions)


def generate_multiple_choice(sentences, key_concepts, num_questions, difficulty, topics):
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
                    "answer": correct_answer,
                    "difficulty": difficulty,
                    "topics": topics
                }
                random.shuffle(question["choices"])
                questions.append(question)
    return questions

def generate_true_false(sentences, num_questions, difficulty, topics):
    questions = []
    for sentence in sentences:
        if sentence.strip() and len(questions) < num_questions:
            question = {
                "question": sentence,
                "answer": random.choice(["True", "False"]),
                "difficulty": difficulty,
                "topics": topics
            }
            questions.append(question)
    return questions

def generate_short_answer(sentences, key_concepts, num_questions, difficulty, topics):
    questions = []
    for sentence in sentences:
        if len(key_concepts) > 0 and len(questions) < num_questions:
            concept = random.choice(key_concepts)
            if concept in sentence:
                question = {
                    "question": sentence.replace(concept, "______"),
                    "answer": concept,
                    "difficulty": difficulty,
                    "topics": topics
                }
                questions.append(question)
    return questions

def generate_matching(sentences, key_concepts, num_questions, difficulty, topics):
    questions = []
    for _ in range(num_questions):
        if len(key_concepts) >= 4:
            pairs = random.sample(key_concepts, 4)
            question = {
                "question": "Match the terms to their definitions.",
                "pairs": [(pairs[i], pairs[i + 1]) for i in range(0, len(pairs), 2)],
                "difficulty": difficulty,
                "topics": topics
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

def generate_questions_with_local_model(prompt, num_questions):
    try:
        response = client.chat_completions.create(
            model="lmstudio-ai/gemma-2b-it-GGUF/gemma-2b-it-q8_0.gguf",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        questions = []
        for choice in response.choices:
            questions.append(choice.message['content'].strip())
        return questions
    except Exception as e:
        print(f"Error generating questions: {e}")
        return ["Error: Could not generate questions. Please try again later."]

def generate_multiple_choice_with_local_model(sentences, num_questions):
    prompt = "Generate multiple choice questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <question>\nA. <option1>\nB. <option2>\nC. <option3>\nD. <option4>\nAnswer: <correct_option>"
    return generate_questions_with_local_model(prompt, num_questions)

def generate_true_false_with_local_model(sentences, num_questions):
    prompt = "Generate true/false questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <question>\nAnswer: <True/False>"
    return generate_questions_with_local_model(prompt, num_questions)

def generate_short_answer_with_local_model(sentences, num_questions):
    prompt = "Generate short answer questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <question>\nAnswer: <answer>"
    return generate_questions_with_local_model(prompt, num_questions)

def generate_matching_with_local_model(sentences, num_questions):
    prompt = "Generate matching questions from the following sentences:\n\n"
    for sentence in sentences:
        prompt += f"- {sentence}\n"
    prompt += "\nGenerate the questions in the format:\nQ: <term1> -> <definition1>\n<term2> -> <definition2>\n..."
    return generate_questions_with_local_model(prompt, num_questions)
@app.route('/')
def upload_file():
    return render_template('upload.html')
@app.route('/uploader', methods=['GET', 'POST'])
def uploader_file():
    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                text = extract_text_from_file(file_path)
            else:
                flash('Invalid file type. Only .txt, .pdf, and .docx files are allowed.')
                return redirect(request.url)
        elif 'pasted_text' in request.form and request.form['pasted_text'].strip() != '':
            text = request.form['pasted_text'].strip()
        else:
            flash('No file or text provided.')
            return redirect(request.url)

        sentences, key_concepts = process_text(text)
        num_questions = int(request.form['num_questions'])
        question_types = request.form.getlist('question_types')
        difficulty = request.form.get('difficulty', 'medium')
        topics = request.form.get('topics', '').split(',')
        preview = 'preview' in request.form

        mc_questions = generate_multiple_choice_with_local_model(sentences, num_questions) if 'mcq' in question_types else []
        tf_questions = generate_true_false_with_local_model(sentences, num_questions) if 'tf' in question_types else []
        sa_questions = generate_short_answer_with_local_model(sentences, num_questions) if 'sa' in question_types else []
        matching_questions = generate_matching_with_local_model(sentences, num_questions) if 'matching' in question_types else []

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

        if preview:
            preview_questions = mc_questions[:2] + tf_questions[:2] + sa_questions[:2] + matching_questions[:2]
            return render_template('preview.html', questions=preview_questions)

        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        with open(output_path, 'w') as out_file:
            out_file.write("\n".join(mc_questions_formatted))
            if format_choice == 'aiken':
                out_file.write("\n".join(tf_questions_formatted))

        return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', debug=True, port=port)
    