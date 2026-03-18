import sys

from plan_utils import evaluate_plan, load_plans, load_plan_reviews
from state_utils import as_bool, as_list, load_state_items, StateParseError


def main() -> int:
    errors: list[str] = []

    try:
        tasks = load_state_items("tasks.yaml", "tasks")
        claims = load_state_items("claims.yaml", "claims")
        verdicts = load_state_items("verdicts.yaml", "verdicts")
        plans = load_plans()
        plan_reviews = load_plan_reviews()
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    verdict_map = {str(item.get("reviewed_item", "")): item for item in verdicts}
    plan_map = {plan.id: plan for plan in plans}
    plan_evaluations = {plan.id: evaluate_plan(plan, plan_reviews) for plan in plans}

    for task in tasks:
        task_id = str(task.get("id", "UNKNOWN"))
        plan_id = str(task.get("plan_id", ""))
        status = str(task.get("status", ""))
        kind = str(task.get("kind", ""))
        validation = as_list(task.get("validation", []))
        reviewer = str(task.get("reviewer", ""))
        stage = str(task.get("stage", ""))

        if status == "done" and kind in {"implementation", "experiment", "debug", "validation"} and not validation:
            errors.append(f"{task_id}: done execution task has no validation plan recorded")
        if status == "done" and task_id not in verdict_map:
            errors.append(f"{task_id}: done task must have a verdict entry")
        if reviewer in {"", "unassigned"}:
            errors.append(f"{task_id}: every task must have a non-unassigned reviewer")
        if stage == "":
            errors.append(f"{task_id}: every task must have a stage")
        if kind in {"implementation", "experiment", "debug", "validation"}:
            if plan_id == "":
                errors.append(f"{task_id}: execution task must include plan_id")
            elif plan_id not in plan_map:
                errors.append(f"{task_id}: execution task references unknown plan '{plan_id}'")
            elif plan_evaluations[plan_id].outcome != "approved":
                errors.append(f"{task_id}: execution task references plan '{plan_id}' that is not approved")

    for claim in claims:
        claim_id = str(claim.get("id", "UNKNOWN"))
        status = str(claim.get("status", ""))
        evidence = as_list(claim.get("evidence", []))
        review_required = as_bool(claim.get("review_required", False))

        if status == "supported" and not evidence:
            errors.append(f"{claim_id}: supported claim must include evidence")
        if status == "supported" and review_required:
            errors.append(f"{claim_id}: supported claim must not still require review")
        if status in {"supported", "rejected"} and claim_id not in verdict_map:
            errors.append(f"{claim_id}: finalized claim must have a verdict entry")

    for plan in plans:
        evaluation = plan_evaluations[plan.id]
        if plan.status in {"approved", "executing", "completed"} and evaluation.outcome != "approved":
            errors.append(f"{plan.id}: plan status '{plan.status}' requires enough approvals and no blocking reviews")
        if plan.status == "completed" and not plan.generated_tasks:
            errors.append(f"{plan.id}: completed plan must record generated_tasks")

    if errors:
        print("[FAIL] Review gate blocked approval:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("[PASS] Review gate passed. Items are safe to advance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
