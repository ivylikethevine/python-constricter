# SPDX-License-Identifier: MIT
"""Jupyter notebooks: their code cells, joined into one module, and where each line came from."""

import json
import re
from collections.abc import Sequence
from typing import Final, NamedTuple, TypeAlias, cast

from constricter import jsonc
from constricter.fix import fixes
from constricter.offences import Offence

SUFFIX: Final = ".ipynb"
_Json: TypeAlias = "str | int | float | bool | list[_Json] | dict[str, _Json] | None"
# IPython syntax that isn't Python: line magics, shell escapes (`!ls`), and help (`obj?`, `?obj`).
_MAGIC: re.Pattern[str] = re.compile(r"\s*([%!?]|[\w.]+\?{1,2}\s*$)")


class Line(NamedTuple):
    """Where a line of the joined module is in the notebook: its cell (from 1) and line in it."""

    cell: int
    line: int


class Cell(NamedTuple):
    """A cell `fix` changed: its number (from 1), and its lines before and after."""

    number: int
    old: list[str]
    new: list[str]


def _text(source: _Json) -> str:
    """Join a cell's source, which a notebook keeps as a string or a list of lines.

    Returns:
      The source, as one string.

    """
    return "".join(str(part) for part in source) if isinstance(source, list) else str(source)


def _cell_lines(source: _Json) -> list[str]:
    """Split a cell into lines; IPython-only lines become blank.

    Returns:
      The lines, each ending in a newline.

    """
    lines: list[str] = _text(source).splitlines()
    if lines and lines[0].lstrip().startswith("%%"):  # a cell magic: the whole cell isn't Python
        return ["\n"] * len(lines)
    return ["\n" if _MAGIC.match(line) else f"{line}\n" for line in lines]


def parse(raw: str, name: str) -> tuple[str, list[Line]]:
    """Return notebook JSON's code cells as one module, and where each of its lines came from.

    Returns:
      The module's source, and a `Line` for each of its lines.

    Raises:
      ValueError: It isn't a notebook (JSON with a `cells` list).

    """
    document: _Json = cast("_Json", jsonc.loads(raw))
    cells: list[_Json]
    match document:
        case {"cells": list() as cells}:
            pass
        case _:
            message: str = f"{name}: not a Jupyter notebook"
            raise ValueError(message)
    joined: list[str] = []
    where: list[Line] = []
    number: int
    cell: _Json
    source: _Json
    for number, cell in enumerate(cells, start=1):
        match cell:
            case {"cell_type": "code", "source": source}:
                lines: list[str] = _cell_lines(source)
                joined += lines
                where += [Line(number, line) for line in range(1, len(lines) + 1)]
            case _:
                pass
    return "".join(joined), where


def fix(raw: str, offences: Sequence[Offence]) -> tuple[str, list[Cell]]:
    """Add each fixable offence's annotation in its cell of the notebook JSON `raw`.

    Returns:
      The notebook's new JSON (its indent, key order and final newline kept), and each changed
      cell's number and old and new lines.

    """
    document: dict[str, _Json] = cast("dict[str, _Json]", jsonc.loads(raw))
    cells: list[_Json] = cast("list[_Json]", document["cells"])
    by_cell: dict[int, list[Offence]] = {}
    o: Offence
    for o in offences:
        if o.edit is not None and o.cell is not None:
            by_cell.setdefault(o.cell, []).append(o)
    changed: list[Cell] = []
    number: int
    for number in sorted(by_cell):
        cell: dict[str, _Json] = cast("dict[str, _Json]", cells[number - 1])
        source: _Json = cell["source"]
        old: list[str] = _text(source).splitlines(keepends=True)
        new: list[str] = fixes.apply(old, by_cell[number])
        cell["source"] = list[_Json](new) if isinstance(source, list) else "".join(new)
        changed.append(Cell(number, old, new))
    indent: re.Match[str] | None = re.match(r"\{\r?\n( +)", raw)
    text: str = json.dumps(document, indent=len(indent.group(1)) if indent else 1, ensure_ascii=False)
    return text + ("\n" if raw.endswith("\n") else ""), changed
