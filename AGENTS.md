# AGENTS.md

> For AI coding agents: read this file on every session.

## Purpose

This repository is a research automation template, not a generic coding sandbox.
The goal is to help Codex and Claude run small, inspectable research loops with durable state.

## Project Scope

- `Codex` is the orchestrator, planner, reviewer, and state owner.
- `Claude` is the bounded executor for implementation, validation, and debugging tasks.
- `memory/`, `state/`, and `runs/` are the source of truth, not the chat thread.
- `state/plans.yaml` and `state/plan_reviews.yaml` decide whether execution work may begin.

## Hard Rules

- Read `memory/NOW.md`, `memory/DECISIONS.md`, `state/plans.yaml`, `state/plan_reviews.yaml`, and `state/tasks.yaml` first.
- Do not perform meaningful work without a task in `state/tasks.yaml`.
- Do not create execution work until the linked plan is approved.
- Do not mark execution-heavy work done without validation evidence.
- Do not finalize claims without evidence and a verdict.
- Treat this file as an index. Keep root agent docs short and move detail into `docs/agent-rules/`.

## Verification Rules

Run these before advancing meaningful work:

```bash
python scripts/orchestrate.py
python scripts/plan_gate.py
python scripts/validate_state.py
python scripts/check_task_quality.py
python scripts/review_gate.py
python scripts/lint_agent_docs.py
```

For execution-heavy tasks, create a run scaffold:

```bash
python scripts/run_task.py TASK-XXXX
```

Execution-heavy tasks should come from an approved plan.

## Domain Terms

- `task`: the smallest durable unit of planned work.
- `claim`: a falsifiable project statement backed by evidence.
- `verdict`: the review decision for a task or claim.
- `run`: per-task artifact folder with plan, logs, and review notes.
- `supported`: claim status only after evidence and review.

## Referenced Files

- `docs/agent-rules/core-rules.md`
- `docs/agent-rules/validation-rules.md`
- `docs/agent-rules/domain-terms.md`
- `docs/agent-rules/workflow.md`
- `docs/agent-rules/git-rules.md`
- `prompts/roles/codex_orchestrator.md`
- `prompts/roles/claude_executor.md`
