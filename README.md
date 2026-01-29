# Deep Learning Research Template

This is the canonical research template for the LAIT Lab, specifically optimized for **Coding Agents**. It enforces strict inheritance, configuration standards, and infrastructure awareness.

## 1. Infrastructure Guide

### 1.1 Server Inventory
Jobs should be submitted to the following SLURM clusters:

| Cluster | Key Partitions | GPUs | Best For |
|---------|----------------|------|----------|
| **soda** | `R3090`, `A100` | 10x 3090, 8x A100 | General purpose, A100 tasks |
| **vegi** | `R4090`, `A6000`, `RTXPRO6000` | 16x 4090, 8x A6000, 16x Pro6000 (96GB) | Blackwell/Pro6000 tasks, high VRAM |
| **potato**| `A6000` | 12x A6000 | A6000 tasks |

**Access:** SSH via `ssh soda`, `ssh vegi`, or `ssh potato`. (Requires `~/.ssh/config` setup).

### 1.2 Storage Hierarchy
- **Home**: `/workspace/gankim` (Code, config, `uv` virtualenvs).
- **Local Scratch**: `/data/gankim` (High-speed storage). **Training data MUST be here.**
- **Shared**: `/nas1`, `/nas2` (Archival datasets).

### 1.3 Data Preparation (Essential)
Agents must copy data from slow NAS to fast Local Scratch before training:
```bash
# Example: Sync dataset to local scratch
rsync -av /nas1/public/datasets/my_dataset /data/gankim/
```

### 1.4 Credentials

## 2. Deployment & Setup

### 2.1 First-time Setup
1.  **Local**: Develop and commit your code.
2.  **Server**: SSH to a cluster (e.g., `ssh vegi`).
3.  **Clone**: 
    ```bash
    # ALWAYS place code in /workspace for persistence and performance
    cd /workspace/gankim
    git clone <your-repo-url>
    cd <repo-name>
    ```
4.  **Environment**: 
    ```bash
    uv sync
    ```

### 2.2 Credentials
Run the following to ensure the server is ready for training:
```bash
# Check if WANDB_API_KEY and other tokens are set
python3 scripts/check_creds.py
```

## 3. Environment (uv)
We use `uv` for fast, reproducible environment management.

- **Local Setup**: `uv sync`
- **Add Dependency**: `uv add <package>`
- **Run on Server**: `uv run python3 src/train.py ...`

## 3. Agent Protocol (SOP)

Agents **MUST** follow these steps to ensure research integrity:

1.  **Read Context**: Check `STATUS.md` for current experiment graph and this `README.md` for project goals.
2.  **Scaffold**:
    ```bash
    ./scripts/create_experiment.sh EXPXXX PARENT_ID "Description"
    ```
    This creates:
    - `src/experiments/EXPXXX/model.py` (The code)
    - `configs/experiment/EXPXXX.yaml` (The hyperparams)
    - `experiments/EXPXXX/README.md` (The documentation)
3.  **Implement**:
    - Edit `src/experiments/EXPXXX/model.py`.
    - **Rule**: Must inherit from `src.core.base_model.BaseModel`.
4.  **Configure**:
    - Edit `configs/experiment/EXPXXX.yaml`.
    - **Rule**: No hardcoding in Python. Use Hydra overrides.
5.  **Verify**:
    ```bash
    python3 scripts/validate.py EXPXXX
    ```
6.  **Sync**: Commit and `git push`.
7.  **Submit**:
    ```bash
    # Check for free GPUs
    python3 scripts/check_servers.py
    
    # Submit job (automates sbatch)
    python3 scripts/submit.py --experiment EXPXXX --device "4x3090" --cluster soda
    ```

### 8. Monitoring & Results
- **Logs**: If a job fails immediately, check SLURM logs:
  ```bash
  tail -f logs/slurm/*.log
  ```
- **WandB**: Primary training metrics.
- **Artifacts**: Checkpoints save to `outputs/EXPXXX/...`.
- **Retrieval**: Sync results back to local machine:
  ```bash
  rsync -avz <cluster>:~/workspace/gankim/dl-template/outputs/ ./outputs/
  ```

## 4. Experiment Tracking
Lineage is tracked in `STATUS.md` via a Mermaid graph. 
Every experiment must declare a `parent` in its `README.md` to maintain the graph.

---
**Maintained by:** Ganghyun Kim (Kyle Kim)
