#!/usr/bin/env python3
"""Hook entry point for Claude Code.

Runs on each UserPromptSubmit. Increments the prompt counter and, when a
question is due, launches trainer.py in a separate terminal window.
Outputs NOTHING to stdout so it never pollutes Claude's context.
"""

import json
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config.json"
PROGRESS_PATH = BASE_DIR / "progress.json"
TRAINER_PATH = BASE_DIR / "trainer.py"


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    config = load_json(CONFIG_PATH)
    if not config.get("enabled", True):
        return

    progress = load_json(PROGRESS_PATH)

    # Increment prompt counter
    progress["prompt_count"] = progress.get("prompt_count", 0) + 1
    freq = config.get("prompt_frequency", 3)

    if progress["prompt_count"] % freq != 0:
        save_json(PROGRESS_PATH, progress)
        return

    # Save counter now (trainer.py will handle the rest)
    save_json(PROGRESS_PATH, progress)

    # Launch trainer.py in a new Windows terminal, detached from this process
    subprocess.Popen(
        ["cmd", "/c", "start", "DSA Trainer", "python", str(TRAINER_PATH), "--hook"],
        creationflags=subprocess.DETACHED_PROCESS,
    )


if __name__ == "__main__":
    main()
