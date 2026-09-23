# SPDX-License-Identifier: MIT
"""The command's defaults, from the nearest `pyproject.toml`'s `[tool.constricter]` table."""

import tomllib
from collections.abc import Callable, Sequence
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeAlias

from constricter.cli.hints import SERVERS
from constricter.jsonc import is_int
from constricter.offences import FIX_KINDS, LEVELS, MESSAGES

if TYPE_CHECKING:
    from datetime import date, datetime, time
    from io import BufferedReader

_Toml: TypeAlias = "str | int | float | bool | datetime | date | time | list[_Toml] | dict[str, _Toml]"
Default: TypeAlias = str | int | float | bool | list[str] | dict[str, str] | dict[str, list[str]]


def unknown_codes(codes: Sequence[str]) -> list[str]:
    """Check `codes` (or code prefixes) against the known codes.

    Returns:
      Those that match none.

    """
    return [code for code in codes if not any(known.startswith(code.upper()) for known in MESSAGES)]


DEFAULT_BASELINE: Final = "constricter-baseline.json"


def project_root(start: Path) -> Path:
    """Find the project's root.

    Returns:
      The directory of the nearest `pyproject.toml`, or `start` if there's none.

    """
    path: Path | None = _pyproject(start)
    return start if path is None else path.parent


def _pyproject(start: Path) -> Path | None:
    """Find the nearest `pyproject.toml` in `start` or above it.

    Returns:
      Its path, or `None`.

    """
    directory: Path
    path: Path
    for directory in (start, *start.parents):
        if (path := directory / "pyproject.toml").is_file():
            return path
    return None


def _table(path: Path) -> dict[str, _Toml]:
    """Return `path`'s `[tool.constricter]` table, or an empty one.

    Returns:
      The table's keys and values, as TOML parsed them.

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
    """Read a level's name or number as the options take it.

    Returns:
      The level's name, or `None` if it isn't one.

    """
    text: str = str(value).lower()
    return text if (isinstance(value, str) or is_int(value)) and text in LEVELS else None


def _whole(value: _Toml, minimum: int) -> int | None:
    return value if is_int(value) and value >= minimum else None


def _strings(value: _Toml) -> list[str] | None:
    return (
        [str(item) for item in value]
        if isinstance(value, list) and all(isinstance(item, str) for item in value)
        else None
    )


def _codes(value: _Toml) -> list[str] | None:
    codes: list[str] | None = _strings(value)
    return None if codes is None or unknown_codes(codes) else [code.upper() for code in codes]


def unknown_fix_kinds(kinds: Sequence[str]) -> list[str]:
    """Check `kinds` against `FIX_KINDS`' ids.

    Returns:
      Those that aren't one.

    """
    return [kind for kind in kinds if kind not in FIX_KINDS]


def _fix_kinds(value: _Toml) -> list[str] | None:
    kinds: list[str] | None = _strings(value)
    return None if kinds is None or unknown_fix_kinds(kinds) else kinds


def _flag(value: _Toml) -> bool | None:
    return value if isinstance(value, bool) else None


def _gigabytes(value: _Toml) -> float | None:
    """Read `infer-memory`: a positive number of gigabytes.

    Returns:
      It, or `None` for anything else.

    """
    return (
        float(value) if isinstance(value, int | float) and not isinstance(value, bool) and value > 0 else None
    )


def _checkers(value: _Toml) -> list[str] | None:
    """Read `infer-with`: a checker, or a list of them, each one it knows.

    Returns:
      Them, or `None` for anything else.

    """
    checkers: list[str] | None = [value] if isinstance(value, str) else _strings(value)
    return checkers if checkers and all(checker in SERVERS for checker in checkers) else None


def _levels(value: _Toml) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    levels: dict[str, str | None] = {glob: _level(level) for glob, level in value.items()}
    return None if None in levels.values() else {glob: str(level) for glob, level in levels.items()}


def _lists(value: _Toml, read: Callable[[_Toml], list[str] | None]) -> dict[str, list[str]] | None:
    """Read a table of lists, each as `read` reads one: `per-file-ignores`' codes, `narrower`'s types.

    Returns:
      It, or `None` if `value` isn't a table, or `read` can't read one of its values.

    """
    if not isinstance(value, dict):
        return None
    lists: dict[str, list[str] | None] = {key: read(item) for key, item in value.items()}
    return None if None in lists.values() else {key: list(item or []) for key, item in lists.items()}


def _baseline(value: _Toml, root: Path) -> str | None:
    """Read a baseline path, relative to `root` (the pyproject.toml that names it).

    Returns:
      The resolved path, or `None` if `value` isn't a non-empty string.

    """
    return str(root / value) if isinstance(value, str) and value else None


# Each key's reader: its option default, or `None` for a wrong value.
_READERS: dict[str, Callable[[_Toml], Default | None]] = {
    "level": _level,
    "nesting": partial(_whole, minimum=1),
    "max-length": partial(_whole, minimum=1),
    "jobs": partial(_whole, minimum=0),
    "exclude": _strings,
    "select": _codes,
    "ignore": _codes,
    "extend-select": _codes,
    "fix-select": _fix_kinds,
    "fix-ignore": _fix_kinds,
    "unsafe-fix-select": _fix_kinds,
    "type-comments": _flag,
    "all-scopes": _flag,
    "per-path-levels": _levels,
    "per-file-ignores": partial(_lists, read=_codes),
    "narrower": partial(_lists, read=_strings),  # a type hierarchy: each type, and those it's narrower than
    "infer-with": _checkers,
    "infer-memory": _gigabytes,
}


def config_defaults(start: Path) -> dict[str, Default]:
    """Return the option defaults in the nearest `pyproject.toml`'s `[tool.constricter]`.

    Returns:
      Each option's default, keyed by its `argparse` name (`type_comments`, not `type-comments`).

    Raises:
      ValueError: The file isn't TOML, or the table has an unknown key or a wrong value.

    """
    path: Path | None
    if (path := _pyproject(start)) is None:
        return {}
    readers: dict[str, Callable[[_Toml], Default | None]] = {
        **_READERS,
        "baseline": partial(_baseline, root=path.parent),
    }
    defaults: dict[str, Default] = {}
    key: str
    value: _Toml
    for key, value in _table(path).items():
        default: Default | None
        if key not in readers or (default := readers[key](value)) is None:
            message: str = f"{path}: [tool.constricter] has an invalid {key} = {value!r}"
            raise ValueError(message)
        defaults[key.replace("-", "_")] = default
    return defaults
