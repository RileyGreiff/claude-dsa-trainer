"""Question selection logic."""

import random

# How many recent question IDs to avoid repeating
RECENT_WINDOW = 5


def select_question(questions, progress):
    """Pick a question, avoiding recent repeats and biasing toward missed ones.

    Args:
        questions: list of question dicts from the question bank.
        progress:  the full progress dict (contains 'recent_ids' and 'questions').

    Returns:
        A single question dict.
    """
    recent_ids = progress.get("recent_ids", [])
    question_stats = progress.get("questions", {})

    # Filter out recently-asked questions (if we have enough to choose from)
    pool = [q for q in questions if q["id"] not in recent_ids]
    if not pool:
        pool = list(questions)

    # Build weighted pool: questions answered incorrectly get extra weight
    weighted = []
    for q in pool:
        stats = question_stats.get(q["id"], {})
        wrong = stats.get("wrong", 0)
        # Base weight 1, +2 for each wrong answer to bias toward weak areas
        weight = 1 + 2 * wrong
        weighted.extend([q] * weight)

    return random.choice(weighted)
