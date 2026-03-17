# State Ledger

`state/` is the machine-readable layer for durable agent handoff.

Use it when:
- multiple agent sessions need to continue the same project,
- a claim needs explicit evidence,
- a task should survive chat resets or thread boundaries.

Files:
- `tasks.yaml`: active queue, ownership, blockers, and next action
- `claims.yaml`: current research claims and their evidence status
- `session_capsules/`: one YAML packet per meaningful session

Rules:
- Prefer short, explicit fields over long prose.
- Every claim should point to concrete evidence such as a README, log, or paper note.
- Update `memory/` for humans and `state/` for agents after significant work.
