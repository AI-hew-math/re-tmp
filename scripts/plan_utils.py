from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from state_utils import (
    ROOT,
    STATE_DIR,
    as_int,
    as_list,
    load_state_items,
    write_top_level_items,
)


PLANS_PATH = STATE_DIR / "plans.yaml"
PLAN_REVIEWS_PATH = STATE_DIR / "plan_reviews.yaml"
TASKS_PATH = STATE_DIR / "tasks.yaml"

PLAN_STATUS = {
    "draft",
    "in_review",
    "changes_requested",
    "approved",
    "rejected",
    "executing",
    "completed",
}
PLAN_REVIEW_DECISIONS = {"approve", "changes_requested", "reject"}


@dataclass
class Plan:
    id: str
    title: str
    status: str
    planner: str
    updated_at: str
    research_question: str
    hypothesis: str
    why: str
    success: str
    next_action: str
    required_approvals: int
    blocking_rejections: int
    execution_owner: str
    execution_reviewer: str
    task_stage: str
    task_kind: str
    task_title: str
    task_why: str
    task_success: str
    task_next_action: str
    task_validation: list[str]
    links: list[str]
    generated_tasks: list[str]


@dataclass
class PlanReview:
    id: str
    plan_id: str
    reviewer: str
    role: str
    decision: str
    rationale: str
    evidence: list[str]
    updated_at: str


@dataclass
class PlanEvaluation:
    plan_id: str
    outcome: str
    approvals: int
    changes_requested: int
    rejections: int
    distinct_reviewers: int
    required_approvals: int
    blocking_rejections: int


def today_stamp() -> str:
    return date.today().isoformat()


def load_plans() -> list[Plan]:
    return [
        Plan(
            id=str(item.get("id", "")),
            title=str(item.get("title", "")),
            status=str(item.get("status", "")),
            planner=str(item.get("planner", "")),
            updated_at=str(item.get("updated_at", "")),
            research_question=str(item.get("research_question", "")),
            hypothesis=str(item.get("hypothesis", "")),
            why=str(item.get("why", "")),
            success=str(item.get("success", "")),
            next_action=str(item.get("next_action", "")),
            required_approvals=as_int(item.get("required_approvals", 1), default=1),
            blocking_rejections=as_int(item.get("blocking_rejections", 1), default=1),
            execution_owner=str(item.get("execution_owner", "")),
            execution_reviewer=str(item.get("execution_reviewer", "")),
            task_stage=str(item.get("task_stage", "")),
            task_kind=str(item.get("task_kind", "")),
            task_title=str(item.get("task_title", "")),
            task_why=str(item.get("task_why", "")),
            task_success=str(item.get("task_success", "")),
            task_next_action=str(item.get("task_next_action", "")),
            task_validation=as_list(item.get("task_validation", [])),
            links=as_list(item.get("links", [])),
            generated_tasks=as_list(item.get("generated_tasks", [])),
        )
        for item in load_state_items("plans.yaml", "plans")
    ]


def load_plan_reviews() -> list[PlanReview]:
    return [
        PlanReview(
            id=str(item.get("id", "")),
            plan_id=str(item.get("plan_id", "")),
            reviewer=str(item.get("reviewer", "")),
            role=str(item.get("role", "")),
            decision=str(item.get("decision", "")),
            rationale=str(item.get("rationale", "")),
            evidence=as_list(item.get("evidence", [])),
            updated_at=str(item.get("updated_at", "")),
        )
        for item in load_state_items("plan_reviews.yaml", "plan_reviews")
    ]


def reviews_for_plan(plan_id: str, reviews: list[PlanReview]) -> list[PlanReview]:
    return [review for review in reviews if review.plan_id == plan_id]


def evaluate_plan(plan: Plan, reviews: list[PlanReview]) -> PlanEvaluation:
    applicable = reviews_for_plan(plan.id, reviews)
    approval_reviewers = {review.reviewer for review in applicable if review.decision == "approve"}
    change_reviewers = {review.reviewer for review in applicable if review.decision == "changes_requested"}
    rejection_reviewers = {review.reviewer for review in applicable if review.decision == "reject"}
    all_reviewers = {review.reviewer for review in applicable}

    if len(rejection_reviewers) >= plan.blocking_rejections:
        outcome = "rejected"
    elif change_reviewers:
        outcome = "changes_requested"
    elif len(approval_reviewers) >= plan.required_approvals:
        outcome = "approved"
    elif applicable:
        outcome = "in_review"
    else:
        outcome = "draft"

    return PlanEvaluation(
        plan_id=plan.id,
        outcome=outcome,
        approvals=len(approval_reviewers),
        changes_requested=len(change_reviewers),
        rejections=len(rejection_reviewers),
        distinct_reviewers=len(all_reviewers),
        required_approvals=plan.required_approvals,
        blocking_rejections=plan.blocking_rejections,
    )


def load_task_dicts() -> list[dict[str, object]]:
    return load_state_items("tasks.yaml", "tasks")


def plan_from_dict(item: dict[str, object]) -> Plan:
    return Plan(
        id=str(item.get("id", "")),
        title=str(item.get("title", "")),
        status=str(item.get("status", "")),
        planner=str(item.get("planner", "")),
        updated_at=str(item.get("updated_at", "")),
        research_question=str(item.get("research_question", "")),
        hypothesis=str(item.get("hypothesis", "")),
        why=str(item.get("why", "")),
        success=str(item.get("success", "")),
        next_action=str(item.get("next_action", "")),
        required_approvals=as_int(item.get("required_approvals", 1), default=1),
        blocking_rejections=as_int(item.get("blocking_rejections", 1), default=1),
        execution_owner=str(item.get("execution_owner", "")),
        execution_reviewer=str(item.get("execution_reviewer", "")),
        task_stage=str(item.get("task_stage", "")),
        task_kind=str(item.get("task_kind", "")),
        task_title=str(item.get("task_title", "")),
        task_why=str(item.get("task_why", "")),
        task_success=str(item.get("task_success", "")),
        task_next_action=str(item.get("task_next_action", "")),
        task_validation=as_list(item.get("task_validation", [])),
        links=as_list(item.get("links", [])),
        generated_tasks=as_list(item.get("generated_tasks", [])),
    )


def load_plan_dicts() -> list[dict[str, object]]:
    return load_state_items("plans.yaml", "plans")


def save_plan_dicts(items: list[dict[str, object]]) -> None:
    write_top_level_items(PLANS_PATH, "plans", items)


def save_task_dicts(items: list[dict[str, object]]) -> None:
    write_top_level_items(TASKS_PATH, "tasks", items)


def derive_task_id(plan_id: str) -> str:
    if plan_id.startswith("PLAN-"):
        return f"TASK-{plan_id[5:]}"
    return f"TASK-{plan_id}"
