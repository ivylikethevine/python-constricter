# SPDX-License-Identifier: MIT
"""The command's defaults, from the nearest `pyproject.toml`'s `[tool.constricter]` table."""

import tomllib
from collections.abc import Callable, Sequence
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, TypeAlias

from constricter.checker import LEVELS, MESSAGES

if TYPE_CHECKING:
  from datetime import date, datetime, time
  from io import BufferedReader

_Toml: TypeAlias = "str | int | float | bool | datetime | date | time | list[_Toml] | dict[str, _Toml]"
Default: TypeAlias = str | int | bool | list[str] | dict[str, str]


def unknown_codes(codes: Sequence[str]) -> list[str]:
  """Return the codes (or code prefixes) in `codes` that match no code."""
  return [code for code in codes if not any(known.startswith(code.upper()) for known in MESSAGES)]


def _pyproject(start: Path) -> Path | None:
  """Return the nearest `pyproject.toml` in `start` or above it."""
  directory: Path
  path: Path
  for directory in (start, *start.parents):
    if (path := directory / "pyproject.toml").is_file():
      return path
  return None


def _table(path: Path) -> dict[str, _Toml]:
  """Return `path`'s `[tool.constricter]` table, or an empty one.

  Raises:
    ValueError: The file isn't TOML, or `tool.constricter` isn't a table.

  """
  file: BufferedReader
  document: dict[str, _Toml]
  message: str
  with path.open("rb") as file:
    try:
      document = tomllib.load(file)
    except tomllib.TOMLDecodeError as error:
      message = f"{path}: {error}"
      raise ValueError(message) from error
  table: dict[str, _Toml]
  match document.get("tool"):
    case {"constricter": dict() as table}:
      return table
    case {"constricter": _}:
      message = f"{path}: [tool.constricter] isn't a table"
      raise ValueError(message)
    case _:
      return {}


def _level(value: _Toml) -> str | None:
  """Return a level's name or number as the options take it, or `None` if it isn't one."""
  text: str = str(value).lower()
  return text if isinstance(value, str | int) and not isinstance(value, bool) and text in LEVELS else None


def _whole(value: _Toml, minimum: int) -> int | None:
  return value if isinstance(value, int) and not isinstance(value, bool) and value >= minimum else None


def _strings(value: _Toml) -> list[str] | None:
  return (
    [str(item) for item in value]
    if isinstance(value, list) and all(isinstance(item, str) for item in value)
    else None
  )


def _codes(value: _Toml) -> list[str] | None:
  codes: list[str] | None = _strings(value)
  return None if codes is None or unknown_codes(codes) else [code.upper() for code in codes]


def _flag(value: _Toml) -> bool | None:
  return value if isinstance(value, bool) else None


def _levels(value: _Toml) -> dict[str, str] | None:
  if not isinstance(value, dict):
    return None
  levels: dict[str, str | None] = {glob: _level(level) for glob, level in value.items()}
  return None if None in levels.values() else {glob: str(level) for glob, level in levels.items()}


# Each key's reader: its option default, or `None` for a wrong value.
_READERS: dict[str, Callable[[_Toml], Default | None]] = {
  "level": _level,
  "nesting": partial(_whole, minimum=1),
  "jobs": partial(_whole, minimum=0),
  "exclude": _strings,
  "select": _codes,
  "ignore": _codes,
  "type-comments": _flag,
  "all-scopes": _flag,
  "per-path-levels": _levels,
}


def config_defaults(start: Path) -> dict[str, Default]:
  """Return the option defaults in the nearest `pyproject.toml`'s `[tool.constricter]`.

  Raises:
    ValueError: The file isn't TOML, or the table has an unknown key or a wrong value.

  """
  path: Path | None
  if (path := _pyproject(start)) is None:
    return {}
  defaults: dict[str, Default] = {}
  key: str
  value: _Toml
  for key, value in _table(path).items():
    default: Default | None
    if key not in _READERS or (default := _READERS[key](value)) is None:
      message: str = f"{path}: [tool.constricter] has an invalid {key} = {value!r}"
      raise ValueError(message)
    defaults[key.replace("-", "_")] = default
  return defaults
