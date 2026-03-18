# Run-Based Task Execution

This repository now keeps lightweight per-task run artifacts in `runs/`.

## Why

This borrows the best part of large pipeline systems without forcing a giant end-to-end runner:
- each meaningful task can get its own artifact folder,
- logs and review notes stop being scattered across chat threads,
- Codex and Claude can hand off through files, not memory.

## Create a Run

```bash
python scripts/run_task.py TASK-XXXX
```

This creates:
- `runs/<timestamp>-task-xxxx/run.json`
- `runs/<timestamp>-task-xxxx/plan.md`
- `runs/<timestamp>-task-xxxx/review.md`
- `runs/<timestamp>-task-xxxx/logs/`

## Recommended Use

1. Codex defines or updates the task in `state/tasks.yaml`.
2. Codex creates a run folder with `python scripts/run_task.py TASK-XXXX`.
3. Claude executes the task and writes logs or notes into that run folder.
4. Codex reviews the evidence and records a verdict in `state/verdicts.yaml`.

## Stage Vocabulary

Use one of:
- `scoping`
- `literature`
- `hypothesis`
- `design`
- `execution`
- `analysis`
- `writing`
- `review`
- `archive`

## Verdict Decisions

Use one of:
- `proceed`
- `refine`
- `pivot`
- `reject`
- `keep_open`

These decisions are intentionally smaller and safer than a full autonomous pipeline.
