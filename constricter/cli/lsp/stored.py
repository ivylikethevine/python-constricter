# SPDX-License-Identifier: MIT
"""A type checker's hints for a round of files, kept between runs: asked for once while nothing changes.

A file's hints rest on the whole program the checker reads, so a round's are kept whole, by what
they rest on (`key`): the checker and its build (see `remembered.build`), the text of every file
asked about, the workspace's settings files (`pyproject.toml`, `pyrightconfig.json`, ...), the
installed distributions of the environments a checker may read (the interpreter's, `VIRTUAL_ENV`'s
and the workspace's own `.venv`), and the code here that asks and reads. Not a file of the
workspace's that isn't asked about: walking a tree costs as much as a round can save, and a
project's files are asked about together. The first round of a project at the
same commit asks again only when one of those changed; a later round's texts are `--fix`'s, so it's
kept as well, for the next run with the same fixes. A round read from the store keeps the files the
checker hung on (see `Session.abandoned`) as it found them.

Each entry is a file in the cache, read again within `_KEPT` seconds of its last use; older ones are
removed as a new one is written. A store that can't be read or written is passed over.
"""

import contextlib
import hashlib
import json
import os
import time
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Final, TypeAlias, TypedDict, cast

from constricter.cli.lsp import connection, protocol, remembered
from constricter.cli.lsp.connection import FileHints, Found
from constricter.fix.core.known import Offered
from constricter.fix.index.stubs.installed import cache_directory, search_path

_KEPT: Final = 14 * 24 * 3600.0  # seconds an entry is kept unused
# A workspace's files that set how a checker reads it.
_SETTINGS: Final = frozenset(
    {"pyproject.toml", "setup.cfg", "pyrightconfig.json", "ty.toml", "pyrefly.toml", "mypy.ini"},
)
_LOCAL_ENVIRONMENT: Final = ".venv"
_VARIABLES: Final = ("VIRTUAL_ENV", "CONDA_PREFIX", "PYTHONPATH")
_SUFFIX: Final = ".json"
_WHERE: Final = ":"  # between a hint's line and column, in an entry
# One file's hints as an entry holds them: by `line:column`, the text and the edits' text and imports.
_Entry: TypeAlias = dict[str, list[str | list[str] | None]]


class _Round(TypedDict):
    """A round as the store holds it: each file's hints, and the files the checker hung on."""

    found: dict[str, _Entry]
    hung: list[str]


def key(checker: str, command: Sequence[str], root: Path, files: Mapping[Path, str]) -> str:
    """Name a round of `checker`'s hints for `files` (each path's current text), in workspace `root`.

    Returns:
      A digest of everything they rest on (see the module docstring).

    """
    build: str = ""
    with contextlib.suppress(OSError):
        build = remembered.build(checker, Path(command[0]))
    texts: list[str] = [checker, *command, build, *(os.environ.get(name, "") for name in _VARIABLES)]
    parts: list[bytes] = [Path(cast("str", code.__file__)).read_bytes() for code in (connection, protocol)]
    asked: dict[str, str] = {_relative(path, root): text for path, text in files.items()}
    name: str
    for name in sorted(asked):
        texts += [name, asked[name]]
    for name in sorted(_SETTINGS):
        with contextlib.suppress(OSError):
            parts += [name.encode("utf-8"), (root / name).read_bytes()]
    texts += _distributions(root)
    parts += [each.encode("utf-8", "replace") for each in texts]
    return hashlib.sha256(b"\0".join(f"{len(part)}:".encode() + part for part in parts)).hexdigest()


def load(name: str, root: Path, paths: Iterable[Path]) -> tuple[Found, frozenset[Path]] | None:
    """Read the round stored as `name` (see `key`) for `paths`, in workspace `root`; and mark it used.

    Returns:
      Each path's hints and those the checker hung on; `None` if there's no such round, or it can't
      be read.

    """
    entry: Path = _entry(name)
    named: dict[str, Path] = {_relative(path, root): path for path in paths}
    read: tuple[Found, frozenset[Path]]
    try:
        read = _read(entry, named)
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return None
    with contextlib.suppress(OSError):
        entry.touch()
    return read


def store(name: str, root: Path, found: Found, hung: frozenset[Path]) -> None:
    """Keep a round's hints as `name` (see `key`), and remove the entries no run has read of late."""
    entry: Path = _entry(name)
    kept: _Round = {
        "found": {_relative(path, root): _entry_of(hints) for path, hints in found.items()},
        "hung": sorted(_relative(path, root) for path in hung),
    }
    with contextlib.suppress(OSError):
        entry.parent.mkdir(parents=True, exist_ok=True)
        written: Path = entry.with_name(f"{entry.name}.{os.getpid()}")
        _ = written.write_text(json.dumps(kept), encoding="utf-8")
        _ = written.replace(entry)  # whole, or not at all: another run may read it meanwhile
        now: float = time.time()
        old: Path
        for old in entry.parent.glob(f"*{_SUFFIX}"):
            with contextlib.suppress(OSError):
                if now - old.stat().st_mtime > _KEPT:
                    old.unlink()


def _read(entry: Path, named: Mapping[str, Path]) -> tuple[Found, frozenset[Path]]:
    """Read a stored round's hints for the paths `named` by the store's names for them.

    Returns:
      Each path's hints, and those the checker hung on.

    """
    kept: _Round = cast("_Round", json.loads(entry.read_text(encoding="utf-8")))
    found: Found = {path: _hints(kept["found"].get(each, {})) for each, path in named.items()}
    return found, frozenset(named[each] for each in kept["hung"])


def _entry(name: str) -> Path:
    """Find where the round `name` is kept.

    Returns:
      Its path in the cache.

    """
    return cache_directory().with_name("hints") / f"{name}{_SUFFIX}"


def _relative(path: Path, root: Path) -> str:
    """Write `path` as the store keeps it: under `root`, relative to it.

    Returns:
      It, as text.

    """
    absolute: Path = path if path.is_absolute() else Path.cwd() / path
    with contextlib.suppress(ValueError):
        return absolute.relative_to(root).as_posix()
    return absolute.as_posix()


def _distributions(root: Path) -> list[str]:
    """List the installed distributions a checker may read: each environment's, by folder and name.

    Returns:
      Each `*.dist-info` folder's path, which holds its version, in a fixed order.

    """
    folders: list[Path] = list(search_path())
    local: Path = root / _LOCAL_ENVIRONMENT
    folders += [*sorted(local.glob("lib/python3*/site-packages")), local / "Lib" / "site-packages"]
    return [str(found) for folder in folders for found in sorted(folder.glob("*.dist-info"))]


def _entry_of(hints: FileHints) -> _Entry:
    """Write one file's hints as an entry holds them.

    Returns:
      Them, by `line:column`.

    """
    return {
        f"{line}{_WHERE}{column}": [
            text,
            None if offered is None else offered.text,
            None if offered is None else list(offered.imports),
        ]
        for (line, column), (text, offered) in hints.items()
    }


def _hints(entry: _Entry) -> FileHints:
    """Read one file's hints from its entry.

    Returns:
      Them, by line and column.

    """
    found: FileHints = {}
    where: str
    parts: list[str | list[str] | None]
    for where, parts in entry.items():
        line: str
        column: str
        line, _, column = where.partition(_WHERE)
        text: str = cast("str", parts[0])
        shown: str | None = cast("str | None", parts[1])
        imports: list[str] = cast("list[str] | None", parts[2]) or []
        found[int(line), int(column)] = (text, None if shown is None else Offered(shown, tuple(imports)))
    return found
