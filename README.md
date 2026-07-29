# claude-dsa-trainer

A lightweight CLI tool that inserts micro DSA (Data Structures & Algorithms) practice questions between your Claude Code prompts. Questions take 10-60 seconds to answer, keeping your fundamentals sharp while you work.

It also ships a separate, self-paced [interview prep mode](#interview-prep-mode) for AI/ML interview questions, where you study strong model answers rather than being graded.

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

### Interview prep mode

A separate, self-paced study mode for AI/ML interview questions. Unlike the quiz, nothing is graded — you get an interview question, think through your own answer out loud, then reveal a strong model answer plus the points an interviewer is actually listening for.

```bash
python trainer.py --interview      # 5 cards (default)
python trainer.py --interview 10   # 10 cards
```

```
  --------------------------------------------------------------------------
  Card 1/5  |  Model Evaluation  |  applied  |  easy
  --------------------------------------------------------------------------

  Your fraud detection model has 99.5% accuracy. Your manager is thrilled.
  Why might you not be?

  [Enter] to reveal a strong answer:

  A strong answer:

  Because fraud is rare, accuracy is almost meaningless here. If 0.5% of
  transactions are fraudulent, a model that predicts 'not fraud' for
  everything scores 99.5% and catches nothing. [...]

  What an interviewer is listening for:
    - Accuracy is dominated by the majority class under imbalance
    - Use precision/recall and PR curves; ROC-AUC is also optimistic here
    - Tie the threshold to the real cost asymmetry of FP vs FN
    - Check per-segment recall, not just the aggregate

  Likely follow-ups:
    - How would you actually choose the threshold?
    - When would you prefer ROC-AUC over a PR curve?

  How'd you do?  [1] nailed it  [2] shaky  [3] blank  (Enter to skip): 2
```

Rate yourself after each card. Ratings feed the same selector the quiz uses, so cards you flagged as shaky or blank come back more often. Press `q` at any prompt to end the session early. This mode runs only when you ask for it — it never fires from the hook.

If an API key is configured, you can ask follow-up questions after each card, answered by an interviewer persona rather than the tutor persona used in the quiz.

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

175 questions across 4 types:

| Type | Description | Example |
|------|-------------|---------|
| **mcq** | Multiple choice A-D | "What is the time complexity of binary search?" |
| **fill_code** | Fill in a blank | `current = current.________` |
| **predict_output** | Predict what Python prints | `print([1,2,3][-1])` |
| **short_answer** | Short text answer | "What is the time complexity of merge sort?" |

Topics covered: Arrays, Strings, Hash Maps, Sets, Stacks, Queues, Linked Lists, Trees, Graphs, Binary Search, Sorting, Recursion, Two Pointers, Sliding Window, Big O / Runtime, and Machine Learning topics like regression, classification, clustering, evaluation, feature scaling, ensembles, and neural networks.

Correct MCQ answers are distributed evenly across A/B/C/D so the letter carries no signal.

## Interview bank

46 cards in `interview_bank.json`, each with a full model answer, the key points an interviewer listens for, and likely follow-up probes.

| Category | Count | Covers |
|----------|-------|--------|
| **conceptual** | 20 | Attention, regularization, calibration, MLE vs MAP, CLT, tokenization |
| **applied** | 16 | Leakage, imbalance, missing data, thresholds, chunking, A/B design |
| **system-design** | 8 | Recsys, monitoring, RAG pipelines, cost/latency, agents, prompt injection |
| **behavioral** | 2 | Structuring a "model you shipped" story, explaining concepts to non-technical stakeholders |

Weighted toward applied ML / MLE, LLM / GenAI, and data science / stats roles.

## Progress tracking

Your stats persist in `progress.json`:

- Total answered / correct
- Per-question correct/wrong counts
- The selector biases toward questions you've gotten wrong before
- Recent questions are avoided to prevent repeats

Interview prep keeps its own stats under the `interview` key, so self-ratings never mix into your quiz accuracy. Both modes cycle through their whole bank before repeating anything.

## Project structure

```
claude-dsa-trainer/
├── trainer.py              # Main CLI + interview mode + follow-up chat
├── hook.py                 # Claude Code hook (launches trainer in new window)
├── hook_record.py          # Records results from hook-based sessions
├── config.json             # Settings (gitignored, contains API key)
├── config.json.example     # Template for config
├── question_bank.json      # 175 quiz questions
├── interview_bank.json     # 46 interview cards with model answers
├── progress.json           # Your stats (gitignored)
├── progress.json.example   # Template for progress
└── utils/
    ├── normalize.py        # Text normalization for answer checking
    ├── scoring.py          # Answer checking logic per question type
    ├── selector.py         # Weighted random question selection
    └── interview.py        # Interview card display + self-rating
```

## Requirements

- Python 3.7+
- No dependencies (standard library only)
- Optional: `pip install anthropic` for follow-up questions
