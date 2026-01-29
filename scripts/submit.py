import argparse
import os
import subprocess
from datetime import datetime

def submit():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=str, required=True)
    parser.add_argument("--device", type=str, default="1x3090")
    parser.add_argument("--cluster", type=str, default="soda")
    args = parser.parse_args()

    # Hardware Mapping (Simplistic example)
    gpu_map = {
        "1x3090": ("R3090", 1),
        "4x3090": ("R3090", 4),
        "1x4090": ("R4090", 1),
        "8x4090": ("R4090", 8),
        "1xa100": ("A100", 1),
    }
    
    partition, gres = gpu_map.get(args.device.lower(), ("R3090", 1))

    job_name = args.experiment
    log_file = f"logs/slurm/{job_name}_%j.log"
    os.makedirs("logs/slurm", exist_ok=True)

    slurm_script = f"""#!/bin/bash
#SBATCH --job-name={job_name}
#SBATCH --partition={partition}
#SBATCH --gres=gpu:{gres}
#SBATCH --ntasks=1
#SBATCH --cpus-per-task={gres * 4}
#SBATCH --mem={gres * 16}G
#SBATCH --output={log_file}

# Load environment
source .env
uv run python3 src/train.py experiment={args.experiment} trainer.devices={gres}
"""

    script_path = f".tmp_submit_{args.experiment}.slurm"
    with open(script_path, "w") as f:
        f.write(slurm_script)

    print(f"Submitting {args.experiment} to {args.cluster}...")
    res = subprocess.run(["ssh", args.cluster, f"sbatch"], input=slurm_script, text=True, capture_output=True)
    
    if res.returncode == 0:
        print(res.stdout.strip())
    else:
        print("Submission Failed:")
        print(res.stderr)

    os.remove(script_path)

if __name__ == "__main__":
    submit()
