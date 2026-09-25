from pathlib import Path
from rich.table import Table

from .console import console

PROJECT_GLOB = "*.prj.yaml"


def discover_targets(root: Path) -> list[Path]:
    targets = sorted(
        {
            marker.parent.resolve()
            for marker in root.rglob(".cxbind")
            if marker.is_dir() and any(marker.glob(PROJECT_GLOB))
        }
    )

    table = Table(title="Discovered cxbind targets")
    table.add_column("#")
    table.add_column("Directory")

    for i, path in enumerate(targets, start=1):
        table.add_row(str(i), str(path))

    console.print(table)

    return targets
