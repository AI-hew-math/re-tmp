#!/usr/bin/env python3
"""
Smart SLURM job submitter.

Usage:
    python scripts/submit.py --experiment EXP001 --device "4x3090" --cluster soda
    python scripts/submit.py --experiment EXP001 --device "1x3090" --interactive
"""
import argparse
import subprocess
import sys


def get_gpu_config(device: str) -> tuple[str, int]:
    """Map device string to (partition, gpu_count)."""
    gpu_map = {
        # soda
        "1x3090": ("R3090", 1),
        "2x3090": ("R3090", 2),
        "4x3090": ("R3090", 4),
        "1xa100": ("A100", 1),
        "2xa100": ("A100", 2),
        "4xa100": ("A100", 4),
        # vegi
        "1x4090": ("R4090", 1),
        "2x4090": ("R4090", 2),
        "4x4090": ("R4090", 4),
        "8x4090": ("R4090", 8),
        "1xa6000": ("A6000", 1),
        "2xa6000": ("A6000", 2),
        "4xa6000": ("A6000", 4),
        "1xpro6000": ("RTXPRO6000", 1),
        "2xpro6000": ("RTXPRO6000", 2),
        # potato
        "1xa6000-potato": ("A6000", 1),
        "4xa6000-potato": ("A6000", 4),
    }
    return gpu_map.get(device.lower(), ("R3090", 1))


def main():
    parser = argparse.ArgumentParser(description="Submit SLURM jobs")
    parser.add_argument("--experiment", "-e", type=str, required=True, help="Experiment ID (e.g., EXP001)")
    parser.add_argument("--device", "-d", type=str, default="1x3090", help="GPU config (e.g., 4x3090, 1xa100)")
    parser.add_argument("--cluster", "-c", type=str, default="soda", help="Cluster name (soda, vegi, potato)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Print srun command for interactive session")
    parser.add_argument("--dry-run", action="store_true", help="Print sbatch script without submitting")
    args = parser.parse_args()

    partition, num_gpus = get_gpu_config(args.device)
    job_name = args.experiment

    # Interactive mode: just print srun command
    if args.interactive:
        print(f"\n{'='*50}")
        print(f"Interactive session on {args.cluster} ({partition})")
        print(f"{'='*50}")
        print(f"\nssh {args.cluster}")
        print(f"srun -p {partition} --gres=gpu:{num_gpus} --cpus-per-task={num_gpus * 4} --mem={num_gpus * 16}G --pty bash")
        print()
        return

    # Build SLURM script
    slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --gres=gpu:{num_gpus}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={num_gpus * 4}
#SBATCH --mem={num_gpus * 16}G
#SBATCH --output=logs/slurm/{job_name}_%j.log
#SBATCH --error=logs/slurm/{job_name}_%j.log

# Setup
cd $SLURM_SUBMIT_DIR
source .env 2>/dev/null || true
mkdir -p logs/slurm

# Run
CMD="uv run python3 src/train.py experiment={args.experiment} trainer.devices={num_gpus}"
if [ {num_gpus} -gt 1 ]; then
    CMD="$CMD trainer.strategy=ddp"
fi

echo "Running: $CMD"
$CMD
"""

    if args.dry_run:
        print(slurm_script)
        return

    # Submit via SSH using heredoc
    ssh_command = f"""cd /workspace/$USER/$(basename $(pwd)) && \\
mkdir -p logs/slurm && \\
sbatch << 'SLURM_SCRIPT'
{slurm_script}
SLURM_SCRIPT"""

    print(f"Submitting {args.experiment} to {args.cluster} ({partition}, {num_gpus} GPU(s))...")

    result = subprocess.run(
        ["ssh", args.cluster, "bash -s"],
        input=ssh_command,
        text=True,
        capture_output=True
    )

    if result.returncode == 0:
        print(result.stdout.strip())
    else:
        print("Submission failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
