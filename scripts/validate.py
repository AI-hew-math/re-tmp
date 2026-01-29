import os
import sys
import importlib.util

def validate(exp_id):
    print(f"Validating {exp_id}...")
    
    # 1. Check folder structure
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

    # 2. Check inheritance
    try:
        # Basic check: read the file and look for 'BaseModel'
        with open(src_path, 'r') as f:
            content = f.read()
            if "BaseModel" not in content:
                print(f"[FAIL] {src_path} does not seem to inherit from BaseModel")
                return False
    except Exception as e:
        print(f"[ERROR] Could not read {src_path}: {e}")
        return False

    print("[PASS] Experiment structure is valid.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/validate.py EXPxxx")
    else:
        validate(sys.argv[1])
