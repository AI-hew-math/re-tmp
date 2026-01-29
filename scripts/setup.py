#!/usr/bin/env python3
"""
Project onboarding script.

Run once after cloning to configure the template for your environment.

Usage:
    uv run python3 scripts/setup.py
"""
import os
import sys
from pathlib import Path

# Default LAIT Lab configuration
DEFAULT_CLUSTERS = [
    {
        "name": "soda",
        "partitions": ["R3090", "A100"],
        "gpus": "10x 3090, 8x A100",
        "devices": ["1x3090", "2x3090", "4x3090", "1xa100", "2xa100", "4xa100"],
    },
    {
        "name": "vegi",
        "partitions": ["R4090", "A6000", "RTXPRO6000"],
        "gpus": "16x 4090, 8x A6000, 16x Pro6000 (96GB)",
        "devices": ["1x4090", "2x4090", "4x4090", "8x4090", "1xa6000", "2xa6000", "4xa6000", "1xpro6000", "2xpro6000"],
    },
    {
        "name": "potato",
        "partitions": ["A6000"],
        "gpus": "12x A6000",
        "devices": ["1xa6000", "2xa6000", "4xa6000"],
    },
]

DEFAULT_PATHS = {
    "workspace": "/workspace/$USER",
    "data": "/data/$USER",
    "nas": ["/nas1", "/nas2"],
}


def prompt(msg: str, default: str = "") -> str:
    """Prompt user for input with optional default."""
    if default:
        val = input(f"{msg} [{default}]: ").strip()
        return val if val else default
    return input(f"{msg}: ").strip()


def prompt_choice(msg: str, options: list[str], default: int = 0) -> str:
    """Prompt user to choose from options."""
    print(f"\n{msg}")
    for i, opt in enumerate(options):
        marker = " (default)" if i == default else ""
        print(f"  [{i + 1}] {opt}{marker}")

    while True:
        val = input(f"Choice [1-{len(options)}]: ").strip()
        if not val:
            return options[default]
        try:
            idx = int(val) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print("Invalid choice, try again.")


def prompt_yn(msg: str, default: bool = True) -> bool:
    """Prompt yes/no question."""
    hint = "[Y/n]" if default else "[y/N]"
    val = input(f"{msg} {hint}: ").strip().lower()
    if not val:
        return default
    return val in ("y", "yes")


