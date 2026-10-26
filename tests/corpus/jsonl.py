"""JSON lines: the files a run's steps write beside their records, a JSON value a line."""

import json
from collections.abc import Iterable
from pathlib import Path
from typing import TypeAlias, cast

Row: TypeAlias = dict[str, object]  # a line's value, as the steps write them


def read(path: Path) -> list[Row]:
    """Read a file of JSON lines.

    Returns:
      Each line's value, blank lines skipped; none where the file isn't there.

    """
    written: str = path.read_text(encoding="utf-8") if path.exists() else ""
    return [cast("Row", json.loads(line)) for line in written.splitlines() if line]


def text(rows: Iterable[object]) -> str:
    """Write values as JSON lines.

    Returns:
      Each one's JSON and a newline.

    """
    return "".join(f"{json.dumps(row)}\n" for row in rows)
