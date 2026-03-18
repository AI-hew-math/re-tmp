from __future__ import annotations

from dataclasses import dataclass
import sys

from plan_utils import evaluate_plan, load_plans, load_plan_reviews
from state_utils import as_bool, as_list, load_state_items, StateParseError


@dataclass
class Task:
    id: str
    title: str
    plan_id: str
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
            plan_id=str(item.get("plan_id", "")),
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


def print_plan_priority() -> bool:
    plans = load_plans()
    reviews = load_plan_reviews()
    if not plans:
        return False

    evaluations = {plan.id: evaluate_plan(plan, reviews) for plan in plans}
    approved_without_tasks = [
        plan for plan in plans if evaluations[plan.id].outcome == "approved" and not plan.generated_tasks
    ]
    if approved_without_tasks:
        plan = approved_without_tasks[0]
        evaluation = evaluations[plan.id]
        print("# Research Orchestrator Summary")
        print()
        print(f"Next plan action: {plan.id} - {plan.title}")
        print(f"Stored status: {plan.status}")
        print(f"Review outcome: {evaluation.outcome}")
        print(f"Approvals: {evaluation.approvals}/{evaluation.required_approvals}")
        print("Next action")
        print(f"- Generate execution work with: python scripts/create_execution_tasks.py {plan.id}")
        print("Why this matters")
        print(f"- {plan.why}")
        print("Success condition")
        print(f"- {plan.success}")
        return True

    review_queue = [plan for plan in plans if evaluations[plan.id].outcome in {"draft", "in_review", "changes_requested"}]
    if review_queue:
        plan = review_queue[0]
        evaluation = evaluations[plan.id]
        print("# Research Orchestrator Summary")
        print()
        print(f"Next plan action: {plan.id} - {plan.title}")
        print(f"Stored status: {plan.status}")
        print(f"Review outcome: {evaluation.outcome}")
        print(f"Approvals: {evaluation.approvals}/{evaluation.required_approvals}")
        print(f"Change requests: {evaluation.changes_requested}")
        print(f"Rejections: {evaluation.rejections}/{evaluation.blocking_rejections}")
        print("Next action")
        print(f"- {plan.next_action}")
        print("Plan gate")
        print(f"- Review current state with: python scripts/plan_gate.py {plan.id}")
        print("Why this matters")
        print(f"- {plan.why}")
        print("Success condition")
        print(f"- {plan.success}")
        return True

    return False


def main() -> int:
    try:
        tasks = load_tasks()
        claims = load_claims()
        if print_plan_priority():
            print()
            print(summarize_claim_context(claims))
            return 0
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    open_tasks = [task for task in tasks if task.status != "done"]
    if not open_tasks:
        print("# Research Orchestrator Summary")
        print()
        print("No open tasks remain in state/tasks.yaml.")
        print(summarize_claim_context(claims))
        return 0

    ordered = sorted(open_tasks, key=score_task)
    next_task = ordered[0]
    suggested_owner = recommend_owner(next_task)

    print("# Research Orchestrator Summary")
    print()
    print(f"Next task: {next_task.id} - {next_task.title}")
    if next_task.plan_id:
        print(f"Plan: {next_task.plan_id}")
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
