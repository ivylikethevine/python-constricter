# SPDX-License-Identifier: MIT
"""What each of a run's steps is given of the machine: its CPUs and its memory, and when it starts.

Every step is a process of its own, started once the CPUs it's expected to keep busy and the memory
it's expected to hold are free (`Slots`). A step is expected to do what it did in the latest earlier
run under the run's output that measured it (`before`: the CPU seconds of every process under it
over its seconds, and the most memory they held at once, `_MARGIN` over). Unmeasured:

- a suite's tests keep its workers busy (`Plan.workers`) and hold `worker-memory` for each; traced,
  what its `tests` step held where only that one is measured; a `heavy` suite's hold all there is;
- a step that starts the type checkers (`infer-CHECKER`, a suite's type checks) keeps `_STEP_CPUS`
  busy and holds `_UNSIZED_SHARE` of the memory: their servers', of no known size;
- any other keeps `_STEP_CPUS` busy (a check runs in bursts between stretches in one process) and
  holds `_JOB_MEMORY` for each of constricter's `--jobs`.

A step that wants all the memory there is, or more, runs alone. The timed steps (`timing`,
`profile`) want every CPU, so nothing runs beside the check timed: they start once the rest is idle.

The steps share the machine's CPUs and `_MEMORY_SHARE` of the memory free as the run starts, unless
the run file says (`cpus`, `memory`). A step's use is read by `corpora_cpu`, which needs `psutil`:
without it nothing is measured, and every step is sized as unmeasured.
"""

import contextlib
import importlib
import importlib.util
import json
import math
import os
import re
import threading
from collections.abc import Mapping
from pathlib import Path
from typing import Final, NamedTuple, Protocol, cast

from constricter.rules import parsed
from tests.corpus.catalog import Suite
from tests.corpus.pipeline import INFER, PROFILE, TESTS, TIMING, TRACED, TYPES, Record
from tests.corpus.run_config import Run
from tests.corpus.trees import Tree

GIB: Final = 1 << 30
USED: Final = "used"  # in a step's record: what its process tree used, and what it was given
_STEP_CPUS: Final = 2  # what a step other than a suite's tests keeps busy, unmeasured
_WORKERS_SHARE: Final = 2  # the most workers a suite's tests take: the CPUs over this
_MEMORY_SHARE: Final = 0.8  # of the memory free as the run starts: the rest is for what else runs
_MARGIN: Final = 1.25  # over the most a step was seen to hold: its readings are seconds apart
_JOB_MEMORY: Final = GIB + GIB // 4  # what a step holds for each of constricter's `--jobs`, unmeasured
_UNSIZED_SHARE: Final = 3  # the unmeasured steps starting the type checkers that the memory is split among
_EARLIER: Final = 4  # the earlier runs read for what a step did
_TESTING: Final = frozenset({TESTS, TRACED})  # the steps that run a suite's tests
TIMED: Final = frozenset({TIMING, PROFILE})  # the steps nothing runs beside
_AVAILABLE: Final = re.compile(r"^MemAvailable:\s*(\d+) kB", re.MULTILINE)
_MEMINFO: Final = Path("/proc/meminfo")
_UNKNOWN: Final = 1 << 62  # the bytes shared where the machine doesn't say what it has: every step fits


class Used(NamedTuple):
    """What a watched process's tree was seen to use: its CPU seconds, and the most memory at once (bytes)."""

    cpu: float = 0.0
    memory: int = 0


class Watcher(Protocol):
    """What counts a process tree's use while it runs: `corpora_cpu.Sampler`."""

    def watch(self, root: int) -> None:
        """Start counting process `root` and what it starts."""

    def used(self, root: int) -> tuple[float, int]:
        """Stop counting it, and say what its tree used: its CPU seconds, and its most bytes at once."""
        raise NotImplementedError


def watcher() -> Watcher | None:
    """Find what counts a step's use.

    Returns:
      `corpora_cpu`'s sampler; `None` where `psutil` isn't installed.

    """
    if importlib.util.find_spec("psutil") is None:
        return None
    return cast("type[Watcher]", importlib.import_module("tests.corpus.corpora_cpu").Sampler)()


class Slots:
    """The machine's CPUs and memory, shared out among the steps running.

    Each holds the CPUs it's expected to keep busy, and the memory it's expected to hold.
    """

    def __init__(self, cpus: int, memory: int) -> None:
        """Start with every one of `cpus` free, and `memory` bytes."""
        self.cpus: int = cpus
        self.free: int = cpus
        self.memory: int = memory
        self.held: int = 0  # the bytes the running steps are expected to hold
        self.running: int = 0
        self.changed: threading.Condition = threading.Condition()
        # How long each waiting step lasts, and the CPUs and the memory it wants.
        self.waiting: list[tuple[float, int, int]] = []

    def _fits(self, cpus: int, memory: int) -> bool:
        """Check that `cpus` are free and `memory` bytes are; a step alone has the memory, whatever it wants.

        Returns:
          Whether they are.

        """
        return self.free >= cpus and (self.held + memory <= self.memory or not self.running)

    def _turn(self, waiter: tuple[float, int, int]) -> bool:
        """Check whether a waiting step may start: it fits, and none waiting goes before it (see `take`).

        Returns:
          Whether it may.

        """
        lasting: float
        memory: int
        lasting, _, memory = waiter
        if not self._fits(waiter[1], memory):
            return False
        if memory >= self.memory:  # it runs alone: nothing is running
            return True
        if any(needs >= self.memory for _, _, needs in self.waiting):
            return False
        return not any(longer > lasting and self._fits(cpus, needs) for longer, cpus, needs in self.waiting)

    def take(self, wanted: int, memory: int = 0, lasting: float = 0.0) -> int:
        """Wait until `wanted` CPUs and `memory` bytes are free, and hold them.

        All the CPUs, for more than there are. `lasting`: the seconds the step is expected to take;
        of the steps waiting, one that lasts longer and fits what's free goes before it, so the long
        steps aren't the last to start. And one that wants all the memory goes before any that
        wants less: it runs once those running have ended.

        Returns:
          How many CPUs are held, to `give` back with the memory.

        """
        held: int = max(1, min(wanted, self.cpus))
        with self.changed:
            waiter: tuple[float, int, int] = (lasting, held, memory)
            self.waiting.append(waiter)
            _ = self.changed.wait_for(lambda: self._turn(waiter))
            self.waiting.remove(waiter)
            self.free -= held
            self.held += memory
            self.running += 1
            self.changed.notify_all()  # one that waited behind this may fit what's left
        return held

    def give(self, held: int, memory: int = 0) -> None:
        """Free the CPUs and the memory a step held."""
        with self.changed:
            self.free += held
            self.held -= memory
            self.running -= 1
            self.changed.notify_all()


