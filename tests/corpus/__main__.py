# SPDX-License-Identifier: MIT
"""Measure corpora as a run file says, into a folder of that run's own.

    local/.venv/bin/python -m tests.corpus RUN.toml                   # a new folder, named by label and time
    local/.venv/bin/python -m tests.corpus RUN.toml --resume FOLDER   # carry on a stopped run in its folder
    local/.venv/bin/python -m tests.corpus RUN.toml --only NAME       # on that corpus or set alone
    local/.venv/bin/python -m tests.corpus RUN.toml --label NAME      # under that label
    local/.venv/bin/python -m tests.corpus RUN.toml --at-once N --jobs M   # sized for this machine
    local/.venv/bin/python -m tests.corpus RUN.toml --share 75        # 75% of its CPUs and memory

The run file (`run_config`) names the corpora (`corpora.toml`'s), the constricter versions, the
steps and the formats. Each execution writes `<output>/<label>-<month>-<day>-<year>-<time>/`:

    run.toml      the run file, copied
    facts.toml    the run as it was read, the commit and the machine
    runner.log    each step's end: its seconds, what it used, what it was given and how long it waited
    records/      <corpus>/<version>/<step>.json, and each fix's patch: what every output is made from
    logs/         what each step's constricter wrote to standard error
    report.json   report.md   tables/*.csv

A run of all its corpora is published where its run file says (`render.publish`); one kept to some
with `--only` isn't.

Corpora are measured side by side, found (cloned, installed) `at-once` at a time. Each step is a
process of its own (`--step`), started once the CPUs it's expected to keep busy and the memory it's
expected to hold are free (`sizing`), and its record says what its processes used: a corpus's steps
side by side, then its suite's own tests and checks one after another on their checkout (those of
one port one suite at a time; its traced tests as soon as `fix-unsafe` has ended and the other
steps have their copies); and once every corpus is measured, each one's timed checks, with nothing
beside them. Every step starts
constricter one way (`launch.run`) on one tree a corpus (`trees.Tree`), so a count in one table is
the count in another.
"""

import contextlib
import itertools
import os
import platform
import shutil
import subprocess  # asks git for the commit, and runs each step
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import IO, TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast

from constricter import __version__
from constricter.rules import parsed
from tests.corpus import catalog, launch, pipeline, render, sizing, suite_steps, trees
from tests.corpus.pipeline import Record
from tests.corpus.run_config import UNSAFE, Run, percent, read

if TYPE_CHECKING:
    import resource

_Held: TypeAlias = contextlib.AbstractContextManager[bool | None]  # a lock, or nothing to hold
_Measured: TypeAlias = tuple[trees.Tree | None, list[str]]  # a corpus's tree, and its steps that failed
_RESUME: Final = "--resume"
_AT_ONCE: Final = "--at-once"  # then how many corpora are found side by side, whatever the file says
_JOBS: Final = "--jobs"  # and constricter's worker processes
_LABEL: Final = "--label"  # then the run's label, whatever its file says
_SHARE: Final = "--share"  # then the percent of the machine its steps share, whatever its file says
_SAID: Final = 2000  # the characters kept of why a corpus couldn't be had: the end of its build's output
_ONLY: Final = "--only"  # then a corpus or a set: the run file's, on that alone
_STEP: Final = "--step"  # then a run's folder, a corpus, a version and a step: that step alone
_ROOT: Final = Path(__file__).resolve().parents[2]
_BOUND: Final = frozenset({pipeline.TESTS, pipeline.TRACED})  # the steps that bind a suite's port
_DONE: Final = True  # what a future's `done` says once it is
_POLL: Final = 0.2  # the seconds between looks at whether a step's process has ended
_LOOK: Final = 60.0  # and between fittings of its hold to what it's using
_MACOS: Final = "darwin"
_LOG: Final = "runner.log"  # in a run's folder
_SUITE_WORKERS: Final = "CORPUS_SUITE_WORKERS"  # in a step's environment: its suite's tests' processes
_SAMPLED: Final = "sampled"  # what read a step's use outside a scope: the sampler, the waited count
_MAXRSS: Final = (
    1 if sys.platform == _MACOS else 1024
)  # the bytes `ru_maxrss` counts in: kilobytes, but there


