# SPDX-License-Identifier: MIT
"""What each of a run's steps is given of the machine: its CPUs and its memory, and when it starts.

Every step is a process of its own, started once the CPUs it's expected to keep busy and the memory
it's expected to hold are free (`Slots`). A step is expected to do what it did in the latest earlier
run under the run's output that measured it, one of its own label first (`before`: the CPU seconds
of every process under it over its seconds, half the machine's CPUs at most, and the most memory
they held at once, `_MARGIN` over). `check` and `census` read one check at `suffocate`, which the
first of them to start runs: each is expected to do the most either did. Unmeasured:

- a suite's tests keep its workers busy (`Plan.workers`) and hold `worker-memory` for each; traced,
  what its `tests` step held where only that one is measured; a `heavy` suite's hold all there is.
  Measured, they hold what they held for each worker then;
- a step that starts the type checkers (`infer-CHECKER`, a suite's type checks) keeps `_STEP_CPUS`
  busy and holds `_UNSIZED_SHARE` of the memory: their servers', of no known size;
- any other keeps `_STEP_CPUS` busy (a check runs in bursts between stretches in one process) and
  holds `_JOB_MEMORY` for each of constricter's `--jobs`.

A step that wants all the memory there is, or more, runs alone. A suite's tests start once half the
CPUs they want are free, or `_MOST_SHARE` of the machine's, and take as many more as are free then,
with as many workers, and the memory for each (`Slots.take`). The timed steps (`timing`,
`profile`) want every CPU, so nothing runs beside the check timed: the run starts them last, one at
a time.

Of the steps waiting, the one with the most seconds still to come starts first: its own and those
of its corpus's suite's steps after it, which wait for it. One that has waited `_PATIENCE` seconds
for what smaller ones keep taking has what's free kept for it. And a running step's hold follows
what it's seen to use (`Plan.fitted`): an unmeasured one gives back what it isn't using, and any
one takes what it uses over its share from the next to start.

The steps share the machine's CPUs and `_MEMORY_SHARE` of the memory free as the run starts, unless
the run file says (`cpus`, `memory`). Where a user's systemd runs, each step starts in a scope of
its own (`scope`), whose control group the kernel counts whole: its CPU seconds and its peak memory,
a fork server's workers and what lives between two readings too (`counted`). Elsewhere a step's use
is read by `corpora_cpu`, which needs `psutil`: without it nothing is measured, and every step is
sized as unmeasured.
"""

import contextlib
import importlib
import importlib.util
import json
import math
import os
import re
import shutil
import subprocess  # starts a scope, to see that it's counted
import sys
import threading
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final, NamedTuple, Protocol, cast

from constricter.rules import parsed
from tests.corpus.catalog import Suite
from tests.corpus.pipeline import INFER, PROFILE, SHARING, TESTS, TIMING, TRACED, TYPES, Record
from tests.corpus.run_config import Run
from tests.corpus.trees import Tree

GIB: Final = 1 << 30
USED: Final = "used"  # in a step's record: what its process tree used, and what it was given
WORKERS: Final = "workers"  # in `USED`, a suite's tests': how many ran them
SCOPE: Final = "scope"  # in a step's record as it ends: what its control group counted
SCOPED: Final = "CORPUS_SCOPED"  # in a step's environment: it started in a scope of its own
_STEP_CPUS: Final = 2  # what a step other than a suite's tests keeps busy, unmeasured
_TESTS_MEMORY: Final = 2  # the run's memory a suite's tests' workers may fill: a half
_MEMORY_SHARE: Final = 0.8  # of the memory free as the run starts: the rest is for what else runs
_MARGIN: Final = 1.25  # over the most a step was seen to hold: its readings are seconds apart
_JOB_MEMORY: Final = GIB + GIB // 4  # what a step holds for each of constricter's `--jobs`, unmeasured
_UNSIZED_SHARE: Final = 3  # the unmeasured steps starting the type checkers that the memory is split among
_MOST_SHARE: Final = 2  # the most CPUs a step is given: the CPUs over this, or it waits for most to be idle
TESTING: Final = frozenset({TESTS, TRACED})  # the steps that run a suite's tests, with so many workers
_CHAIN: Final = (TRACED, TESTS, TYPES)  # a suite's steps, each waiting for the one before it
_PATIENCE: Final = 300.0  # the seconds a step waits before what's free is kept for it
_SLACK: Final = 2.0  # over what an unmeasured step holds a minute in: it may hold more later
TIMED: Final = frozenset({TIMING, PROFILE})  # the steps nothing runs beside
_AVAILABLE: Final = re.compile(r"^MemAvailable:\s*(\d+) kB", re.MULTILINE)
_MEMINFO: Final = Path("/proc/meminfo")
_STAMPED: Final = re.compile(r"(-\d+){4}$")  # after a run's label in its folder's name: when it started
_UNKNOWN: Final = 1 << 62  # the bytes shared where the machine doesn't say what it has: every step fits
_CGROUPS: Final = Path("/sys/fs/cgroup")
_PROC: Final = Path("/proc")
_UNIFIED: Final = "0::"  # a process's control group in the unified hierarchy, in `/proc/PID/cgroup`
_COUNTS: Final = ("cpu.stat", "memory.peak")  # in a control group's folder
_USAGE: Final = re.compile(r"^usage_usec (\d+)$", re.MULTILINE)  # in `cpu.stat`
_LINUX: Final = "linux"
_SYSTEMD_RUN: Final = "systemd-run"
_SCOPE: Final = (_SYSTEMD_RUN, "--user", "--scope", "--quiet", "--collect")  # then the command, run in it
_PROBE: Final = (  # run in a scope by `scope`: whether its control group counts it
    "import sys; from tests.corpus import sizing; sys.exit(sizing.counted(sizing.group()) is None)"
)


