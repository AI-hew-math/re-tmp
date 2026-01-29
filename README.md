# Deep Learning Research Template

Standardized PyTorch Lightning template for LAIT Lab experiments. Designed for reproducibility and **AI coding agent compatibility**.

## Quick Start

```bash
# 1. Fork or clone this template
git clone <repo-url> my-project
cd my-project

# 2. Install dependencies
uv sync

# 3. Run interactive setup
uv run python3 scripts/setup.py

# 4. Verify everything works
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
| `literature/related-work.md` | Paper survey and references |

## Features

- **Hydra configs** - All hyperparameters in YAML, not code
- **Experiment lineage** - Parent-child tracking in `STATUS.md`
- **Scaffolding** - `./scripts/create_experiment.sh` auto-generates structure
- **SLURM integration** - Smart submission via `scripts/submit.py`
- **WandB logging** - Automatic if `WANDB_API_KEY` is set
- **Literature tracking** - `literature/related-work.md` for paper management

## Structure

```
├── AGENTS.md           # Agent instructions (read this!)
├── STATUS.md           # Experiment graph
├── src/
│   ├── core/           # Base classes (don't modify)
│   └── experiments/    # Your experiment implementations
├── configs/            # Hydra configurations
├── experiments/        # Documentation per experiment
├── literature/         # Related work and paper notes
└── scripts/            # Automation tools
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
| `scripts/check_servers.py` | Check GPU availability |
| `scripts/check_creds.py` | Verify credentials are set |

---
**Maintained by:** Ganghyun Kim (Kyle Kim)
