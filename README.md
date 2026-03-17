# Deep Learning Research Template

Standardized PyTorch Lightning template for LAIT Lab experiments. Designed for reproducibility and AI coding agent compatibility.

This repository is organized as a small research OS:
- `memory/` is the short human handoff layer.
- `state/` is the machine-readable handoff layer for agents.
- `experiments/` and `literature/` are the durable research record.

## Prerequisites

- Python 3.11+ (`python3 --version`)
- `uv` ([install guide](https://docs.astral.sh/uv/getting-started/installation/))
- WandB account (optional but recommended)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Quick Start

```bash
# 1. SSH to cluster and clone
ssh vegi  # or soda, potato
cd /workspace/$USER
git clone <repo-url> my-project
cd my-project

# 2. Install dependencies
uv sync

# 3. Generate local site config
uv run python3 scripts/setup.py

# 4. Open your AI coding agent
claude  # or cursor, code, codex, etc.
# Agent reads AGENTS.md -> ONBOARDING.md and walks you through setup

# 5. Verify baseline works
uv run python3 src/train.py experiment=EXP001 trainer.fast_dev_run=true
```

### Manual Setup

If not using an AI agent, see `ONBOARDING.md` for:
- cluster selection,
- data placement strategy,
- creating `configs/site.yaml`,
- setting up `.env` credentials.

## Using With AI Coding Agents

This template is optimized for Claude Code, Codex, Cursor, Copilot, and similar tools.

### Setup

1. Fork or clone this template.
2. Run `uv run python3 scripts/setup.py` to create `configs/site.yaml`.
3. Open your AI agent in the project directory.

### How Agents Use This Template

When an agent opens this project, it reads `AGENTS.md`, which contains:
- infrastructure details,
- experiment SOP and validation rules,
- literature management rules,
- memory and state update rules.

### Example Agent Interactions

Creating a new experiment:

```text
You: "Create an experiment that adds attention to the baseline model"
Agent: [Reads AGENTS.md, runs create_experiment.sh, edits model.py and config]
```

Running experiments:

```text
You: "Check available GPUs and submit EXP002 to vegi"
Agent: [Runs check_servers.py, then submit.py with correct flags]
```

Literature review:

```text
You: "Add this paper to related work: arxiv.org/abs/2401.12345"
Agent: [Updates literature/related-work.md with paper details]
```

### Key Files For Agents

| File | Purpose |
|------|---------|
| `AGENTS.md` | Primary instructions |
| `STATUS.md` | Experiment graph and active thread |
| `memory/NOW.md` | Short working-memory snapshot |
| `state/tasks.yaml` | Machine-readable task queue |
| `state/claims.yaml` | Machine-readable research claims |
| `literature/papers.yaml` | Paper database |
| `literature/papers/<key>.md` | Detailed paper notes |

## Features

- Hydra configs for hyperparameters
- Experiment lineage in `STATUS.md`
- Scaffolding via `./scripts/create_experiment.sh`
- SLURM submission helpers
- Optional WandB logging
- Literature tracking and arXiv fetch helpers
- Durable agent state via YAML ledgers for tasks, claims, and session capsules

## Structure

```text
AGENTS.md                  # Agent instructions
STATUS.md                  # Experiment graph + history
configs/                   # Hydra config tree + local site config example
experiments/               # Experiment docs and outcomes
literature/                # Paper database and notes
memory/                    # Human-readable session memory
state/                     # Machine-readable task/claim/session ledgers
scripts/                   # Automation and validation tools
src/                       # Training code
templates/                 # Canonical templates for agents
```

## For Humans

1. Create experiment: `./scripts/create_experiment.sh EXP002 EXP001 "description"`
2. Implement: `src/experiments/EXP002/model.py`
3. Configure: `configs/experiment/EXP002.yaml`
4. Validate: `uv run python3 scripts/validate.py EXP002`
5. Submit: `python3 scripts/submit.py -e EXP002 -d "4x3090" -c soda`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/create_experiment.sh` | Scaffold new experiment |
| `scripts/validate.py` | Verify experiment structure |
| `scripts/validate_state.py` | Verify agent state ledgers |
| `scripts/submit.py` | Submit SLURM jobs |
| `scripts/check_servers.py` | Check GPU availability |
| `scripts/check_creds.py` | Verify credentials |
| `scripts/setup.py` | Generate local `configs/site.yaml` |
| `scripts/fetch_paper.py` | Fetch arXiv metadata and tex source |
| `scripts/lit_index.py` | Generate literature citation index |

## Troubleshooting

`uv: command not found`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

`ModuleNotFoundError` when running scripts

```bash
uv sync
uv run python3 <script>
```

`configs/site.yaml` is missing

```bash
uv run python3 scripts/setup.py
```

Import errors for `src.core...`

```bash
uv sync
uv pip install -e .
```

Data path issues

```bash
uv run python3 src/train.py experiment=EXP001 data.data_dir=/path/to/data
```

WandB not logging

```bash
uv run python3 scripts/check_creds.py
```

SLURM job fails immediately

```bash
cat logs/slurm/EXPXXX_*.log
```

---
Maintained by LAIT Lab
