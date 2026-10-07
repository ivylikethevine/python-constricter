# SPDX-License-Identifier: MIT
"""The CPU seconds a process and everything under it used, read from `/proc` while it runs.

A step's own count (`resource.getrusage`) has only the processes it waited for, which leaves out
constricter's workers: the fork server starts them, and no one waits for it. One thread reads every
process's parent and CPU time every `_EVERY` seconds, and keeps the most each process under a
watched one was seen to have used: a process is counted to its last reading before it ended. Where
there's no `/proc`, nothing is counted.
"""

import os
import threading
from functools import partial
from pathlib import Path
from typing import Final

_PROC: Final = Path("/proc")
_EVERY: Final = 2.0  # seconds between readings
_STATE: Final = 0  # a `stat` line's fields after the command's name: its state, then its parent
_PARENT: Final = 1
_USER: Final = 11
_SYSTEM: Final = 12
_WOKEN: Final = True  # what the thread's wait gives once it's told to stop


def _readings() -> dict[int, tuple[int, int]]:
    """Read every process's parent and the clock ticks it has used.

    Returns:
      Them, by its id; none where `/proc` can't be read.

    """
    found: dict[int, tuple[int, int]] = {}
    try:
        entries: list[Path] = [entry for entry in _PROC.iterdir() if entry.name.isdigit()]
    except OSError:
        return found
    entry: Path
    for entry in entries:
        try:
            line: str = (entry / "stat").read_text(encoding="utf-8", errors="replace")
        except OSError:  # it ended since it was listed
            continue
        fields: list[str] = line.rpartition(")")[2].split()  # a command's name may hold spaces
        if len(fields) > _SYSTEM and fields[_STATE]:
            found[int(entry.name)] = (int(fields[_PARENT]), int(fields[_USER]) + int(fields[_SYSTEM]))
    return found


def _watched(
    process: int,
    found: dict[int, tuple[int, int]],
    watched: dict[int, dict[int, int]],
) -> int | None:
    """Find the watched process a process is, or is under.

    Returns:
      Its id, or `None`.

    """
    above: int = process
    for _ in found:  # no deeper than there are processes
        if above in watched:
            return above
        if above not in found:
            break
        above = found[above][0]
    return None


class Sampler:
    """Counts the CPU seconds of each watched process's tree, from a thread of its own."""

    def __init__(self) -> None:
        """Start with nothing watched; the thread starts with the first `watch`."""
        self._lock: threading.Lock = threading.Lock()
        self._used: dict[int, dict[int, int]] = {}  # each watched process's tree: each one's ticks
        self._wake: threading.Event = threading.Event()
        self._thread: threading.Thread | None = None

    def watch(self, root: int) -> None:
        """Start counting process `root` and what it starts."""
        with self._lock:
            self._used[root] = {}
            if self._thread is None:
                self._thread = threading.Thread(target=self._sample, daemon=True)
                self._thread.start()

    def used(self, root: int) -> float:
        """Stop counting process `root`.

        Returns:
          The CPU seconds its tree was seen to use.

        """
        with self._lock:
            ticks: int = sum(self._used.pop(root, {}).values())
        return ticks / os.sysconf("SC_CLK_TCK")

    def _sample(self) -> None:
        for _ in iter(partial(self._wake.wait, _EVERY), _WOKEN):
            self.read()

    def read(self) -> None:
        """Take one reading, for every watched process."""
        found: dict[int, tuple[int, int]] = _readings()
        with self._lock:
            process: int
            ticks: int
            above: int | None
            for process, (_, ticks) in found.items():
                if (above := _watched(process, found, self._used)) is not None:
                    tree: dict[int, int] = self._used[above]
                    tree[process] = max(tree.get(process, 0), ticks)
