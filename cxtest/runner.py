import subprocess
from pathlib import Path

from rich.panel import Panel
from rich.text import Text

from .console import console

def run_command(command: list[str], cwd: Path):

    console.print(f"[bold cyan]Running[/] {' '.join(command)}")
    console.print(f"[dim]{cwd}[/]")

    result = subprocess.run(command, cwd=cwd)

    if result.returncode != 0:

        console.print(
            Panel(
                f"[red]Command failed[/]\n\n"
                f"[bold]cwd:[/] {cwd}\n"
                f"[bold]command:[/] {' '.join(command)}\n"
                f"[bold]exit code:[/] {result.returncode}",
                title="cxtest error",
            )
        )

        raise RuntimeError("command failed")

def run_cxbind(target: Path) -> None:
    run_command(["cxbind"], target)


def build_project(root: Path) -> None:
    run_command(["cmake", "--build", "build"], root)


def run_pytest(root: Path) -> None:
    run_command(["pytest"], root)