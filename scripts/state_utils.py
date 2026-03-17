from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "state"


class StateParseError(ValueError):
    pass



def parse_top_level_items(path: Path, section_name: str) -> list[dict[str, object]]:
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if not lines or lines[0].strip() != f"{section_name}:":
        raise StateParseError(f"{path.relative_to(ROOT)} must start with '{section_name}:'")

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
            current.setdefault(current_list_key, [])
            casted = current[current_list_key]
            if isinstance(casted, list):
                casted.append(value)

    return items



def load_state_items(filename: str, section_name: str) -> list[dict[str, object]]:
    return parse_top_level_items(STATE_DIR / filename, section_name)



def as_list(value: object) -> list[str]:
    return list(value) if isinstance(value, list) else []



def as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False
