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
> **Thread:** Initial project setup following the approved plan.
> **Next:** Implement src/core base classes and config schema.
> **Blocker:** None
> **Recent:** Created folder structure, initialized uv, and wrote STATUS.md.

# Deep Learning Research Template

This project is a canonical deep learning research repository designed for the LAIT Lab environment and optimized for **Coding Agents**.

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
