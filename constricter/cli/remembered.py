# SPDX-License-Identifier: MIT
"""The files a type checker's server hung on, remembered between runs.

A server that hangs on a file costs the run its timeout twice, and a restart each time: once with
the file among others, once with it alone. The file's text, with the checker and its build (its
installed distribution's version, else its executable's size and when it changed), names an empty
file in the cache; while there's one, the file is left without hints from the start. So is the file
at that path for `_RECENT` seconds, whatever it holds: a second pass over files the first one fixed
sees the text it fixed. A new version of the checker, or a changed file after that, is asked again.
"""

import contextlib
import hashlib
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from constricter.fix.index.installed import cache_directory

_RECENT: Final = 3600.0  # seconds a hang is remembered by the file's path, as well as by its text
# Where an executable's environment keeps its distributions, from its `bin` (or `Scripts`) directory.
_DISTRIBUTIONS: Final = ("lib/python*/site-packages", "Lib/site-packages")


def _marker(checker: str, command: Sequence[str], named: str) -> Path:
    """Name what remembers that `checker`, started by `command`, hung on a file `named` so.

    Returns:
      Its path in the cache.

    """
    build: str = ""
    with contextlib.suppress(OSError):
        build = _build(checker, Path(command[0]))
    key: str = "\0".join((checker, command[0], build, named))
    return cache_directory().with_name("hung") / hashlib.sha256(key.encode("utf-8", "replace")).hexdigest()


def _build(checker: str, executable: Path) -> str:
    """Say which build of `checker` `executable` starts: its distribution's, where its environment has one.

    Not the executable's own where there is: an install writes the script again for the same version.

    Returns:
      The distribution's folder's name, which holds its version; else the executable's size and when
      it changed.

    """
    pattern: str
    for pattern in _DISTRIBUTIONS:
        found: list[Path]
        if found := sorted(executable.parent.parent.glob(f"{pattern}/{checker}-*.dist-info")):
            return found[0].name
    return f"{executable.stat().st_size}:{executable.stat().st_mtime_ns}"


def hung(checker: str, command: Sequence[str], text: str, path: Path | None = None) -> bool:
    """Check whether `checker` hung on a file holding `text` in an earlier run, or at `path` of late.

    Returns:
      Whether it did.

    """
    if _marker(checker, command, text).exists():
        return True
    if path is None:
        return False
    with contextlib.suppress(OSError):
        return time.time() - _marker(checker, command, str(path.absolute())).stat().st_mtime < _RECENT
    return False


def remember(checker: str, command: Sequence[str], text: str, path: Path | None = None) -> None:
    """Remember that `checker` hung on a file holding `text`, at `path`; not where the cache can't be."""
    each: str
    for each in (text,) if path is None else (text, str(path.absolute())):
        marker: Path = _marker(checker, command, each)
        with contextlib.suppress(OSError):
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.touch()
