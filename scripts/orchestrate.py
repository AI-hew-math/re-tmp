from __future__ import annotations

from dataclasses import dataclass
import sys

from state_utils import as_bool, as_list, load_state_items, StateParseError


@dataclass
class Task:
    id: str
    title: str
    stage: str
    kind: str
    status: str
    owner: str
    reviewer: str
    updated_at: str
    why: str
    success: str
    next_action: str
    blockers: list[str]
    validation: list[str]
    links: list[str]


@dataclass
class Claim:
    id: str
    claim: str
    status: str
    evidence: list[str]
    updated_at: str
    confidence: str
    review_required: bool
    reviewer: str
    notes: str



def load_tasks() -> list[Task]:
    raw_tasks = load_state_items("tasks.yaml", "tasks")
    return [
        Task(
            id=str(item.get("id", "")),
            title=str(item.get("title", "")),
            stage=str(item.get("stage", "")),
            kind=str(item.get("kind", "")),
            status=str(item.get("status", "")),
            owner=str(item.get("owner", "")),
            reviewer=str(item.get("reviewer", "")),
            updated_at=str(item.get("updated_at", "")),
            why=str(item.get("why", "")),
            success=str(item.get("success", "")),
            next_action=str(item.get("next_action", "")),
            blockers=as_list(item.get("blockers", [])),
            validation=as_list(item.get("validation", [])),
            links=as_list(item.get("links", [])),
        )
        for item in raw_tasks
    ]



def load_claims() -> list[Claim]:
    raw_claims = load_state_items("claims.yaml", "claims")
    return [
        Claim(
            id=str(item.get("id", "")),
            claim=str(item.get("claim", "")),
            status=str(item.get("status", "")),
            evidence=as_list(item.get("evidence", [])),
            updated_at=str(item.get("updated_at", "")),
            confidence=str(item.get("confidence", "")),
            review_required=as_bool(item.get("review_required", False)),
            reviewer=str(item.get("reviewer", "")),
            notes=str(item.get("notes", "")),
        )
        for item in raw_claims
    ]



def score_task(task: Task) -> tuple[int, int, int]:
    status_rank = {
        "ready": 0,
        "pending": 1,
        "in_progress": 2,
        "blocked": 3,
        "done": 4,
    }.get(task.status, 5)
    owner_rank = {
        "codex": 0,
        "unassigned": 1,
        "shared": 2,
        "claude": 3,
        "human": 4,
    }.get(task.owner, 5)
    risk_rank = 0 if task.kind in {"research", "review", "claim"} else 1
    return (status_rank, owner_rank, risk_rank)



def recommend_owner(task: Task) -> str:
    if task.kind in {"implementation", "experiment", "debug", "validation"}:
        return "claude"
    return "codex"



def summarize_claim_context(claims: list[Claim]) -> str:
    if not claims:
        return "No claims recorded yet."
    open_claims = [claim for claim in claims if claim.status in {"provisional", "needs_review"}]
    if open_claims:
        claim = open_claims[0]
        return f"Focus claim: {claim.id} [{claim.status}, confidence={claim.confidence}] - {claim.claim}"
    claim = claims[0]
    return f"Latest claim: {claim.id} [{claim.status}, confidence={claim.confidence}] - {claim.claim}"



def main() -> int:
    try:
        tasks = load_tasks()
        claims = load_claims()
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    if not tasks:
        print("No tasks available in state/tasks.yaml")
        return 0

    ordered = sorted(tasks, key=score_task)
    next_task = ordered[0]
    suggested_owner = recommend_owner(next_task)

    print("# Research Orchestrator Summary")
    print()
    print(f"Next task: {next_task.id} - {next_task.title}")
    print(f"Stage: {next_task.stage}")
    print(f"Kind: {next_task.kind}")
    print(f"Current status: {next_task.status}")
    print(f"Recorded owner: {next_task.owner}")
    print(f"Suggested owner: {suggested_owner}")
    print(f"Reviewer: {next_task.reviewer}")
    print(f"Updated at: {next_task.updated_at}")
    print()
    print("Why this task matters")
    print(f"- {next_task.why}")
    print("Success condition")
    print(f"- {next_task.success}")
    print("Next action")
    print(f"- {next_task.next_action}")
    if next_task.validation:
        print("Required validation")
        for item in next_task.validation:
            print(f"- {item}")
    if next_task.blockers:
        print("Blockers")
        for blocker in next_task.blockers:
            print(f"- {blocker}")
    if next_task.links:
        print("Relevant links")
        for link in next_task.links:
            print(f"- {link}")
    print()
    print(summarize_claim_context(claims))
    print()
    print("Handoff")
    if suggested_owner == "claude":
        print("- Send this task to Claude for bounded implementation or execution.")
        print("- Require Claude to report validations, evidence paths, and blockers before the task can move to done.")
        print(f"- Return review to {next_task.reviewer}.")
    else:
        print("- Keep this with Codex for planning, review, or claim-state updates before delegating execution.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
