# SPDX-License-Identifier: MIT
"""Measure every corpus every way this checkout can, side by side, and record it in docs/RUNS.md.

  local/.venv/bin/python -m tests.corpus.super_corpora            # everything; a stopped run resumes
  local/.venv/bin/python -m tests.corpus.super_corpora --fresh    # forget what a stopped run finished
  local/.venv/bin/python -m tests.corpus.super_corpora --print    # print the section, don't record it
  local/.venv/bin/python -m tests.corpus.super_corpora NAME ...   # only these corpora, printed

The corpora are `tests/corpus/corpus_table.py`'s, and each one's steps `tests/corpus/corpora_steps.py`'s:
the table, the census, `--infer-with` each installed checker, its package's own tests and type
checks where `corpus_suite.SUITES` has it, and a timed check.

The machine sizes the run. Every step of every corpus starts once the CPUs it's expected to keep
busy are free (`Slots`): each works on a copy of its own, but a suite's type checks, which wait
for its tests on their checkout unless the plan gives them checkouts of their own (`Plan.apart`:
pandas's, whose checks take the longest), and the tests of suites that bind one port, one at a
time (`Plan.ports`). A step is expected to keep busy what it did in the last
run that measured it (the CPU seconds of every process under it, over its seconds: see
`corpora_cpu`); else its suite's workers for its tests
(`corpus_suite.workers`), and `_STEP_CPUS` for any other: one of constricter's checks in bursts
between stretches in one process, and a type checker runs in one or two. So a step in one process
doesn't hold a share of the machine it leaves idle, and constricter gets `_JOBS_SHARE` of the CPUs
as its `--jobs` for its bursts. The `check` steps run last, one at a time with every CPU, so their
timings are of the check alone. The corpora of `_FIRST` (pandas, whose chain is the longest) start
first, never wait for CPUs, and take `_FIRST_JOBS` times the others' `--jobs`: the run ends when
the longest chain does.

Each step is a process of its own, its result kept in `local/super-corpora/<version>-<stamp>/`
(the stamp: a hash of `constricter/`'s sources): a run that stopped starts again from the steps
it lacks, and a change to the code starts a new one. The section it writes, `## Super corpora`,
names the machine: timings don't compare across machines. It exits 1 on anything a fix broke (a
file that no longer compiles, a second pass with more to fix, a test's outcome changed, a type
error a certain fix or a guess added) or a step that failed, each listed on standard error. Run
it outside a sandbox: it starts worker processes, and the suites need the network once.
"""

import contextlib
import hashlib
import math
import os
import pickle
import shutil
import subprocess  # runs each step
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Final, NamedTuple, TextIO, TypeAlias, cast

from constricter import __version__
from constricter.rules import parsed
from tests.corpus import corpora_section, corpora_steps, corpus_suite, corpus_table
from tests.corpus.corpora_cpu import Sampler
from tests.corpus.corpora_steps import CHECK, Sizes, Step, Steps
from tests.corpus.corpus_table import Corpus

_ROOT: Final = Path(__file__).resolve().parents[2]
# Constricter's `--jobs`: the CPUs over this. With half of 16, a corpus's table and `--infer-with`
# steps took up to twice as long as with a quarter: each checker's servers are as many as the jobs.
_JOBS_SHARE: Final = 4
_WORKERS_SHARE: Final = 2  # the most workers a suite's tests take: the CPUs over this
_STEP_CPUS: Final = 2  # what a step other than a suite's tests keeps busy, unmeasured
_APART_CPUS: Final = 8  # and a suite's type checks on checkouts of their own, each fixed run at once
_FIRST: Final = ("pandas",)  # the corpora whose steps never wait: the longest chains
_FIRST_JOBS: Final = 2  # and how many times the others' `--jobs` theirs take (a checker's servers too)
_SLOTS_VARIABLE: Final = "CORPUS_SLOTS"  # how many CPUs the steps share, if not every one
_STEP_FLAG: Final = "--step"
_FRESH_FLAG: Final = "--fresh"
_PRINT_FLAG: Final = "--print"
_KEPT: Final = ".pickle"
# What an unreadable kept result raises: one an earlier version of these scripts wrote.
_UNREADABLE: Final = (pickle.UnpicklingError, AttributeError, ImportError, EOFError, TypeError)


