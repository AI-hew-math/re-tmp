# Fast Approval Gates

This project is designed for fast iteration with small automatic safety gates.

## Goal

Let humans approve quickly without letting the research drift or allowing untested changes to silently accumulate.

## Rules

- No work without a task in `state/tasks.yaml`.
- No direction change without a `why` field and a Codex review.
- No implementation task can move to `done` without at least one validation step.
- No supported claim without evidence.
- No finalized task or claim without a verdict in `state/verdicts.yaml`.
- Prefer different owner and reviewer when possible.

## Required Checks

Run these before approving meaningful progress:

```bash
python scripts/validate_state.py
python scripts/check_task_quality.py
python scripts/review_gate.py
```

For code changes, also run task-specific validation from the task's `validation` field.

## Approval Pattern

1. Codex defines task.
2. Claude executes task.
3. Claude returns evidence.
4. Codex records verdict.
5. Only then can the task or claim be advanced.

## Why This Works

The goal is not to eliminate mistakes.
The goal is to catch them while they are still small.