def main():
    print("=" * 60)
    print("  Deep Learning Research Template - Setup")
    print("=" * 60)
    print("\nThis script configures the template for your environment.")
    print("Press Enter to accept defaults (shown in brackets).\n")

    # 1. Project Info
    print("─" * 40)
    print("PROJECT INFO")
    print("─" * 40)

    project_name = prompt("Project name (e.g., 'my-research')", "dl-research")
    project_desc = prompt("Brief description", "Deep learning research project")
    wandb_project = prompt("WandB project name", project_name)

    # 2. Infrastructure
    print("\n" + "─" * 40)
    print("INFRASTRUCTURE")
    print("─" * 40)

    use_lait = prompt_yn("Use LAIT Lab default clusters (soda/vegi/potato)?", True)

    if use_lait:
        clusters = DEFAULT_CLUSTERS
        paths = DEFAULT_PATHS
    else:
        print("\nDefine your clusters (enter empty name to finish):")
        clusters = []
        while True:
            name = prompt(f"  Cluster {len(clusters) + 1} name", "")
            if not name:
                break
            partitions = prompt(f"  Partitions for {name} (comma-sep)", "gpu").split(",")
            gpus = prompt(f"  GPU description", "8x A100")
            devices = prompt(f"  Device options (comma-sep, e.g., '1xa100,2xa100,4xa100')", "1xa100,2xa100,4xa100").split(",")
            clusters.append({
                "name": name.strip(),
                "partitions": [p.strip() for p in partitions],
                "gpus": gpus.strip(),
                "devices": [d.strip() for d in devices],
            })

        if not clusters:
            print("No clusters defined. Using local-only mode.")
            clusters = [{
                "name": "local",
                "partitions": ["default"],
                "gpus": "local GPU",
                "devices": ["1xgpu"],
            }]

        print("\nStorage paths:")
        paths = {
            "workspace": prompt("Workspace path (code lives here)", "/workspace/$USER"),
            "data": prompt("Data path (datasets, fast storage)", "/data/$USER"),
            "nas": prompt("NAS paths (comma-sep, or 'none')", "/nas1,/nas2"),
        }
        if paths["nas"].lower() == "none":
            paths["nas"] = []
        else:
            paths["nas"] = [p.strip() for p in paths["nas"].split(",")]

    # 3. Preferences
    print("\n" + "─" * 40)
    print("PREFERENCES")
    print("─" * 40)

    # Select default cluster
    cluster_names = [f"{c['name']} ({c['gpus']})" for c in clusters]
    cluster_choice = prompt_choice("Default cluster for job submission:", cluster_names, 0)
    default_cluster_idx = cluster_names.index(cluster_choice)
    default_cluster = clusters[default_cluster_idx]["name"]

    # Select default device based on chosen cluster
    available_devices = clusters[default_cluster_idx]["devices"]
    default_device = prompt_choice(
        f"Default GPU device for {default_cluster}:",
        available_devices,
        0
    )

    # 4. Literature Management
    print("\n" + "─" * 40)
    print("LITERATURE MANAGEMENT")
    print("─" * 40)

    research_topic = prompt("Research topic (for related-work.md)", "Deep Learning")
    setup_literature = prompt_yn("Create literature/ directory with related-work.md template?", True)

    # 5. Summary
    print("\n" + "=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"""
Project:        {project_name}
Description:    {project_desc}
WandB Project:  {wandb_project}

Clusters:       {', '.join(c['name'] for c in clusters)}
Default:        {default_cluster}
Default Device: {default_device}

Workspace:      {paths['workspace']}
Data Path:      {paths['data']}
NAS:            {', '.join(paths['nas']) if paths['nas'] else 'None'}

Research Topic: {research_topic}
Literature Dir: {'Yes' if setup_literature else 'No'}
""")

    if not prompt_yn("Proceed with this configuration?", True):
        print("Setup cancelled.")
        sys.exit(0)

    # 6. Generate Files
    print("\nGenerating configuration files...")

    # configs/site.yaml
    site_yaml = f"""# Site-specific configuration (gitignored)
# Generated by scripts/setup.py

project_name: "{project_name}"
description: "{project_desc}"
wandb_project: "{wandb_project}"

# Infrastructure
default_cluster: "{default_cluster}"
default_device: "{default_device}"

paths:
  workspace: "{paths['workspace']}"
  data: "{paths['data']}"
  nas: {paths['nas']}

clusters:
"""
    for c in clusters:
        site_yaml += f"""  - name: "{c['name']}"
    partitions: {c['partitions']}
    gpus: "{c['gpus']}"
    devices: {c['devices']}
"""

    Path("configs/site.yaml").write_text(site_yaml)
    print("  ✓ configs/site.yaml")

    # Update .gitignore
    gitignore_path = Path(".gitignore")
    gitignore_entries = ["configs/site.yaml", ".env", "logs/", "outputs/", "__pycache__/", "*.pyc", ".venv/"]

    existing = gitignore_path.read_text() if gitignore_path.exists() else ""
    new_entries = [e for e in gitignore_entries if e not in existing]

    if new_entries:
        with open(gitignore_path, "a") as f:
            f.write("\n# Added by setup.py\n")
            for entry in new_entries:
                f.write(f"{entry}\n")
        print("  ✓ .gitignore (updated)")

    # .env from .env.example
    if not Path(".env").exists() and Path(".env.example").exists():
        Path(".env").write_text(Path(".env.example").read_text())
        print("  ✓ .env (from .env.example)")

    # Update configs/config.yaml
    config_path = Path("configs/config.yaml")
    if config_path.exists():
        config = config_path.read_text()
        config = config.replace('project_name: "dl-research"', f'project_name: "{wandb_project}"')
        config_path.write_text(config)
        print("  ✓ configs/config.yaml (updated project_name)")

    # Update configs/data/default.yaml with correct path
    data_config_path = Path("configs/data/default.yaml")
    if data_config_path.exists():
        data_config = data_config_path.read_text()
        # Replace the data_dir path
        new_data_dir = paths['data'].replace('$USER', '${oc.env:USER}') + "/datasets"
        data_config = data_config.replace(
            'data_dir: "/data/${oc.env:USER}/datasets"',
            f'data_dir: "{new_data_dir}"'
        )
        data_config_path.write_text(data_config)
        print("  ✓ configs/data/default.yaml (updated paths)")

    # Literature directory
    if setup_literature:
        lit_dir = Path("literature")
        lit_dir.mkdir(exist_ok=True)

        related_work = f"""# {research_topic} - Related Work

Comprehensive survey of related work. Not all will go in paper - for reference.

**Last updated:** (date)

---

## 1. Core Methods

| Method | Year | Venue | Key Idea | Notes |
|--------|------|-------|----------|-------|
| Example | 2024 | NeurIPS | Description | Link |

### References
- [Paper Name (arXiv:XXXX.XXXXX)](https://arxiv.org/abs/XXXX.XXXXX)

---

## 2. Benchmarks & Datasets

| Dataset | Type | Samples | Classes | SOTA | Notes |
|---------|------|---------|---------|------|-------|
| Example | Classification | 10,000 | 10 | 95% | Standard benchmark |

---

## 3. Our Positioning

### What makes this work different
1. vs Method A: ...
2. vs Method B: ...

### Claims to validate
| Claim | Evidence | Comparison |
|-------|----------|------------|
| Better X | EXPXXX | vs baseline |

---

## 4. Papers to Cite

**Must cite** (directly comparable):
- Paper A (Author 2024) - why

**Should cite** (context):
- Paper B (Author 2023) - why

---

## References (Full List)

### Category 1
- https://arxiv.org/abs/XXXX.XXXXX

### Category 2
- https://arxiv.org/abs/XXXX.XXXXX
"""
        (lit_dir / "related-work.md").write_text(related_work)
        print("  ✓ literature/related-work.md")

    # 7. Done
    print("\n" + "=" * 60)
    print("  Setup complete!")
    print("=" * 60)
    print(f"""
Next steps:
  1. Add your WandB API key to .env
  2. Verify baseline: uv run python3 src/train.py experiment=EXP001 trainer.accelerator=cpu trainer.fast_dev_run=true
  3. Create first experiment: ./scripts/create_experiment.sh EXP002 EXP001 "description"
  4. Start documenting related work: literature/related-work.md
""")


if __name__ == "__main__":
    main()
