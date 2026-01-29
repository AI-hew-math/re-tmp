---
type: project
name: Deep Learning Research Template
status: active
tags: [template, deep-learning, productivity, automation, agent-optimized]
started: 2026-01-29
completed: null
goal: "Create a standardized, robust deep learning project template specifically designed for Agents to perform consistent, verifiable experiments."
codebase: null
---

## ::resume
> **Updated:** 2026-01-29
> **Thread:** Documentation and infrastructure integration.
> **Next:** Final verification of smart submission logic.
> **Blocker:** None
> **Recent:** Wrote comprehensive README.md, implemented check_creds.py, and documented storage hierarchy.

# Deep Learning Research Template

## Infrastructure

### Clusters
- **soda**: 10x 3090, 8x A100.
- **vegi**: 16x 4090, 8x A6000, 16x Pro6000 (96GB Blackwell).
- **potato**: 12x A6000.

### Storage
- **Home**: `/workspace/gankim`
- **Data (Local)**: `/data/gankim` (Scratch space per login node)
- **NAS (Shared)**: `/nas1`, `/nas2`

## Agent Protocol

**ATTENTION AGENTS:** Follow these rules strictly.

### 1. How to Create a New Experiment
Do not manually create files. Use the script:
```bash
./scripts/create_experiment.sh NEW_EXP_ID PARENT_EXP_ID "Description"
```

### 2. How to Modify Logic
- **Global Logic:** Edit `src/core/`. (Affects EVERYONE).
- **Experiment Logic:**
    1. Create/edit model in `src/experiments/EXPxxx/model.py`.
    2. Ensure it inherits from `src.core.base_model.BaseModel`.

### 3. How to Configure
- **NEVER** hardcode hyperparameters in Python.
- **ALWAYS** use `configs/experiment/EXPxxx.yaml`.

### 4. How to Sync & Run
1. Develop locally.
2. `git push`.
3. SSH to cluster (`ssh vegi`).
4. `git pull && uv sync`.
5. Run using the smart submitter:
```bash
python scripts/submit.py experiment=EXPxxx device="4x3090"
```

## Directory Map
- `src/core/`: Immutable base classes.
- `src/experiments/`: Custom experiment logic.
- `configs/`: Hydra configurations.
- `experiments/`: Documentation and Results.
- `scripts/`: Automation for scaffolding and SLURM.

## References

- [[dl-template-plan]]
- [[slurm-experiments]]
- [[server-specs]]
