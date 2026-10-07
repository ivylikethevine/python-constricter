# SPDX-License-Identifier: MIT
"""The files a type checker's server hung on, remembered between runs.

A server that hangs on a file costs the run its timeout twice, and a restart each time: once with
the file among others, once with it alone. The file's text, with the checker and its executable as
it was (its size and when it changed), names an empty file in the cache; while there's one, the
file is left without hints from the start. A new version of the checker, or a changed file, is
asked again.
"""

import contextlib
import hashlib
from collections.abc import Sequence
from pathlib import Path

from constricter.fix.index.installed import cache_directory


def _marker(checker: str, command: Sequence[str], text: str) -> Path:
    """Name what remembers that `checker`, started by `command`, hung on a file holding `text`.

    Returns:
      Its path in the cache.

    """
    version: str = ""
    with contextlib.suppress(OSError):
        version = _version(Path(command[0]))
    key: str = "\0".join((checker, command[0], version, text))
    return cache_directory().with_name("hung") / hashlib.sha256(key.encode("utf-8", "replace")).hexdigest()


def _version(executable: Path) -> str:  # which build of it: its size and when it changed
    return f"{executable.stat().st_size}:{executable.stat().st_mtime_ns}"


def hung(checker: str, command: Sequence[str], text: str) -> bool:
    """Check whether `checker` hung on a file holding `text`, in an earlier run.

    Returns:
      Whether it did.

    """
    return _marker(checker, command, text).exists()


def remember(checker: str, command: Sequence[str], text: str) -> None:
    """Remember that `checker` hung on a file holding `text`; nothing, where the cache can't be written."""
    marker: Path = _marker(checker, command, text)
    with contextlib.suppress(OSError):
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.touch()
