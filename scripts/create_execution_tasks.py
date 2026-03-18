from __future__ import annotations

import sys

from plan_utils import (
    derive_task_id,
    evaluate_plan,
    load_plan_dicts,
    load_plan_reviews,
    load_task_dicts,
    plan_from_dict,
    save_plan_dicts,
    save_task_dicts,
    today_stamp,
)
from state_utils import StateParseError


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_execution_tasks.py PLAN-XXXX")
        return 1

    plan_id = sys.argv[1]

    try:
        plan_dicts = load_plan_dicts()
        reviews = load_plan_reviews()
        task_dicts = load_task_dicts()
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    target = None
    for item in plan_dicts:
        if str(item.get("id", "")) == plan_id:
            target = item
            break

    if target is None:
        print(f"[FAIL] Plan not found: {plan_id}")
        return 1

    plan = plan_from_dict(target)
    evaluation = evaluate_plan(plan, reviews)
    if evaluation.outcome != "approved":
        print(
            f"[FAIL] {plan.id} is not approved. "
            f"Current outcome is '{evaluation.outcome}' with {evaluation.approvals}/{evaluation.required_approvals} approvals."
        )
        return 1

    if plan.generated_tasks:
        print(f"[FAIL] {plan.id} already generated tasks: {', '.join(plan.generated_tasks)}")
        return 1

    task_id = derive_task_id(plan.id)
    if any(str(task.get("id", "")) == task_id for task in task_dicts):
        print(f"[FAIL] Derived task id already exists: {task_id}")
        return 1

    task = {
        "id": task_id,
        "title": plan.task_title,
        "plan_id": plan.id,
        "stage": plan.task_stage,
        "kind": plan.task_kind,
        "status": "ready",
        "owner": plan.execution_owner,
        "reviewer": plan.execution_reviewer,
        "updated_at": today_stamp(),
        "why": plan.task_why,
        "success": plan.task_success,
        "next_action": plan.task_next_action,
        "blockers": [],
        "validation": plan.task_validation,
        "links": plan.links,
    }
    task_dicts.append(task)

    target["status"] = "executing"
    target["updated_at"] = today_stamp()
    target["next_action"] = f"Execute {task_id} and return evidence through runs/ and verdicts."
    target["generated_tasks"] = [task_id]

    save_task_dicts(task_dicts)
    save_plan_dicts(plan_dicts)

    print(f"[PASS] Created execution task from approved plan: {task_id}")
    print(f"- Plan: {plan.id}")
    print(f"- Owner: {plan.execution_owner}")
    print(f"- Reviewer: {plan.execution_reviewer}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
