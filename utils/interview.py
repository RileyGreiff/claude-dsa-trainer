"""Interview prep mode: read a question, think, then study a strong answer.

Unlike the quiz, nothing here is graded. Each card shows an interview question,
waits while you form your own answer, then reveals a model answer plus the key
points an interviewer listens for. You rate yourself afterwards, and that rating
feeds the same selector the quiz uses so weak cards resurface more often.
"""

import textwrap

WIDTH = 76
INDENT = "  "

# Self-ratings, keyed by the number the user types. Each maps to the
# correct/wrong counters that utils.selector already knows how to weight.
RATINGS = {
    "1": ("nailed it", 1, 0),
    "2": ("shaky", 0, 1),
    "3": ("blank", 0, 2),
}


def wrap(text, indent=INDENT):
    """Wrap a possibly multi-paragraph string for terminal display."""
    paragraphs = text.split("\n\n")
    wrapped = [
        textwrap.fill(p, width=WIDTH, initial_indent=indent, subsequent_indent=indent)
        for p in paragraphs
    ]
    return "\n\n".join(wrapped)


def bullets(items, indent=INDENT + "  "):
    """Render a list as wrapped bullet points."""
    lines = []
    for item in items:
        lines.append(
            textwrap.fill(
                item,
                width=WIDTH,
                initial_indent=indent + "- ",
                subsequent_indent=indent + "  ",
            )
        )
    return "\n".join(lines)


def empty_progress():
    """Fresh interview progress block.

    Deliberately uses the same key names as the quiz progress dict so it can be
    handed straight to utils.selector.select_question.
    """
    return {"cards_seen": 0, "recent_ids": [], "questions": {}, "cycle_seen": []}


def get_interview_progress(progress):
    """Fetch (and initialize if absent) the interview section of progress.json."""
    section = progress.setdefault("interview", empty_progress())
    for key, default in empty_progress().items():
        section.setdefault(key, default)
    return section


def display_card(card, index, total):
    """Print the question side of a card."""
    print(f"\n{INDENT}{'-' * (WIDTH - 2)}")
    print(f"{INDENT}Card {index}/{total}  |  {card['topic']}  |  "
          f"{card['category']}  |  {card['difficulty']}")
    print(f"{INDENT}{'-' * (WIDTH - 2)}\n")
    print(wrap(card["question"]))
    print()


def reveal_card(card):
    """Print the model answer, key points, and likely follow-ups."""
    print(f"\n{INDENT}A strong answer:\n")
    print(wrap(card["answer"]))
    print(f"\n{INDENT}What an interviewer is listening for:")
    print(bullets(card["key_points"]))
    print(f"\n{INDENT}Likely follow-ups:")
    print(bullets(card["followups"]))
    print()


def prompt_enter(message):
    """Wait for Enter. Returns False if the user wants to quit."""
    try:
        response = input(f"{INDENT}{message}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return response not in ("q", "quit", "exit")


def get_rating():
    """Ask how it went. Returns a RATINGS key, or None if skipped/aborted."""
    prompt = f"{INDENT}How'd you do?  [1] nailed it  [2] shaky  [3] blank  (Enter to skip): "
    while True:
        try:
            choice = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if not choice:
            return None
        if choice in RATINGS:
            return choice
        print(f"{INDENT}  Enter 1, 2, 3, or just press Enter.")


def record_rating(section, card_id, rating):
    """Fold a self-rating into the interview progress block."""
    section["cards_seen"] += 1

    stats = section["questions"].setdefault(card_id, {"correct": 0, "wrong": 0})
    if rating is not None:
        _, correct, wrong = RATINGS[rating]
        stats["correct"] += correct
        stats["wrong"] += wrong

    recent = section["recent_ids"]
    recent.append(card_id)
    # Keep the same short window the quiz uses to avoid back-to-back repeats.
    if len(recent) > 5:
        section["recent_ids"] = recent[-5:]


def print_summary(tally, section):
    """Print the end-of-session recap."""
    done = sum(tally.values())
    if not done:
        print(f"\n{INDENT}No cards rated this session.\n")
        return

    print(f"\n{INDENT}{'-' * (WIDTH - 2)}")
    print(f"{INDENT}Session recap")
    for key in ("1", "2", "3"):
        label = RATINGS[key][0]
        print(f"{INDENT}  {label:<10} {tally[key]}")
    print(f"{INDENT}  {'total':<10} {done}")
    print(f"{INDENT}Cards studied all-time: {section['cards_seen']}")
    print(f"{INDENT}{'-' * (WIDTH - 2)}\n")
