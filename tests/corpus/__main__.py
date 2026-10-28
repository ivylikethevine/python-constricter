"""Measure corpora as a run file says, into a folder of that run's own.

    local/.venv/bin/python -m tests.corpus RUN.toml                   # a new folder, named by label and time
    local/.venv/bin/python -m tests.corpus RUN.toml --resume FOLDER   # carry on a stopped run in its folder
    local/.venv/bin/python -m tests.corpus RUN.toml --only NAME       # on that corpus or set alone
    local/.venv/bin/python -m tests.corpus RUN.toml --minus NAME      # less that corpus, set or run file's
    local/.venv/bin/python -m tests.corpus RUN.toml --label NAME      # under that label
    local/.venv/bin/python -m tests.corpus RUN.toml --at-once N --jobs M   # sized for this machine
    local/.venv/bin/python -m tests.corpus RUN.toml --share 75        # 75% of its CPUs and memory
    local/.venv/bin/python -m tests.corpus RUN.toml --stage fixes     # that stage's steps alone (`stages`)
    local/.venv/bin/python -m tests.corpus RUN.toml --resume FOLDER --stage tests   # the next, joined to it

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

A run can be made in stages, each at its own time (`--stage`, see `stages`): each execution runs one
stage's steps into the folder, a step whose needs are a stage still to run left for later, and the
report is written from the records so far, naming the stages left; it's published once every stage
is in. A stage joins a folder only on the commit, the uncommitted changes and the run file the
folder's earlier stages ran on, unless `--join-anyway`: its facts then give each stage's.

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
import math
import os
import shutil
import subprocess  # asks git for the commit, and runs each step
import sys
import threading
import time
from collections.abc import Callable, Generator, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import IO, TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast

from tests.corpus import (
    catalog,
    launch,
    pipeline,
    planning,
    render,
    report_tables,
    resume,
    sizing,
    stages,
    suite_checkouts,
    suite_steps,
    trees,
)
from tests.corpus.pipeline import Record
from tests.corpus.run_config import FACTS, JOBS, LABEL, ROOT, Command, Run, percent, read, read_command

if TYPE_CHECKING:
    import resource

_Measured: TypeAlias = tuple[trees.Tree | None, list[str]]  # a corpus's tree, and its steps that failed
_STEP: Final = "--step"  # then a run's folder, a corpus, a version and a step: that step alone
_LEFT: Final = "stages-left"  # in a run's facts: the stages still to run
_POLL: Final = 0.2  # the seconds between looks at whether a step's process has ended
_LOOK: Final = 60.0  # and between fittings of its hold to what it's using
_DONE: Final = True  # what an event's `wait` says once it's set
_MACOS: Final = "darwin"
_QUEUE: Final = "queue.log"  # in a run's folder: its queue, each minute steps wait
_SUITE_WORKERS: Final = "CORPUS_SUITE_WORKERS"  # in a step's environment: its suite's tests' processes
_SAMPLED: Final = "sampled"  # what read a step's use outside a scope: the sampler, the waited count
_MAXRSS: Final = (
    1 if sys.platform == _MACOS else 1024
)  # the bytes `ru_maxrss` counts in: kilobytes, but there


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
    checkouts: dict[tuple[str, str], threading.Lock]  # each suite checkout's lock, as `ports`, made as asked
    scope: tuple[str, ...] = ()  # what starts a step in a scope of its own (`sizing.scope`): nothing, none
    ranks: Mapping[tuple[str, str], float] | None = None  # each step's planned start (`planning.ranks`)
    chosen: Callable[[str], bool] | None = None  # the steps this execution's stage runs: `None`, every one

    def process(self, entry: catalog.Entry, job: pipeline.Job, name: str, hold: "_Hold") -> sizing.Used:
        """Run one step in a process of its own, what it says kept in its log.

        `hold`: what it holds of the machine, fitted every `_LOOK` seconds to what it's using.

        In a scope of its own where `scope` says, which it reads the count of as it ends (`_step`). A
        suite's tests take the workers its hold says (`Wanted.started`), and a hinted step's servers
        the memory (`Wanted.hinted`).

        Returns:
          What the process and every one under it used: the most of what was read as it ran and
          of what the system counted for it and those it waited for, which has the ones too short
          to read (their CPU seconds, and the largest one's most memory). Nothing where nothing
          counts it.

        """
        command: list[str] = [*self.scope, sys.executable, "-m", "tests.corpus", _STEP, str(self.store.root)]
        scoped: dict[str, str] = {sizing.SCOPED: "1"} if self.scope else {}
        scoped |= {_SUITE_WORKERS: str(hold.wanted.workers)} if sizing.testing(name) else {}
        servers: int = hold.wanted.servers
        scoped |= {pipeline.INFER_MEMORY: f"{servers / sizing.GIB:.2f}"} if servers else {}
        said: list[str] = [
            LABEL,
            self.run.label,
            JOBS,
            str(self.run.jobs),
        ]  # what the run's command said
        file: IO[str]
        process: subprocess.Popen[bytes]
        with (
            self.store.logged(job.tree.name, job.recorded, name).open("a", encoding="utf-8") as file,
            subprocess.Popen(
                [*command, entry.name, job.version, name, *said],
                stdout=file,
                stderr=subprocess.STDOUT,
                cwd=ROOT,
                env=os.environ | _suited(self.run) | scoped,
            ) as process,
        ):
            if self.watcher is not None:
                self.watcher.watch(process.pid)
            counted: sizing.Used = self._waited(process, hold, f"{entry.name}/{name}")
        if self.watcher is None:
            return sizing.Used()
        used: sizing.Used = self.watcher.used(process.pid)
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
                seen: sizing.Used = self.watcher.seen(process.pid)
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
        given: sizing.Wanted = wanted._replace(
            cpus=held,
            memory=memory,
            workers=wanted.started(held),
            servers=wanted.hinted(held),
        )
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
        port: threading.Lock | None = self.ports.get(entry.port) if suite_checkouts.binds(name) else None
        locks: list[threading.Lock] = [
            self.checkouts.setdefault((entry.name, each), threading.Lock())
            for each in (suite_checkouts.checkouts(job, name) if job.tree.suite is not None else ())
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
        with (self.store.root / resume.LOG).open("a", encoding="utf-8") as file:
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
        if name == pipeline.TESTS_RELEASED and (taken := suite_steps.taken(job)) is not None:
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
                why: str = f"{entry.name}: not found: {str(failure)[-pipeline.TAIL :]}"
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
        checkouts it works on are installed (`suite_checkouts.checkouts`): those of a suite's steps, a
        kind each, one after another beside the steps before them. Only the stage's, where the
        execution runs one (`chosen`), less those needing a step of a stage still to run.

        Returns:
          The steps that failed.

        """
        last: frozenset[str] = sizing.held_last(self.run)
        beside: list[str] = [name for name in pipeline.steps(self.run) if name not in last]
        suited: list[str] = [name for name in suite_steps.waiting(job) if self._chosen(name)]
        needs: dict[str, frozenset[str]] = suite_steps.needs(job)
        names: list[str] = self._runnable(job, _ordered([*beside, *suited], needs), needs)
        suited = [name for name in suited if name in names]
        ended: dict[str, Future[bool]] = {}
        installing: ThreadPoolExecutor
        pool: ThreadPoolExecutor
        # Each step waits on its own thread; the checkouts are installed one after another.
        with ThreadPoolExecutor(1) as installing, ThreadPoolExecutor(max(1, len(names))) as pool:
            installed: dict[str, Future[Path]] = {
                each: installing.submit(suite_checkouts.prepared, job, each)
                for each in dict.fromkeys(
                    each for name in suited for each in suite_checkouts.checkouts(job, name)
                )
            }
            name: str
            for name in names:  # those a step waits for come before it
                after: list[Future[bool]] = [ended[each] for each in needs.get(name, ()) if each in ended]
                ready: list[Future[Path]] = (
                    [installed[each] for each in suite_checkouts.checkouts(job, name)]
                    if name in suited
                    else []
                )
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
        last: frozenset[str] = sizing.held_last(self.run)
        version: str
        for version in self.run.versions:
            job: pipeline.Job = pipeline.Job(self.run, self.store, tree, version)
            failed += self.steps(
                entry,
                job,
                [name for name in pipeline.steps(self.run) if name in last and self._chosen(name)],
            )
        return failed

    def _chosen(self, name: str) -> bool:
        return (self.chosen or stages.every)(name)

    def _runnable(
        self,
        job: pipeline.Job,
        names: Sequence[str],
        needs: Mapping[str, frozenset[str]],
    ) -> list[str]:
        """Keep the stage's steps of `names` (`chosen`) whose needs this execution makes or a record has.

        Returns:
          Them, in order; each left for later said in the run's log.

        """
        kept: list[str]
        left: list[str]
        kept, left = stages.runnable(
            [name for name in names if self._chosen(name)],
            needs,
            lambda each: self.store.read(job.tree.name, job.recorded, each) is not None,
        )
        name: str
        for name in left:
            self.said(f"{job.recorded} on {job.tree.name}: {name}: left for the stage it needs")
        return kept


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


def commanded(run: Run, said: Command) -> Run:
    """Read what a command says of its run, whatever the run file does.

    Returns:
      The run, with the command's corpora, label, corpora at once, `--jobs` and `--share`.

    """
    if said.only is not None:
        run = run._replace(include=(said.only,))
    if said.minus is not None:
        less: Run | None = read(Path(said.minus)) if said.minus.endswith(".toml") else None
        names: list[str] = [said.minus] if less is None else catalog.load().names(list(less.include))
        run = run._replace(minus=tuple(names))
    if said.label is not None:
        run = run._replace(label=said.label)
    if said.at_once is not None:
        run = run._replace(at_once=said.at_once)
    if said.jobs is not None:
        run = run._replace(jobs=said.jobs)
    if said.share is not None:
        run = run._replace(share=percent(said.share))
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
    run: Run = commanded(read(folder / "run.toml"), read_command(argv[4:], run_file=False))
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
    said: Command = read_command(argv)
    earlier: Record = resume.resumed_facts(said)
    run: Run = resume.relabelled(commanded(read(cast("Path", said.run_file)), said), said, earlier)
    stage: str | None = None if said.stage is None else stages.named(said.stage, run.stages)
    launch.configure(run.options)
    facts: Record = resume.carried(
        resume.run_facts(run, datetime.now().astimezone()),
        earlier,
        resume.last_written(said),
    )
    facts = resume.joined(said, earlier, facts, stage)
    folder: Path = resume.run_folder(said, run, facts)
    store: pipeline.Store = pipeline.Store(folder)
    measured: list[_Measured] = _all(run, store, None if stage is None else stages.chosen(stage, run.stages))
    shutil.rmtree(folder / "work", ignore_errors=True)  # the copies its fixes worked on
    facts = resume.finished(facts, (time.perf_counter() - start) / 60)
    if resume.STAGES in facts:
        facts[_LEFT] = stages.left(
            run.stages,
            resume.missing(run, store, [tree for tree, _ in measured if tree]),
        )
    _ = (folder / FACTS).write_text(resume.facts_toml(facts), encoding="utf-8")
    records: report_tables.Records = render.gathered(run, store, [tree for tree, _ in measured if tree])
    written: list[Path] = render.write(records, folder, facts)
    # A part of its corpora, or of its stages, isn't what its section is of.
    if said.only is None and said.minus is None and not facts.get(_LEFT):
        render.publish(records, ROOT, facts)
    _ = sys.stdout.write("".join(f"{path}\n" for path in written))
    failed: list[str] = [f"failed: {each}" for _, failures in measured for each in failures]
    failed += [f"problem: {each}" for each in render.problems(records)]
    noted: list[str] = [f"note: {each}" for each in render.notes(records)]
    _ = sys.stderr.write("".join(f"{each}\n" for each in (*noted, *failed)))
    return int(bool(failed))


def _all(run: Run, store: pipeline.Store, chosen: Callable[[str], bool] | None = None) -> list[_Measured]:
    """Measure the run's corpora side by side, found `at-once` at a time, then time each: nothing beside it.

    Each corpus's steps wait for the machine alone (`sizing`): a corpus whose step waits keeps no
    other from starting. `chosen`: the steps a stage runs (`stages.chosen`); `None`, every one.

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
    plan: sizing.Plan = sizing.plan(run, store.root, ROOT)
    # Its steps held to its share of the machine, where it has one.
    scope: tuple[str, ...] = sizing.scope(ROOT, plan if run.share else None)
    running: Running = Running(
        run,
        store,
        plan,
        sizing.Slots(plan.cpus, plan.memory),
        sizing.watcher(scoped=bool(scope)),
        {entry.port: threading.Lock() for entry in entries if entry.port},
        threading.Semaphore(max(1, run.at_once)),
        {},
        scope,
        planning.ranks(run, entries, plan, chosen),
        chosen,
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
