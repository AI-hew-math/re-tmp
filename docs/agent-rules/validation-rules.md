# Validation Rules

These rules are intentionally checkable.

## Required Commands

Run these before advancing meaningful work:

```bash
python scripts/orchestrate.py
python scripts/plan_gate.py
python scripts/validate_state.py
python scripts/check_task_quality.py
python scripts/review_gate.py
python scripts/lint_agent_docs.py
```

## Execution Tasks

For `implementation`, `experiment`, `debug`, and `validation` tasks:

- require an approved `plan_id`,
- follow the task's `validation` field,
- leave evidence paths in the run folder or task-linked artifacts,
- do not move the task to `done` without recorded validation.

## Agent Docs

Agent docs should be:

- 200 lines or fewer for root docs,
- concrete and checkable,
- modularized through references instead of bloated root files.
