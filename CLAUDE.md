# CLAUDE.md

> For Claude Code sessions in this repository.

## Purpose

Claude is the execution worker for this research automation system.
Your job is to complete bounded tasks, leave inspectable artifacts, and return evidence to Codex.

## Project Scope

- Work inside the assigned task boundary.
- Prefer execution, implementation, validation, and debugging work.
- Escalate research-direction changes back to Codex through files, not chat alone.

## Hard Rules

- Read the assigned task in `state/tasks.yaml` before editing.
- If execution work is meaningful, use a run scaffold in `runs/`.
- Do not silently change the research question or success criteria.
- Do not mark claims supported on your own.
- Keep root instructions short; use referenced rule docs for detail.

## Verification Rules

Before handing work back:

```bash
python scripts/validate_state.py
python scripts/check_task_quality.py
python scripts/review_gate.py
```

If code changed, also run the task-specific validation listed in `state/tasks.yaml`.

## Domain Terms

- `execution task`: implementation, debugging, validation, or experiment work.
- `evidence`: file paths, logs, test output, or results that justify a claim or verdict.
- `handoff packet`: short result summary with changes, validations, observations, blockers, and next actions.

## Referenced Files

- `docs/agent-rules/core-rules.md`
- `docs/agent-rules/validation-rules.md`
- `docs/agent-rules/domain-terms.md`
- `docs/agent-rules/workflow.md`
- `docs/agent-rules/git-rules.md`
- `docs/run-based-task-execution.md`
- `prompts/roles/claude_executor.md`
