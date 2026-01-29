#!/bin/bash
# templates/reference_job.slurm
# Reference SLURM script. 
# NOTE: In this repo, 'scripts/submit.py' generates this automatically.
# This file exists for debugging and transparency.

#SBATCH --job-name=EXP_NAME
#SBATCH --partition=R3090       # Partition (Queue)
#SBATCH --gres=gpu:1            # Number of GPUs
#SBATCH --ntasks=1              # Tasks (Processes)
#SBATCH --cpus-per-task=4       # CPU cores per GPU
#SBATCH --mem=32G               # System RAM
#SBATCH --time=48:00:00         # Time Limit (Max 2 days usually)
#SBATCH --output=logs/slurm/%x_%j.log  # Standard Output (%x=job_name, %j=job_id)
#SBATCH --error=logs/slurm/%x_%j.err   # Standard Error

# 1. Environment Setup
source .env
export PYTHONUNBUFFERED=1

# 2. Debug Info
echo "Job ID: $SLURM_JOB_ID"
echo "Node: $SLURMD_NODENAME"
echo "Date: $(date)"
nvidia-smi

# 3. Execution
# Note: trainer.devices must match --gres=gpu count
# Note: trainer.strategy=ddp required if gpus > 1
uv run python3 src/train.py \
    experiment=EXP_NAME \
    trainer.devices=1 \
    trainer.strategy=auto