class Plan(NamedTuple):
    """A run: the module that runs its steps, its section, where its results go, and what it measures."""

    module: str
    heading: str
    intro: str  # the section's first words
    work: Path
    corpora: Callable[[], list[Corpus]]
    suites: Mapping[str, corpus_suite.Suite]
    apart: frozenset[str] = frozenset()  # the corpora whose type checks get checkouts of their own
    # The port a corpus's tests bind, by its name: those of one port run one at a time.
    ports: Mapping[str, str] = {}


SUPER: Final = Plan(
    "tests.corpus.super_corpora",
    "## Super corpora",
    "Every corpus, every way (`tests/corpus/super_corpora.py`):",
    _ROOT / "local" / "super-corpora",
    corpus_table.corpora,
    corpus_suite.SUITES,
    frozenset(_FIRST),
)


class Slots:
    """The machine's CPUs, shared out among the steps running: each holds what it's expected to keep busy."""

    def __init__(self, cpus: int) -> None:
        """Start with every one of `cpus` free."""
        self.cpus: int = cpus
        self.free: int = cpus
        self.changed: threading.Condition = threading.Condition()
        self.waiting: list[tuple[float, int]] = []  # how long each waiting step lasts, and what it wants

    def take(self, wanted: int, *, first: bool = False, lasting: float = 0.0) -> int:
        """Wait until `wanted` CPUs are free (all of them, for more than there are), and hold them.

        `first`: hold them without waiting, whatever is free: the others wait the longer.
        `lasting`: the seconds the step is expected to take; of the steps waiting, one that lasts
        longer and fits what's free goes before it, so the long steps aren't the last to start.

        Returns:
          How many are held, to `give` back.

        """
        held: int = max(1, min(wanted, self.cpus))
        with self.changed:
            if not first:
                waiter: tuple[float, int] = (lasting, held)
                self.waiting.append(waiter)
                _ = self.changed.wait_for(
                    lambda: (
                        self.free >= held
                        and not any(longer > lasting and needs <= self.free for longer, needs in self.waiting)
                    ),
                )
                self.waiting.remove(waiter)
            self.free -= held
            self.changed.notify_all()  # one that waited behind this may fit what's left
        return held

    def give(self, held: int) -> None:
        """Free the CPUs a step held."""
        with self.changed:
            self.free += held
            self.changed.notify_all()


