"""What each of a run's steps is given of the machine: its CPUs and its memory, and when it starts.

Every step is a process of its own, started once the CPUs it's expected to keep busy and the memory
it's expected to hold are free (`Slots`). A step is expected to do what it did in the latest earlier
run under the run's output that measured it, one of its own label first (`before`: the CPU seconds
of every process under it over its seconds, half the machine's CPUs at most, and the most memory
they held at once, `_MARGIN` over). `check` and `census` read one check at `suffocate`, which the
first of them to start runs: each is expected to do the most either did. Unmeasured:

- a suite's tests keep its workers busy (`Plan.workers`) and hold `worker-memory` for each; traced,
  what its `tests` step held where only that one is measured; a `heavy` suite's hold all there is.
  Measured, they hold what they held for each worker then, and the CPUs they kept busy, a margin
  over, with as many workers as then. Traced by its `script`, in one process,
  as any other step;
- a part of a suite's tests or type checks takes what its kind's largest measured part took (the
  released tests', say), or else its kind's whole step, its seconds shared among its parts;
- the fix with every checker (`infer-union`), asked in turn (`--infer-in-turn`), takes the memory
  the largest of its corpus's checkers' steps took, the most CPUs any kept busy, and their seconds
  together;
- a step that starts the type checkers (`infer-CHECKER`, a suite's type checks) keeps `_STEP_CPUS`
  busy and holds `_UNSIZED_SHARE` of the memory: their servers', of no known size;
- any other keeps `_STEP_CPUS` busy (a check runs in bursts between stretches in one process) and
  holds `_JOB_MEMORY` for each of constricter's `--jobs`.

A step that wants all the memory there is, or more, runs alone. A suite's tests start once half the
CPUs they want are free, or `_MOST_SHARE` of the machine's, and take as many more as are free then,
with as many workers, and the memory for each (`Slots.take`). A step that asks the type checkers
for hints starts with as few CPUs as hold, by their share of its memory, one server of each of its
checkers for the corpus (`Plan._hinted`), its servers then given that share of `hints.MEMORY`,
rounded up to whole servers of its largest checker, one a CPU held (`--infer-memory`,
`Wanted.hinted`); with all it wants, the default. Only one whose last run took `_BRIEF` seconds at
most starts short: it keeps what it started with, so a long one on one CPU would hold the run's end
(stripe's basedpyright, 36 minutes). The timed steps (`timing`,
`profile`) want every CPU, so nothing runs beside the check timed: the run starts them last, one at
a time.

Of the steps waiting, the one with the most seconds still to come starts first: its own and those
of its corpus's suite's steps after it, which wait for it. One that has waited `_PATIENCE` seconds
for what smaller ones keep taking has what's free kept for it, from all but those that go before it
and those its last run says end within `_BESIDE` seconds. And a running step's hold follows
what it's seen to use (`Plan.fitted`): an unmeasured one gives back what it isn't using, and any
one takes what it uses over its share from the next to start.

The steps share the machine's CPUs and `_MEMORY_SHARE` of the memory free as the run starts, unless
the run file says (`cpus`, `memory`), or a share of the machine (`share`, `--share`): that percent
of its CPUs and of its memory, no more than that much of what's free. Where its steps start in
scopes, a slice holds them to it together (`_sliced`), whatever they were sized to. Where a user's
systemd runs, each step starts in a scope of its own (`scope`), whose control group the kernel
counts whole: its CPU seconds and its peak memory, a fork server's workers and what lives between
two readings too (`counted`). Elsewhere a step's use is read by `corpora_cpu`, which needs `psutil`:
without it nothing is measured, and every step is sized as unmeasured.
"""

import importlib
import importlib.util
import math
import os
import re
import shutil
import subprocess  # starts a scope, to see that it's counted
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import cache, partial
from pathlib import Path
from typing import Final, NamedTuple, Protocol, cast

