from pathlib import Path

import typer
from rich.rule import Rule

from .console import console
from .discover import discover_targets
from .runner import run_command
from .snapshot import SnapshotResult, check_snapshot, find_generated, report

app = typer.Typer()


@app.command()
def run(
    root: Path = Path("."),
    update: bool = typer.Option(
        False, "--update", "-u", help="Accept current generated output as the new snapshots."
    ),
    pattern: list[str] = typer.Option(
        ["*_py_auto.cpp", "*.pyi"], "--pattern", "-p", help="Glob for generated files to snapshot (repeatable)."
    ),
    snapshots: bool = typer.Option(
        True, "--snapshots/--no-snapshots", help="Compare generated output against snapshots."
    ),
):
    root = root.resolve()

    console.print(Rule("[bold]cxtest"))

    targets = discover_targets(root)

    results: list[SnapshotResult] = []
    for target in targets:
        run_command(["cxbind"], target)
        if snapshots:
            for generated in find_generated(target, pattern):
                results.append(check_snapshot(generated, target, update))

    snapshots_ok = True
    if snapshots:
        console.print(Rule("[bold]snapshots"))
        snapshots_ok = report(results, root)

    # Keep going on snapshot changes: build and test results still say
    # whether a change is a regression or an improvement.
    run_command(["cmake", "--build", "build"], root)

    run_command(["pytest"], root)

    if not snapshots_ok:
        raise typer.Exit(code=1)