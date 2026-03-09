from pathlib import Path
import typer
from rich.rule import Rule

from .console import console
from .discover import discover_targets
from .runner import run_command

app = typer.Typer()


@app.command()
def run(root: Path = Path(".")):

    root = root.resolve()

    console.print(Rule("[bold]cxtest"))

    targets = discover_targets(root)

    for target in targets:
        run_command(["cxbind"], target)

    run_command(["cmake", "--build", "build"], root)

    run_command(["pytest"], root)