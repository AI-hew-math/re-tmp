# Decisions

### 2026-03-18: Use a mock plan to test the research workflow

**Context**: The repository needs a dry-run that proves plan review and execution gating work before real research starts.

**Decision**: Add a small mock plan fixture and replay it through the automation scripts.

**Reasoning**: This creates a benchmark workflow for future debugging and refactoring.

**Alternatives Rejected**:
- Option A: Test only with the live repository state. Too risky for repeated debugging.
- Option B: Skip fixtures and trust manual inspection. Too easy to miss regressions.

**Implications**: Future changes to planning or review logic should keep this fixture flow passing.
