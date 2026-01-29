# Deep Learning Research Template

Standardized PyTorch Lightning template for LAIT Lab experiments. Designed for reproducibility and **AI coding agent compatibility**.

## Prerequisites

- **Python 3.11+** (check: `python3 --version`)
- **uv** - Fast Python package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
  ```bash
  # macOS/Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **WandB account** (optional but recommended) - [wandb.ai](https://wandb.ai)

## Quick Start

```bash
# 1. Fork or clone this template
git clone <repo-url> my-project
cd my-project

# 2. Install dependencies
uv sync

# 3. Run interactive setup (configures clusters, paths, WandB)
uv run python3 scripts/setup.py

# 4. Set up credentials
cp .env.example .env
# Edit .env and add your WANDB_API_KEY

# 5. Verify everything works
uv run python3 src/train.py experiment=EXP001 trainer.accelerator=cpu trainer.fast_dev_run=true
```

## Using with AI Coding Agents

This template is optimized for AI agents (Claude Code, Cursor, Copilot, Codex, etc.).

### Setup

1. **Fork/Clone** this template to start a new research project
2. **Run setup**: `uv run python3 scripts/setup.py` (configures paths, clusters, etc.)
3. **Open your AI agent** in the project directory:
   ```bash
   # Claude Code
   cd my-project && claude

   # Cursor
   cursor my-project

   # VS Code + Copilot
   code my-project
   ```

### How Agents Use This Template

When an agent opens this project, it reads `AGENTS.md` which contains:
- Infrastructure details (clusters, storage paths)
- Standard Operating Procedure (SOP) for experiments
- Code style rules and validation commands
- Literature management guidelines

### Example Agent Interactions

**Creating a new experiment:**
```
You: "Create an experiment that adds attention to the baseline model"

Agent: [Reads AGENTS.md, runs create_experiment.sh, edits model.py and config]
```

**Running experiments:**
```
You: "Check available GPUs and submit EXP002 to vegi"

Agent: [Runs check_servers.py, then submit.py with correct flags]
```

**Literature review:**
```
You: "Add this paper to related work: arxiv.org/abs/2401.12345"

Agent: [Updates literature/related-work.md with paper details]
```

### Key Files for Agents

| File | Purpose |
|------|---------|
| `AGENTS.md` | **Primary instructions** - agents read this first |
| `STATUS.md` | Current experiment graph and active thread |
| `literature/papers.yaml` | Paper database (metadata, repos, links) |
| `literature/papers/<key>.md` | Detailed paper notes with full content |

## Features

- **Hydra configs** - All hyperparameters in YAML, not code
- **Experiment lineage** - Parent-child tracking in `STATUS.md`
- **Scaffolding** - `./scripts/create_experiment.sh` auto-generates structure
- **SLURM integration** - Smart submission via `scripts/submit.py`
- **WandB logging** - Automatic if `WANDB_API_KEY` is set
- **Literature tracking** - `papers.yaml` database + detailed notes with full paper content
- **Arxiv integration** - Auto-fetch paper metadata and tex source

## Structure

```
├── AGENTS.md              # Agent instructions (read this!)
├── STATUS.md              # Experiment graph + history
├── src/
│   ├── core/              # Base classes (don't modify)
│   │   ├── base_model.py  # Inherit for all models
│   │   └── base_data.py   # Inherit for all datasets
│   ├── experiments/       # Your experiment implementations
│   │   └── EXP001/        # One folder per experiment
│   └── train.py           # Main training entry point
├── configs/
│   ├── config.yaml        # Root config
│   ├── experiment/        # Per-experiment overrides
│   ├── model/             # Model configs
│   ├── data/              # Dataset configs
│   └── trainer/           # Trainer configs
├── experiments/           # Documentation per experiment
│   └── EXP001/README.md   # Hypothesis, method, results
├── literature/
│   ├── papers.yaml        # Paper database
│   ├── papers/            # Detailed notes per paper
│   └── index.md           # Auto-generated citation index
└── scripts/               # Automation tools
```

## For Humans (Without AI Agent)

1. Create experiment: `./scripts/create_experiment.sh EXP002 EXP001 "description"`
2. Implement: `src/experiments/EXP002/model.py`
3. Configure: `configs/experiment/EXP002.yaml`
4. Validate: `python3 scripts/validate.py EXP002`
5. Submit: `python3 scripts/submit.py -e EXP002 -d "4x3090" -c soda`

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/setup.py` | Interactive project configuration |
| `scripts/create_experiment.sh` | Scaffold new experiment |
| `scripts/validate.py` | Verify experiment structure |
| `scripts/submit.py` | Submit SLURM jobs |
| `scripts/check_servers.py` | Check GPU availability across clusters |
| `scripts/check_creds.py` | Verify credentials are set |
| `scripts/fetch_paper.py` | Fetch arxiv paper metadata + tex source |
| `scripts/lit_index.py` | Generate literature citation index |

## Troubleshooting

**`uv: command not found`**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal
```

**`ModuleNotFoundError` when running scripts**
```bash
uv sync  # Ensure dependencies are installed
uv run python3 <script>  # Use uv run, not python3 directly
```

**Can't connect to cluster**
```bash
# Verify SSH config
ssh soda  # Should connect without password prompt
# If not, set up SSH keys: ssh-copy-id soda
```

**WandB not logging**
```bash
# Check credentials
uv run python3 scripts/check_creds.py
# Ensure .env has WANDB_API_KEY
```

**SLURM job fails immediately**
```bash
# Check the log
cat logs/slurm/EXPXXX_*.log
# Common issues: wrong partition, missing data, OOM
```

---
**Maintained by:** LAIT Lab
