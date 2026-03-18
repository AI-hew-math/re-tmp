from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import sys

from plan_utils import evaluate_plan, load_plans, load_plan_reviews
from state_utils import as_list, load_state_items, StateParseError


ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "runs"


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def load_task(task_id: str) -> dict[str, object]:
    tasks = load_state_items("tasks.yaml", "tasks")
    for task in tasks:
        if str(task.get("id", "")) == task_id:
            return task
    raise StateParseError(f"Task not found: {task_id}")


def create_run(task: dict[str, object]) -> Path:
    run_id = f"{utc_stamp()}-{str(task.get('id', 'TASK')).lower()}"
    run_dir = RUNS_DIR / run_id
    (run_dir / "logs").mkdir(parents=True, exist_ok=True)
    metadata = {
        "run_id": run_id,
        "task_id": str(task.get("id", "")),
        "plan_id": str(task.get("plan_id", "")),
        "title": str(task.get("title", "")),
        "stage": str(task.get("stage", "")),
        "kind": str(task.get("kind", "")),
        "owner": str(task.get("owner", "")),
        "reviewer": str(task.get("reviewer", "")),
        "why": str(task.get("why", "")),
        "success": str(task.get("success", "")),
        "next_action": str(task.get("next_action", "")),
        "validation": as_list(task.get("validation", [])),
        "links": as_list(task.get("links", [])),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "status": "created",
    }
    (run_dir / "run.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (run_dir / "plan.md").write_text(
        "\n".join(
            [
                f"# {metadata['task_id']} - {metadata['title']}",
                "",
                *([f"- Plan: {metadata['plan_id']}"] if metadata["plan_id"] else []),
                f"- Stage: {metadata['stage']}",
                f"- Kind: {metadata['kind']}",
                f"- Owner: {metadata['owner']}",
                f"- Reviewer: {metadata['reviewer']}",
                "",
                "## Why",
                str(metadata["why"]),
                "",
                "## Success",
                str(metadata["success"]),
                "",
                "## Next Action",
                str(metadata["next_action"]),
                "",
                "## Validation",
                *[f"- {item}" for item in metadata["validation"]],
                "",
                "## Links",
                *[f"- {item}" for item in metadata["links"]],
                "",
            ]
        ),
        encoding="utf-8",
    )
    (run_dir / "review.md").write_text(
        "# Review Notes\n\n- Add findings, evidence, and verdict rationale here.\n",
        encoding="utf-8",
    )
    return run_dir


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_task.py TASK-XXXX")
        return 1

    task_id = sys.argv[1]
    try:
        task = load_task(task_id)
        if str(task.get("status", "")) == "done":
            print(f"[FAIL] Refusing to create a new run for completed task: {task_id}")
            return 1
        if str(task.get("status", "")) == "blocked":
            print(f"[FAIL] Refusing to create a run for blocked task: {task_id}")
            return 1

        kind = str(task.get("kind", ""))
        if kind in {"implementation", "experiment", "debug", "validation"}:
            plan_id = str(task.get("plan_id", ""))
            if not plan_id:
                print(f"[FAIL] Execution task has no plan_id: {task_id}")
                return 1
            plans = {plan.id: plan for plan in load_plans()}
            reviews = load_plan_reviews()
            plan = plans.get(plan_id)
            if plan is None:
                print(f"[FAIL] Execution task references unknown plan: {plan_id}")
                return 1
            evaluation = evaluate_plan(plan, reviews)
            if evaluation.outcome != "approved":
                print(f"[FAIL] Execution task plan is not approved yet: {plan_id} [{evaluation.outcome}]")
                return 1
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    run_dir = create_run(task)
    print(f"[PASS] Created run scaffold: {run_dir}")
    print(f"- Metadata: {run_dir / 'run.json'}")
    print(f"- Plan: {run_dir / 'plan.md'}")
    print(f"- Review notes: {run_dir / 'review.md'}")
    print(f"- Logs dir: {run_dir / 'logs'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