from constricter.cli import paths
from constricter.cli.lsp import hints
from constricter.cli.lsp.protocol import SERVERS, Server
from constricter.rules import parsed
from tests.corpus import archive
from tests.corpus.catalog import Suite
from tests.corpus.pipeline import (
    IMPLIED,
    INFER,
    PROFILE,
    SHARING,
    TESTS,
    TIMING,
    TRACED,
    TYPES,
    UNION,
    Record,
    parts,
)
from tests.corpus.run_config import Run, started
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
_UNION_STEP: Final = f"{INFER}{UNION}"
_MOST_SHARE: Final = 2  # the most CPUs a step is given: the CPUs over this, or it waits for most to be idle
_CHAIN: Final = (TRACED, TESTS, TYPES)  # a suite's kinds of step: their parts wait for the kind before


def testing(step: str) -> bool:
    """Check whether a step runs a suite's tests, with so many workers: its traced tests, or a part.

    Returns:
      Whether it does.

    """
    return step in {TESTS, TRACED} or step.startswith(f"{TESTS}-")


@cache
def _size(root: Path) -> int:  # the bytes of a tree's Python files, which its checkers' servers load
    return sum(path.stat().st_size for path in paths.python_files([root]))


def _kind(step: str) -> str:  # a suite step's kind: a part's, or its own
    return next((kind for kind in _CHAIN if step == kind or step.startswith(f"{kind}-")), step)


_PATIENCE: Final = 300.0  # the seconds a step waits before what's free is kept for it
_BESIDE: Final = 300.0  # but from a step expected to end within so many seconds
_SLACK: Final = 2.0  # over what an unmeasured step holds a minute in: it may hold more later
_BRIEF: Final = 300.0  # the most seconds a hinted step's last run took for it to start short (`Plan._hinted`)
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
_SYSTEMCTL: Final = "systemctl"
_SLICE: Final = "constricter-corpus.slice"  # a run's steps' scopes, held to its share (`_sliced`)
_WHOLE: Final = 100  # a share's percent of the whole machine
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
    seconds: float = 0.0  # its own, as its last run took: 0 where none did
    locks: tuple[threading.Lock, ...] = ()  # its checkouts' and its port's, taken as it starts
    name: str = ""  # its corpus and step, as the queue's log names it
    rank: float = math.inf  # when the run's plan starts it (`planning`): `inf` for one not planned


def _ahead(one: _Waiter, other: _Waiter) -> bool:
    """Check whether a waiting step goes before another: ranked first by the run's plan, else lasting longer.

    Returns:
      Whether it does.

    """
    return (one.rank, -one.lasting) < (other.rank, -other.lasting)


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


