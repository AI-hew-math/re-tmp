import subprocess
import sys
import os

CLUSTERS = ["soda", "vegi", "potato"]

def check_cluster(name):
    print(f"--- Cluster: {name} ---")
    try:
        # Check node availability
        res = subprocess.run(
            ["ssh", name, "sinfo --format='%n %G %e %t'"], 
            capture_output=True, text=True, timeout=5
        )
        if res.returncode == 0:
            print(res.stdout.strip())
        else:
            print(f"Error accessing {name}")
    except Exception as e:
        print(f"Timeout or Error connecting to {name}")

if __name__ == "__main__":
    for c in CLUSTERS:
        check_cluster(c)
