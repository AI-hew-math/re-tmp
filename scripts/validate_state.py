from pathlib import Path
import sys

from state_utils import ROOT, StateParseError, load_state_items


TASKS_PATH = ROOT / "state" / "tasks.yaml"
CLAIMS_PATH = ROOT / "state" / "claims.yaml"
VERDICTS_PATH = ROOT / "state" / "verdicts.yaml"
CAPSULES_DIR = ROOT / "state" / "session_capsules"


TASK_REQUIRED = {
    "id", "title", "stage", "kind", "status", "owner", "reviewer", "updated_at", "why", "success", "next_action"
}
CLAIM_REQUIRED = {
    "id", "claim", "status", "evidence", "updated_at", "confidence", "review_required", "reviewer", "notes"
}
VERDICT_REQUIRED = {
    "id", "reviewed_item", "decision", "status", "rationale", "evidence", "updated_at", "reviewer", "follow_up"
}


def validate_items(filename: str, section_name: str, required: set[str]) -> list[str]:
    errors: list[str] = []
    items = load_state_items(filename, section_name)
    for idx, item in enumerate(items, start=1):
        missing = sorted(required - set(item))
        if missing:
            errors.append(f"state/{filename} item #{idx} missing keys: {', '.join(missing)}")
    return errors


def validate_capsules_dir() -> list[str]:
    if CAPSULES_DIR.exists() and CAPSULES_DIR.is_dir():
        return []
    return ["state/session_capsules/ must exist"]


def main() -> int:
    errors: list[str] = []
    for path in (TASKS_PATH, CLAIMS_PATH, VERDICTS_PATH):
        if not path.exists():
            errors.append(f"Missing required state file: {path.relative_to(ROOT)}")
    errors.extend(validate_capsules_dir())

    if not errors:
        try:
            errors.extend(validate_items("tasks.yaml", "tasks", TASK_REQUIRED))
            errors.extend(validate_items("claims.yaml", "claims", CLAIM_REQUIRED))
            errors.extend(validate_items("verdicts.yaml", "verdicts", VERDICT_REQUIRED))
        except StateParseError as exc:
            errors.append(str(exc))

    if errors:
        print("[FAIL] Agent state validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("[PASS] Agent state is valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