def sizes() -> Sizes:
    """Size a run for this machine (see the module's docstring).

    Returns:
      The sizes.

    """
    cpus: int = os.cpu_count() or 1
    return Sizes(cpus, parsed.memory(), max(1, cpus // _JOBS_SHARE), max(1, cpus // _WORKERS_SHARE))


def stamp() -> str:
    """Hash this checkout's `constricter/` sources: what a kept step's result is of.

    Returns:
      The hash's first hex digits.

    """
    sources: list[bytes] = [
        part
        for path in sorted((_ROOT / "constricter").rglob("*.py"))
        for part in (path.relative_to(_ROOT).as_posix().encode(), path.read_bytes())
    ]
    return hashlib.sha256(b"\0".join(sources)).hexdigest()[:12]


def steps(corpus: Corpus, plan: Plan) -> list[str]:
    """List a corpus's steps run beside the other corpora's, in order (`CHECK` comes after them all).

    Returns:
      Their names.

    """
    found: list[str] = [
        corpora_steps.TABLE,
        corpora_steps.CENSUS,
        *(f"{corpora_steps.INFER}{checker}" for checker in corpora_steps.checkers()),
    ]
    suite: corpus_suite.Suite | None
    if (suite := plan.suites.get(corpus.name)) is not None:
        found.append(corpora_steps.TESTS)
        if suite.checks:
            found.append(corpora_steps.TYPES)
    return found


def _kept(run: Path, corpus: str, name: str) -> Path:
    return run / corpus.replace(" ", "-") / f"{name}{_KEPT}"


def _read(kept: Path) -> Step | None:
    """Read a step's kept result.

    Returns:
      It; `None` if there's none, or none these scripts can read.

    """
    try:
        return cast("Step", pickle.loads(kept.read_bytes()))
    except (OSError, *_UNREADABLE):
        return None


def run_step(plan: Plan, name: str, corpus: str, out: Path) -> int:
    """Run one step on one corpus, in this process, and keep its result in `out`.

    Returns:
      0.

    """
    chosen: Corpus = next(each for each in plan.corpora() if each.name == corpus)
    kept: Step = corpora_steps.run(name, chosen, plan.suites.get(corpus))
    out.parent.mkdir(parents=True, exist_ok=True)
    partial: Path = out.with_suffix(".partial")
    _ = partial.write_bytes(pickle.dumps(kept))
    _ = partial.replace(out)
    return 0


def measured_before(plan: Plan, run: Path) -> dict[tuple[str, str], tuple[float, float]]:
    """Read what each step kept busy, and how long it took, in the latest other run that measured it.

    Returns:
      Each step's CPUs (its CPU seconds over its seconds) and its seconds, by its corpus's
      directory and its name.

    """
    found: dict[tuple[str, str], tuple[float, float]] = {}
    earlier: list[Path] = [each for each in plan.work.glob("*") if each.is_dir() and each != run]
    other: Path
    for other in sorted(earlier, key=lambda each: each.stat().st_mtime):
        kept: Path
        for kept in other.glob(f"*/*{_KEPT}"):
            step: Step | None
            if (step := _read(kept)) is not None and step.value is not None and step.cpu and step.seconds:
                found[kept.parent.name, kept.stem] = (step.cpu / step.seconds, step.seconds)
    return found


# A corpus's steps that run one after another, started: its name, theirs, and their results to come.
_Started: TypeAlias = tuple[str, list[str], Future[list[Step]]]


class _Running(NamedTuple):
    """A run under way: its plan, directory and sizes, the CPUs to share, and what steps kept busy before."""

    plan: Plan
    run: Path
    sized: Sizes
    slots: Slots
    before: Mapping[tuple[str, str], tuple[float, float]]
    bound: Mapping[str, threading.Lock]  # each port's lock, held while a suite's tests have the port
    sampler: Sampler  # counts each step's CPU seconds, its processes' processes' too

    def expected(self, corpus: Corpus, name: str) -> int:
        """Estimate the CPUs a step keeps busy (see the module's docstring).

        Returns:
          Them.

        """
        known: tuple[float, float] | None
        if (known := self.before.get((corpus.name.replace(" ", "-"), name))) is not None:
            return math.ceil(known[0])
        suite: corpus_suite.Suite | None = self.plan.suites.get(corpus.name)
        if name == corpora_steps.TESTS and suite is not None:
            return min(corpus_suite.workers(suite), self.sized.workers)
        return _APART_CPUS if name == corpora_steps.TYPES and corpus.name in self.plan.apart else _STEP_CPUS

    def process(self, corpus: Corpus, name: str, out: Path, jobs: int) -> int:
        """Run a step in a process of its own, its output beside `out`, where it keeps its result.

        With the CPU seconds of every process under it, where that's more than the step counted
        itself: constricter's workers aren't its to wait for.

        Returns:
          Its exit status.

        """
        log: TextIO
        step: subprocess.Popen[bytes]
        with (
            out.with_suffix(".log").open("w", encoding="utf-8") as log,
            subprocess.Popen(
                [sys.executable, "-m", self.plan.module, _STEP_FLAG, name, corpus.name, str(out)],
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=_ROOT,
                env={
                    **os.environ,
                    corpora_steps.JOBS_VARIABLE: str(jobs),
                    corpora_steps.WORKERS_VARIABLE: str(self.sized.workers),
                    corpora_steps.APART_VARIABLE: "1" if corpus.name in self.plan.apart else "",
                },
            ) as step,
        ):
            self.sampler.watch(step.pid)
            status: int = step.wait()
        used: float = self.sampler.used(step.pid)
        kept: Step | None = None if status else _read(out)
        if kept is not None and used > kept.cpu:
            _ = out.write_bytes(pickle.dumps(kept._replace(cpu=used)))
        return status

    def started(self, corpus: Corpus, name: str, cpus: int | None = None) -> Step:
        """Run a step (see `process`), unless the run has its result already.

        Holding `cpus` of the machine's meanwhile (default: what it's expected to keep busy).

        Returns:
          Its result; one with no value if it failed (its output is beside where the result would be).

        """
        out: Path = _kept(self.run, corpus.name, name)
        kept: Step | None
        if (kept := _read(out)) is not None:
            return kept
        out.parent.mkdir(parents=True, exist_ok=True)
        wanted: int = self.expected(corpus, name) if cpus is None else cpus
        # Its tests' port first, if they bind one: waited for holding no CPUs.
        port: threading.Lock | None = (
            self.bound.get(self.plan.ports.get(corpus.name, "")) if name == corpora_steps.TESTS else None
        )
        stack: contextlib.ExitStack
        with contextlib.ExitStack() as stack:
            if port is not None:
                _ = stack.enter_context(port)
            held: int = self.slots.take(
                wanted,
                first=cpus is None and corpus.name in _FIRST,
                lasting=self.before.get((corpus.name.replace(" ", "-"), name), (0.0, 0.0))[1],
            )
            _ = stack.callback(self.slots.give, held)
            start: float = time.perf_counter()
            status: int = self.process(
                corpus,
                name,
                out,
                self.sized.cpus
                if cpus is not None
                else self.sized.jobs * (_FIRST_JOBS if corpus.name in _FIRST else 1),
            )
        seconds: float = time.perf_counter() - start
        done: Step | None = None if status else _read(out)
        said: str = "FAILED" if done is None else f"done, {done.cpu / max(done.seconds, 1e-9):.1f} CPUs busy"
        _ = sys.stderr.write(f"{corpus.name}: {name}: {said} in {seconds:.0f}s (held {held})\n")
        return done or Step(seconds, None)

    def together(self, corpus: Corpus, names: Sequence[str]) -> list[Step]:
        """Run steps of a corpus that share a checkout, one after another.

        Returns:
          Their results, in order.

        """
        return [self.started(corpus, name) for name in names]


def _groups(corpus: Corpus, plan: Plan) -> list[list[str]]:
    """Group a corpus's steps by what must run one after another: its tests and type checks, on one checkout.

    Returns:
      Each group's steps; every other step alone.

    """
    shared: set[str] = set() if corpus.name in plan.apart else {corpora_steps.TESTS, corpora_steps.TYPES}
    names: list[str] = steps(corpus, plan)
    alone: list[list[str]] = [[name] for name in names if name not in shared]
    return [*alone, *([[name for name in names if name in shared]] if shared & set(names) else [])]


def measured(running: _Running, chosen: Sequence[Corpus]) -> dict[str, Steps]:
    """Run every step of every corpus, side by side, then each corpus's timed check alone.

    Returns:
      Each corpus's steps' results, by its name.

    """
    found: dict[str, Steps] = {corpus.name: {} for corpus in chosen}
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, sum(len(steps(corpus, running.plan)) for corpus in chosen))) as pool:
        started: list[_Started] = [
            (corpus.name, group, pool.submit(running.together, corpus, group))
            for corpus in sorted(chosen, key=lambda each: each.name not in _FIRST)
            for group in _groups(corpus, running.plan)
        ]
        name: str
        group: list[str]
        results: Future[list[Step]]
        for name, group, results in started:
            found[name].update(zip(group, results.result(), strict=True))
    # Recorded in the corpora's and their steps' own order, whatever started first.
    each: Corpus
    for each in chosen:
        found[each.name] = {step: found[each.name][step] for step in steps(each, running.plan)}
    corpus: Corpus
    for corpus in chosen:
        found[corpus.name][CHECK] = running.started(corpus, CHECK, running.sized.cpus)
    return found


