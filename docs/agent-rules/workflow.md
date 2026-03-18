# Workflow

This repository uses a small-loop research workflow.

## Standard Loop

1. Codex reads plans, plan reviews, and tasks.
2. Codex drafts or refines a plan.
3. Reviewers record plan reviews.
4. Approved plans generate execution tasks.
5. Codex creates a run scaffold if execution artifacts are needed.
6. Claude executes the task and records evidence.
7. Codex reviews the evidence and writes a verdict.
8. State is updated and the next task is chosen.

## Run-Based Execution

Create a run folder with:

```bash
python scripts/run_task.py TASK-XXXX
```

The run folder should contain:

- `run.json`
- `plan.md`
- `review.md`
- `logs/`

## Learning Loop

- When an agent repeatedly fails, add a short rule.
- When a root doc grows too long, move the detail into a referenced rule file.
- When a task closes too easily, strengthen the gate rather than writing a vague instruction.
