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
- `status`
- `owner`
- `updated_at`
- `next_action`

Optional but recommended:
- `blockers`
- `links`
- `kind`
- `priority`

Suggested statuses:
- `pending`
- `ready`
- `in_progress`
- `blocked`
- `done`

Suggested owners:
- `codex`
- `claude`
- `human`
- `shared`
- `unassigned`

### `state/claims.yaml`
Tracks research claims and evidence.

Suggested statuses:
- `provisional`
- `supported`
- `rejected`
- `needs_review`

### `state/verdicts.yaml`
Tracks decisions made from evidence.

Each verdict should answer:
- what was reviewed
- what decision was made
- which evidence justified it
- what follow-up task was created

### `state/session_capsules/`
One YAML packet per meaningful session or execution burst.

Each capsule should contain:
- what changed
- what was observed
- what remains blocked
- what should happen next

## Workflow Loop

1. Codex reads `memory/` and `state/`.
2. Codex selects the highest-value ready task.
3. Codex assigns execution to Claude when code or validation work is needed.
4. Claude performs the task and emits a compact result packet.
5. Codex reviews the packet and evidence.
6. Codex updates claims, verdicts, and next tasks.
7. The loop repeats.

## Decision Rules

### Codex should own
- experiment prioritization
- interpretation of ambiguous results
- whether a claim is accepted, revised, or rejected
- whether to pivot, repeat, or scale an experiment

### Claude should own
- implementation details inside the current task boundary
- validation and test execution
- narrow debugging loops
- translating a research task into repository edits

## Minimal Packet Contract

A Claude execution result should be easy for Codex to consume.

Recommended packet shape:

```yaml
session_id: SESSION-YYYYMMDD-HHMM
task_id: TASK-XXXX
actor: claude
summary: One paragraph on what was done
completed:
  - concrete action
observations:
  - concrete finding
artifacts:
  - file path or log path
next_actions:
  - suggested follow-up
```

## Why This Split

This split avoids letting both agents do the same thing.

- Codex spends tokens on reasoning, synthesis, and coordination.
- Claude spends tokens on implementation and execution.
- The repository state prevents drift across sessions and tool boundaries.

## Immediate Next Step

Use `python scripts/orchestrate.py` to inspect the current state and generate the next recommended research action.
