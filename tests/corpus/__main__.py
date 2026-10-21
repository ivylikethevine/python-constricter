# SPDX-License-Identifier: MIT
"""Measure corpora as a run file says, into a folder of that run's own.

    local/.venv/bin/python -m tests.corpus RUN.toml                   # a new folder, named by label and time
    local/.venv/bin/python -m tests.corpus RUN.toml --resume FOLDER   # carry on a stopped run in its folder
    local/.venv/bin/python -m tests.corpus RUN.toml --only NAME       # on that corpus or set alone
    local/.venv/bin/python -m tests.corpus RUN.toml --minus NAME      # less that corpus, set or run file's
    local/.venv/bin/python -m tests.corpus RUN.toml --label NAME      # under that label
    local/.venv/bin/python -m tests.corpus RUN.toml --at-once N --jobs M   # sized for this machine
    local/.venv/bin/python -m tests.corpus RUN.toml --share 75        # 75% of its CPUs and memory

The run file (`run_config`) names the corpora (`corpora.toml`'s), the constricter versions, the
steps and the formats. Each execution writes `<output>/<label>-<month>-<day>-<year>-<time>/`:

    run.toml      the run file, copied
    facts.toml    the run as it was read, the commit, the machine, the checkers' and parser's versions,
                  and how long its executions took
    runner.log    each step's end: its seconds, what it used, what it was given and how long it waited;
                  and each corpus that can't be had, as it fails
    queue.log     each minute steps wait: what's running, and why each waits (`sizing.Slots.report`)
    records/      <corpus>/<version>/<step>.json, and each fix's patch: what every output is made from
    logs/         what each step's constricter wrote to standard error
    report.json   report.md   tables/*.csv

A run of all its corpora is published where its run file says (`render.publish`); one kept to some
with `--only` or `--minus` isn't: `super.toml --minus original` measures only what `super` adds, beside
a run of `original`. A resumed run is given the same `--minus`.

Corpora are measured side by side, found (cloned, installed) `at-once` at a time. Each step is a
process of its own (`--step`), started once the CPUs it's expected to keep busy and the memory it's
expected to hold are free (`sizing`), and its record says what its processes used. A corpus's steps
start side by side; its suite's each once the fixes it reads are made (`suite_steps.needs`), on
checkouts of the suite's own, taking their locks and its port's with its share of the machine, never
holding one while it waits; and once every corpus is measured, each one's timed checks, with
nothing beside them. Every step starts constricter one way (`launch.run`) on one tree a corpus
(`trees.Tree`), so a count in one table is the count in another.
"""

import contextlib
import graphlib
import itertools
import math
import os
import platform
import shutil
import subprocess  # asks git for the commit, and runs each step
import sys
import threading
import time
import tomllib
from collections.abc import Callable, Generator, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import IO, TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast

from constricter import __version__
from constricter.rules import parsed
from tests.corpus import (
    catalog,
    corpus_suite,
    launch,
    pipeline,
    planning,
    render,
    report_tables,
    sizing,
    suite_steps,
    trees,
)
from tests.corpus.pipeline import Record
from tests.corpus.run_config import Run, percent, read

if TYPE_CHECKING:
    import resource

_Measured: TypeAlias = tuple[trees.Tree | None, list[str]]  # a corpus's tree, and its steps that failed
_RESUME: Final = "--resume"
_AT_ONCE: Final = "--at-once"  # then how many corpora are found side by side, whatever the file says
_JOBS: Final = "--jobs"  # and constricter's worker processes
_LABEL: Final = "--label"  # then the run's label, whatever its file says
_SHARE: Final = "--share"  # then the percent of the machine its steps share, whatever its file says
_SAID: Final = 2000  # the characters kept of why a corpus couldn't be had: the end of its build's output
_ONLY: Final = "--only"  # then a corpus or a set: the run file's, on that alone
_MINUS: Final = "--minus"  # then a corpus, a set or a run file: the run's corpora less its
_STEP: Final = "--step"  # then a run's folder, a corpus, a version and a step: that step alone
_ROOT: Final = Path(__file__).resolve().parents[2]
_POLL: Final = 0.2  # the seconds between looks at whether a step's process has ended
_LOOK: Final = 60.0  # and between fittings of its hold to what it's using
_DONE: Final = True  # what an event's `wait` says once it's set
_MACOS: Final = "darwin"
_LOG: Final = "runner.log"  # in a run's folder
_FACTS: Final = "facts.toml"  # and the run as it was read
_STARTED: Final = "started"  # in its facts: when its first execution started
_RUNNING: Final = "running"  # and when the one under way did: gone once it ends
_QUEUE: Final = "queue.log"  # and its queue, each minute steps wait
_SUITE_WORKERS: Final = "CORPUS_SUITE_WORKERS"  # in a step's environment: its suite's tests' processes
_RELEASED: Final = pipeline.part(pipeline.TESTS, pipeline.RELEASED)  # a suite's tests as released
_SAMPLED: Final = "sampled"  # what read a step's use outside a scope: the sampler, the waited count
_MAXRSS: Final = (
    1 if sys.platform == _MACOS else 1024
)  # the bytes `ru_maxrss` counts in: kilobytes, but there


