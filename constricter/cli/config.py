# SPDX-License-Identifier: MIT
"""The command's defaults, from the nearest `pyproject.toml`'s `[tool.constricter]` table."""

import re
import tomllib
from collections.abc import Callable, Sequence
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeAlias, cast

from constricter.cli.protocol import SERVERS
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
_MIN_PYTHON: Final = "min_python"
_VERSION: Final = re.compile(r"\d+\.\d+")  # `min-python`'s: `3.11`
# A lower bound among `requires-python`'s specifiers: `>=3.11`, `~=3.11`, `==3.11.*`, `>3.10`.
_LOWER_BOUND: Final = re.compile(r"(?:>=|~=|==|>)\s*(\d+)(?:\.(\d+))?")


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


def _document(path: Path) -> dict[str, _Toml]:
    """Read `path`, a `pyproject.toml`.

    Returns:
      Its tables, as TOML parsed them.

    Raises:
      ValueError: The file isn't TOML.

    """
    file: BufferedReader
    with path.open("rb") as file:
        try:
            return tomllib.load(file)
        except tomllib.TOMLDecodeError as error:
            message: str = f"{path}: {error}"
            raise ValueError(message) from error


def _table(path: Path, document: dict[str, _Toml]) -> dict[str, _Toml]:
    """Return the `[tool.constricter]` table of `document` (`path`'s), or an empty one.

    Returns:
      The table's keys and values, as TOML parsed them.

    Raises:
      ValueError: `tool.constricter` isn't a table.

    """
    table: dict[str, _Toml]
    match document.get("tool"):
        case {"constricter": dict() as table}:
            return table
        case {"constricter": _}:
            message: str = f"{path}: [tool.constricter] isn't a table"
            raise ValueError(message)
        case _:
            return {}


def _required(document: dict[str, _Toml]) -> str | None:
    """Read the oldest Python a project's `requires-python` allows: its highest lower bound.

    Returns:
      It (`3.11`, for `>=3.11,<4`), or `None` if the project doesn't say.

    """
    required: str
    match document.get("project"):
        case {"requires-python": str() as required}:
            pass
        case _:
            return None
    found: list[tuple[str, str]] = cast("list[tuple[str, str]]", _LOWER_BOUND.findall(required))
    bounds: list[tuple[int, int]] = [(int(major), int(minor or 0)) for major, minor in found]
    oldest: tuple[int, int] | None = max(bounds, default=None)
    return None if oldest is None else f"{oldest[0]}.{oldest[1]}"


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


def _version(value: _Toml) -> str | None:
    """Read `min-python`: a Python version, as text (`"3.11"`).

    Returns:
      It, or `None` for anything else.

    """
    return value if isinstance(value, str) and _VERSION.fullmatch(value) else None


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
    """Read a baseline's or a trace's path, relative to `root` (the pyproject.toml that names it).

    Returns:
      The resolved path, or `None` if `value` isn't a non-empty string.

    """
    return str(root / value) if isinstance(value, str) and value else None


# Each key's reader: its option default, or `None` for a wrong value.
_READERS: dict[str, Callable[[_Toml], Default | None]] = {
    "level": _level,
    "nesting": partial(_whole, minimum=1),
    "max-length": partial(_whole, minimum=1),
    "vague": partial(_whole, minimum=-1),
    "jobs": partial(_whole, minimum=0),
    "exclude": _strings,
    "select": _codes,
    "ignore": _codes,
    "extend-select": _codes,
    "fix-select": _fix_kinds,
    "fix-ignore": _fix_kinds,
    "unsafe-fix-select": _fix_kinds,
    "fix-plain-bases": _strings,
    "type-comments": _flag,
    "all-scopes": _flag,
    "per-path-levels": _levels,
    "per-file-ignores": partial(_lists, read=_codes),
    "narrower": partial(_lists, read=_strings),  # a type hierarchy: each type, and those it's narrower than
    "infer-with": _checkers,
    "infer-memory": _gigabytes,
    "min-python": _version,
}


def config_defaults(start: Path) -> dict[str, Default]:
    """Return the option defaults in the nearest `pyproject.toml`'s `[tool.constricter]`.

    And `min-python`'s from the project's `requires-python`, where the table doesn't set it.

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
        "infer-from": partial(_baseline, root=path.parent),
    }
    defaults: dict[str, Default] = {}
    key: str
    value: _Toml
    document: dict[str, _Toml] = _document(path)
    for key, value in _table(path, document).items():
        default: Default | None
        if key not in readers or (default := readers[key](value)) is None:
            message: str = f"{path}: [tool.constricter] has an invalid {key} = {value!r}"
            raise ValueError(message)
        defaults[key.replace("-", "_")] = default
    required: str | None
    if _MIN_PYTHON not in defaults and (required := _required(document)) is not None:
        defaults[_MIN_PYTHON] = required
    return defaults
