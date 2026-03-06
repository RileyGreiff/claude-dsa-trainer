#!/usr/bin/env python3
"""Record a question result after Claude checks the user's answer.

Usage: python hook_record.py <question_id> <correct|wrong|skip>
"""

import json
import sys
from pathlib import Path

PROGRESS_PATH = Path(__file__).parent / "progress.json"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    if len(sys.argv) != 3:
        print("Usage: python hook_record.py <question_id> <correct|wrong|skip>")
        sys.exit(1)

    qid = sys.argv[1]
    result = sys.argv[2].lower()

    if result not in ("correct", "wrong", "skip"):
        print(f"Invalid result: {result}. Must be correct, wrong, or skip.")
        sys.exit(1)

    progress = load_json(PROGRESS_PATH)

    if result != "skip":
        progress["total_answered"] = progress.get("total_answered", 0) + 1
        if result == "correct":
            progress["total_correct"] = progress.get("total_correct", 0) + 1

        qstats = progress.setdefault("questions", {}).setdefault(qid, {"correct": 0, "wrong": 0})
        qstats[result] += 1

    save_json(PROGRESS_PATH, progress)
    print(f"Recorded {result} for {qid}.")


if __name__ == "__main__":
    main()