def run_facts(run: Run, started: datetime) -> Record:
    """Gather what a run's outputs say of the run itself.

    Returns:
      The run file's values, this checkout's version and commit, the machine's CPUs and memory,
      and the keys a record is comparable across runs by: each type checker's version, and the
      version of what reads a suite's tests' output.

    """
    commit: str = subprocess.run(
        ["git", "rev-parse", "--short=12", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=_ROOT,
    ).stdout.strip()
    return {
        "label": run.label,
        "started": started.isoformat(timespec="seconds"),
        "versions": list(run.versions),
        "formats": list(run.formats),
        "jobs": run.jobs,
        "at-once": run.at_once,
        "corpora": list(run.include),
        "minus": list(run.minus),
        "check": run.steps.check,
        "fix": list(run.steps.fix),
        "coverage": run.steps.coverage,
        "infer-with": list(run.steps.infer),
        "census": run.steps.census,
        "tests": run.steps.tests,
        "types": run.steps.types,
        "traced": run.steps.traced,
        "timing": run.steps.timing,
        "profile": run.steps.profile,
        "install": run.install,
        "suite-seconds": run.suite_seconds,
        "suite-workers": run.suite_workers,
        "constricter": __version__,
        "commit": commit,
        "python": platform.python_version(),
        "system": platform.system(),
        "cpus": os.cpu_count() or 1,
        "share": run.share,
        "gigabytes": round((parsed.memory() or 0) / sizing.GIB),
        "checkers": checkers(run),
        "parser": corpus_suite.parser(),
    }


def checkers(run: Run) -> list[str]:
    """Name each type checker the run's `infer-with` starts, with its version: `--version`'s first line.

    Found as `--infer-with` finds it: on the path, or beside this Python.

    Returns:
      Them; `(not found)` for one that isn't installed.

    """
    found: list[str] = []
    name: str
    for name in run.steps.infer:
        path: str | None
        if (path := shutil.which(name) or shutil.which(name, path=str(Path(sys.executable).parent))) is None:
            found.append(f"{name} (not found)")
            continue
        said: str = subprocess.run([path, "--version"], capture_output=True, text=True, check=False).stdout
        line: str = said.strip().partition("\n")[0]
        found.append(line if line.startswith(name) else f"{name} {line}")
    return found


def _toml(facts: Record) -> str:
    """Write flat facts as TOML: strings, numbers, booleans and lists of strings.

    Returns:
      The text.

    """

    def value(each: object) -> str:
        if isinstance(each, bool):
            return str(each).lower()
        if isinstance(each, list):
            return "[" + ", ".join(value(one) for one in cast("list[object]", each)) + "]"
        return (
            str(each)
            if isinstance(each, int)
            else '"' + str(each).replace("\\", "\\\\").replace('"', '\\"') + '"'
        )

    return "".join(f"{key} = {value(each)}\n" for key, each in facts.items())


def _suited(run: Run) -> dict[str, str]:
    """Say what a suite's steps read of the run in their environment (`corpus_suite`).

    Returns:
      How long its tests may run, and the most processes they take, where the run says.

    """
    said: dict[str, str] = {"CORPUS_SUITE_SECONDS": str(run.suite_seconds)}
    return said | ({_SUITE_WORKERS: str(run.suite_workers)} if run.suite_workers else {})


@dataclass
class _Hold:
    """What a running step was sized to take, and the CPUs and the bytes it holds now."""

    wanted: sizing.Wanted
    held: tuple[int, int]


class Running(NamedTuple):
    """A run under way: its folder, what its steps share of the machine, and what counts their use."""

    run: Run
    store: pipeline.Store
    plan: sizing.Plan
    slots: sizing.Slots
    watcher: sizing.Watcher | None  # `None`: nothing counts a step's use
    ports: dict[str, threading.Lock]  # each port's lock, taken with its share of the machine (`Slots.take`)
    finding: threading.Semaphore  # the corpora found at once: cloned, installed
    scope: tuple[str, ...] = ()  # what starts a step in a scope of its own (`sizing.scope`): nothing, none
    checkouts: dict[tuple[str, str], threading.Lock] | None = None  # each suite checkout's lock, as `ports`
    ranks: Mapping[tuple[str, str], float] | None = None  # each step's planned start (`planning.ranks`)

    def process(self, entry: catalog.Entry, job: pipeline.Job, name: str, hold: "_Hold") -> sizing.Used:
        """Run one step in a process of its own, what it says kept in its log.

        `hold`: what it holds of the machine, fitted every `_LOOK` seconds to what it's using.

        In a scope of its own where `scope` says, which it reads the count of as it ends (`_step`). A
        suite's tests take the workers its hold says (`Wanted.started`).

        Returns:
          What the process and every one under it used: the most of what was read as it ran and
          of what the system counted for it and those it waited for, which has the ones too short
          to read (their CPU seconds, and the largest one's most memory). Nothing where nothing
          counts it.

        """
        command: list[str] = [*self.scope, sys.executable, "-m", "tests.corpus", _STEP, str(self.store.root)]
        scoped: dict[str, str] = {sizing.SCOPED: "1"} if self.scope else {}
        scoped |= {_SUITE_WORKERS: str(hold.wanted.workers)} if sizing.testing(name) else {}
        said: list[str] = [_LABEL, self.run.label, _JOBS, str(self.run.jobs)]  # what the run's command said
        file: IO[str]
        process: subprocess.Popen[bytes]
        with (
            self.store.logged(job.tree.name, job.recorded, name).open("a", encoding="utf-8") as file,
            subprocess.Popen(
                [*command, entry.name, job.version, name, *said],
                stdout=file,
                stderr=subprocess.STDOUT,
                cwd=_ROOT,
                env=os.environ | _suited(self.run) | scoped,
            ) as process,
        ):
            if self.watcher is not None:
                self.watcher.watch(process.pid)
            counted: sizing.Used = self._waited(process, hold, f"{entry.name}/{name}")
        if self.watcher is None:
            return sizing.Used()
        used: sizing.Used = sizing.Used(*self.watcher.used(process.pid))
        return sizing.Used(max(used.cpu, counted.cpu), max(used.memory, counted.memory))

    def _waited(self, process: subprocess.Popen[bytes], hold: "_Hold", named: str) -> sizing.Used:
        """Wait for a step's process, `named` in the queue, its hold fitted to what it uses (`Plan.fitted`).

        Returns:
          What the system counted for it and the processes it waited for: their CPU seconds, and
          the most memory the largest of them held.

        """
        looked: float = time.perf_counter()
        before: float = 0.0
        ended: int
        status: int
        usage: resource.struct_rusage
        for ended, status, usage in iter(partial(os.wait4, process.pid, os.WNOHANG), None):
            if ended:
                process.returncode = os.waitstatus_to_exitcode(status)
                return sizing.Used(usage.ru_utime + usage.ru_stime, usage.ru_maxrss * _MAXRSS)
            time.sleep(_POLL)
            now: float = time.perf_counter()
            if self.watcher is not None and now - looked >= _LOOK:
                seen: sizing.Used = sizing.Used(*self.watcher.seen(process.pid))
                fitted: tuple[int, int] = self.plan.fitted(
                    hold.wanted,
                    hold.held,
                    (seen.cpu - before) / (now - looked),
                    seen.memory,
                )
                hold.held = self.slots.resize(hold.held, fitted, named)
                looked, before = now, seen.cpu
        return sizing.Used()

    def step(self, entry: catalog.Entry, job: pipeline.Job, name: str) -> bool:
        """Run one step (`process`), once what it's expected to take is free (`sizing`).

        With the locks of the checkouts it works on and of its tests' port, if they bind one, taken
        with the rest: waited for holding nothing. What it used goes into the step's record
        (`_recorded`).

        Returns:
          Whether the step has a record: one that failed has none, and its log says why.

        """
        wanted: sizing.Wanted = self.plan.wanted(job.tree, name, heavy=entry.heavy)
        locks: list[threading.Lock] = self.locks(entry, job, name)
        asked: float = time.perf_counter()
        rank: float = (self.ranks or {}).get((entry.name, name), math.inf)
        held: int = self.slots.take(wanted, locks, f"{entry.name}/{name}", rank)
        memory: int = self.slots.share(wanted.cpus, wanted.memory, held)
        given: sizing.Wanted = wanted._replace(cpus=held, memory=memory, workers=wanted.started(held))
        hold: _Hold = _Hold(given, (held, memory))
        start: float = time.perf_counter()
        try:
            used: sizing.Used = self.process(entry, job, name, hold)
        finally:
            self.slots.give(*hold.held, locks, f"{entry.name}/{name}")
        return self.recorded(job, name, hold.wanted, used, (start - asked, time.perf_counter() - start))

    def locks(self, entry: catalog.Entry, job: pipeline.Job, name: str) -> list[threading.Lock]:
        """Find the locks a step (`step`) takes: of the checkouts it works on, and of its tests' port.

        Returns:
          Them, the port's last if it binds one.

        """
        port: threading.Lock | None = self.ports.get(entry.port) if suite_steps.binds(name) else None
        held_too: dict[tuple[str, str], threading.Lock] = self.checkouts if self.checkouts is not None else {}
        locks: list[threading.Lock] = [
            held_too.setdefault((entry.name, each), threading.Lock())
            for each in (suite_steps.checkouts(job, name) if job.tree.suite is not None else ())
        ]
        return locks + ([port] if port is not None else [])

    def recorded(
        self,
        job: pipeline.Job,
        name: str,
        wanted: sizing.Wanted,
        used: sizing.Used,
        took: tuple[float, float],
    ) -> bool:
        """Put what a step used into its record, with what it was given (`wanted`) and `took`.

        `took`: the seconds it waited to start, and the seconds it ran. Its control group's count
        where it has one; when it started; and the workers a suite's tests ran with. Said in the
        run's log too.

        Returns:
          Whether the step has a record.

        """
        waited: float
        seconds: float
        waited, seconds = took
        record: Record | None = self.store.read(job.tree.name, job.recorded, name)
        given: Record = {
            "cpus": wanted.cpus,
            "memory": round(min(wanted.memory, self.plan.memory) / sizing.GIB, 2),
        }
        by: str
        used, by = _counted(record, used)
        if record is not None:
            record[sizing.USED] = {
                "by": by,
                "started": round(time.time() - seconds, 1),
                "waited": round(waited, 1),
                "seconds": round(seconds, 1),
                "cpu": round(used.cpu, 1),
                "memory": round(used.memory / sizing.GIB, 2),
                "given": given,
                "alone": wanted.memory >= self.plan.memory,
            } | ({sizing.WORKERS: wanted.started(wanted.cpus)} if sizing.testing(name) else {})
            self.store.write(job.tree.name, job.recorded, name, record)
        said: str = (
            "failed" if record is None else f"{used.cpu:.0f} CPU seconds, {used.memory / sizing.GIB:.1f} GB"
        )
        said += f" (given {given['cpus']} CPUs, {given['memory']} GB; waited {waited:.0f}s)"
        self.said(f"{job.recorded} on {job.tree.name}: {name}: {seconds:.0f}s, {said}")
        return record is not None

    def said(self, line: str) -> None:
        """Write a line to the run's output and, timed, to its `runner.log`."""
        _ = sys.stderr.write(f"{line}\n")
        file: IO[str]
        with (self.store.root / _LOG).open("a", encoding="utf-8") as file:
            _ = file.write(f"{datetime.now().astimezone():%H:%M:%S} {line}\n")

    def steps(self, entry: catalog.Entry, job: pipeline.Job, names: Sequence[str]) -> list[str]:
        """Run each of `names`, the job's steps, that has no record yet, one after another.

        Returns:
          Those that failed, each as the run's last lines say it.

        """
        done: list[bool] = [self._after(entry, job, name, [], []) for name in names]
        return self._failed(entry, job, names, done)

    def _failed(
        self,
        entry: catalog.Entry,
        job: pipeline.Job,
        names: Sequence[str],
        done: Sequence[bool],
    ) -> list[str]:
        """Name the steps of `names` that failed, by `done`.

        Returns:
          Each as the run's last lines say it.

        """
        log: Path = self.store.logged(job.tree.name, job.recorded, "").parent
        return [
            f"{entry.name}, {job.recorded}: {name} ({log / name}.log)"
            for name, has in zip(names, done, strict=True)
            if not has
        ]

    def _after(
        self,
        entry: catalog.Entry,
        job: pipeline.Job,
        name: str,
        after: Sequence["Future[bool]"],
        ready: Sequence["Future[Path]"],
    ) -> bool:
        """Run a step that has no record yet once the steps it comes `after` and its checkouts are `ready`.

        Waited for holding nothing. The tests as released, where an earlier run's record of them
        may be taken (`suite_steps.taken`: the run doesn't run them, or the traced tests confirm
        it), are that record, not run.

        Returns:
          Whether it has a record.

        """
        _ = wait(after)  # each one failing is the step's to say: it reads what's missing
        _ = wait(ready)
        if self.store.read(job.tree.name, job.recorded, name) is not None:
            return True
        taken: Record | None
        if name == _RELEASED and (taken := suite_steps.taken(job)) is not None:
            self.store.write(job.tree.name, job.recorded, name, taken)
            said: str = (
                f", as {taken[suite_steps.CONFIRMED]} found them" if suite_steps.CONFIRMED in taken else ""
            )
            _ = sys.stderr.write(
                f"{job.recorded} on {job.tree.name}: {name}: {taken[pipeline.FROM]}'s{said}\n",
            )
            return True
        return self.step(entry, job, name)

    def measured(self, entry: catalog.Entry) -> _Measured:
        """Measure one corpus with each of the run's versions.

        Its steps side by side, each on a copy or reading the tree; its suite's on checkouts of their
        own, each once the fixes it reads are made (`_versioned`). Not the timed ones (`timed`).

        Returns:
          The corpus's tree, and the steps that failed: each has its traceback in its log, and no
          record. No tree, and why, for a corpus that isn't to be had: the run goes on without it,
          and says why at once, not only in its last lines.

        """
        with self.finding:
            try:
                tree: trees.Tree = trees.found(entry, install=self.run.install)
            except (OSError, RuntimeError, ValueError) as failure:  # it can't be cloned, installed or fetched
                why: str = f"{entry.name}: not found: {str(failure)[-_SAID:]}"
                self.said(why)
                return None, [why]
        failed: list[str] = []
        version: str
        for version in self.run.versions:
            failed += self._versioned(entry, pipeline.Job(self.run, self.store, tree, version))
        return tree, failed

    def _versioned(self, entry: catalog.Entry, job: pipeline.Job) -> list[str]:
        """Measure one corpus with one version (see `measured`).

        Every step starts as soon as the steps it reads have ended (`suite_steps.needs`) and the
        checkouts it works on are installed (`suite_steps.checkouts`): those of a suite's steps, a
        kind each, one after another beside the steps before them.

        Returns:
          The steps that failed.

        """
        beside: list[str] = [name for name in pipeline.steps(self.run) if name not in sizing.TIMED]
        suited: list[str] = list(suite_steps.waiting(job))
        needs: dict[str, frozenset[str]] = suite_steps.needs(job)
        names: list[str] = _ordered([*beside, *suited], needs)
        ended: dict[str, Future[bool]] = {}
        installing: ThreadPoolExecutor
        pool: ThreadPoolExecutor
        # Each step waits on its own thread; the checkouts are installed one after another.
        with ThreadPoolExecutor(1) as installing, ThreadPoolExecutor(max(1, len(names))) as pool:
            installed: dict[str, Future[Path]] = {
                each: installing.submit(suite_steps.prepared, job, each)
                for each in dict.fromkeys(
                    each for name in suited for each in suite_steps.checkouts(job, name)
                )
            }
            name: str
            for name in names:  # those a step waits for come before it
                used: tuple[str, ...] = suite_steps.checkouts(job, name) if name in suited else ()
                after: list[Future[bool]] = [ended[each] for each in needs.get(name, ()) if each in ended]
                ready: list[Future[Path]] = [installed[each] for each in used]
                ended[name] = pool.submit(self._after, entry, job, name, after, ready)
        return self._failed(entry, job, names, [ended[name].result() for name in names])

    def timed(self, entry: catalog.Entry, tree: trees.Tree) -> list[str]:
        """Run a corpus's timed steps with each of the run's versions, one after another.

        Each holds every CPU: started while other corpora are measured, it would wait for them all
        holding its corpus's turn, and no other corpus would start.

        Returns:
          The steps that failed.

        """
        failed: list[str] = []
        version: str
        for version in self.run.versions:
            job: pipeline.Job = pipeline.Job(self.run, self.store, tree, version)
            failed += self.steps(
                entry,
                job,
                [name for name in pipeline.steps(self.run) if name in sizing.TIMED],
            )
        return failed


def _ordered(names: Sequence[str], needs: Mapping[str, frozenset[str]]) -> list[str]:
    """Order `names` so that each comes after those of them it `needs`.

    Returns:
      Them.

    """
    among: frozenset[str] = frozenset(names)
    graph: dict[str, frozenset[str]] = {name: needs.get(name, frozenset()) & among for name in names}
    return list(graphlib.TopologicalSorter(graph).static_order())


@contextlib.contextmanager
def _queue_logged(slots: sizing.Slots, log: Path) -> Generator[None]:
    """Log the queue's state to `log` while the block runs (`_queued`).

    Yields:
      Nothing, once the logging's begun.

    """
    stop: threading.Event = threading.Event()
    watching: threading.Thread = threading.Thread(target=_queued, args=(slots, log, stop), daemon=True)
    watching.start()
    try:
        yield
    finally:
        stop.set()
        watching.join()


def _queued(slots: sizing.Slots, log: Path, stop: threading.Event) -> None:
    """Write the queue's state to `log` each `_LOOK` seconds a step waits (`Slots.report`), until `stop`."""
    _tick: bool
    file: IO[str]
    for _tick in iter(partial(stop.wait, _LOOK), _DONE):
        if slots.waiting:
            lines: list[str] = slots.report()
            stamp: str = datetime.now().astimezone().strftime("%H:%M:%S")
            with log.open("a", encoding="utf-8") as file:
                _ = file.write("".join(f"{stamp} {line}\n" for line in lines) + "\n")


def _counted(record: Record | None, used: sizing.Used) -> tuple[sizing.Used, str]:
    """Take a step's control group's count out of its record, where the step put one (`_step`).

    Returns:
      What it used: by that count, else `used`, as `Running.process` read it; and which.

    """
    scoped: Record = cast("Record", (record or {}).pop(sizing.SCOPE, {}))
    counted: sizing.Used = sizing.Used(
        cast("float", scoped.get("cpu", 0.0)),
        cast("int", scoped.get("memory", 0)),
    )
    return (counted, sizing.SCOPE) if scoped else (used, _SAMPLED)


def commanded(run: Run, argv: Sequence[str]) -> Run:
    """Read what a command says of its run, whatever the run file does.

    Returns:
      The run, with the command's corpora, label, corpora at once, `--jobs` and `--share`.

    """
    if _ONLY in argv:
        run = run._replace(include=(argv[argv.index(_ONLY) + 1],))
    if _MINUS in argv:
        minus: str = argv[argv.index(_MINUS) + 1]
        less: Run | None = read(Path(minus)) if minus.endswith(".toml") else None
        names: list[str] = [minus] if less is None else catalog.load().names(list(less.include))
        run = run._replace(minus=tuple(names))
    if _LABEL in argv:
        run = run._replace(label=argv[argv.index(_LABEL) + 1])
    if _AT_ONCE in argv:
        run = run._replace(at_once=int(argv[argv.index(_AT_ONCE) + 1]))
    if _JOBS in argv:
        run = run._replace(jobs=int(argv[argv.index(_JOBS) + 1]))
    if _SHARE in argv:
        run = run._replace(share=percent(int(argv[argv.index(_SHARE) + 1])))
    return run


def _step(argv: Sequence[str]) -> int:
    """Run one step of one corpus with one version, in the run whose folder is named.

    `argv`: the folder, the corpus, the version and the step, then what the run's command said.

    Returns:
      1 if it failed (its traceback is in its log, and it has no record), else 0.

    """
    folder: Path = Path(argv[0])
    corpus: str
    version: str
    name: str
    corpus, version, name = argv[1:4]
    run: Run = commanded(read(folder / "run.toml"), argv[4:])
    launch.configure(run.options)
    # A suite's type checks have a checkout of their own, and run beside its tests on the other.
    tree: trees.Tree = trees.found(
        catalog.load().entry(corpus),
        install=run.install,
        settle=name != pipeline.TYPES,
    )
    job: pipeline.Job = pipeline.Job(run, pipeline.Store(folder), tree, version)
    step: Callable[[pipeline.Job], Record] = (pipeline.steps(run) | suite_steps.waiting(job))[name]
    job.store.path(tree.name, job.recorded, name).parent.mkdir(parents=True, exist_ok=True)
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(1) as pool:  # a future keeps what the step raises, whatever it is
        done: Future[Record] = pool.submit(step, job)
    settled: bool = pipeline.settled(job, name, done)
    # Started in a scope of its own: its control group's count, every process it started's included.
    found: sizing.Used | None = sizing.counted(sizing.group()) if os.environ.get(sizing.SCOPED) else None
    record: Record | None = job.store.read(tree.name, job.recorded, name) if found is not None else None
    if found is not None and record is not None:
        record[sizing.SCOPE] = {"cpu": round(found.cpu, 1), "memory": found.memory}
        job.store.write(tree.name, job.recorded, name, record)
    return int(not settled)


def main(argv: Sequence[str]) -> int:
    """Run the run file named, write its folder, and say where it is.

    Returns:
      1 if a step failed (the outputs have the rest; `--resume` makes it again) or a fix broke
      something (`render.problems`), else 0.

    """
    if argv[:1] == [_STEP]:
        return _step(argv[1:])
    start: float = time.perf_counter()
    earlier: Record = resumed_facts(argv)
    run: Run = relabelled(commanded(read(Path(argv[0])), argv), argv, earlier)
    launch.configure(run.options)
    facts: Record = carried(run_facts(run, datetime.now().astimezone()), earlier, _last_written(argv))
    folder: Path = _folder(argv, run, facts)
    store: pipeline.Store = pipeline.Store(folder)
    measured: list[_Measured] = _all(run, store)
    shutil.rmtree(folder / "work", ignore_errors=True)  # the copies its fixes worked on
    facts = finished(facts, (time.perf_counter() - start) / 60)
    _ = (folder / _FACTS).write_text(_toml(facts), encoding="utf-8")
    records: report_tables.Records = render.gathered(run, store, [tree for tree, _ in measured if tree])
    written: list[Path] = render.write(records, folder, facts)
    if _ONLY not in argv and _MINUS not in argv:  # a part of its corpora isn't what its section is of
        render.publish(records, _ROOT, facts)
    _ = sys.stdout.write("".join(f"{path}\n" for path in written))
    failed: list[str] = [f"failed: {each}" for _, failures in measured for each in failures]
    failed += [f"problem: {each}" for each in render.problems(records)]
    noted: list[str] = [f"note: {each}" for each in render.notes(records)]
    _ = sys.stderr.write("".join(f"{each}\n" for each in (*noted, *failed)))
    return int(bool(failed))


def resumed_facts(argv: Sequence[str]) -> Record:
    """Read the facts of the run `--resume` carries on.

    Returns:
      Its folder's `facts.toml`; nothing for a new run, or a folder that has none.

    """
    if _RESUME not in argv:
        return {}
    path: Path = Path(argv[argv.index(_RESUME) + 1]) / _FACTS
    return tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _last_written(argv: Sequence[str]) -> datetime | None:
    """Say when the run `--resume` carries on last wrote its `runner.log`: a step's end.

    Returns:
      The time; `None` for a new run, or one that ended no step.

    """
    if _RESUME not in argv:
        return None
    log: Path = Path(argv[argv.index(_RESUME) + 1]) / _LOG
    return datetime.fromtimestamp(log.stat().st_mtime).astimezone() if log.exists() else None


def relabelled(run: Run, argv: Sequence[str], earlier: Record) -> Run:
    """Give a resumed run the label it was started under, whatever its run file says.

    `earlier`: the facts of the run it carries on (`resumed_facts`).

    Returns:
      The run, under that label.

    Raises:
      SystemExit: `--label` names another, which would measure every corpus again beside it.

    """
    label: str | None
    if (label := cast("str | None", earlier.get("label"))) is None:  # `_toml` writes it as a string
        return run
    if _LABEL in argv and run.label != label:
        message: str = (
            f"{_RESUME} carries on the run labelled {label!r}, not {run.label!r}: leave out {_LABEL}"
        )
        raise SystemExit(message)
    return run._replace(label=label)


def carried(facts: Record, earlier: Record, last: datetime | None) -> Record:
    """Carry a stopped run's start and time into a resumed one's facts.

    `earlier`: the stopped run's facts; `last`: when it last ended a step. Its executions' minutes
    are those that ended (`finished`), and one that was stopped from where it started to `last`.

    Returns:
      The facts, with the first execution's start, the minutes before this one, and this one's start.

    """
    now: str = str(facts[_STARTED])
    if not earlier:
        return facts | {_RUNNING: now}
    before: float = float(cast("float", earlier.get(render.MINUTES, 0)))
    stopped: str | None = cast("str | None", earlier.get(_RUNNING))
    if stopped is None and render.MINUTES not in earlier:  # no minutes: its one execution was stopped
        stopped = cast("str | None", earlier.get(_STARTED))
    if stopped is not None and last is not None:
        before += max(0.0, (last - datetime.fromisoformat(stopped)).total_seconds() / 60)
    return facts | {_STARTED: earlier.get(_STARTED, now), render.MINUTES: round(before), _RUNNING: now}


def finished(facts: Record, minutes: float) -> Record:
    """Add an execution's minutes to its run's, as it ends.

    Returns:
      The facts, with the run's minutes and none under way.

    """
    total: int = round(float(cast("float", facts.get(render.MINUTES, 0))) + minutes)
    return {key: value for key, value in facts.items() if key != _RUNNING} | {render.MINUTES: total}


def _folder(argv: Sequence[str], run: Run, facts: Record) -> Path:
    """Make the folder this execution writes, or take the one `--resume` names, and keep the run file there.

    Returns:
      The folder.

    """
    resumed: Path | None = Path(argv[argv.index(_RESUME) + 1]) if _RESUME in argv else None
    started: datetime = datetime.fromisoformat(str(facts["started"]))
    folder: Path = (resumed or _ROOT / run.folder(started)).resolve()
    named: str = folder.name
    again: int
    for again in itertools.count(2):  # past another execution of the label, started that minute
        if resumed is not None or not folder.exists():
            break
        folder = folder.with_name(f"{named}-{again}")
    folder.mkdir(parents=True, exist_ok=True)
    if not (resumed and (folder / "run.toml").exists()):
        _ = shutil.copyfile(argv[0], folder / "run.toml")
    _ = (folder / _FACTS).write_text(_toml(facts), encoding="utf-8")
    return folder


def _all(run: Run, store: pipeline.Store) -> list[_Measured]:
    """Measure the run's corpora side by side, found `at-once` at a time, then time each: nothing beside it.

    Each corpus's steps wait for the machine alone (`sizing`): a corpus whose step waits keeps no
    other from starting.

    Each version's constricter is found first, a release installed: the steps are processes of
    their own, and two would install it at once.

    Returns:
      Each one's tree and failed steps, in the run's order.

    """
    known: catalog.Catalog = catalog.load()
    names: list[str] = known.names(list(run.include), list(run.minus))
    entries: list[catalog.Entry] = [known.entry(name) for name in names]
    version: str
    for version in run.versions:
        _ = launch.python(version)
    plan: sizing.Plan = sizing.plan(run, store.root, _ROOT)
    # Its steps held to its share of the machine, where it has one.
    scope: tuple[str, ...] = sizing.scope(_ROOT, plan if run.share else None)
    running: Running = Running(
        run,
        store,
        plan,
        sizing.Slots(plan.cpus, plan.memory),
        sizing.watcher(scoped=bool(scope)),
        {entry.port: threading.Lock() for entry in entries if entry.port},
        threading.Semaphore(max(1, run.at_once)),
        scope,
        {},
        planning.ranks(run, entries, plan),
    )
    pool: ThreadPoolExecutor
    with _queue_logged(running.slots, store.root / _QUEUE), ThreadPoolExecutor(max(1, len(entries))) as pool:
        measured: list[_Measured] = list(pool.map(running.measured, entries))
    entry: catalog.Entry
    tree: trees.Tree | None
    failed: list[str]
    for entry, (tree, failed) in zip(entries, measured, strict=True):
        if tree is not None:
            failed.extend(running.timed(entry, tree))
    return measured


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
