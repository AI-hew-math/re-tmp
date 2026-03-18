import sys

from state_utils import as_bool, as_list, load_state_items, StateParseError


VALID_TASK_KINDS = {"research", "implementation", "experiment", "debug", "validation", "review", "claim"}
VALID_TASK_STATUS = {"pending", "ready", "in_progress", "blocked", "done"}
VALID_OWNERS = {"codex", "claude", "human", "shared", "unassigned"}
VALID_CLAIM_STATUS = {"provisional", "supported", "rejected", "needs_review"}
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
    except StateParseError as exc:
        print(f"[FAIL] {exc}")
        return 1

    for task in tasks:
        task_id = str(task.get("id", "UNKNOWN"))
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
        if decision not in VALID_VERDICT_DECISIONS:
            errors.append(f"{verdict_id}: invalid verdict decision '{decision}'")

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
