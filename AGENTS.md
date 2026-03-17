# AGENTS.md

> For AI coding agents: read this file on every session.

This is the canonical research template for LAIT Lab, optimized for AI coding agents.

## Session Start Checklist

1. Read `memory/NOW.md`.
2. Read `memory/DECISIONS.md`.
3. Read `state/tasks.yaml`.
4. Check `configs/site.yaml`. If missing, this is the first session, so read `ONBOARDING.md`.

## Memory System

Sessions can end abruptly. Never wait for the end of the session to update state.

`memory/` is the human-readable handoff layer:

```text
memory/
- NOW.md        # What to do now
- DECISIONS.md  # Append-only decisions
- log.md        # Session history
```

`state/` is the machine-readable handoff layer:

```text
state/
- tasks.yaml            # Open tasks, blockers, owners, next action
- claims.yaml           # Research claims and evidence
- session_capsules/     # One YAML packet per meaningful session
```

### When To Update

| Action | Update |
|--------|--------|
| Submit experiment | `memory/NOW.md`, `state/tasks.yaml` |
| Make decision | `memory/DECISIONS.md`, optionally `state/claims.yaml` |
| Complete experiment | `memory/NOW.md`, `memory/log.md`, `state/claims.yaml`, `state/tasks.yaml` |
| Finish significant work | `memory/log.md`, `state/session_capsules/` |

### NOW.md Structure

```markdown
## Check First
- EXP002 job 12345 on vegi - done?

## Current Focus
- Implementing EXP003

## Next Actions
- If EXP002 done -> log results
- Submit EXP003 when ready
```

Keep it under 200 tokens. Remove completed items.

### DECISIONS.md

Append-only. Never delete. Use the exact format from `templates/DECISION.md`.

## Templates

Never write documentation from scratch. Copy from `templates/` and fill in.

```text
templates/
- EXPERIMENT_README.md
- DECISION.md
- STATUS_HISTORY.md
- SESSION_LOG.md
- PLAN_MODE.md
- STATE_TASK.yaml
- STATE_CLAIM.yaml
- SESSION_CAPSULE.yaml
```

## Environment Setup

### Clone And Configure

```bash
ssh <cluster>  # soda, vegi, or potato
cd /workspace/$USER
git clone <repo-url>
cd <repo-name>
uv sync
uv run python3 scripts/setup.py
```

### Credentials

Before any training:

```bash
python3 scripts/check_creds.py
```

Required secrets in `.env`:
- `WANDB_API_KEY`
- `HF_TOKEN` (optional)

## Infrastructure

### Clusters

| Cluster | Partitions | GPUs | SSH |
|---------|------------|------|-----|
| soda | `R3090`, `A100` | 10x 3090, 8x A100 | `ssh soda` |
| vegi | `R4090`, `A6000`, `RTXPRO6000` | 16x 4090, 8x A6000, 16x Pro6000 (96GB) | `ssh vegi` |
| potato | `A6000` | 12x A6000 | `ssh potato` |

### Storage Hierarchy

| Path | Purpose | Speed |
|------|---------|-------|
| `/workspace/$USER` | Code, configs, venvs | Fast |
| `/data/$USER` | Training data (local) | Fastest |
| `/nas1`, `/nas2` | Archival datasets | Slow |

Copy data from NAS to local scratch before training:

```bash
rsync -av /nas1/public/datasets/my_dataset /data/$USER/
```

### Path Handling

All configs should use `${oc.env:USER}` for user-dependent paths:

```yaml
data_dir: "/data/${oc.env:USER}/datasets"
```

No hardcoded usernames.

### Test Before Submit

Before any `sbatch`, do a quick `srun` test:

```bash
srun -p R3090 --gres=gpu:1 --mem=16G --cpus-per-task=4 python3 src/train.py experiment=EXPXXX trainer.fast_dev_run=true
```

## Baseline Experiment

The template includes a working CIFAR-10 baseline:

```bash
uv run python3 src/train.py experiment=EXP001 trainer.accelerator=cpu trainer.fast_dev_run=true
python3 scripts/submit.py --experiment EXP001 --device "1x3090" --cluster soda
```

Expected result: about 85% accuracy in 50 epochs.

## Research Loop

```text
Understand Context -> Design Experiment -> Document Hypothesis -> Run -> Log Results
```

### 1. Understand Context

Before any experiments, understand:
- the problem,
- relevant papers,
- the baseline,
- what has already been tried.

### 2. Plan Mode

Before creating any experiment, enter Plan Mode.

Copy `templates/PLAN_MODE.md`, fill it in, and wait for confirmation.

### 3. Document Before Running

Before running, the experiment README must include:
- hypothesis,
- method,
- success criteria.

### 4. Create Experiment

```bash
./scripts/create_experiment.sh EXP002 EXP001 "Brief description"
```

Creates:
- `src/experiments/EXP002/model.py`
- `configs/experiment/EXP002.yaml`
- `experiments/EXP002/README.md`

### 5. Implement And Validate

1. Edit `src/experiments/EXPXXX/model.py`.
2. Edit `configs/experiment/EXPXXX.yaml`.
3. Run `python3 scripts/validate.py EXPXXX`.

### 6. Submit

```bash
python3 scripts/check_servers.py
git add -A && git commit -m "EXP002: description" && git push

ssh vegi
cd /workspace/$USER/<repo>
git pull
uv sync
python3 scripts/submit.py --experiment EXP002 --device "4x3090" --cluster soda
```

### 7. Log Results

After an experiment completes:

1. Update `experiments/EXPXXX/README.md`.
2. Update `STATUS.md`.
3. Update `state/claims.yaml`, `state/tasks.yaml`, and `state/session_capsules/`.
4. Append to `memory/log.md`.
5. Commit the result.

## Code Style

### Model Structure

```python
from src.core.base_model import BaseModel
import torch.nn as nn

class Model(BaseModel):
    def __init__(self, hidden_dim: int = 256, **kwargs):
        super().__init__(**kwargs)
        self.net = nn.Sequential(...)
```

### Config Structure

```yaml
# configs/experiment/EXPXXX.yaml
# @package _global_
defaults:
  - override /model: default

experiment_name: "EXPXXX"
model:
  _target_: src.experiments.EXPXXX.model.Model
  hidden_dim: 512
```

### Rules

- Keep hyperparameters in YAML.
- Inherit from `BaseModel` and `BaseDataModule`.
- Document the hypothesis before running.
- Update `STATUS.md` and state ledgers after significant progress.
