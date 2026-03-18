# Core Rules

Use this file for shared agent behavior that should not bloat the root agent docs.

## State First

- Treat `memory/`, `state/`, and `runs/` as durable memory.
- Do not rely on the chat thread as the project record.
- Read `memory/NOW.md`, `memory/DECISIONS.md`, and `state/tasks.yaml` before substantial work.

## Task Discipline

- No meaningful change without a task.
- Every task must explain `why`, `success`, and `next_action`.
- Prefer small tasks over giant autonomous runs.

## Review Discipline

- Prefer different owner and reviewer when possible.
- A task can be implemented by one agent and reviewed by the other.
- A claim is not final until a verdict exists.

## Modularity

- Root `AGENTS.md` and `CLAUDE.md` stay short.
- Put detailed rules in `docs/agent-rules/`.
- Add a new rule when an agent makes the same mistake twice.
