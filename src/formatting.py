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
