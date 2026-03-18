# Domain Terms

These terms should be used consistently across tasks, claims, verdicts, prompts, and reviews.

## Research Terms

- `task`: the smallest durable unit of planned work.
- `plan`: the durable proposal that must be reviewed before execution work is created.
- `plan review`: an independent approval, rejection, or changes-request packet for a plan.
- `claim`: a falsifiable statement about the project, experiment, or debugging hypothesis.
- `verdict`: a review decision on a task or claim.
- `run`: a folder in `runs/` containing task execution artifacts.
- `evidence`: paths to logs, outputs, results, or documents that justify a claim or verdict.

## Plan Status

- `draft`: not yet ready for review.
- `in_review`: waiting for enough approvals.
- `changes_requested`: at least one reviewer asked for revision.
- `approved`: enough approvals exist and no blocking review remains.
- `rejected`: blocking rejection threshold was reached.
- `executing`: approved plan already generated execution work.
- `completed`: execution work finished and the plan is closed.

## Claim Status

- `provisional`: plausible but not yet accepted.
- `supported`: justified by evidence and review.
- `rejected`: evidence contradicts or fails the claim.
- `needs_review`: evidence exists but review is incomplete.

## Verdict Decisions

- `proceed`: continue to the next step.
- `refine`: keep direction but improve the current line of work.
- `pivot`: change direction or hypothesis.
- `reject`: stop or roll back the current line.
- `keep_open`: insufficient basis to close the task or claim.
