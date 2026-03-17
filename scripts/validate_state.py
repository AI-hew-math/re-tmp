from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TASKS_PATH = ROOT / "state" / "tasks.yaml"
CLAIMS_PATH = ROOT / "state" / "claims.yaml"
CAPSULES_DIR = ROOT / "state" / "session_capsules"



def parse_top_level_items(path: Path, section_name: str) -> list[dict[str, object]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != f"{section_name}:":
        raise ValueError(f"{path.relative_to(ROOT)} must start with '{section_name}:'")

    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_list_key: str | None = None

    for raw_line in lines[1:]:
        if not raw_line.strip():
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 2 and line.startswith("- "):
            current = {}
            items.append(current)
            current_list_key = None
            remainder = line[2:]
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = value.strip()
            continue

        if current is None:
            continue

        if indent == 4 and line.endswith(":"):
            key = line[:-1].strip()
            current[key] = []
            current_list_key = key
            continue

        if indent == 4 and ":" in line:
            key, value = line.split(":", 1)
            value = value.strip()
            if value == "[]":
                current[key.strip()] = []
            else:
                current[key.strip()] = value
            current_list_key = None
            continue

        if indent == 6 and line.startswith("- ") and current_list_key:
            value = line[2:].strip()
            current[current_list_key].append(value)

    return items



def validate_tasks() -> list[str]:
    errors: list[str] = []
    tasks = parse_top_level_items(TASKS_PATH, "tasks")
    required = {"id", "title", "status", "owner", "updated_at", "next_action"}
    for idx, task in enumerate(tasks, start=1):
        missing = sorted(required - set(task))
        if missing:
            errors.append(f"state/tasks.yaml task #{idx} missing keys: {', '.join(missing)}")
    return errors



def validate_claims() -> list[str]:
    errors: list[str] = []
    claims = parse_top_level_items(CLAIMS_PATH, "claims")
    required = {"id", "claim", "status", "evidence", "updated_at"}
    for idx, claim in enumerate(claims, start=1):
        missing = sorted(required - set(claim))
        if missing:
            errors.append(f"state/claims.yaml claim #{idx} missing keys: {', '.join(missing)}")
    return errors



def validate_capsules_dir() -> list[str]:
    if CAPSULES_DIR.exists() and CAPSULES_DIR.is_dir():
        return []
    return ["state/session_capsules/ must exist"]



def main() -> int:
    errors: list[str] = []
    for path in (TASKS_PATH, CLAIMS_PATH):
        if not path.exists():
            errors.append(f"Missing required state file: {path.relative_to(ROOT)}")
    errors.extend(validate_capsules_dir())

    if not errors:
        try:
            errors.extend(validate_tasks())
            errors.extend(validate_claims())
        except ValueError as exc:
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