def main(argv: Sequence[str], plan: Plan = SUPER) -> int:
    """Run every step of every corpus (or one step, for `--step`), and record or print the section.

    Returns:
      1 if a fix broke anything or a step failed, else 0.

    """
    if argv[:1] == [_STEP_FLAG]:
        return run_step(plan, argv[1], argv[2], Path(argv[3]))
    named: list[str] = [arg for arg in argv if not arg.startswith("-")]
    chosen: list[Corpus] = [each for each in plan.corpora() if not named or each.name in named]
    marked: str = stamp()
    run: Path = plan.work / f"{__version__}-{marked}"
    if _FRESH_FLAG in argv:
        shutil.rmtree(run, ignore_errors=True)
    resumed: bool = any(run.glob(f"*/*{_KEPT}"))
    sized: Sizes = sizes()
    running: _Running = _Running(
        plan,
        run,
        sized,
        Slots(int(os.environ.get(_SLOTS_VARIABLE) or sized.cpus)),
        measured_before(plan, run),
        {port: threading.Lock() for port in set(plan.ports.values())},
        Sampler(),
    )
    _ = sys.stderr.write(
        f"{run}: {len(chosen)} corpora, --jobs={sized.jobs}, {sized.workers} workers a suite\n",
    )
    start: float = time.perf_counter()
    found: dict[str, Steps] = measured(running, chosen)
    minutes: float | None = None if resumed else (time.perf_counter() - start) / 60
    text: str = corpora_section.section(
        found,
        corpora_section.Described(plan.heading, plan.intro, marked, sized, minutes),
    )
    if named or _PRINT_FLAG in argv:
        _ = sys.stdout.write(text)
    else:
        corpora_section.record(text, plan.heading)
    lines: list[str] = corpora_section.broken(found)
    _ = sys.stderr.writelines(f"{line}\n" for line in lines)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