class Before(NamedTuple):
    """What a step did in an earlier run: the CPUs it kept busy, its seconds, and the bytes it held."""

    cpus: float
    seconds: float
    memory: int


def before(output: Path, run: Path) -> dict[tuple[str, str], Before]:
    """Read what each step did in the latest earlier runs under `output` that measured it.

    `run`: this run's folder, whose own records say nothing of a step still to run.

    Returns:
      Each step's use, by its corpus's directory and its name.

    """
    earlier: list[Path] = sorted(
        (each for each in output.glob("*/records") if each.parent != run),
        key=lambda each: each.stat().st_mtime,
    )
    found: dict[tuple[str, str], Before] = {}
    kept: Path
    for kept in (kept for records in earlier[-_EARLIER:] for kept in sorted(records.glob("*/*/*.json"))):
        used: Record = {}
        with contextlib.suppress(OSError, ValueError):
            used = cast("Record", cast("Record", json.loads(kept.read_text(encoding="utf-8"))).get(USED, {}))
        seconds: float = cast("float", used.get("seconds", 0.0))
        cpu: float = cast("float", used.get("cpu", 0.0))
        if seconds and cpu:
            held: int = int(cast("float", used.get("memory", 0.0)) * GIB)
            found[kept.parent.parent.name, kept.stem] = Before(cpu / seconds, seconds, held)
    return found


def available() -> int | None:
    """Read the memory free for the run's steps as it starts.

    Returns:
      It, in bytes: what the system says is available, within this process's limit
      (`parsed.memory`); `None` where it says neither.

    """
    limit: int | None = parsed.memory()
    try:
        free: re.Match[str] | None = _AVAILABLE.search(_MEMINFO.read_text(encoding="ascii"))
    except OSError:
        return limit
    return limit if free is None else min(int(free[1]) * 1024, limit or int(free[1]) * 1024)


class Wanted(NamedTuple):
    """What a step is expected to take: the CPUs, the bytes, and its seconds (0: unmeasured)."""

    cpus: int
    memory: int
    lasting: float = 0.0


class Plan(NamedTuple):
    """A run sized for a machine: the CPUs and the memory its steps share, and what each did before."""

    run: Run
    cpus: int
    memory: int  # bytes
    before: Mapping[tuple[str, str], Before]

    def workers(self, suite: Suite) -> int:
        """Size a suite's tests' processes: what it can keep busy, within the run's share of the CPUs.

        Returns:
          How many.

        """
        return max(1, min(suite.most, self.run.suite_workers or self.cpus // _WORKERS_SHARE))

    def wanted(self, tree: Tree, step: str, *, heavy: bool = False) -> Wanted:
        """Estimate what a step takes (see the module's docstring).

        `heavy`: the corpus's suite's tests hold more than a machine has to share.

        Returns:
          The CPUs it keeps busy, the memory it holds at most, and how long it lasts.

        """
        directory: str = tree.name.replace(" ", "-")
        known: Before | None = self.before.get((directory, step))
        tested: Before | None = self.before.get((directory, TESTS)) if step == TRACED else None
        testing: bool = step in _TESTING and tree.suite is not None
        workers: int = self.workers(tree.suite) if tree.suite is not None else 1
        cpus: int = math.ceil(known.cpus) if known is not None else workers if testing else _STEP_CPUS
        memory: int
        if known is not None and known.memory:
            memory = int(known.memory * _MARGIN)
        elif tested is not None and tested.memory:
            memory = int(tested.memory * _MARGIN)
        elif testing:
            memory = self.memory if heavy else int(workers * cast("Suite", tree.suite).worker_memory * GIB)
        elif step.startswith(INFER) or step == TYPES:
            memory = self.memory // _UNSIZED_SHARE
        else:
            memory = (self.run.jobs or self.cpus) * _JOB_MEMORY
        return Wanted(self.cpus if step in TIMED else cpus, memory, known.seconds if known else 0.0)


def plan(run: Run, folder: Path, root: Path) -> Plan:
    """Size `run` for this machine, from what its steps did before (see the module's docstring).

    `folder`: the run's own; `root`: what its output is relative to.

    Returns:
      The plan.

    """
    cpus: int = run.cpus or os.cpu_count() or 1
    free: int | None = available()
    memory: int = int(run.memory * GIB) if run.memory else int((free or 0) * _MEMORY_SHARE)
    return Plan(run, cpus, memory or _UNKNOWN, before(root / run.output, folder))
