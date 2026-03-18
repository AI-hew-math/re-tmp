import sys

from plan_utils import PLAN_REVIEW_DECISIONS, PLAN_STATUS, evaluate_plan, load_plans, load_plan_reviews
from state_utils import as_bool, as_list, load_state_items, StateParseError


VALID_TASK_KINDS = {"research", "implementation", "experiment", "debug", "validation", "review", "claim"}
VALID_TASK_STATUS = {"pending", "ready", "in_progress", "blocked", "done"}
VALID_OWNERS = {"codex", "claude", "human", "shared", "unassigned"}
VALID_CLAIM_STATUS = {"provisional", "supported", "rejected", "needs_review"}
VALID_VERDICT_STATUS = {"active", "closed"}
VALID_PLAN_OWNERS = {"codex", "claude", "human", "shared"}
VALID_STAGES = {
    "scoping",
    "literature",
    "hypothesis",
    "design",
    "execution",
    "analysis",
    "writing",
    "review",
    "archive",
}
VALID_VERDICT_DECISIONS = {"proceed", "refine", "pivot", "reject", "keep_open"}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        tasks = load_state_items("tasks.yaml", "tasks")
        claims = load_state_items("claims.yaml", "claims")
        verdicts = load_state_items("verdicts.yaml", "verdicts")
        plans = load_plans()
        plan_reviews = load_plan_reviews()
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    plan_map = {plan.id: plan for plan in plans}
    plan_evaluations = {plan.id: evaluate_plan(plan, plan_reviews) for plan in plans}

    for task in tasks:
        task_id = str(task.get("id", "UNKNOWN"))
        plan_id = str(task.get("plan_id", ""))
        stage = str(task.get("stage", ""))
        kind = str(task.get("kind", ""))
        status = str(task.get("status", ""))
        owner = str(task.get("owner", ""))
        reviewer = str(task.get("reviewer", ""))
        why = str(task.get("why", ""))
        success = str(task.get("success", ""))
        validation = as_list(task.get("validation", []))
        links = as_list(task.get("links", []))

        if stage not in VALID_STAGES:
            errors.append(f"{task_id}: invalid stage '{stage}'")
        if kind not in VALID_TASK_KINDS:
            errors.append(f"{task_id}: invalid kind '{kind}'")
        if status not in VALID_TASK_STATUS:
            errors.append(f"{task_id}: invalid status '{status}'")
        if owner not in VALID_OWNERS:
            errors.append(f"{task_id}: invalid owner '{owner}'")
        if reviewer not in VALID_OWNERS - {"unassigned"}:
            errors.append(f"{task_id}: invalid reviewer '{reviewer}'")
        if len(why.split()) < 5:
            warnings.append(f"{task_id}: why field is too short to protect research direction")
        if len(success.split()) < 4:
            warnings.append(f"{task_id}: success field is too short")
        if kind in {"implementation", "experiment", "debug", "validation"} and not validation:
            errors.append(f"{task_id}: execution task must define at least one validation step")
        if kind in {"implementation", "experiment", "debug", "validation"} and not plan_id:
            errors.append(f"{task_id}: execution task must reference an approved plan via plan_id")
        if plan_id and plan_id not in plan_map:
            errors.append(f"{task_id}: plan_id '{plan_id}' does not exist in state/plans.yaml")
        if plan_id and kind in {"implementation", "experiment", "debug", "validation"}:
            evaluation = plan_evaluations.get(plan_id)
            if evaluation and evaluation.outcome != "approved":
                errors.append(f"{task_id}: execution task references plan '{plan_id}' that is not approved")
        if not links:
            warnings.append(f"{task_id}: no links provided")
        if owner == reviewer and owner in {"codex", "claude"}:
            warnings.append(f"{task_id}: owner and reviewer are the same; prefer cross-checking")

    for claim in claims:
        claim_id = str(claim.get("id", "UNKNOWN"))
        status = str(claim.get("status", ""))
        evidence = as_list(claim.get("evidence", []))
        reviewer = str(claim.get("reviewer", ""))
        review_required = as_bool(claim.get("review_required", False))
        confidence = str(claim.get("confidence", ""))

        if status not in VALID_CLAIM_STATUS:
            errors.append(f"{claim_id}: invalid claim status '{status}'")
        if not evidence:
            errors.append(f"{claim_id}: claims must include at least one evidence path")
        if status == "supported" and review_required:
            errors.append(f"{claim_id}: supported claims cannot remain review_required=true")
        if reviewer not in VALID_OWNERS - {"unassigned"}:
            errors.append(f"{claim_id}: invalid reviewer '{reviewer}'")
        if confidence not in {"low", "medium", "high"}:
            warnings.append(f"{claim_id}: confidence should be low, medium, or high")

    for verdict in verdicts:
        verdict_id = str(verdict.get("id", "UNKNOWN"))
        decision = str(verdict.get("decision", ""))
        status = str(verdict.get("status", ""))
        reviewer = str(verdict.get("reviewer", ""))
        evidence = as_list(verdict.get("evidence", []))
        if decision not in VALID_VERDICT_DECISIONS:
            errors.append(f"{verdict_id}: invalid verdict decision '{decision}'")
        if status not in VALID_VERDICT_STATUS:
            errors.append(f"{verdict_id}: invalid verdict status '{status}'")
        if reviewer not in VALID_OWNERS - {"unassigned"}:
            errors.append(f"{verdict_id}: invalid reviewer '{reviewer}'")
        if not evidence:
            errors.append(f"{verdict_id}: verdicts must include at least one evidence path")

    for plan in plans:
        evaluation = plan_evaluations[plan.id]
        if plan.status not in PLAN_STATUS:
            errors.append(f"{plan.id}: invalid plan status '{plan.status}'")
        if plan.planner not in VALID_PLAN_OWNERS:
            errors.append(f"{plan.id}: invalid planner '{plan.planner}'")
        if plan.execution_owner not in VALID_PLAN_OWNERS:
            errors.append(f"{plan.id}: invalid execution_owner '{plan.execution_owner}'")
        if plan.execution_reviewer not in VALID_PLAN_OWNERS:
            errors.append(f"{plan.id}: invalid execution_reviewer '{plan.execution_reviewer}'")
        if plan.required_approvals < 1:
            errors.append(f"{plan.id}: required_approvals must be at least 1")
        if plan.blocking_rejections < 1:
            errors.append(f"{plan.id}: blocking_rejections must be at least 1")
        if plan.task_stage not in VALID_STAGES:
            errors.append(f"{plan.id}: invalid task_stage '{plan.task_stage}'")
        if plan.task_kind not in VALID_TASK_KINDS:
            errors.append(f"{plan.id}: invalid task_kind '{plan.task_kind}'")
        if len(plan.generated_tasks) != len(set(plan.generated_tasks)):
            errors.append(f"{plan.id}: generated_tasks contains duplicates")
        if plan.status == "executing" and not plan.generated_tasks:
            errors.append(f"{plan.id}: executing plans must record generated_tasks")
        if plan.status in {"approved", "executing", "completed"} and evaluation.outcome != "approved":
            errors.append(f"{plan.id}: stored status '{plan.status}' does not match review outcome '{evaluation.outcome}'")
        for generated_task in plan.generated_tasks:
            if generated_task not in {str(task.get("id", "")) for task in tasks}:
                errors.append(f"{plan.id}: generated task '{generated_task}' is missing from state/tasks.yaml")

    for review in plan_reviews:
        if review.plan_id not in plan_map:
            errors.append(f"{review.id}: references unknown plan '{review.plan_id}'")
        if review.decision not in PLAN_REVIEW_DECISIONS:
            errors.append(f"{review.id}: invalid plan review decision '{review.decision}'")
        if review.reviewer not in VALID_OWNERS - {"unassigned"}:
            errors.append(f"{review.id}: invalid reviewer '{review.reviewer}'")
        if not review.role:
            warnings.append(f"{review.id}: review role is empty")
        if not review.evidence:
            errors.append(f"{review.id}: plan reviews must include at least one evidence path")

    for warning in warnings:
        print(f"[WARN] {warning}")

    if errors:
        print("[FAIL] Task quality checks failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("[PASS] Task and claim quality checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