def scope(root: Path, held: "Plan | None" = None) -> tuple[str, ...]:
    """Find how to start a step in a scope of its own, which its control group then counts (`counted`).

    `root`: the checkout, where the probe imports this module. `held`: a run's plan, its CPUs and
    memory a share of the machine (`Run.share`), which its steps' scopes are held to together: in a
    slice whose CPU quota and memory ceiling are those, so what else runs has the rest.

    Returns:
      The command a step runs under: `systemd-run`'s, where it starts a scope whose CPU and memory
      the kernel counts, in that slice where one's asked for and systemd takes its limits; else
      nothing.

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
    if done.returncode:
        return ()
    return _SCOPE if held is None else (*_SCOPE, *_sliced(held))


def _sliced(held: "Plan") -> tuple[str, ...]:
    """Hold a run's steps to its share of the machine: a slice whose limits are its `Plan`'s CPUs and bytes.

    The memory a ceiling the kernel reclaims down to (`MemoryHigh`), not a limit that kills a step.

    Returns:
      `systemd-run`'s option putting a scope in it; nothing where systemd won't set them, and the
      share is only the steps' sizing.

    """
    limits: list[str] = [f"CPUQuota={held.cpus * _WHOLE}%", f"MemoryHigh={held.memory}"]
    try:
        done: subprocess.CompletedProcess[bytes] = subprocess.run(
            [_SYSTEMCTL, "--user", "set-property", "--runtime", _SLICE, *limits],
            capture_output=True,
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ()
    return () if done.returncode else (f"--slice={_SLICE}",)


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
        # Each running step's expected end (`inf` where nothing says), CPUs and bytes, by its name.
        self.ran: dict[str, tuple[float, int, int]] = {}

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
        if not self._ready(waiter):
            return False
        if waiter.memory >= self.memory:  # it runs alone: nothing is running
            return True
        if any(other.memory >= self.memory for other in self.waiting):
            return False
        # One ranked first goes first, but only one that could start now: one held back itself
        # would hold back the rest with it.
        return not any(
            _ahead(other, waiter) and self._ready(other) and not self._kept(other) for other in self.waiting
        ) and not self._kept(waiter)

    def _ready(self, waiter: _Waiter) -> bool:
        """Check that a waiting step fits what's free, its locks too: no other step holds one.

        Returns:
          Whether it does.

        """
        return self._fits(waiter.cpus, waiter.memory) and not any(lock.locked() for lock in waiter.locks)

    def _kept(self, waiter: _Waiter) -> bool:
        """Check whether a waiting step is held back for one before it (`_keeping`).

        Returns:
          Whether it is.

        """
        return self._keeping(waiter) is not None

    def _keeping(self, waiter: _Waiter) -> _Waiter | None:
        """Find one that came before a waiting step and has waited `_PATIENCE` seconds without fitting.

        What's free is kept for it, from all but a step that goes before it (`_ahead`: the run's plan
        starts it first, or it lasts longer), one whose last run ended within `_BESIDE` seconds, or
        one that's expected to end before what's running frees enough for it (`_shadow`): starting
        such a step doesn't keep the other waiting longer.

        Returns:
          The step it's held back for; `None` where none holds it back.

        """
        if 0 < waiter.seconds <= _BESIDE:
            return None
        now: float = time.monotonic()
        # Those that came before it, by their place: a coarse clock gives two the same time.
        other: _Waiter
        for other in self.waiting[: self.waiting.index(waiter)]:
            if other.since <= now - _PATIENCE and not self._ready(other) and not _ahead(waiter, other):
                shadow: float = self._shadow(other)  # `inf`: a step it waits on has no expected end
                if waiter.seconds and now + waiter.seconds <= shadow < math.inf:
                    continue  # it ends before the other could start
                return other
        return None

    def _shadow(self, waiter: _Waiter) -> float:
        """Find when what's running is expected to have freed enough for a waiting step to fit.

        Returns:
          The time (`time.monotonic`'s); `inf` where a step it waits on has no expected end.

        """
        free: int = self.free
        held: int = self.held
        end: float
        cpus: int
        memory: int
        for end, cpus, memory in sorted(self.ran.values()):
            if free >= waiter.cpus and held + waiter.memory <= self.memory:
                break
            free, held = free + cpus, held - memory
            if end == math.inf or (free >= waiter.cpus and held + waiter.memory <= self.memory):
                return end
        return time.monotonic() if free >= waiter.cpus and held + waiter.memory <= self.memory else math.inf

    def report(self) -> list[str]:
        """Say what's running, and why each step waiting waits: for the run's queue log.

        Returns:
          A line each.

        """
        now: float = time.monotonic()
        with self.changed:
            lines: list[str] = [
                f"running {name}: {cpus} CPUs, {memory / GIB:.1f} GB, "
                + ("end unknown" if end == math.inf else f"ends in {end - now:.0f}s")
                for name, (end, cpus, memory) in sorted(self.ran.items(), key=lambda each: each[1][0])
            ]
            lines.append(f"free: {self.free} of {self.cpus} CPUs, {(self.memory - self.held) / GIB:.1f} GB")
            lines += [
                f"waiting {each.name} {now - each.since:.0f}s: {self._why(each)}" for each in self.waiting
            ]
        return lines

    def _why(self, waiter: _Waiter) -> str:
        """Say why a waiting step waits (`_turn`).

        Returns:
          It.

        """
        if not self._fits(waiter.cpus, waiter.memory):
            return f"wants {waiter.cpus} CPUs and {waiter.memory / GIB:.1f} GB"
        if any(lock.locked() for lock in waiter.locks):
            return "its checkout or its port is in use"
        whole: list[_Waiter] = [other for other in self.waiting if other.memory >= self.memory]
        if waiter.memory < self.memory and whole:
            return f"{whole[0].name} wants all the memory"
        keeping: _Waiter | None
        if (keeping := self._keeping(waiter)) is not None:
            return f"what's free is kept for {keeping.name}"
        longer: list[_Waiter] = [
            other
            for other in self.waiting
            if _ahead(other, waiter) and self._ready(other) and not self._kept(other)
        ]
        return f"{longer[0].name} goes first" if longer else "starting"

    def take(
        self,
        wanted: "Wanted",
        locks: Sequence[threading.Lock] = (),
        name: str = "",
        rank: float = math.inf,
    ) -> int:
        """Wait until the CPUs and the memory a step `wanted` are free, and its `locks`, and hold them.

        All the CPUs, for more than there are. Its `least`: the fewest it may start with, then holding
        as many more as are free, and `share` of the memory. Its `lasting`: the seconds the step and what
        waits for it are expected to take; of the steps waiting, one that lasts longer and could
        start now goes before it, so the long steps aren't the last to start. One that wants all the
        memory goes before any that wants less: it runs once those running have ended. And one that
        has waited `_PATIENCE` seconds without fitting goes before any that came after it, but one
        that goes before it anyway, one whose own `seconds`, as its last run took, are `_BESIDE` at
        most, or one that's expected to end before the other could start. `locks`: those of the
        checkouts it works on and the port its tests bind, taken with the rest as it starts, none
        held while it waits. `name`: what the queue's log calls it (`report`), and `give` frees by.
        `rank`: when the run's plan starts it (`planning`); of the steps that could start, the one
        ranked first does, then the one that lasts longest.

        Returns:
          How many CPUs are held, to `give` back with their `share` of the memory, and the locks.

        """
        most: int = max(1, min(wanted.cpus, self.cpus))
        held: int = max(1, min(wanted.least or most, most))
        share: Callable[[int], int] = partial(self.share, wanted.cpus, wanted.memory)
        with self.changed:
            waiter: _Waiter = _Waiter(
                wanted.lasting,
                held,
                share(held),
                time.monotonic(),
                wanted.seconds,
                tuple(locks),
                name,
                rank,
            )
            self.waiting.append(waiter)
            _ = self.changed.wait_for(lambda: self._turn(waiter))
            self.waiting.remove(waiter)
            lock: threading.Lock
            for lock in locks:
                _ = lock.acquire(blocking=False)  # free: only steps taken here hold one
            fitting: list[int] = [count for count in range(most, held, -1) if self._fits(count, share(count))]
            held = fitting[0] if fitting else held  # as many as are free
            self.free -= held
            self.held += share(held)
            self.running += 1
            end: float = time.monotonic() + wanted.seconds if wanted.seconds else math.inf
            self.ran[name] = (end, held, share(held))
            self.changed.notify_all()  # one that waited behind this may fit what's left
        return held

    def share(self, wanted: int, memory: int, held: int) -> int:
        """Find what of `memory` a step that wants `wanted` CPUs holds with `held` of them: as much for each.

        Returns:
          The bytes.

        """
        return memory * held // max(1, min(wanted, self.cpus))

    def resize(self, held: tuple[int, int], now: tuple[int, int], name: str = "") -> tuple[int, int]:
        """Change what a running step, `name`d, holds: its CPUs and its bytes, from `held` to `now`.

        More than is free too: the next step then waits for it.

        Returns:
          What it holds now.

        """
        with self.changed:
            self.free += held[0] - now[0]
            self.held += now[1] - held[1]
            if name in self.ran:
                self.ran[name] = (self.ran[name][0], *now)
            self.changed.notify_all()
        return now

    def give(self, held: int, memory: int = 0, locks: Sequence[threading.Lock] = (), name: str = "") -> None:
        """Free the CPUs, the memory and the locks a step `name`d held."""
        with self.changed:
            self.free += held
            self.held -= memory
            self.running -= 1
            _ = self.ran.pop(name, None)
            lock: threading.Lock
            for lock in locks:
                lock.release()
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
    of a step still to run. A suite's part that read another's outcome (`IMPLIED`) ran no tests, and
    may run them next time: it measured nothing.

    Returns:
      Each step's use, by its corpus's directory and its name.

    """
    label: str = _STAMPED.sub("", run.name)
    earlier: list[Path] = sorted(
        (each for each in archive.runs(output) if each != run),
        key=lambda each: (_STAMPED.sub("", each.name) == label, started(each)),
    )
    found: dict[tuple[str, str], Before] = {}
    corpus: str
    step: str
    record: Record
    for (corpus, _, step), record in (
        each for folder in earlier for each in sorted(archive.kept(folder).items())
    ):
        used: Record = {} if IMPLIED in record else cast("Record", record.get(USED, {}))
        seconds: float = cast("float", used.get("seconds", 0.0))
        cpu: float = cast("float", used.get("cpu", 0.0))
        if seconds and cpu:
            held: int = int(cast("float", used.get("memory", 0.0)) * GIB)
            workers: int = cast("int", used.get(WORKERS, 0))
            found[corpus, step] = Before(cpu / seconds, seconds, held, workers)
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
    seconds: float = 0.0  # its own, as its last run took: 0 where none did
    workers: int = 0  # a suite's tests' processes, where they're more than its CPUs (`started`)
    servers: int = 0  # a hinted step's servers' bytes with every CPU it wants: `hints.MEMORY` (`hinted`)
    server: int = 0  # one of its largest checker's servers, for the corpus's files (`Plan._hinted`)

    def hinted(self, held: int) -> int:
        """Size the memory a hinted step's servers may use, holding `held` CPUs (`--infer-memory`).

        Returns:
          Its `servers`' bytes, as many fewer as it holds fewer CPUs, but whole servers for each CPU
          held, as many as all of them hold: a share between two leaves one, a CPU idle. 0 where it
          holds all it wants, or isn't hinted: its checkers' own default.

        """
        if not self.servers or held >= self.cpus:
            return 0
        whole: int = min(held, self.servers // self.server) * self.server if self.server else 0
        return max(self.servers * held // self.cpus, whole)

    def started(self, held: int) -> int:
        """Count the processes a suite's tests start with, holding `held` CPUs.

        Returns:
          Its `workers` for its every CPU held, as many fewer as it holds fewer; one a CPU where it
          has none of its own.

        """
        return max(1, self.workers * held // self.cpus) if self.workers else held


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
        known: Before | None = (
            self.before.get((directory, step))
            or self._parted(directory, step)
            or self._united(directory, step)
        )
        if step in SHARING:  # either may run their one check: the most either took
            both: list[Before] = [
                self.before[directory, each] for each in sorted(SHARING) if (directory, each) in self.before
            ]
            if both:
                known = Before(*(max(each) for each in zip(*both, strict=True)))
        behind: tuple[str, ...] = _CHAIN[_CHAIN.index(_kind(step)) + 1 :] if _kind(step) in _CHAIN else _CHAIN
        lasting: float = sum(
            self.before[directory, each].seconds
            for each in (step, *(behind if tree.suite is not None else ()))
            if (directory, each) in self.before
        )
        if testing(step) and tree.suite is not None and not (step == TRACED and tree.suite.script):
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
        seconds: float = known.seconds if known is not None else 0.0
        least: int
        server: int
        least, server = self._hinted(tree, step, cpus) if seconds <= _BRIEF else (0, 0)
        return Wanted(
            self.cpus if step in TIMED else cpus,
            memory,
            lasting,
            known is not None,
            least=least,
            seconds=seconds,
            servers=hints.MEMORY if least else 0,
            server=server,
        )

    def _hinted(self, tree: Tree, step: str, cpus: int) -> tuple[int, int]:
        """Find the fewest of `cpus` a step asking the type checkers for hints may start with.

        As few as hold, by their share of `hints.MEMORY`, one server of each of its checkers for
        the tree's files (`Server.fitting`): fewer, and a server's heap would be capped under what
        it holds.

        Returns:
          Them, and the bytes of one of its largest checker's servers; 0 and 0 for one asking none.

        """
        checkers: Sequence[str] = (
            self.run.steps.infer
            if step == _UNION_STEP
            else (step.removeprefix(INFER),)
            if step.startswith(INFER)
            else ()
        )
        named: list[Server]
        if not (named := [SERVERS[each] for each in checkers if each in SERVERS]):
            return 0, 0
        size: int = _size(tree.root)
        one: int = max(server.memory + server.per_byte * size for server in named)
        return min(cpus, max(1, math.ceil(cpus * one / hints.MEMORY))), one

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
        `worker-memory`. Measured itself, it holds the CPUs it kept busy, a margin over, as many
        workers on them as before: a suite's workers seldom all run at once. A `heavy` suite's hold
        all there is.

        Returns:
          What they take, and the fewest CPUs they start with.

        """
        workers: int = self.workers(suite)
        least: int = min(workers, max(_STEP_CPUS, self.cpus // _MOST_SHARE))
        seconds: float = known[0].seconds if known[0] is not None else 0.0
        if heavy:
            return Wanted(workers, self.memory, lasting, least=least, seconds=seconds)
        runs: list[Before]
        if not (runs := [each for each in known if each is not None and each.workers]):
            memory: int = int(workers * suite.worker_memory * GIB)
            return Wanted(workers, memory, lasting, least=least, seconds=seconds)
        memory = int(runs[0].memory * _MARGIN * workers / runs[0].workers)
        if runs[0] is not known[0]:  # traced, sized by its tests
            return Wanted(workers, memory, lasting, least=least, seconds=seconds)
        busy: int = max(1, min(workers, math.ceil(runs[0].cpus * _MARGIN)))
        return Wanted(
            busy,
            memory,
            lasting,
            measured=True,
            least=min(least, busy),
            seconds=seconds,
            workers=workers if busy < workers else 0,
        )

    def _parted(self, directory: str, step: str) -> Before | None:
        """Estimate a part of a suite's tests or type checks no run has measured, by its kind's others.

        As much as the kind's largest measured part took, by CPU seconds (the released tests'): a
        whole step's record holds what it did itself, little more than read its parts'. Else as much
        as the kind's whole took, its seconds shared among its parts.

        Returns:
          It; `None` for another step, or a kind no run has measured.

        """
        kind: str
        if (kind := _kind(step)) == step:
            return None
        measured: list[Before] = [
            known
            for (where, each), known in self.before.items()
            if where == directory and each.startswith(f"{kind}-")
        ]
        if measured:
            return max(measured, key=lambda known: known.cpus * known.seconds)
        whole: Before | None
        if (whole := self.before.get((directory, kind))) is None:
            return None
        return whole._replace(seconds=whole.seconds / max(1, len(parts(self.run, kind))))

    def _united(self, directory: str, step: str) -> Before | None:
        """Estimate the fix with every checker (`infer-union`), unmeasured, by its checkers' steps.

        Returns:
          It (see the module docstring); `None` for another step, or where no checker's is measured.

        """
        checkers: list[Before] = [
            self.before[directory, each]
            for each in (f"{INFER}{checker}" for checker in self.run.steps.infer)
            if (directory, each) in self.before
        ]
        if step != _UNION_STEP or not checkers:
            return None
        return Before(
            max(each.cpus for each in checkers),
            sum(each.seconds for each in checkers),
            max(each.memory for each in checkers),  # one checker's servers at a time
        )

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
    machine: int = os.cpu_count() or 1
    cpus: int = run.cpus or (max(1, machine * run.share // _WHOLE) if run.share else machine)
    free: int = int((available() or 0) * _MEMORY_SHARE)
    shared: int = (parsed.memory() or 0) * run.share // _WHOLE
    memory: int = int(run.memory * GIB) if run.memory else min(free, shared or free)
    return Plan(run, cpus, memory or _UNKNOWN, before(root / run.output, folder))
