from pathlib import Path
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
SITE_CONFIG = ROOT / "configs" / "site.yaml"
SITE_EXAMPLE = ROOT / "configs" / "site.yaml.example"



def main() -> int:
    if SITE_CONFIG.exists():
        print(f"[SKIP] {SITE_CONFIG} already exists")
        return 0

    if not SITE_EXAMPLE.exists():
        print(f"[FAIL] Missing template: {SITE_EXAMPLE}")
        return 1

    shutil.copyfile(SITE_EXAMPLE, SITE_CONFIG)
    print(f"[OK] Created {SITE_CONFIG}")
    print("Next steps:")
    print("1. Edit configs/site.yaml for your cluster, project, and paths")
    print("2. Copy .env.example to .env and add credentials")
    print("3. Run: uv run python3 scripts/check_creds.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
