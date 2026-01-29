import os
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

def check():
    load_dotenv()
    console = Console()
    
    required = ["WANDB_API_KEY", "HF_TOKEN"]
    
    table = Table(title="Credential Check")
    table.add_column("Secret", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Value (Masked)", style="green")

    for key in required:
        val = os.getenv(key)
        if val:
            masked = val[:4] + "*" * (len(val) - 8) + val[-4:] if len(val) > 8 else "****"
            table.add_row(key, "[green]FOUND[/green]", masked)
        else:
            table.add_row(key, "[red]MISSING[/red]", "N/A")

    console.print(table)
    
    if not all(os.getenv(k) for k in required):
        console.print("\n[yellow]Warning: Some credentials are missing. Check your .env file.[/yellow]")

if __name__ == "__main__":
    check()
