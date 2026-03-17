from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "state"
TASKS_PATH = STATE_DIR / "tasks.yaml"
CLAIMS_PATH = STATE_DIR / "claims.yaml"
VERDICTS_PATH = STATE_DIR / "verdicts.yaml"


@dataclass
class Task:
    id: str
    title: str
    status: str
    owner: str
    updated_at: str
    next_action: str
    blockers: list[str]
    links: list[str]
    extra: dict[str, object]


@dataclass
class Claim:
    id: str
    claim: str
    status: str
    evidence: list[str]
    updated_at: str
    notes: str


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
            casted_list = current.setdefault(current_list_key, [])
            if isinstance(casted_list, list):
                casted_list.append(value)

    return items


def load_tasks() -> list[Task]:
    raw_tasks = parse_top_level_items(TASKS_PATH, "tasks")
    tasks: list[Task] = []
    for item in raw_tasks:
        tasks.append(
            Task(
                id=str(item.get("id", "")),
                title=str(item.get("title", "")),
                status=str(item.get("status", "")),
                owner=str(item.get("owner", "")),
                updated_at=str(item.get("updated_at", "")),
                next_action=str(item.get("next_action", "")),
                blockers=list(item.get("blockers", [])) if isinstance(item.get("blockers", []), list) else [],
                links=list(item.get("links", [])) if isinstance(item.get("links", []), list) else [],
                extra={k: v for k, v in item.items() if k not in {"id", "title", "status", "owner", "updated_at", "next_action", "blockers", "links"}},
            )
        )
    return tasks


def load_claims() -> list[Claim]:
    raw_claims = parse_top_level_items(CLAIMS_PATH, "claims")
    claims: list[Claim] = []
    for item in raw_claims:
        claims.append(
            Claim(
                id=str(item.get("id", "")),
                claim=str(item.get("claim", "")),
                status=str(item.get("status", "")),
                evidence=list(item.get("evidence", [])) if isinstance(item.get("evidence", []), list) else [],
                updated_at=str(item.get("updated_at", "")),
                notes=str(item.get("notes", "")),
            )
        )
    return claims


def score_task(task: Task) -> tuple[int, int]:
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
    return (status_rank, owner_rank)


def recommend_owner(task: Task) -> str:
    execution_markers = ("implement", "edit", "run", "validate", "debug", "train", "test", "fix", "scaffold")
    text = f"{task.title} {task.next_action}".lower()
    if any(marker in text for marker in execution_markers):
        return "claude"
    return "codex"


def summarize_claim_context(claims: list[Claim]) -> str:
    if not claims:
        return "No claims recorded yet."
    open_claims = [claim for claim in claims if claim.status in {"provisional", "needs_review"}]
    if open_claims:
        claim = open_claims[0]
        return f"Focus claim: {claim.id} [{claim.status}] - {claim.claim}"
    claim = claims[0]
    return f"Latest claim: {claim.id} [{claim.status}] - {claim.claim}"


def main() -> int:
    try:
        tasks = load_tasks()
        claims = load_claims()
    except ValueError as exc:
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
    print(f"Current status: {next_task.status}")
    print(f"Recorded owner: {next_task.owner}")
    print(f"Suggested owner: {suggested_owner}")
    print(f"Updated at: {next_task.updated_at}")
    print()
    print("Next action")
    print(f"- {next_task.next_action}")
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
    if suggested_owner == "claude":
        print("Handoff")
        print("- Send this task to Claude for implementation/execution.")
        print("- Ask Claude to return a compact packet with changes, validations, observations, and blockers.")
    else:
        print("Handoff")
        print("- Keep this with Codex for planning/review/state updates before delegating execution.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
