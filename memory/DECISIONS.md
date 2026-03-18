# Decisions

> Agent: Read this every session. Append new decisions immediately when made.
> Never delete entries - this is the canonical record of project decisions.

## Research Direction
<!-- What's the research goal? What's the approach? -->


## Technical Choices
<!-- Architecture, methods, why chosen over alternatives -->

### 2026-03-17: Add a machine-readable state layer

**Context**: The template already had human-readable memory files, but the shared design discussion emphasized durable agent handoffs through ledgers and packets rather than chat history alone.

**Decision**: Add `state/tasks.yaml`, `state/claims.yaml`, and `state/session_capsules/` as the canonical machine-readable state layer, alongside lightweight validation in CI.

**Reasoning**: This keeps the template useful for both human collaborators and multi-agent workflows, while reducing drift between sessions and making follow-up tasks easier to automate.

**Alternatives Rejected**:
- Option A: Keep only `memory/` markdown files. Easier for humans, weaker for agent-to-agent handoff.
- Option B: Introduce a heavier database-backed state system. More complex than needed for a template repo.

**Implications**: Future agents should update both `memory/` and `state/` after significant work, and CI should fail if the state skeleton is missing.


### 2026-03-17: Use Codex as orchestrator and Claude as executor

**Context**: The project goal is research automation rather than general coding assistance, and the working preference is to keep high-level planning and state management in Codex while using Claude for bounded execution.

**Decision**: Define Codex as the planner, reviewer, and state owner, and Claude as the implementation and execution worker.

**Reasoning**: This separates research judgment from repository execution, keeps long-running state updates centralized, and makes task handoff explicit through repository files instead of chat memory.

**Alternatives Rejected**:
- Option A: Let both agents freely plan and code. This increases overlap and drift.
- Option B: Make Claude the default orchestrator. This conflicts with the preferred working style for this project.

**Implications**: New automation docs, prompts, and scripts should assume Codex reads and updates state first, then delegates execution tasks to Claude.


### 2026-03-18: Add fast approval gates for research automation

**Context**: The project needs to move quickly, but quick approvals can cause direction drift, unsupported claims, and accumulating bugs if there are no automatic gates.

**Decision**: Require task-level why/success/reviewer fields, claim-level confidence/review flags, and gate scripts that block unsupported approvals.

**Reasoning**: This keeps human approval lightweight while forcing the repository state to carry enough structure for review, testing, and post-hoc inspection.

**Alternatives Rejected**:
- Option A: Trust the chat thread and human judgment alone. Too easy to drift.
- Option B: Add a heavy workflow engine before the process is proven. Too much complexity too early.

**Implications**: Future tasks, claims, and verdicts should be created in the richer format, and review gates should be run before meaningful items are advanced.


### 2026-03-18: Add per-task run artifacts instead of a monolithic pipeline

**Context**: Large autonomous research pipelines are useful references, but this project needs smaller, inspectable loops that fit the tasks/claims/verdicts model.

**Decision**: Add a lightweight `runs/` directory and `scripts/run_task.py` so each meaningful task can get its own artifact folder, plan, logs, and review notes.

**Reasoning**: This keeps the system inspectable, preserves evidence between agents, and imports the best part of pipeline-based systems without forcing a huge single-shot orchestrator.

**Alternatives Rejected**:
- Option A: Keep everything in chat and state files only. This makes execution evidence harder to inspect.
- Option B: Build a full AutoResearchClaw-style monolithic runner immediately. Too much complexity for the current phase.

**Implications**: Future execution-heavy tasks should be scaffolded into `runs/`, and verdict decisions should use `proceed`, `refine`, `pivot`, `reject`, or `keep_open`.


### 2026-03-18: Enforce agent docs with linted modular rules

**Context**: The project depends on reusable instructions for Codex and Claude, but root agent docs are only guidance unless the repository enforces quality, modularity, and checkable commands.

**Decision**: Keep `AGENTS.md` and `CLAUDE.md` short, move detail into `docs/agent-rules/`, and enforce those docs with `scripts/lint_agent_docs.py` in both local checks and CI.

**Reasoning**: This turns instruction quality into a tracked, testable part of the system and makes future rule updates easy to review through Git diffs.

**Alternatives Rejected**:
- Option A: Keep long monolithic root docs. Too noisy and easy for agents to ignore.
- Option B: Rely on chat prompts alone. Not durable across sessions or agents.

**Implications**: Future agent mistakes should be fixed by updating tracked rule docs or templates, then re-running the lint and review gates.


## Infrastructure
<!-- Cluster, data location, paths -->


<!--
## Template for new decisions:

### YYYY-MM-DD: [Brief title]
**Decision**: What was decided
**Reason**: Why this over alternatives
**Alternatives rejected**: What else was considered
-->
