# AGENTS.md

> **For AI Coding Agents**: This file contains your operating instructions for this project.
> Read this file completely before making any changes to the codebase.

This is the canonical research template for LAIT Lab, optimized for AI coding agents.

## First-Time Setup

If `configs/site.yaml` doesn't exist, this is a fresh project. Read `ONBOARDING.md` and walk the user through setup (cluster selection, data discussion, credentials).

After onboarding, you won't need to read `ONBOARDING.md` again.

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

## Research Loop

The core workflow follows the scientific method:

```
Understand Context → Design Experiment → Document Hypothesis → Run → Log Results
```

### 1. Understand Context (First Session)

Before any experiments, understand the research:
- What problem is the user solving?
- What papers are relevant? (Add to `literature/papers.yaml`)
- What has been tried? What's the baseline?

**Ask questions until you fully understand the research direction.**

### 2. Plan Mode (REQUIRED Before Any Experiment)

Before creating or implementing any experiment, enter **Plan Mode**. Output your thinking explicitly:

```
📋 PLAN MODE

**Research Question**: What are we trying to learn?

**Proposed Experiment**: EXP00X - [name]

**Why This Experiment**:
- What gap does this fill?
- Why now? (What do we know that makes this the logical next step?)

**Hypothesis**: 
- Expected outcome and reasoning

**Alternatives Considered**:
- Option A: ... (why not)
- Option B: ... (why not)
- Chosen: ... (why yes)

**Dependencies**:
- Papers: [@key1], [@key2]
- Builds on: EXP00Y
- Data needed: ...

**Risks**:
- What could go wrong?
- How will we know if it failed vs just needs tuning?

Ready to proceed? [Wait for user confirmation]
```

**Do NOT skip Plan Mode.** Even if user says "just do X", output the plan first and confirm.

### 3. Document BEFORE Running

**CRITICAL**: Before running, the experiment README must have:
- **Hypothesis**: What do you expect to happen and why?
- **Method**: What specifically are you changing?
- **Success criteria**: How will you know if it worked?

This is non-negotiable. No undocumented experiments.

### 4. Create Experiment

```bash
./scripts/create_experiment.sh EXP002 EXP001 "Brief description"
```

Creates:
- `src/experiments/EXP002/model.py` - Implementation (copied from parent)
- `configs/experiment/EXP002.yaml` - Hyperparameters
- `experiments/EXP002/README.md` - Documentation

### 5. Implement & Validate

1. **Edit model**: `src/experiments/EXPXXX/model.py`
2. **Edit config**: `configs/experiment/EXPXXX.yaml`
3. **Validate**: `python3 scripts/validate.py EXPXXX`

### 6. Submit

```bash
python3 scripts/check_servers.py  # Check GPU availability
git add -A && git commit -m "EXP002: description" && git push

# On cluster
ssh vegi && cd /workspace/$USER/<repo>
git pull && uv sync
python3 scripts/submit.py --experiment EXP002 --device "4x3090" --cluster soda
```

### 7. Log Results (CRITICAL)

After experiment completes:

1. **Update experiment README** with actual results:
   ```markdown
   ## Results
   - Accuracy: X% (expected Y%)
   - Training time: Z hours
   - Observations: ...
   
   ## Conclusion
   Hypothesis [confirmed/rejected]. Next: ...
   ```

2. **Update STATUS.md**:
   - Change status: `planned` → `running` → `done`
   - Add to History section

3. **Commit**: `git commit -m "EXP002: results - [brief finding]"`

### Experiment Lifecycle

| Phase | README Status | STATUS.md |
|-------|---------------|-----------|
| Designed | Hypothesis filled | `planned` |
| Running | - | `running` |
| Complete | Results filled | `done` |
| Failed | Results + why | `failed` |

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

### Validation
```bash
# Validate experiment structure
python3 scripts/validate.py EXPXXX

# Dry run (fast_dev_run = 1 batch only)
uv run python3 src/train.py experiment=EXPXXX trainer.fast_dev_run=true
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

**Step 1: Fetch paper and create notes**
```bash
uv run python scripts/fetch_paper.py <arxiv-id-or-url> --key <short-key> --create --full
```

Example:
```bash
uv run python scripts/fetch_paper.py 1706.03762 --key transformer --create --full
```

This automatically:
- Fetches title, authors, abstract from arxiv API
- Downloads full tex source
- Outputs YAML to paste into `papers.yaml`
- Creates `papers/<key>.md` with template pre-filled + full source embedded

**Step 2: Update papers.yaml**

Copy the YAML output from the script into `literature/papers.yaml`:
```yaml
transformer:
  title: "Attention Is All You Need"
  authors: "Vaswani et al."
  year: 2017
  venue: NeurIPS  # Update from "arXiv" once published
  arxiv: "1706.03762"
  repo: "https://github.com/tensorflow/tensor2tensor"  # Search GitHub for official repo
  tags: [attention, architecture]  # Use: architecture, training, data, vision, nlp, efficiency
  notes: "Self-attention replaces recurrence"
  details: papers/transformer.md
```

**Step 3: Write contextualized summary**

Open `literature/papers/<key>.md` and fill in:
- **Summary (In Context)** - Why this paper matters *for this project*, not generic abstract
- **Code to Borrow** - Actual snippets worth adapting
- **Relevance to Our Experiments** - Which experiments could use this

The full paper tex is already saved in the collapsible section at the bottom.

**Step 4: Commit**
```bash
git add literature/ && git commit -m "lit: add <paper-name>"
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
