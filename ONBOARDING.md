# Onboarding Guide

> **For AI Agents**: Read this file ONLY on first setup. After onboarding is complete, you don't need to read it again.

This guide walks through initial project setup with your user.

## 1. Cluster Selection

Ask the user:
- **Which cluster(s) will you use?** (soda, vegi, potato)
- **Will you need multiple clusters?** (e.g., A100s on soda for large models, 4090s on vegi for quick iterations)

### Cluster Reference

| Cluster | Best For | GPUs |
|---------|----------|------|
| soda | Large models, A100 workloads | 10x 3090, 8x A100 |
| vegi | General purpose, high throughput | 16x 4090, 8x A6000, 16x Pro6000 (96GB) |
| potato | A6000 workloads | 12x A6000 |

### Data Sync Strategy

If using **one cluster**: Data stays in `/data/$USER/` on that cluster.

If using **multiple clusters**: Decide sync strategy:
- **Option A**: Keep data on one cluster, submit jobs only there
- **Option B**: Sync data to all clusters you'll use:
  ```bash
  # Example: sync from vegi to soda
  rsync -avz vegi:/data/$USER/datasets/ soda:/data/$USER/datasets/
  ```

## 2. Dataset Discussion

Ask the user:
- **What dataset(s) will you use?**
- **How big is it?**
- **Where is it currently?** (NAS, local, needs download)

### Data Placement Rules

| Size | Location | Config |
|------|----------|--------|
| Small (<1GB) | Project folder `./data/` | `data_dir: ./data` |
| Large (>1GB) | Cluster storage `/data/$USER/` | `data_dir: /data/${oc.env:USER}/datasets` |
| On NAS | **Copy to cluster first** | Never train from NAS |

### Moving Data

```bash
# From NAS to cluster
rsync -av /nas1/datasets/my_dataset /data/$USER/

# Download to cluster (e.g., HuggingFace)
ssh vegi
cd /data/$USER
huggingface-cli download <dataset>
```

## 3. Project Configuration

After discussion, create these files:

### `configs/site.yaml`
```yaml
project_name: "<user's project name>"
wandb_project: "<same or different>"

default_cluster: "<primary cluster>"  # vegi, soda, or potato
default_device: "<preferred GPU, e.g., 1x4090, 4x3090>"

paths:
  workspace: "/workspace/$USER"
  data: "/data/$USER"  # or ./data for small datasets
```

### Update `configs/data/default.yaml` if needed
```yaml
data_dir: "/data/${oc.env:USER}/datasets"  # Large datasets
# or
data_dir: "./data"  # Small datasets
```

### Update `.gitignore` (append if not present)
```
configs/site.yaml
.env
```

## 4. Credentials

Remind user to set up `.env`:
```bash
cp .env.example .env
# Edit and add WANDB_API_KEY
```

Verify with:
```bash
uv run python3 scripts/check_creds.py
```

## 5. Verify Setup

Run baseline to confirm everything works:
```bash
uv run python3 src/train.py experiment=EXP001 trainer.fast_dev_run=true
```

## 6. Mark Onboarding Complete

After successful setup, tell the user:
> "Setup complete! I won't need to ask these questions again. Ready to create your first experiment."

---

## Quick Reference for Agent

**Questions to ask:**
1. Which cluster(s)?
2. What dataset? How big? Where is it?
3. Project name for WandB?

**Files to create:**
- `configs/site.yaml` - cluster/path config
- `.env` - credentials (user fills in)

**Verify:**
- `uv run python3 scripts/check_creds.py`
- `uv run python3 src/train.py experiment=EXP001 trainer.fast_dev_run=true`
