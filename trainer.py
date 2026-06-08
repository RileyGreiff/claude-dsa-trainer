#!/usr/bin/env python3
"""claude-dsa-trainer: micro coding practice between AI prompts."""

import json
import sys
from pathlib import Path

from utils.normalize import normalize_text
from utils.scoring import check_answer
from utils.selector import select_question, RECENT_WINDOW

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
QUESTIONS_PATH = BASE_DIR / "question_bank.json"
PROGRESS_PATH = BASE_DIR / "progress.json"


def has_api_key(config):
    """Check if an Anthropic API key is configured."""
    return bool(config.get("anthropic_api_key", "").strip())


def ask_followup(question, config):
    """Let the user ask follow-up questions about the topic using Claude API."""
    try:
        import anthropic
    except ImportError:
        print("  (Install the anthropic package to enable follow-ups: pip install anthropic)\n")
        return

    client = anthropic.Anthropic(api_key=config["anthropic_api_key"])

    context = f"Topic: {question['topic']}\n"
    context += f"Question: {question['question']}\n"
    correct = question["answer"]
    if isinstance(correct, list):
        correct = correct[0]
    context += f"Answer: {correct}\n"
    context += f"Explanation: {question['explanation']}"

    messages = []

    while True:
        try:
            followup = input("  Follow-up (Enter to close): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not followup:
            break

        messages.append({"role": "user", "content": followup})

        try:
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=300,
                system=f"You are a concise DSA tutor. Answer based on this context:\n\n{context}\n\nKeep answers short (2-4 sentences). Use simple language.",
                messages=messages,
            )
            reply = response.content[0].text
            print(f"\n  {reply}\n")
            messages.append({"role": "assistant", "content": reply})
        except Exception as e:
            print(f"\n  API error: {e}\n")
            break


def setup_api_key():
    """Prompt the user to enter their Anthropic API key."""
    config = load_json(CONFIG_PATH)
    current = config.get("anthropic_api_key", "")

    if current:
        masked = current[:8] + "..." + current[-4:]
        print(f"\n  Current API key: {masked}")
        print("  Enter a new key to replace it, or press Enter to keep it.\n")
    else:
        print("\n  No API key configured.")
        print("  Get one at: https://console.anthropic.com/settings/keys\n")

    try:
        key = input("  Anthropic API key: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n  Cancelled.\n")
        return

    if not key:
        print("  No changes made.\n")
        return

    config["anthropic_api_key"] = key
    save_json(CONFIG_PATH, config)
    print("  API key saved. Follow-up questions are now enabled.\n")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def display_question(question):
    """Print the question to the terminal."""
    print(f"\n  Topic: {question['topic']}")
    print(f"  Difficulty: {question['difficulty'].capitalize()}\n")
    print(f"  {question['question']}\n")

    if question["type"] == "mcq":
        for letter, text in question["choices"].items():
            print(f"    {letter}. {text}")
        print()


def get_user_answer(config):
    """Prompt for an answer. Returns the answer string, or None if skipped."""
    hints = []
    if config["allow_skip"]:
        hints.append("'skip'")
    hints.append("'?' for answer")
    hint_text = f" ({', '.join(hints)})" if hints else ""
    try:
        answer = input(f"  Your answer{hint_text}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    if config["allow_skip"] and normalize_text(answer) == "skip":
        return None
    return answer


def show_answer(question):
    """Reveal the correct answer and explanation."""
    correct_display = question["answer"]
    if isinstance(correct_display, list):
        correct_display = correct_display[0]
    print(f"\n  Answer: {correct_display}")
    print(f"  Explanation: {question['explanation']}\n")


def run_question(question, config):
    """Present a question and return (answered: bool, correct: bool)."""
    display_question(question)

    retries = config.get("max_retries", 2)
    for attempt in range(1, retries + 1):
        answer = get_user_answer(config)
        if answer is None:
            print("\n  Skipped.\n")
            return False, False

        if answer == "?":
            show_answer(question)
            return True, False

        if check_answer(question, answer):
            print(f"\n  Correct!")
            print(f"  Explanation: {question['explanation']}\n")
            return True, True

        remaining = retries - attempt
        if remaining > 0:
            print(f"\n  Not quite. {remaining} {'try' if remaining == 1 else 'tries'} left.")
        else:
            show_answer(question)

    return True, False


def update_progress(progress, question_id, answered, correct):
    """Update progress stats after a question attempt."""
    if answered:
        progress["total_answered"] += 1
    if correct:
        progress["total_correct"] += 1

    # Per-question stats
    qstats = progress["questions"].setdefault(question_id, {"correct": 0, "wrong": 0})
    if answered:
        if correct:
            qstats["correct"] += 1
        else:
            qstats["wrong"] += 1

    # Track recent IDs to avoid repeats
    recent = progress.setdefault("recent_ids", [])
    recent.append(question_id)
    if len(recent) > RECENT_WINDOW:
        progress["recent_ids"] = recent[-RECENT_WINDOW:]


def main():
    # Load data
    config = load_json(CONFIG_PATH)
    questions = load_json(QUESTIONS_PATH)
    progress = load_json(PROGRESS_PATH)

    if not config.get("enabled", True):
        return

    # When launched by hook, the counter is already incremented.
    # When launched manually, increment it ourselves.
    launched_by_hook = "--hook" in sys.argv
    if not launched_by_hook:
        progress["prompt_count"] = progress.get("prompt_count", 0) + 1
        freq = config.get("prompt_frequency", 3)
        if progress["prompt_count"] % freq != 0:
            save_json(PROGRESS_PATH, progress)
            return

    # Show header
    prompt_num = progress["prompt_count"]
    print(f"\n  Prompt #{prompt_num} triggered a quick ML rep.")

    # Select and run a question
    question = select_question(questions, progress)
    answered, correct = run_question(question, config)
    update_progress(progress, question["id"], answered, correct)
    save_json(PROGRESS_PATH, progress)

    # Stats summary
    total = progress["total_answered"]
    right = progress["total_correct"]
    pct = (right / total * 100) if total > 0 else 0
    print(f"  Stats: {right}/{total} correct ({pct:.0f}%)")
    print("  You may now continue your AI prompt.\n")

    # Offer follow-up if API key is configured
    if has_api_key(config) and answered:
        ask_followup(question, config)
    elif launched_by_hook:
        input("  Press Enter to close...")


if __name__ == "__main__":
    if "--setup" in sys.argv:
        setup_api_key()
    else:
        main()
