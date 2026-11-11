"""The settings the checkers `--infer-with` starts read for a corpus: its own, never this project's.

A checker with no settings in its workspace reads the nearest above it, and a suite's checkout and a
fix's copy lie under this project, whose settings name its own source, environment and Python.
"""

import tomllib
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

# Each checker: its settings file, what an empty one holds, and the `pyproject.toml` tables that
# are its settings too.
_CHECKERS: Final = (
    ("pyrightconfig.json", "{}\n", ("pyright", "basedpyright")),
    ("pyrefly.toml", "", ("pyrefly",)),
    ("ty.toml", "", ("ty",)),
)
_PROJECT: Final = "pyproject.toml"
_Table: TypeAlias = dict[str, object]  # a table of a `pyproject.toml`, as `tomllib` reads it
# The settings a copy of a checkout takes with its files (`launch.copied`).
FILES: Final = (_PROJECT, *(name for name, _, _ in _CHECKERS))


def own(root: Path) -> list[str]:
    """Keep each checker to `root`'s settings: an empty file of its own, where it has none there.

    A `pyproject.toml` is a checker's only where it holds that checker's table: pyrefly and ty pass
    over one with mypy's or Pyright's alone.

    Returns:
      The names of the files written.

    """
    tools: frozenset[str] = _tools(root / _PROJECT)
    written: list[str] = []
    name: str
    empty: str
    tables: tuple[str, ...]
    for name, empty, tables in _CHECKERS:
        if not (root / name).exists() and not tools.intersection(tables):
            _ = (root / name).write_text(empty, encoding="utf-8")
            written.append(name)
    return written


def settled(root: Path) -> None:
    """Keep each checker to checkout `root`'s settings (see `own`); git is told to pass over each file."""
    name: str
    for name in own(root):
        stream: IO[str]
        with (root / ".git" / "info" / "exclude").open("a", encoding="utf-8") as stream:
            _ = stream.write(f"/{name}\n")


def _tools(project: Path) -> frozenset[str]:
    """Name the tools a `pyproject.toml` holds settings for.

    Returns:
      Each `[tool.NAME]` table's name; none for a file that isn't there, or isn't TOML.

    """
    try:
        text: str = project.read_text(encoding="utf-8")
    except (OSError, ValueError):  # a `UnicodeDecodeError` is a `ValueError`
        return frozenset()
    try:
        read: _Table = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return frozenset()
    tables: _Table | None = cast("_Table | None", read.get("tool"))
    return frozenset(tables) if isinstance(tables, dict) else frozenset()
