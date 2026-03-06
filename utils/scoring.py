"""Answer checking logic for each question type."""

from utils.normalize import (
    normalize_text,
    normalize_code_fragment,
    normalize_complexity,
)


def check_answer(question, user_input):
    """Return True if user_input is a correct answer for the given question.

    Supports question types: mcq, fill_code, predict_output, short_answer.
    """
    qtype = question["type"]
    correct = question["answer"]

    if qtype == "mcq":
        return normalize_text(user_input) == normalize_text(correct)

    if qtype == "fill_code":
        # Accept any of the valid answers (answer can be a string or list)
        accepted = correct if isinstance(correct, list) else [correct]
        user_norm = normalize_code_fragment(user_input)
        return any(normalize_code_fragment(a) == user_norm for a in accepted)

    if qtype == "predict_output":
        return normalize_text(user_input) == normalize_text(correct)

    if qtype == "short_answer":
        # Accept any of the valid answers
        accepted = correct if isinstance(correct, list) else [correct]
        user_norm = normalize_complexity(user_input)
        return any(normalize_complexity(a) == user_norm for a in accepted)

    return False
