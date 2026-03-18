# Git Rules

## Commit Discipline

- Keep agent instructions, validation rules, and state ledgers in Git so diffs remain inspectable.
- Do not commit meaningful research progress until the relevant gate commands have passed.
- Use commits to explain why a rule changed, not just what changed.

## Learning Loop

- If an agent repeats a mistake, add or refine a rule in the tracked docs.
- Review rule changes through normal diffs instead of relying on chat memory.
- Keep reusable guidance in tracked files, not in one-off prompts only.

## Safe Collaboration

- Avoid reverting unrelated user changes.
- Keep root agent docs small so rule updates stay readable in reviews.
- Treat Git history as the durable audit trail for policy changes and evidence-backed progress.
