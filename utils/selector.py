"""Question selection logic."""

import random

# How many recent question IDs to avoid repeating back-to-back
RECENT_WINDOW = 5

# Extra weight added per wrong answer. Kept small so missed questions are
# only *slightly* favored rather than dominating the rotation.
WRONG_WEIGHT = 0.25


def select_question(questions, progress):
    """Pick a question by cycling through the whole bank in randomized order.

    Every question is shown once per cycle before any of them repeat, so the
    rotation covers the entire bank instead of fixating on the most-missed
    ones. Within each cycle the order is random, with a slight bias toward
    questions the user has missed more often.

    Args:
        questions: list of question dicts from the question bank.
        progress:  the full progress dict (mutated to track the current cycle).

    Returns:
        A single question dict.
    """
    recent_ids = progress.get("recent_ids", [])
    question_stats = progress.get("questions", {})

    all_ids = {q["id"] for q in questions}

    # Drop ids for questions that no longer exist, and start a fresh cycle once
    # every question has been shown.
    seen_this_cycle = [
        qid for qid in progress.get("cycle_seen", []) if qid in all_ids
    ]
    if set(seen_this_cycle) >= all_ids:
        seen_this_cycle = []

    # Prefer questions not yet shown in this cycle...
    pool = [q for q in questions if q["id"] not in seen_this_cycle]
    # ...and, when possible, avoid immediately repeating a recent question.
    non_recent = [q for q in pool if q["id"] not in recent_ids]
    if non_recent:
        pool = non_recent

    # Slight bias toward questions missed more often.
    weights = [
        1 + WRONG_WEIGHT * question_stats.get(q["id"], {}).get("wrong", 0)
        for q in pool
    ]

    chosen = random.choices(pool, weights=weights, k=1)[0]

    seen_this_cycle.append(chosen["id"])
    progress["cycle_seen"] = seen_this_cycle

    return chosen
