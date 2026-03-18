# Research Automation Architecture

This repository uses a split-agent research workflow.

## Core Principle

The chat thread is working memory.
The repository is durable memory.

Durable memory is split into:
- `memory/`: short human-readable handoff
- `state/`: machine-readable ledgers for tasks, claims, verdicts, and session packets
- `experiments/`: experiment design and result record
- `literature/`: external evidence and paper notes
- `runs/`: per-task execution artifacts, logs, and review notes

## Recommended Role Split

### Codex Orchestrator

Codex is the research coordinator.

Responsibilities:
- define or refine the research question
- read papers, claims, experiment results, and logs
- decide priority tasks
- approve or reject claims based on evidence
- generate the next experiment or analysis task
- update `state/tasks.yaml`, `state/claims.yaml`, and `state/verdicts.yaml`
- keep `memory/NOW.md` aligned with current priorities

Codex should not do large implementation work by default when Claude can execute it.

### Claude Executor

Claude is the implementation and execution worker.

Responsibilities:
- implement model or config changes
- scaffold experiments
- run validation and tests
- inspect training failures and logs
- summarize execution outcomes in a compact packet
- propose concrete fixes when blocked

Claude should not silently redefine research direction. If execution changes the plan, it should hand back a packet to Codex.

## Shared State Interface

### `state/tasks.yaml`
Tracks open work.

Required fields per task:
- `id`
- `title`
- `stage`
- `kind`
- `status`
- `owner`
- `reviewer`
- `updated_at`
- `why`
- `success`
- `next_action`

Recommended fields:
- `blockers`
- `validation`
- `links`

Recommended task stages:
- `scoping`
- `literature`
- `hypothesis`
- `design`
- `execution`
- `analysis`
- `writing`
- `review`
- `archive`

### `state/claims.yaml`
Tracks research claims and evidence.

Required fields per claim:
- `id`
- `claim`
- `status`
- `evidence`
- `updated_at`
- `confidence`
- `review_required`
- `reviewer`
- `notes`

### `state/verdicts.yaml`
Tracks decisions made from evidence.

Each verdict should answer:
- what was reviewed
- what decision was made
- which evidence justified it
- who reviewed it
- what follow-up task was created

Recommended decisions:
- `proceed`
- `refine`
- `pivot`
- `reject`
- `keep_open`

### `runs/`
Tracks execution artifacts for a specific task run.

A run directory should contain:
- `run.json`
- `plan.md`
- `review.md`
- `logs/`

## Workflow Loop

1. Codex reads `memory/` and `state/`.
2. Codex selects the highest-value ready task.
3. Codex creates a run scaffold when the task needs executable artifacts.
4. Codex assigns execution to Claude when code or validation work is needed.
5. Claude performs the task and records outputs in the run directory.
6. Codex reviews the packet and evidence.
7. Codex updates claims, verdicts, and next tasks.
8. Gate scripts are run before advancing important items.
9. The loop repeats.

## Safety Rules

- No work without a task.
- No direction change without `why` and `success`.
- No implementation completion without validation.
- No finalized claim without evidence and verdict.
- Prefer different owner and reviewer when possible.

See also:
- `docs/fast-approval-gates.md`
- `docs/run-based-task-execution.md`
- `docs/testing-the-research-system.md`

## Immediate Next Step

Use `python scripts/orchestrate.py` to inspect the current state and generate the next recommended research action.
Then create a run with `python scripts/run_task.py TASK-XXXX` when the task needs execution artifacts.
