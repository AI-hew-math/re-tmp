# Plan Review Workflow

This repository now treats a plan as a first-class state object.

## State Files

- `state/plans.yaml`: the planner's durable proposal
- `state/plan_reviews.yaml`: one review packet per reviewer
- `state/tasks.yaml`: execution work generated only after plan approval

## Flow

1. Draft the plan in `state/plans.yaml`.
2. Collect reviews in `state/plan_reviews.yaml`.
3. Inspect the current review state with `python scripts/plan_gate.py PLAN-XXXX`.
4. Confirm approval with `python scripts/plan_gate.py PLAN-XXXX --require-approved`.
5. When the plan is approved, generate execution work with:

```bash
python scripts/create_execution_tasks.py PLAN-XXXX
```

6. Execute the generated task through `runs/`.

## Approval Logic

- A plan needs `required_approvals` distinct approvals.
- A plan is blocked if `blocking_rejections` is reached.
- Any `changes_requested` review keeps the plan out of execution.

## Why This Exists

This keeps planning, review, and execution visibly separated, which makes research direction changes easier to inspect and harder to smuggle through implementation work alone.
