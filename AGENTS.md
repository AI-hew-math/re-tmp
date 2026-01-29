# AGENTS.md

> **For AI Coding Agents**: This file contains your operating instructions for this project.
> Read this file completely before making any changes to the codebase.
> Follow the SOP (Standard Operating Procedure) strictly to maintain research integrity.

This is the canonical research template for LAIT Lab, optimized for AI coding agents.

## First-Time Setup (Onboarding)

After cloning, run the setup script to configure for your environment:
```bash
uv run python3 scripts/setup.py
```

This interactively configures:
- **Project name** - WandB project, experiment naming
- **Clusters** - Available SLURM clusters (or use LAIT defaults)
- **Paths** - Workspace, data, NAS locations
- **Preferences** - Default cluster, GPU device
- **Literature** - Creates `literature/related-work.md` template

Generated files:
- `configs/site.yaml` - Site-specific config (gitignored)
- `.env` - Credentials (from `.env.example`)
- `literature/related-work.md` - Paper survey template

## Environment Setup

### Clone & Configure
```bash
# ALWAYS place code in /workspace for persistence
ssh <cluster>  # soda, vegi, or potato
cd /workspace/$USER
git clone <repo-url>
cd <repo-name>
uv sync
```

### Credentials
Before any training, verify credentials are configured:
```bash
python3 scripts/check_creds.py
```

Required secrets in `.env`:
- `WANDB_API_KEY` - Weights & Biases logging
- `HF_TOKEN` - HuggingFace model access (optional)

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
| `/data/$USER` | Training data (LOCAL) | Fastest |
| `/nas1`, `/nas2` | Archival datasets | Slow |

**CRITICAL**: Copy data from NAS to local scratch before training:
```bash
rsync -av /nas1/public/datasets/my_dataset /data/$USER/
```

### Path Handling
All configs use `${oc.env:USER}` for automatic user-based paths:
```yaml
data_dir: "/data/${oc.env:USER}/datasets"  # Resolves to /data/gankim/datasets
```
No hardcoded usernames. Paths resolve automatically per user.

## Baseline Experiment (EXP001)

The template includes a working CIFAR-10 baseline to verify the pipeline:
```bash
# Quick validation (CPU, 1 batch)
uv run python3 src/train.py experiment=EXP001 trainer.accelerator=cpu trainer.fast_dev_run=true

# Full training
python3 scripts/submit.py --experiment EXP001 --device "1x3090" --cluster soda
```
CIFAR-10 downloads automatically. Expected: ~85% accuracy in 50 epochs.

## Workflow (SOP)

### Creating a New Experiment

**NEVER** manually create experiment files. Use the scaffolding script:
```bash
./scripts/create_experiment.sh EXP002 EXP001 "Brief description of changes"
```

This creates:
- `src/experiments/EXP002/model.py` - Implementation
- `configs/experiment/EXP002.yaml` - Hyperparameters
- `experiments/EXP002/README.md` - Documentation

### Implementing Changes

1. **Edit model**: `src/experiments/EXPXXX/model.py`
   - MUST inherit from `src.core.base_model.BaseModel`
   - Override `__init__` to define architecture
   - Override step methods only if necessary

2. **Edit config**: `configs/experiment/EXPXXX.yaml`
   - **NEVER** hardcode hyperparameters in Python
   - Use Hydra config overrides

### Validation

Before committing, verify experiment structure:
```bash
python3 scripts/validate.py EXPXXX
```

### Submission

```bash
# 1. Check GPU availability
python3 scripts/check_servers.py

# 2. Commit and push
git add -A && git commit -m "EXP002: description" && git push

# 3. On cluster: pull and submit
ssh vegi
cd /workspace/$USER/<repo>
git pull && uv sync
python3 scripts/submit.py --experiment EXP002 --device "4x3090" --cluster soda

# Interactive debug shell
python3 scripts/submit.py --experiment EXP002 --device "1x3090" --interactive
```

## Code Style

### Model Structure
```python
from src.core.base_model import BaseModel
import torch.nn as nn

class Model(BaseModel):
    def __init__(self, hidden_dim: int = 256, **kwargs):
        super().__init__(**kwargs)
        self.net = nn.Sequential(...)  # Your architecture
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
- All hyperparameters in YAML configs, not Python
- Inherit from BaseModel/BaseDataModule
- Document hypothesis in `experiments/EXPXXX/README.md`
- Update `STATUS.md` experiment graph after creation

## Testing

### Local Validation
```bash
# Validate experiment structure
python3 scripts/validate.py EXPXXX

# Dry run (CPU, 1 batch)
uv run python3 src/train.py experiment=EXPXXX trainer.accelerator=cpu trainer.fast_dev_run=true
```

### Monitoring Running Jobs
```bash
# SLURM logs
tail -f logs/slurm/EXPXXX_*.log

# WandB dashboard (primary metrics)
# Check project: dl-research
```

## Commit Guidelines

Format: `EXPXXX: brief description`

Examples:
- `EXP002: add attention mechanism to encoder`
- `EXP003: ablate learning rate schedule`
- `fix: correct data path in config`

## Directory Structure

```
├── src/
│   ├── core/           # IMMUTABLE base classes
│   │   ├── base_model.py
│   │   └── base_data.py
│   ├── experiments/    # Experiment implementations
│   │   └── EXPXXX/
│   │       └── model.py
│   └── train.py        # Main training entry
├── configs/
│   ├── config.yaml     # Root config
│   ├── experiment/     # Per-experiment overrides
│   ├── model/
│   ├── data/
│   └── trainer/
├── experiments/        # Documentation & results
│   └── EXPXXX/
│       └── README.md
├── scripts/
│   ├── create_experiment.sh
│   ├── submit.py
│   ├── validate.py
│   └── check_servers.py
├── STATUS.md           # Experiment lineage graph
└── outputs/            # Checkpoints & artifacts
```

## Retrieving Results

Sync outputs back to local machine:
```bash
rsync -avz vegi:/workspace/$USER/<repo>/outputs/ ./outputs/
```

## Literature Management

### Structure
```
literature/
└── related-work.md    # Main survey document
```

### related-work.md Format
Organize papers by category with tables:
```markdown
## 1. Core Methods
| Method | Year | Venue | Key Idea | Notes |
|--------|------|-------|----------|-------|
| Paper A | 2024 | NeurIPS | Description | Link |

### References
- [Paper A (arXiv:XXXX.XXXXX)](https://arxiv.org/abs/XXXX.XXXXX)
```

### Linking Papers to Experiments
In `experiments/EXPXXX/README.md`, include:
```markdown
## Paper Use
Demonstrates X (cite: Paper A, Paper B).
Answers reviewer question about Y.
```

### Adding Papers
When you find a relevant paper:
1. Add entry to appropriate section in `literature/related-work.md`
2. Include: Method name, Year, Venue, Key idea, arXiv link
3. Note relevance to your work in "Our Positioning" section
