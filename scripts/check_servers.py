#!/usr/bin/env python3
"""
Check GPU availability across SLURM clusters.

Usage:
    python scripts/check_servers.py           # Check all clusters
    python scripts/check_servers.py soda      # Check specific cluster
    python scripts/check_servers.py --quick   # Just show available GPUs
"""
import subprocess
import sys
import argparse
from rich.console import Console
from rich.table import Table

CLUSTERS = ["soda", "vegi", "potato"]

console = Console()


def check_cluster(name: str, quick: bool = False) -> bool:
    """Check a single cluster's GPU availability."""
    try:
        # Get node info with GPU counts
        cmd = f"sinfo -N -o '%n %P %G %e %t' --noheader"
        res = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=3", name, cmd],
            capture_output=True, text=True, timeout=10
        )
        
        if res.returncode != 0:
            console.print(f"[red]✗ {name}[/red]: Could not connect")
            return False
        
        lines = [l.strip() for l in res.stdout.strip().split('\n') if l.strip()]
        
        if not lines:
            console.print(f"[yellow]? {name}[/yellow]: No nodes found")
            return False
        
        if quick:
            # Just count available GPUs
            idle_gpus = 0
            for line in lines:
                parts = line.split()
                if len(parts) >= 5 and parts[4] == 'idle':
                    # Parse gpu count from gres (e.g., "gpu:8" or "gpu:3090:8")
                    gres = parts[2]
                    if 'gpu:' in gres:
                        try:
                            gpu_count = int(gres.split(':')[-1])
                            idle_gpus += gpu_count
                        except ValueError:
                            pass
            console.print(f"[green]✓ {name}[/green]: {idle_gpus} GPUs available")
        else:
            # Show full table
            table = Table(title=f"📊 {name}", show_header=True)
            table.add_column("Node", style="cyan")
            table.add_column("Partition", style="magenta")
            table.add_column("GPUs", style="green")
            table.add_column("Free Mem", style="yellow")
            table.add_column("State", style="bold")
            
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    node, partition, gres, mem, state = parts[:5]
                    # Color state
                    if state == 'idle':
                        state = f"[green]{state}[/green]"
                    elif state == 'mix':
                        state = f"[yellow]{state}[/yellow]"
                    else:
                        state = f"[red]{state}[/red]"
                    table.add_row(node, partition, gres, f"{mem}MB", state)
            
            console.print(table)
            console.print()
        
        return True
        
    except subprocess.TimeoutExpired:
        console.print(f"[red]✗ {name}[/red]: Timeout")
        return False
    except Exception as e:
        console.print(f"[red]✗ {name}[/red]: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Check GPU availability")
    parser.add_argument("clusters", nargs="*", default=CLUSTERS, help="Clusters to check")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick summary only")
    args = parser.parse_args()
    
    if not args.quick:
        console.print("[bold]Checking cluster availability...[/bold]\n")
    
    for cluster in args.clusters:
        if cluster not in CLUSTERS:
            console.print(f"[yellow]Unknown cluster: {cluster}[/yellow]")
            continue
        check_cluster(cluster, args.quick)


if __name__ == "__main__":
    main()
