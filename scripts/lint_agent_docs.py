from __future__ import annotations

from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
ROOT_DOCS = [ROOT / "AGENTS.md", ROOT / "CLAUDE.md"]
RULE_DOCS_DIR = ROOT / "docs" / "agent-rules"

REQUIRED_SECTIONS = [
    "## Purpose",
    "## Project Scope",
    "## Hard Rules",
    "## Verification Rules",
    "## Domain Terms",
    "## Referenced Files",
]

AMBIGUOUS_PATTERNS = [
    "\uc801\uc808\ud558",
    "\uc798 ",
    "\uac00\ub2a5\ud558\uba74",
    "\uc54c\uc544\uc11c",
    "\uc720\uc5f0\ud558\uac8c",
    "\uae54\ub054\ud55c \ucf54\ub4dc\ub97c",
    "\ud14c\uc2a4\ud2b8\ub97c \uc798",
    r"\bproperly\b",
    r"\bclean code\b",
    r"\bdo your best\b",
    r"\bif possible\b",
    r"\bas appropriate\b",
]

VERIFICATION_HINTS = [
    "python scripts/",
    "uv run python",
]


def count_lines(path: Path) -> int:
    return len(path.read_text(encoding="utf-8-sig").splitlines())


def contains_required_sections(text: str) -> list[str]:
    return [section for section in REQUIRED_SECTIONS if section not in text]


def find_ambiguous_lines(text: str) -> list[str]:
    findings: list[str] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        for pattern in AMBIGUOUS_PATTERNS:
            if re.search(pattern, lowered):
                findings.append(f"line {idx}: {line.strip()}")
                break
    return findings


def has_verification_command(text: str) -> bool:
    return any(hint in text for hint in VERIFICATION_HINTS)


def has_rule_references(text: str) -> bool:
    return "docs/agent-rules/" in text


def lint_root_doc(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.exists():
        return [f"Missing required root agent doc: {path.name}"]

    text = path.read_text(encoding="utf-8-sig")
    line_count = count_lines(path)
    if line_count > 200:
        errors.append(f"{path.name}: exceeds 200 lines ({line_count})")

    missing_sections = contains_required_sections(text)
    if missing_sections:
        errors.append(f"{path.name}: missing sections: {', '.join(missing_sections)}")

    ambiguous = find_ambiguous_lines(text)
    if ambiguous:
        errors.append(f"{path.name}: contains ambiguous guidance: {' | '.join(ambiguous[:8])}")

    if not has_verification_command(text):
        errors.append(f"{path.name}: missing concrete verification commands")

    if not has_rule_references(text):
        errors.append(f"{path.name}: should reference modular docs in docs/agent-rules/")

    return errors


def lint_rule_docs() -> list[str]:
    errors: list[str] = []
    if not RULE_DOCS_DIR.exists():
        return ["Missing docs/agent-rules/ directory"]

    markdown_files = sorted(RULE_DOCS_DIR.glob("*.md"))
    if not markdown_files:
        return ["docs/agent-rules/ has no markdown rule files"]

    for path in markdown_files:
        text = path.read_text(encoding="utf-8-sig")
        if len(text.splitlines()) > 250:
            errors.append(f"{path.relative_to(ROOT)}: rule doc is too long; split it further")
        ambiguous = find_ambiguous_lines(text)
        if ambiguous:
            errors.append(
                f"{path.relative_to(ROOT)}: contains ambiguous guidance: {' | '.join(ambiguous[:6])}"
            )
    return errors


def main() -> int:
    errors: list[str] = []
    for path in ROOT_DOCS:
        errors.extend(lint_root_doc(path))
    errors.extend(lint_rule_docs())

    if errors:
        print("[FAIL] Agent doc lint failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("[PASS] Agent docs satisfy the enforced writing rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
