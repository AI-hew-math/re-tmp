# Testing The Research Automation System

Testing an LLM-agent system is different from printing one function output.
The right approach is to test the system in layers.

## 1. State Contract Tests

These tests verify the repository state is valid.

Run:

```bash
python scripts/validate_state.py
python scripts/check_task_quality.py
python scripts/review_gate.py
```

These act like schema and invariant tests.

## 2. Golden Path Replay

Keep one or two small benchmark workflows and replay them.

Example benchmark:
- create a small validation task
- route it through Codex planning
- route execution to Claude
- require a verdict
- verify state files advance correctly

A system is healthy if the same benchmark still works after changes.

This repository now includes one such replay:

```bash
python -m unittest tests.test_mock_research_flow
```

It checks:
- draft plan cannot generate execution work,
- enough approvals flip the plan gate,
- approved plan generates exactly one execution task,
- that task can create a run scaffold,
- a deliberately broken done task is rejected by `review_gate.py`.

## 3. Failure Injection

Deliberately create bad states and make sure the gates block them.

Examples:
- mark a claim as `supported` with no evidence
- mark an implementation task as `done` with no validation
- set owner and reviewer fields incorrectly
- remove `why` or `success` from a task

The system is working if the scripts fail loudly.

## 4. Shadow Mode

Before trusting automation, run it in recommendation mode.

That means:
- Codex suggests the next task
- Claude suggests the patch or action
- a human still decides whether to accept

This is the safest way to evaluate whether the workflow is aligned.

## 5. Outcome-Level Evaluation

Do not only ask whether the script ran.
Ask whether the research process improved.

Track:
- fewer direction drifts
- fewer unsupported claims
- faster debugging turnaround
- smaller bug accumulation
- better experiment documentation

## 6. Review Sampled Sessions

Every few sessions, inspect a small sample:
- task definition
- execution result
- evidence paths
- verdict quality
- next-task quality

This helps detect slow process drift.

## Recommended Practical Test Loop

1. Add one real task to `state/tasks.yaml`.
2. Run `python scripts/orchestrate.py`.
3. Let the execution agent complete the task.
4. Record evidence and a verdict.
5. Run all gate scripts.
6. Inspect whether the next task is reasonable.

If that loop works repeatedly on small tasks, the system is healthy.

## What To Watch For

Bad agent systems often look successful while drifting.
Watch for:
- verbose but weak evidence
- tasks closing too easily
- claims marked supported too early
- same agent writing and approving everything
- no benchmark tasks being replayed

A good agent system is not one that talks confidently.
It is one that fails safely and leaves inspectable state.