class Used(NamedTuple):
    """What a watched process's tree was seen to use: its CPU seconds, and the most memory at once (bytes)."""

    cpu: float = 0.0
    memory: int = 0


class Watcher(Protocol):
    """What counts a process tree's use while it runs: `corpora_cpu.Sampler`."""

    def watch(self, root: int) -> None:
        """Start counting process `root` and what it starts."""

    def seen(self, root: int) -> tuple[float, int]:
        """Say what its tree has used so far: its CPU seconds, and its most bytes at once."""
        raise NotImplementedError

    def used(self, root: int) -> tuple[float, int]:
        """Stop counting it, and say what its tree used: its CPU seconds, and its most bytes at once."""
        raise NotImplementedError


@dataclass(eq=False)
class _Waiter:
    """A step waiting for its turn: how long it and what's behind it last, what it wants, since when."""

    lasting: float
    cpus: int
    memory: int
    since: float


def group(process: int | None = None) -> Path | None:
    """Find a process's control group: this one's, by default.

    Returns:
      Its folder; `None` where the system has no unified hierarchy.

    """
    try:
        said: str = (_PROC / str(process or "self") / "cgroup").read_text(encoding="ascii")
    except OSError:
        return None
    line: str
    for line in said.splitlines():
        if line.startswith(_UNIFIED):
            return _CGROUPS / line.removeprefix(_UNIFIED).lstrip("/")
    return None


def counted(folder: Path | None) -> Used | None:
    """Read what every process in a control group used, those that ended too.

    Returns:
      Its CPU seconds (`cpu.stat`) and the most memory it held at once (`memory.peak`); `None` where
      the kernel doesn't count one of them.

    """
    if folder is None:
        return None
    stat: str
    peak: str
    try:
        stat, peak = ((folder / each).read_text(encoding="ascii").strip() for each in _COUNTS)
    except OSError:
        return None
    usage: re.Match[str] | None = _USAGE.search(stat)
    return Used(int(usage[1]) / 1e6, int(peak)) if usage is not None and peak.isdigit() else None


