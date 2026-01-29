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

Literature is **integrated** with experiments, not a separate concern.

### Structure
```
literature/
├── papers.yaml        # Paper database (metadata + repo links)
├── papers/            # Detailed notes for important papers
│   ├── .template.md   # Template for paper notes
│   └── <key>.md       # Deep-dive: method, code snippets, relevance
├── related-work.md    # Survey narrative (created by setup.py)
└── index.md           # Auto-generated reverse index
```

### Adding a Paper (Agent Workflow)

When user shares an arxiv link or asks to add a paper:

**Step 1: Fetch metadata**
```bash
# Auto-fetch from arxiv
uv run python scripts/fetch_paper.py 1706.03762 --key transformer --create --full
```

This will:
- Fetch title, authors, abstract from arxiv API
- Try to download full tex source
- Output YAML to paste into `papers.yaml`
- Create `papers/<key>.md` with template + source

Then update `papers.yaml`:
```yaml
transformer:
  title: "Attention Is All You Need"
  authors: "Vaswani et al."
  year: 2017
  venue: NeurIPS
  arxiv: "1706.03762"
  repo: "https://github.com/tensorflow/tensor2tensor"  # Find official repo
  tags: [attention, architecture]
  notes: "Self-attention mechanism"
  details: papers/transformer.md
```

**Step 2: (For important papers) Create detailed notes**
```bash
cp literature/papers/.template.md literature/papers/<key>.md
```

When reading the paper, fill in:
- **Contextualized summary** - Not generic abstract. Why this paper matters *for this project*
- **Key contributions** - What's novel
- **Method/architecture** - How it works, details needed to implement
- **Code worth borrowing** - Actual snippets to adapt
- **Relevance** - Specific experiments this enables or informs

**Step 2b: Save full paper content**

Fetch full text (arxiv tex or PDF text) and paste into the collapsible section at bottom of notes.
This preserves the source for future reference without cluttering the summary.

```markdown
<details>
<summary>📄 Full Paper Content</summary>
[FULL TEX / TEXT HERE]
</details>
```

**Step 3: Cite in experiments**

In `experiments/EXPXXX/README.md`:
```markdown
## References
- [@transformer] - Using self-attention for feature extraction
```

**Step 4: Regenerate index**
```bash
python scripts/lit_index.py
```

### Quick Add vs Deep Add

| Scenario | Action |
|----------|--------|
| Background reference | Add to `papers.yaml` only |
| Building on this paper | Add to yaml + create `papers/<key>.md` |
| Implementing their method | Full notes with code snippets |

### Validation
```bash
python scripts/lit_index.py --check
```
Fails if experiments cite papers not in database.
