import random
import spacy

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def process_text(text):
    # Process the text using SpaCy
    doc = nlp(text)
    
    # Extract sentences
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    # Extract key concepts (nouns and proper nouns)
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


# Example usage
if __name__ == "__main__":
    sample_text = """
    The ArrayList class is a resizable array, which can be found in the java.util package.
    The difference between a built-in array and an ArrayList in Java, is that the size of an array cannot be modified (if you want to add or remove elements to/from an array, you have to create a new one). 
    While elements can be added and removed from an ArrayList whenever you want.
    """
    sentences, key_concepts = process_text(sample_text)
    mc_questions = generate_multiple_choice(sentences, key_concepts)
    tf_questions = generate_true_false(sentences)
    
    aiken_mc_questions = [format_multiple_choice_aiken(q) for q in mc_questions]
    aiken_tf_questions = [format_true_false_aiken(q) for q in tf_questions]
    
    print("Aiken Multiple Choice Questions:\n", "\n".join(aiken_mc_questions))
    print("Aiken True/False Questions:\n", "\n".join(aiken_tf_questions))
