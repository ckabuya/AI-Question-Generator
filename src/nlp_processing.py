import spacy
import random

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def process_text(text):
    # Process the text using SpaCy
    doc = nlp(text)
    
    # Extract sentences
    sentences = [sent.text for sent in doc.sents]
    
    # Extract key concepts (nouns and proper nouns)
    key_concepts = [chunk.text for chunk in doc.noun_chunks]
    
    return sentences, key_concepts

def generate_multiple_choice(sentences, key_concepts):
    questions = []
    for sentence in sentences:
        if len(key_concepts) > 3:
            correct_answer = random.choice(key_concepts)
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
        question = {
            "question": sentence,
            "answer": random.choice(["True", "False"])
        }
        questions.append(question)
    return questions

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
    
    print("Multiple Choice Questions:", mc_questions)
    print("True/False Questions:", tf_questions)
