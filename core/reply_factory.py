
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []
    next_question_id = None
    if "answers" not in session:
        session["answers"] = {}

    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        bot_responses.append(error)
    else:
        next_question, next_question_id = get_next_question(current_question_id)

        if next_question:
            question_info = PYTHON_QUESTION_LIST[next_question_id]
            options_text = "\n".join(f"{index+1}. {option}" for index, option in enumerate(question_info['options']))
            next_question_with_options = f"{question_info['question_text']}\nOptions:\n{options_text}"
            bot_responses.append(next_question_with_options)
        else:
            final_response = generate_final_response(session)
            bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to session.
    '''
    if not current_question_id:
        return True, ""

    question = PYTHON_QUESTION_LIST[current_question_id]

    if answer not in question['options']:
        return PYTHON_QUESTION_LIST[current_question_id]['options']

    # Store the user's answer in the session for later evaluation
    session["answers"][current_question_id] = answer
    session.save()

    return True, ""


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    if current_question_id is None:
        next_question_id = 0
    else:
        next_question_id = current_question_id + 1

    if next_question_id < len(PYTHON_QUESTION_LIST):
        return PYTHON_QUESTION_LIST[next_question_id]['question_text'], next_question_id
    else:
        return None, None


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get("answers", {})
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0

    for question_id, question in enumerate(PYTHON_QUESTION_LIST):
        user_answer = user_answers.get(question_id)
        if user_answer and user_answer == question['answer']:
            correct_answers += 1

    score = (correct_answers / total_questions) * 100
    final_response = f"Your quiz is complete!\nYou answered {correct_answers} out of {total_questions} questions correctly.\nYour score: {score:.2f}%"

    return final_response