def _facts(run: Run, started: datetime) -> Record:
    """Gather what a run's outputs say of the run itself.

    Returns:
      The run file's values, this checkout's version and commit, and the machine's CPUs and memory.

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
    }


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
    ports: dict[str, threading.Lock]  # each port's lock, held while a suite's tests have the port
    finding: threading.Semaphore  # the corpora found at once: cloned, installed
    scope: tuple[str, ...] = ()  # what starts a step in a scope of its own (`sizing.scope`): nothing, none

    def process(self, entry: catalog.Entry, job: pipeline.Job, name: str, hold: "_Hold") -> sizing.Used:
        """Run one step in a process of its own, what it says kept in its log.

        `hold`: what it holds of the machine, fitted every `_LOOK` seconds to what it's using.

        In a scope of its own where `scope` says, which it reads the count of as it ends (`_step`). A
        suite's tests take a worker for each CPU they started with.

        Returns:
          What the process and every one under it used: the most of what was read as it ran and
          of what the system counted for it and those it waited for, which has the ones too short
          to read (their CPU seconds, and the largest one's most memory). Nothing where nothing
          counts it.

        """
        command: list[str] = [*self.scope, sys.executable, "-m", "tests.corpus", _STEP, str(self.store.root)]
        scoped: dict[str, str] = {sizing.SCOPED: "1"} if self.scope else {}
        scoped |= {_SUITE_WORKERS: str(hold.held[0])} if name in sizing.TESTING else {}
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
            counted: sizing.Used = self._waited(process, hold)
        if self.watcher is None:
            return sizing.Used()
        used: sizing.Used = sizing.Used(*self.watcher.used(process.pid))
        return sizing.Used(max(used.cpu, counted.cpu), max(used.memory, counted.memory))

    def _waited(self, process: subprocess.Popen[bytes], hold: "_Hold") -> sizing.Used:
        """Wait for a step's process, fitting its hold to what it's using as it runs (`Plan.fitted`).

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
                hold.held = self.slots.resize(hold.held, fitted)
                looked, before = now, seen.cpu
        return sizing.Used()

    def step(
        self,
        entry: catalog.Entry,
        job: pipeline.Job,
        name: str,
        ready: Mapping[str, Future[Path]] | None = None,
    ) -> bool:
        """Run one step (`process`), once what it's expected to take is free (`sizing`).

        Its tests' port first, if they bind one, and what it's `ready` for, if anything: waited for
        holding nothing. What it used goes into the step's record (`_recorded`).

        Returns:
          Whether the step has a record: one that failed has none, and its log says why.

        """
        first: Future[Path] | None
        if (first := (ready or {}).get(name)) is not None:
            _ = first.exception()  # it failing is the step's to say
        wanted: sizing.Wanted = self.plan.wanted(job.tree, name, heavy=entry.heavy)
        port: _Held = (self.ports.get(entry.port) if name in _BOUND else None) or contextlib.nullcontext()
        asked: float = time.perf_counter()
        with port:
            held: int = self.slots.take(wanted.cpus, wanted.memory, wanted.lasting, wanted.least)
            memory: int = self.slots.share(wanted.cpus, wanted.memory, held)
            hold: _Hold = _Hold(wanted._replace(cpus=held, memory=memory), (held, memory))
            start: float = time.perf_counter()
            try:
                used: sizing.Used = self.process(entry, job, name, hold)
            finally:
                self.slots.give(*hold.held)
        return self.recorded(job, name, hold.wanted, used, (start - asked, time.perf_counter() - start))

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
            } | ({sizing.WORKERS: wanted.cpus} if name in sizing.TESTING else {})
            self.store.write(job.tree.name, job.recorded, name, record)
        said: str = (
            "failed" if record is None else f"{used.cpu:.0f} CPU seconds, {used.memory / sizing.GIB:.1f} GB"
        )
        said += f" (given {given['cpus']} CPUs, {given['memory']} GB; waited {waited:.0f}s)"
        line: str = f"{job.recorded} on {job.tree.name}: {name}: {seconds:.0f}s, {said}\n"
        _ = sys.stderr.write(line)
        file: IO[str]
        with (self.store.root / _LOG).open("a", encoding="utf-8") as file:
            _ = file.write(f"{datetime.now().astimezone():%H:%M:%S} {line}")
        return record is not None

    def steps(
        self,
        entry: catalog.Entry,
        job: pipeline.Job,
        names: Sequence[str],
        at_once: int = 1,
        ready: Mapping[str, Future[Path]] | None = None,
    ) -> list[str]:
        """Run each of `names`, the job's steps, that has no record yet, `at_once` of them side by side.

        `ready`: what a step waits for before it asks for its share of the machine.

        Returns:
          Those that failed, each as the run's last lines say it.

        """
        lacking: list[str] = [
            name for name in names if self.store.read(job.tree.name, job.recorded, name) is None
        ]
        pool: ThreadPoolExecutor
        with ThreadPoolExecutor(max(1, min(at_once, len(lacking)))) as pool:
            done: list[bool] = list(pool.map(partial(self.step, entry, job, ready=ready), lacking))
        log: Path = self.store.logged(job.tree.name, job.recorded, "").parent
        return [
            f"{entry.name}, {job.recorded}: {name} ({log / name}.log)"
            for name, has in zip(lacking, done, strict=True)
            if not has
        ]

    def measured(self, entry: catalog.Entry) -> _Measured:
        """Measure one corpus with each of the run's versions.

        Its steps side by side, each on a copy or reading the tree; then its suite's, which wait
        for its fixes: its traced tests, then its tests beside its type checks, which have a
        checkout of their own, installed beside the steps before them. Its traced tests start
        sooner: they run the released source and want only `fix-unsafe`'s fixes, so they wait for
        that step, and for each other to end or to have its copy of the tree (`_started`). Not the
        timed ones (`timed`).

        Returns:
          The corpus's tree, and the steps that failed: each has its traceback in its log, and no
          record. No tree, and why, for a corpus that isn't to be had: the run goes on without it.

        """
        with self.finding:
            try:
                tree: trees.Tree = trees.found(entry, install=self.run.install)
            except (OSError, RuntimeError, ValueError) as failure:  # it can't be cloned, installed or fetched
                return None, [f"{entry.name}: not found: {str(failure)[-_SAID:]}"]
        failed: list[str] = []
        version: str
        for version in self.run.versions:
            failed += self._versioned(entry, pipeline.Job(self.run, self.store, tree, version))
        return tree, failed

    def _versioned(self, entry: catalog.Entry, job: pipeline.Job) -> list[str]:
        """Measure one corpus with one version (see `measured`).

        Returns:
          The steps that failed.

        """
        beside: list[str] = [name for name in pipeline.steps(self.run) if name not in sizing.TIMED]
        waiting: list[str] = list(suite_steps.waiting(job))
        early: list[str] = [name for name in waiting if name == pipeline.TRACED]
        name: str
        for name in beside:
            (job.work(name) / launch.COPIED).unlink(missing_ok=True)  # an earlier attempt's
        failed: list[str] = []
        ran: list[str] = []
        installing: ThreadPoolExecutor = ThreadPoolExecutor(1)
        ready: dict[str, Future[Path]] = (
            {pipeline.TYPES: installing.submit(suite_steps.apart, job)} if pipeline.TYPES in waiting else {}
        )
        pool: ThreadPoolExecutor
        with ThreadPoolExecutor(1) as pool:
            sides: Future[list[str]] = pool.submit(self.steps, entry, job, beside, len(beside))
            if early and self._started(job, beside, sides):
                ran = early
                failed += self.steps(entry, job, ran)
            failed += sides.result()
        failed += self.steps(entry, job, [name for name in early if name not in ran])
        after: list[str] = [name for name in waiting if name not in early]
        try:
            return failed + self.steps(entry, job, after, len(after), ready)  # its tests, and its type checks
        finally:
            installing.shutdown()

    def _started(self, job: pipeline.Job, beside: Sequence[str], sides: "Future[list[str]]") -> bool:
        """Wait until a corpus's traced tests may start beside its other steps, `beside`, under way.

        Until `fix-unsafe` has its record, and each other step has ended or has made its copy of
        the tree (`launch.COPIED`): the traced tests write into the checkout the others read.

        Returns:
          Whether they may: not once the steps have all ended, which leaves them their turn after.

        """
        unsafe: str = f"{pipeline.FIX}{UNSAFE}"
        for _ in iter(sides.done, _DONE):
            ended: set[str] = {
                name for name in beside if self.store.read(job.tree.name, job.recorded, name) is not None
            }
            if unsafe in ended and all(
                name in ended or (job.work(name) / launch.COPIED).exists() for name in beside
            ):
                return True
            time.sleep(_POLL)
        return False

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
    run: Run = commanded(read(Path(argv[0])), argv)
    facts: Record = _facts(run, datetime.now().astimezone())
    folder: Path = _folder(argv, run, facts)
    store: pipeline.Store = pipeline.Store(folder)
    measured: list[_Measured] = _all(run, store)
    shutil.rmtree(folder / "work", ignore_errors=True)  # the copies its fixes worked on
    if _RESUME not in argv:  # a resumed run's own time says nothing of the whole run's
        facts[render.MINUTES] = round((time.perf_counter() - start) / 60)
    records: render.Records = render.gathered(run, store, [tree for tree, _ in measured if tree])
    written: list[Path] = render.write(records, folder, facts)
    if _ONLY not in argv:  # a part of the run's corpora isn't what its section is of
        render.publish(records, _ROOT, facts)
    _ = sys.stdout.write("".join(f"{path}\n" for path in written))
    failed: list[str] = [f"failed: {each}" for _, failures in measured for each in failures]
    failed += [f"problem: {each}" for each in render.problems(records)]
    noted: list[str] = [f"note: {each}" for each in render.notes(records)]
    _ = sys.stderr.write("".join(f"{each}\n" for each in (*noted, *failed)))
    return int(bool(failed))


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
    _ = (folder / "facts.toml").write_text(_toml(facts), encoding="utf-8")
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
    entries: list[catalog.Entry] = [known.entry(name) for name in known.names(list(run.include))]
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
    )
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, len(entries))) as pool:
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
