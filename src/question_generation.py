import random

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
