# SPDX-License-Identifier: MIT
"""Jupyter notebooks: their code cells, joined into one module, and where each line came from."""

import re
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from constricter import jsonc

SUFFIX: Final = ".ipynb"
_Json: TypeAlias = "str | int | float | bool | list[_Json] | dict[str, _Json] | None"
# IPython syntax that isn't Python: line magics, shell escapes (`!ls`), and help (`obj?`, `?obj`).
_MAGIC: re.Pattern[str] = re.compile(r"\s*([%!?]|[\w.]+\?{1,2}\s*$)")


class Line(NamedTuple):
  """Where a line of the joined module is in the notebook: its cell (from 1) and line in it."""

  cell: int
  line: int


def _cell_lines(source: _Json) -> list[str]:
  """Return a cell's lines, each ending in a newline; IPython-only lines become blank."""
  text: str = "".join(str(part) for part in source) if isinstance(source, list) else str(source)
  lines: list[str] = text.splitlines()
  if lines and lines[0].lstrip().startswith("%%"):  # a cell magic: the whole cell isn't Python
    return ["\n"] * len(lines)
  return ["\n" if _MAGIC.match(line) else f"{line}\n" for line in lines]


def read(path: Path) -> tuple[str, list[Line]]:
  """Return a notebook's code cells as one module, and where each of its lines came from.

  Returns:
    The module's source, and a `Line` for each of its lines.

  Raises:
    ValueError: It isn't a notebook (JSON with a `cells` list).

  """
  document: _Json = cast("_Json", jsonc.loads(path.read_bytes()))
  cells: list[_Json]
  match document:
    case {"cells": list() as cells}:
      pass
    case _:
      message: str = f"{path}: not a Jupyter notebook"
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
