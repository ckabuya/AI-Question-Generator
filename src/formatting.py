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
    for i, pair in enumerate(question['pairs']):
        formatted_question += f"   {pair[0]} -> {pair[1]}\n"
    formatted_question += "}\n"
    return formatted_question


