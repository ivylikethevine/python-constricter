# SPDX-License-Identifier: MIT
"""The CPU seconds and the memory a process and everything under it used, read by `psutil` while it runs.

A step's own count (`resource.getrusage`) has only the processes it waited for, which leaves out
constricter's workers: the fork server starts them, and no one waits for it. One thread reads each
watched process's tree every `_EVERY` seconds, and keeps the most each process in it was seen to
have used (a process is counted to its last reading before it ended), and the most memory the tree
held at one reading.
"""

import contextlib
import threading
from functools import partial
from typing import Final, NamedTuple, cast

import psutil

_EVERY: Final = 2.0  # seconds between readings
_WOKEN: Final = True  # what the thread's wait gives once it's told to stop


class Used(NamedTuple):
    """What a watched process's tree was seen to use: its CPU seconds, and the most memory at once (bytes)."""

    cpu: float = 0.0
    memory: int = 0


def _reading(root: int) -> dict[int, tuple[float, int]]:
    """Read the CPU seconds and the resident memory of process `root` and each process under it.

    Returns:
      Them, by each one's id; nothing for a process that ended.

    """
    found: dict[int, tuple[float, int]] = {}
    tree: list[psutil.Process] = []
    with contextlib.suppress(psutil.Error):
        top: psutil.Process = psutil.Process(root)
        tree = [top, *top.children(recursive=True)]
    process: psutil.Process
    for process in tree:
        with contextlib.suppress(psutil.Error), process.oneshot():  # it may have ended since it was listed
            user: float
            system: float
            user, system, *_ = process.cpu_times()
            # Its resident memory, the first field on every platform (the stubs know only three's).
            held: int = cast("tuple[int, ...]", process.memory_info())[0]
            found[process.pid] = (user + system, held)
    return found


class Sampler:
    """Counts the CPU seconds and the memory of each watched process's tree, from a thread of its own."""

    def __init__(self) -> None:
        """Start with nothing watched; the thread starts with the first `watch`."""
        self._lock: threading.Lock = threading.Lock()
        self._used: dict[int, dict[int, float]] = {}  # each watched process's tree: each one's seconds
        self._peak: dict[int, int] = {}  # the most each tree held at one reading
        self._wake: threading.Event = threading.Event()
        self._thread: threading.Thread | None = None

    def watch(self, root: int) -> None:
        """Start counting process `root` and what it starts."""
        with self._lock:
            self._used[root] = {}
            self._peak[root] = 0
            if self._thread is None:
                self._thread = threading.Thread(target=self._sample, daemon=True)
                self._thread.start()

    def used(self, root: int) -> Used:
        """Stop counting process `root`.

        Returns:
          What its tree was seen to use.

        """
        with self._lock:
            return Used(sum(self._used.pop(root, {}).values()), self._peak.pop(root, 0))

    def _sample(self) -> None:
        for _ in iter(partial(self._wake.wait, _EVERY), _WOKEN):
            self.read()

    def read(self) -> None:
        """Take one reading, for every watched process."""
        with self._lock:
            roots: list[int] = list(self._used)
        root: int
        for root in roots:
            found: dict[int, tuple[float, int]] = _reading(root)
            with self._lock:
                if root not in self._used:  # no longer watched
                    continue
                tree: dict[int, float] = self._used[root]
                process: int
                seconds: float
                for process, (seconds, _) in found.items():
                    tree[process] = max(tree.get(process, 0.0), seconds)
                self._peak[root] = max(self._peak[root], sum(memory for _, memory in found.values()))
