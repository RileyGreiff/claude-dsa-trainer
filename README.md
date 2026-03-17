# claude-dsa-trainer

A lightweight CLI tool that inserts micro DSA (Data Structures & Algorithms) practice questions between your Claude Code prompts. Questions take 10-60 seconds to answer, keeping your fundamentals sharp while you work.

## How it works

A Claude Code hook silently counts your prompts. Every 3rd prompt, a separate terminal window pops up with a quick question. You answer it, close the window, and continue coding. Zero interruption to your Claude session.

```
Prompt #6 triggered a quick coding rep.

  Topic: Hash Map
  Difficulty: Easy

  Complete the blank to check for a complement:

    if target - num in ________:

  Your answer ('skip', '?' for answer): seen

  Correct!
  Explanation: A set or dictionary allows average O(1) membership checks.

  Stats: 4/5 correct (80%)
  You may now continue your AI prompt.
```

## Setup

1. Clone the repo:
```bash
git clone https://github.com/RileyGreiff/claude-dsa-trainer.git
```

2. Copy the example files:
```bash
cp config.json.example config.json
cp progress.json.example progress.json
```

3. Add the hook to your Claude Code settings (`~/.claude/settings.json`):
```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"/path/to/claude-dsa-trainer/hook.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

4. Start using Claude Code. A question will pop up every 3rd prompt.

## Usage

### During a question

- Type your answer and press Enter
- Type `?` to reveal the answer
- Type `skip` to skip the question

### Run manually

```bash
python trainer.py
```

### Configure

Edit `config.json`:

| Setting | Default | Description |
|---------|---------|-------------|
| `enabled` | `true` | Enable/disable the trainer |
| `prompt_frequency` | `3` | Ask a question every N prompts |
| `allow_skip` | `true` | Allow skipping questions |
| `max_retries` | `2` | Attempts before revealing the answer |
| `anthropic_api_key` | `""` | Optional API key for follow-up questions |

### Follow-up questions (optional)

If you add an Anthropic API key, you can ask follow-up questions about any topic after answering:

```bash
python trainer.py --setup
```

```
  Follow-up (Enter to close): why is hash map lookup O(1)?

  Hash maps use a hash function to compute an array index directly
  from the key, so no searching is needed.

  Follow-up (Enter to close):
```

Uses Claude Haiku to keep costs minimal.

## Question bank

140 questions across 4 types:

| Type | Description | Example |
|------|-------------|---------|
| **mcq** | Multiple choice A-D | "What is the time complexity of binary search?" |
| **fill_code** | Fill in a blank | `current = current.________` |
| **predict_output** | Predict what Python prints | `print([1,2,3][-1])` |
| **short_answer** | Short text answer | "What is the time complexity of merge sort?" |

Topics covered: Arrays, Strings, Hash Maps, Sets, Stacks, Queues, Linked Lists, Trees, Graphs, Binary Search, Sorting, Recursion, Two Pointers, Sliding Window, Big O / Runtime, and Machine Learning topics like regression, classification, clustering, evaluation, feature scaling, ensembles, and neural networks.

## Progress tracking

Your stats persist in `progress.json`:

- Total answered / correct
- Per-question correct/wrong counts
- The selector biases toward questions you've gotten wrong before
- Recent questions are avoided to prevent repeats

## Project structure

```
claude-dsa-trainer/
├── trainer.py              # Main CLI + follow-up chat
├── hook.py                 # Claude Code hook (launches trainer in new window)
├── hook_record.py          # Records results from hook-based sessions
├── config.json             # Settings (gitignored, contains API key)
├── config.json.example     # Template for config
├── question_bank.json      # 115 questions
├── progress.json           # Your stats (gitignored)
├── progress.json.example   # Template for progress
└── utils/
    ├── normalize.py        # Text normalization for answer checking
    ├── scoring.py          # Answer checking logic per question type
    └── selector.py         # Weighted random question selection
```

## Requirements

- Python 3.7+
- No dependencies (standard library only)
- Optional: `pip install anthropic` for follow-up questions
