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
    """Map device string to (partition, gpu_count).

    Parses strings like '4x3090', '8xa100', '2xpro6000' dynamically.
    """
    import re

    # GPU type to partition mapping
    gpu_to_partition = {
        "3090": "R3090",
        "a100": "A100",
        "4090": "R4090",
        "a6000": "A6000",
        "pro6000": "RTXPRO6000",
    }

    device = device.lower().strip()

    # Parse format: NxGPU (e.g., "4x3090", "8xa100")
    match = re.match(r"(\d+)x(.+)", device)
    if match:
        count = int(match.group(1))
        gpu_type = match.group(2)
        partition = gpu_to_partition.get(gpu_type)
        if partition:
            return (partition, count)

    # Fallback
    print(f"Warning: Unknown device '{device}', defaulting to R3090 x1")
    return ("R3090", 1)


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
