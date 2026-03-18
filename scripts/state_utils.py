from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "state"


class StateParseError(ValueError):
    pass


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines()


def parse_top_level_items(path: Path, section_name: str) -> list[dict[str, object]]:
    lines = _read_lines(path)
    if not lines or lines[0].strip() != f"{section_name}:":
        raise StateParseError(f"{display_path(path)} must start with '{section_name}:'")

    items: list[dict[str, object]] = []
    current: dict[str, object] | None = None
    current_list_key: str | None = None

    for line_no, raw_line in enumerate(lines[1:], start=2):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if indent == 2 and stripped.startswith("- "):
            current = {}
            items.append(current)
            current_list_key = None
            remainder = stripped[2:]
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                current[key.strip()] = value.strip()
            elif remainder:
                raise StateParseError(
                    f"{display_path(path)} line {line_no}: top-level list items must be mappings"
                )
            continue

        if current is None:
            raise StateParseError(f"{display_path(path)} line {line_no}: content must belong to a list item")

        if indent == 4 and stripped.endswith(":"):
            key = stripped[:-1].strip()
            current[key] = []
            current_list_key = key
            continue

        if indent == 4 and ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip()
            current[key.strip()] = [] if value == "[]" else value
            current_list_key = None
            continue

        if indent == 6 and stripped.startswith("- ") and current_list_key:
            casted = current.get(current_list_key)
            if not isinstance(casted, list):
                raise StateParseError(
                    f"{display_path(path)} line {line_no}: '{current_list_key}' must be a list before adding items"
                )
            casted.append(stripped[2:].strip())
            continue

        raise StateParseError(f"{display_path(path)} line {line_no}: unsupported structure '{stripped}'")

    return items


def parse_flat_mapping(path: Path) -> dict[str, object]:
    data: dict[str, object] = {}
    current_list_key: str | None = None

    for line_no, raw_line in enumerate(_read_lines(path), start=1):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if indent == 0 and stripped.endswith(":"):
            key = stripped[:-1].strip()
            data[key] = []
            current_list_key = key
            continue

        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            value = value.strip()
            data[key.strip()] = [] if value == "[]" else value
            current_list_key = None
            continue

        if indent == 2 and stripped.startswith("- ") and current_list_key:
            casted = data.get(current_list_key)
            if not isinstance(casted, list):
                raise StateParseError(
                    f"{display_path(path)} line {line_no}: '{current_list_key}' must be a list before adding items"
                )
            casted.append(stripped[2:].strip())
            continue

        raise StateParseError(f"{display_path(path)} line {line_no}: unsupported structure '{stripped}'")

    return data


def load_state_items(filename: str, section_name: str) -> list[dict[str, object]]:
    return parse_top_level_items(STATE_DIR / filename, section_name)


def _format_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def write_top_level_items(path: Path, section_name: str, items: list[dict[str, object]]) -> None:
    lines = [f"{section_name}:"]
    for item in items:
        if not item:
            continue
        first = True
        for key, value in item.items():
            if isinstance(value, list):
                if first:
                    lines.append(f"  - {key}:")
                    first = False
                else:
                    lines.append(f"    {key}:")
                for entry in value:
                    lines.append(f"      - {_format_scalar(entry)}")
                if not value:
                    lines[-1] = f"{lines[-1]} []"
                continue

            prefix = "  - " if first else "    "
            lines.append(f"{prefix}{key}: {_format_scalar(value)}")
            first = False
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def as_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return default
