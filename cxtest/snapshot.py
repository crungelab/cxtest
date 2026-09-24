"""
Golden-file snapshots of cxbind's generated output.

Each generated file is compared with a committed copy under
<target>/__snapshots__/<relative path>.snap. The .snap suffix keeps
recursive CMake globs and pytest collection away from the copies.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from rich.syntax import Syntax

from .console import console

GENERATED_DIR = "src"  # cxbind writes generated sources to <target>/src
SNAPSHOT_DIR = "__snapshots__"
SNAPSHOT_SUFFIX = ".snap"
EXCLUDED_DIRS = {SNAPSHOT_DIR, "build", ".git"}


class Status(Enum):
    MATCH = "match"
    NEW = "new"
    UPDATED = "updated"
    CHANGED = "changed"


@dataclass
class SnapshotResult:
    generated: Path
    status: Status
    diff: str = ""


def find_generated(target: Path, patterns: list[str]) -> list[Path]:
    # Only look in the target's own src/, so a target nested inside another
    # target's tree is never snapshotted twice.
    search = target / GENERATED_DIR
    if not search.is_dir():
        return []

    files: set[Path] = set()
    for pattern in patterns:
        for path in search.rglob(pattern):
            rel_parts = path.relative_to(target).parts
            if path.is_file() and not EXCLUDED_DIRS.intersection(rel_parts):
                files.add(path)
    return sorted(files)


def snapshot_path(generated: Path, target: Path) -> Path:
    rel = generated.relative_to(target)
    return target / SNAPSHOT_DIR / rel.with_name(rel.name + SNAPSHOT_SUFFIX)


def check_snapshot(generated: Path, target: Path, update: bool) -> SnapshotResult:
    snap = snapshot_path(generated, target)
    actual = generated.read_text()

    if not snap.exists():
        snap.parent.mkdir(parents=True, exist_ok=True)
        snap.write_text(actual)
        return SnapshotResult(generated, Status.NEW)

    expected = snap.read_text()
    if expected == actual:
        return SnapshotResult(generated, Status.MATCH)

    if update:
        snap.write_text(actual)
        return SnapshotResult(generated, Status.UPDATED)

    diff = "".join(
        difflib.unified_diff(
            expected.splitlines(keepends=True),
            actual.splitlines(keepends=True),
            fromfile=str(snap.relative_to(target)),
            tofile=str(generated.relative_to(target)),
        )
    )
    return SnapshotResult(generated, Status.CHANGED, diff)


STATUS_STYLE = {
    Status.MATCH: "[green]match[/green]",
    Status.NEW: "[cyan]new[/cyan]",
    Status.UPDATED: "[yellow]updated[/yellow]",
    Status.CHANGED: "[bold red]changed[/bold red]",
}


def report(results: list[SnapshotResult], root: Path) -> bool:
    """Print results; return True if no snapshot changed unexpectedly."""
    if not results:
        console.print("[yellow]No generated files matched; nothing snapshotted.[/yellow]")
        return True

    for result in results:
        rel = result.generated.relative_to(root)
        console.print(f"  {STATUS_STYLE[result.status]:<30} {rel}")
        if result.status is Status.CHANGED:
            console.print(Syntax(result.diff, "diff", theme="ansi_dark", word_wrap=True))

    changed = [r for r in results if r.status is Status.CHANGED]
    if changed:
        console.print(
            f"[bold red]{len(changed)} snapshot(s) changed.[/bold red] "
            "Review the diffs; rerun with --update to accept them."
        )
        return False
    return True