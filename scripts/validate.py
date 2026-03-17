import os
import sys
from pathlib import Path


REQUIRED_STATE_FILES = [
    Path("state/tasks.yaml"),
    Path("state/claims.yaml"),
    Path("state/session_capsules/.gitkeep"),
]



def validate_state_layout() -> bool:
    missing = [str(path) for path in REQUIRED_STATE_FILES if not path.exists()]
    if missing:
        print("[FAIL] Missing required state files:")
        for path in missing:
            print(f"  - {path}")
        return False
    return True



def validate(exp_id: str) -> bool:
    print(f"Validating {exp_id}...")

    if not validate_state_layout():
        return False

    src_path = f"src/experiments/{exp_id}/model.py"
    if not os.path.exists(src_path):
        print(f"[FAIL] Missing {src_path}")
        return False

    config_path = f"configs/experiment/{exp_id}.yaml"
    if not os.path.exists(config_path):
        print(f"[FAIL] Missing {config_path}")
        return False

    readme_path = f"experiments/{exp_id}/README.md"
    if not os.path.exists(readme_path):
        print(f"[FAIL] Missing {readme_path}")
        return False

    try:
        with open(src_path, "r", encoding="utf-8") as handle:
            content = handle.read()
        if "BaseModel" not in content:
            print(f"[FAIL] {src_path} does not seem to inherit from BaseModel")
            return False
    except Exception as exc:
        print(f"[ERROR] Could not read {src_path}: {exc}")
        return False

    print("[PASS] Experiment structure is valid.")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate.py EXPxxx")
    else:
        sys.exit(0 if validate(sys.argv[1]) else 1)
