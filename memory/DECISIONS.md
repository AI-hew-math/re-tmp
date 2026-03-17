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


## Infrastructure
<!-- Cluster, data location, paths -->


<!--
## Template for new decisions:

### YYYY-MM-DD: [Brief title]
**Decision**: What was decided
**Reason**: Why this over alternatives
**Alternatives rejected**: What else was considered
-->

### 2026-03-17: Use Codex as orchestrator and Claude as executor

**Context**: The project goal is research automation rather than general coding assistance, and the working preference is to keep high-level planning and state management in Codex while using Claude for bounded execution.

**Decision**: Define Codex as the planner, reviewer, and state owner, and Claude as the implementation and execution worker.

**Reasoning**: This separates research judgment from repository execution, keeps long-running state updates centralized, and makes task handoff explicit through repository files instead of chat memory.

**Alternatives Rejected**:
- Option A: Let both agents freely plan and code. This increases overlap and drift.
- Option B: Make Claude the default orchestrator. This conflicts with the preferred working style for this project.

**Implications**: New automation docs, prompts, and scripts should assume Codex reads and updates state first, then delegates execution tasks to Claude.

