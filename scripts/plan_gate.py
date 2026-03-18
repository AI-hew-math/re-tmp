import sys

from plan_utils import PLAN_STATUS, evaluate_plan, load_plans, load_plan_reviews, reviews_for_plan
from state_utils import StateParseError


def summarize(plan_id: str | None = None, require_approved: bool = False) -> int:
    try:
        plans = load_plans()
        reviews = load_plan_reviews()
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    selected = [plan for plan in plans if plan_id in {None, plan.id}]
    if plan_id and not selected:
        print(f"[FAIL] Plan not found: {plan_id}")
        return 1

    errors: list[str] = []

    print("# Plan Gate Summary")
    print()
    for plan in selected:
        evaluation = evaluate_plan(plan, reviews)
        plan_reviews = reviews_for_plan(plan.id, reviews)

        print(f"Plan: {plan.id} - {plan.title}")
        print(f"- Stored status: {plan.status}")
        print(f"- Review outcome: {evaluation.outcome}")
        print(f"- Approvals: {evaluation.approvals}/{evaluation.required_approvals}")
        print(f"- Change requests: {evaluation.changes_requested}")
        print(f"- Rejections: {evaluation.rejections}/{evaluation.blocking_rejections}")
        print(f"- Generated tasks: {', '.join(plan.generated_tasks) if plan.generated_tasks else 'none'}")

        if plan_reviews:
            print("- Reviews:")
            for review in plan_reviews:
                print(f"  - {review.id}: {review.reviewer} [{review.role}] -> {review.decision}")
        else:
            print("- Reviews: none yet")
        print()

        if plan.status not in PLAN_STATUS:
            errors.append(f"{plan.id}: invalid stored status '{plan.status}'")
        if plan.status in {"approved", "executing", "completed"} and evaluation.outcome != "approved":
            errors.append(f"{plan.id}: stored status '{plan.status}' does not match review outcome '{evaluation.outcome}'")

    if errors:
        print("[FAIL] Plan gate blocked advancement:")
        for error in errors:
            print(f"  - {error}")
        return 1

    if plan_id and require_approved:
        evaluation = evaluate_plan(selected[0], reviews)
        if evaluation.outcome != "approved":
            print(f"[INFO] {selected[0].id} is not approved yet.")
            return 1

    print("[PASS] Plan gate check completed.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    require_approved = False
    if "--require-approved" in args:
        require_approved = True
        args = [arg for arg in args if arg != "--require-approved"]
    target = args[0] if args else None
    return summarize(target, require_approved=require_approved)


if __name__ == "__main__":
    sys.exit(main())