def scope(root: Path) -> tuple[str, ...]:
    """Find how to start a step in a scope of its own, which its control group then counts (`counted`).

    `root`: the checkout, where the probe imports this module.

    Returns:
      The command a step runs under: `systemd-run`'s, where it starts a scope whose CPU and memory
      the kernel counts; else nothing.

    """
    if sys.platform != _LINUX or shutil.which(_SYSTEMD_RUN) is None:
        return ()
    probe: list[str] = [*_SCOPE, sys.executable, "-c", _PROBE]
    try:
        done: subprocess.CompletedProcess[bytes] = subprocess.run(
            probe,
            cwd=root,
            capture_output=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ()
    return _SCOPE if done.returncode == 0 else ()


class Grouped:
    """Counts a step started in a scope of its own by its control group, as it runs."""

    def __init__(self) -> None:
        """Start with nothing watched."""
        self.own: Path | None = group()  # the runner's: a step's until `systemd-run` moves it
        self.last: dict[int, Used] = {}

    def watch(self, root: int) -> None:
        """Start counting process `root`'s scope."""
        self.last[root] = Used()

    def seen(self, root: int) -> Used:
        """Say what process `root`'s scope has used so far: as last read, if it has ended.

        Returns:
          It.

        """
        folder: Path | None = group(root)
        found: Used | None = None if folder == self.own else counted(folder)
        self.last[root] = found if found is not None else self.last.get(root, Used())
        return self.last[root]

    def used(self, root: int) -> Used:
        """Stop counting process `root`'s scope.

        Returns:
          What it used, as last read: the step itself reads its whole count as it ends (`SCOPE`).

        """
        _ = self.seen(root)
        return self.last.pop(root, Used())


def watcher(*, scoped: bool = False) -> Watcher | None:
    """Find what counts a step's use.

    `scoped`: each step starts in a scope of its own (`scope`).

    Returns:
      The control group's count, for a step in a scope; else `corpora_cpu`'s sampler; `None` where
      `psutil` isn't installed.

    """
    if scoped:
        return Grouped()
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
        self.waiting: list[_Waiter] = []

    def _fits(self, cpus: int, memory: int) -> bool:
        """Check that `cpus` are free and `memory` bytes are; a step alone has the memory, whatever it wants.

        Returns:
          Whether they are.

        """
        return self.free >= cpus and (self.held + memory <= self.memory or not self.running)

    def _turn(self, waiter: _Waiter) -> bool:
        """Check whether a waiting step may start: it fits, and none waiting goes before it (see `take`).

        Returns:
          Whether it may.

        """
        if not self._fits(waiter.cpus, waiter.memory):
            return False
        if waiter.memory >= self.memory:  # it runs alone: nothing is running
            return True
        if any(other.memory >= self.memory for other in self.waiting):
            return False
        kept: float = time.monotonic() - _PATIENCE
        # Those that came before it, by their place: a coarse clock gives two the same time.
        ahead: list[_Waiter] = self.waiting[: self.waiting.index(waiter)]
        if any(other.since <= kept and not self._fits(other.cpus, other.memory) for other in ahead):
            return False
        return not any(
            other.lasting > waiter.lasting and self._fits(other.cpus, other.memory) for other in self.waiting
        )

    def take(self, wanted: int, memory: int = 0, lasting: float = 0.0, least: int = 0) -> int:
        """Wait until `wanted` CPUs and `memory` bytes are free, and hold them.

        All the CPUs, for more than there are. `least`: the fewest it may start with, then holding
        as many more as are free, and `share` of the memory. `lasting`: the seconds the step and what
        waits for it are expected to take; of the steps waiting, one that lasts longer and fits
        what's free goes before it, so the long steps aren't the last to start. One that wants all
        the memory goes before any that wants less: it runs once those running have ended. And one
        that has waited `_PATIENCE` seconds without fitting goes before any that came after it.

        Returns:
          How many CPUs are held, to `give` back with their `share` of the memory.

        """
        most: int = max(1, min(wanted, self.cpus))
        held: int = max(1, min(least or most, most))
        with self.changed:
            waiter: _Waiter = _Waiter(lasting, held, self.share(wanted, memory, held), time.monotonic())
            self.waiting.append(waiter)
            _ = self.changed.wait_for(lambda: self._turn(waiter))
            self.waiting.remove(waiter)
            fitting: list[int] = [
                count
                for count in range(most, held, -1)
                if self._fits(count, self.share(wanted, memory, count))
            ]
            held = fitting[0] if fitting else held  # as many as are free
            self.free -= held
            self.held += self.share(wanted, memory, held)
            self.running += 1
            self.changed.notify_all()  # one that waited behind this may fit what's left
        return held

    def share(self, wanted: int, memory: int, held: int) -> int:
        """Find what of `memory` a step that wants `wanted` CPUs holds with `held` of them: as much for each.

        Returns:
          The bytes.

        """
        return memory * held // max(1, min(wanted, self.cpus))

    def resize(self, held: tuple[int, int], now: tuple[int, int]) -> tuple[int, int]:
        """Change what a running step holds, its CPUs and its bytes, from `held` to `now`.

        More than is free too: the next step then waits for it.

        Returns:
          What it holds now.

        """
        with self.changed:
            self.free += held[0] - now[0]
            self.held += now[1] - held[1]
            self.changed.notify_all()
        return now

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
    workers: int = 0  # a suite's tests': how many ran them; 0 where the record doesn't say


def before(output: Path, run: Path) -> dict[tuple[str, str], Before]:
    """Read what each step did in the latest earlier run under `output` that measured it.

    A run with this one's label, if any measured it: a probe's or a stopped run's steps under another
    label size only what none of its own has. `run`: this run's folder, whose own records say nothing
    of a step still to run.

    Returns:
      Each step's use, by its corpus's directory and its name.

    """
    label: str = _STAMPED.sub("", run.name)
    earlier: list[Path] = sorted(
        (each for each in output.glob("*/records") if each.parent != run),
        key=lambda each: (_STAMPED.sub("", each.parent.name) == label, each.stat().st_mtime),
    )
    found: dict[tuple[str, str], Before] = {}
    kept: Path
    for kept in (kept for records in earlier for kept in sorted(records.glob("*/*/*.json"))):
        used: Record = {}
        with contextlib.suppress(OSError, ValueError):
            used = cast("Record", cast("Record", json.loads(kept.read_text(encoding="utf-8"))).get(USED, {}))
        seconds: float = cast("float", used.get("seconds", 0.0))
        cpu: float = cast("float", used.get("cpu", 0.0))
        if seconds and cpu:
            held: int = int(cast("float", used.get("memory", 0.0)) * GIB)
            workers: int = cast("int", used.get(WORKERS, 0))
            found[kept.parent.parent.name, kept.stem] = Before(cpu / seconds, seconds, held, workers)
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
    """What a step is expected to take: the CPUs, the bytes, and the seconds it and what waits for it last."""

    cpus: int
    memory: int
    lasting: float = 0.0
    measured: bool = False  # by an earlier run: held to it, unless it uses more
    least: int = 0  # the fewest CPUs it may start with, `memory` shared out among them (`Slots.take`)


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
        fitting: int = int(self.memory / _TESTS_MEMORY / (suite.worker_memory * GIB))
        return max(1, min(suite.most, self.run.suite_workers or self.cpus, fitting))

    def wanted(self, tree: Tree, step: str, *, heavy: bool = False) -> Wanted:
        """Estimate what a step takes (see the module's docstring).

        `heavy`: the corpus's suite's tests hold more than a machine has to share.

        Returns:
          The CPUs it keeps busy, the memory it holds at most, and how long it lasts.

        """
        directory: str = tree.name.replace(" ", "-")
        known: Before | None = self.before.get((directory, step))
        if step in SHARING:  # either may run their one check: the most either took
            both: list[Before] = [
                self.before[directory, each] for each in sorted(SHARING) if (directory, each) in self.before
            ]
            if both:
                known = Before(*(max(each) for each in zip(*both, strict=True)))
        behind: tuple[str, ...] = _CHAIN[_CHAIN.index(step) + 1 :] if step in _CHAIN else _CHAIN
        lasting: float = sum(
            self.before[directory, each].seconds
            for each in (step, *(behind if tree.suite is not None else ()))
            if (directory, each) in self.before
        )
        if step in TESTING and tree.suite is not None:
            tested: Before | None = self.before.get((directory, TESTS)) if step == TRACED else None
            return self._testing(tree.suite, (known, tested), lasting, heavy=heavy)
        cpus: int = math.ceil(known.cpus) if known is not None else _STEP_CPUS
        cpus = min(cpus, max(_STEP_CPUS, self.cpus // _MOST_SHARE))
        memory: int
        if known is not None and known.memory:
            memory = int(known.memory * _MARGIN)
        elif step.startswith(INFER) or step == TYPES:
            memory = self.memory // _UNSIZED_SHARE
        else:
            memory = (self.run.jobs or self.cpus) * _JOB_MEMORY
        return Wanted(self.cpus if step in TIMED else cpus, memory, lasting, known is not None)

    def _testing(
        self,
        suite: Suite,
        known: tuple[Before | None, Before | None],
        lasting: float,
        *,
        heavy: bool,
    ) -> Wanted:
        """Estimate what a suite's tests take: a CPU for each worker, and the memory for each.

        `known`: the step's last run, and its tests' where it's traced. Each worker is expected to
        hold what one held in the first of them that says how many ran, a margin over; else its
        `worker-memory`. A `heavy` suite's hold all there is.

        Returns:
          What they take, and the fewest CPUs they start with.

        """
        workers: int = self.workers(suite)
        least: int = min(workers, max(_STEP_CPUS, self.cpus // _MOST_SHARE))
        if heavy:
            return Wanted(workers, self.memory, lasting, least=least)
        runs: list[Before]
        if not (runs := [each for each in known if each is not None and each.workers]):
            return Wanted(workers, int(workers * suite.worker_memory * GIB), lasting, least=least)
        memory: int = int(runs[0].memory * _MARGIN * workers / runs[0].workers)
        return Wanted(workers, memory, lasting, measured=runs[0] is known[0], least=least)

    def fitted(self, wanted: Wanted, held: tuple[int, int], busy: float, peak: int) -> tuple[int, int]:
        """Fit a running step's hold to what it's seen to use: `busy` CPUs of late, `peak` bytes at most.

        `held`: its CPUs and its bytes now. A measured step keeps what its last run took, and an
        unmeasured one gives back what it isn't using, `_SLACK` over what it holds; either takes
        what it uses over that. Not a step that runs alone.

        Returns:
          The CPUs and the bytes to hold.

        """
        if wanted.cpus >= self.cpus or wanted.memory >= self.memory:
            return held
        using: int = max(1, min(math.ceil(busy), self.cpus))
        holding: int = int(peak * _MARGIN)
        if wanted.measured:
            return max(wanted.cpus, using), max(wanted.memory, holding)
        return using, min(max(int(peak * _SLACK), holding), max(wanted.memory, holding))


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
