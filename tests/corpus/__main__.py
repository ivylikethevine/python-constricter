# SPDX-License-Identifier: MIT
"""Measure corpora as a run file says, into a folder of that run's own.

    local/.venv/bin/python -m tests.corpus RUN.toml                   # a new folder, named by label and time
    local/.venv/bin/python -m tests.corpus RUN.toml --resume FOLDER   # carry on a stopped run in its folder
    local/.venv/bin/python -m tests.corpus RUN.toml --only NAME       # on that corpus or set alone
    local/.venv/bin/python -m tests.corpus RUN.toml --label NAME      # under that label
    local/.venv/bin/python -m tests.corpus RUN.toml --at-once N --jobs M   # sized for this machine

The run file (`run_config`) names the corpora (`corpora.toml`'s), the constricter versions, the
steps and the formats. Each execution writes `<output>/<label>-<month>-<day>-<year>-<time>/`:

    run.toml      the run file, copied
    facts.toml    the run as it was read, the commit and the machine
    records/      <corpus>/<version>/<step>.json, and each fix's patch: what every output is made from
    logs/         what each step's constricter wrote to standard error
    report.json   report.md   tables/*.csv

A run of all its corpora is published where its run file says (`render.publish`); one kept to some
with `--only` isn't.

Corpora are measured `at-once` at a time. Each step is a process of its own (`--step`), started once
the CPUs it's expected to keep busy and the memory it's expected to hold are free (`sizing`), and its
record says what its processes used: a corpus's steps side by side, then its suite's own tests and
checks one after another on their checkout (those of one port one suite at a time); and once every
corpus is measured, each one's timed checks, with nothing beside them. Every step starts
constricter one way (`launch.run`) on one tree a corpus (`trees.Tree`), so a count in one table is
the count in another.
"""

import contextlib
import itertools
import os
import platform
import re
import shutil
import subprocess  # asks git for the commit, and runs each step
import sys
import threading
import time
from collections.abc import Callable, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import __version__
from constricter.rules import parsed
from tests.corpus import catalog, launch, pipeline, render, sizing, suite_steps, trees
from tests.corpus.pipeline import Record
from tests.corpus.run_config import Run, read

_Held: TypeAlias = contextlib.AbstractContextManager[bool | None]  # a lock, or nothing to hold
_Measured: TypeAlias = tuple[trees.Tree | None, list[str]]  # a corpus's tree, and its steps that failed
_RESUME: Final = "--resume"
_AT_ONCE: Final = "--at-once"  # then how many corpora are measured side by side, whatever the file says
_JOBS: Final = "--jobs"  # and constricter's worker processes
_LABEL: Final = "--label"  # then the run's label, whatever its file says
_SAID: Final = 2000  # the characters kept of why a corpus couldn't be had: the end of its build's output
_ONLY: Final = "--only"  # then a corpus or a set: the run file's, on that alone
_STEP: Final = "--step"  # then a run's folder, a corpus, a version and a step: that step alone
_ROOT: Final = Path(__file__).resolve().parents[2]
_MODEL: Final = re.compile(r"^model name\s*:\s*(.+)$", re.MULTILINE)  # in Linux's `/proc/cpuinfo`
_BOUND: Final = frozenset({pipeline.TESTS, pipeline.TRACED})  # the steps that bind a suite's port


def _facts(run: Run, started: datetime) -> Record:
    """Gather what a run's outputs say of the run itself.

    Returns:
      The run file's values, this checkout's version and commit, and the machine.

    """
    try:
        model: re.Match[str] | None = _MODEL.search(Path("/proc/cpuinfo").read_text(encoding="utf-8"))
    except OSError:
        model = None
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
        "machine": model[1] if model else platform.processor() or platform.machine(),
        "system": platform.system(),
        "cpus": os.cpu_count() or 1,
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
    return said | ({"CORPUS_SUITE_WORKERS": str(run.suite_workers)} if run.suite_workers else {})


class Running(NamedTuple):
    """A run under way: its folder, what its steps share of the machine, and what counts their use."""

    run: Run
    store: pipeline.Store
    plan: sizing.Plan
    slots: sizing.Slots
    watcher: sizing.Watcher | None  # `None`: nothing counts a step's use
    ports: dict[str, threading.Lock]  # each port's lock, held while a suite's tests have the port

    def process(self, entry: catalog.Entry, job: pipeline.Job, name: str) -> sizing.Used:
        """Run one step in a process of its own, what it says kept in its log.

        Returns:
          What the process and every one under it used; nothing where nothing counts it.

        """
        command: list[str] = [sys.executable, "-m", "tests.corpus", _STEP, str(self.store.root)]
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
                env=os.environ | _suited(self.run),
            ) as process,
        ):
            if self.watcher is not None:
                self.watcher.watch(process.pid)
            _ = process.wait()
        return sizing.Used() if self.watcher is None else sizing.Used(*self.watcher.used(process.pid))

    def step(self, entry: catalog.Entry, job: pipeline.Job, name: str) -> bool:
        """Run one step (`process`), once what it's expected to take is free (`sizing`).

        Its tests' port first, if they bind one: waited for holding nothing. What it used goes
        into the step's record, with what it was given.

        Returns:
          Whether the step has a record: one that failed has none, and its log says why.

        """
        wanted: sizing.Wanted = self.plan.wanted(job.tree, name, heavy=entry.heavy)
        port: _Held = (self.ports.get(entry.port) if name in _BOUND else None) or contextlib.nullcontext()
        with port:
            held: int = self.slots.take(*wanted)
            start: float = time.perf_counter()
            try:
                used: sizing.Used = self.process(entry, job, name)
            finally:
                self.slots.give(held, wanted.memory)
        seconds: float = time.perf_counter() - start
        record: Record | None = self.store.read(job.tree.name, job.recorded, name)
        given: Record = {"cpus": held, "memory": round(min(wanted.memory, self.plan.memory) / sizing.GIB, 2)}
        if record is not None:
            record[sizing.USED] = {
                "seconds": round(seconds, 1),
                "cpu": round(used.cpu, 1),
                "memory": round(used.memory / sizing.GIB, 2),
                "given": given,
                "alone": wanted.memory >= self.plan.memory,
            }
            self.store.write(job.tree.name, job.recorded, name, record)
        said: str = (
            "failed" if record is None else f"{used.cpu:.0f} CPU seconds, {used.memory / sizing.GIB:.1f} GB"
        )
        had: str = f"given {given['cpus']} CPUs, {given['memory']} GB"
        _ = sys.stderr.write(f"{job.recorded} on {job.tree.name}: {name}: {seconds:.0f}s, {said} ({had})\n")
        return record is not None

    def steps(
        self,
        entry: catalog.Entry,
        job: pipeline.Job,
        names: Sequence[str],
        at_once: int = 1,
    ) -> list[str]:
        """Run each of `names`, the job's steps, that has no record yet, `at_once` of them side by side.

        Returns:
          Those that failed, each as the run's last lines say it.

        """
        lacking: list[str] = [
            name for name in names if self.store.read(job.tree.name, job.recorded, name) is None
        ]
        pool: ThreadPoolExecutor
        with ThreadPoolExecutor(max(1, min(at_once, len(lacking)))) as pool:
            done: list[bool] = list(pool.map(partial(self.step, entry, job), lacking))
        log: Path = self.store.logged(job.tree.name, job.recorded, "").parent
        return [
            f"{entry.name}, {job.recorded}: {name} ({log / name}.log)"
            for name, has in zip(lacking, done, strict=True)
            if not has
        ]

    def measured(self, entry: catalog.Entry) -> _Measured:
        """Measure one corpus with each of the run's versions.

        Its steps side by side, each on a copy or reading the tree; then its suite's, which wait
        for its fixes and share its checkout, one after another. Not the timed ones (`timed`).

        Returns:
          The corpus's tree, and the steps that failed: each has its traceback in its log, and no
          record. No tree, and why, for a corpus that isn't to be had: the run goes on without it.

        """
        try:
            tree: trees.Tree = trees.found(entry, install=self.run.install)
        except (OSError, RuntimeError, ValueError) as failure:  # it can't be cloned, installed or fetched
            return None, [f"{entry.name}: not found: {str(failure)[-_SAID:]}"]
        failed: list[str] = []
        version: str
        for version in self.run.versions:
            job: pipeline.Job = pipeline.Job(self.run, self.store, tree, version)
            every: list[str] = list(pipeline.steps(self.run))
            beside: list[str] = [name for name in every if name not in sizing.TIMED]
            failed += self.steps(entry, job, beside, len(beside))
            failed += self.steps(entry, job, list(suite_steps.waiting(job)))
        return tree, failed

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


def _said(run: Run, argv: Sequence[str]) -> Run:
    """Read what a command says of its run, whatever the run file does.

    Returns:
      The run, with the command's corpora, label, corpora at once and `--jobs`.

    """
    if _ONLY in argv:
        run = run._replace(include=(argv[argv.index(_ONLY) + 1],))
    if _LABEL in argv:
        run = run._replace(label=argv[argv.index(_LABEL) + 1])
    if _AT_ONCE in argv:
        run = run._replace(at_once=int(argv[argv.index(_AT_ONCE) + 1]))
    if _JOBS in argv:
        run = run._replace(jobs=int(argv[argv.index(_JOBS) + 1]))
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
    run: Run = _said(read(folder / "run.toml"), argv[4:])
    tree: trees.Tree = trees.found(catalog.load().entry(corpus), install=run.install)
    job: pipeline.Job = pipeline.Job(run, pipeline.Store(folder), tree, version)
    step: Callable[[pipeline.Job], Record] = (pipeline.steps(run) | suite_steps.waiting(job))[name]
    job.store.path(tree.name, job.recorded, name).parent.mkdir(parents=True, exist_ok=True)
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(1) as pool:  # a future keeps what the step raises, whatever it is
        done: Future[Record] = pool.submit(step, job)
    return int(not pipeline.settled(job, name, done))


def main(argv: Sequence[str]) -> int:
    """Run the run file named, write its folder, and say where it is.

    Returns:
      1 if a step failed (the outputs have the rest; `--resume` makes it again) or a fix broke
      something (`render.problems`), else 0.

    """
    if argv[:1] == [_STEP]:
        return _step(argv[1:])
    start: float = time.perf_counter()
    run: Run = _said(read(Path(argv[0])), argv)
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
    """Measure each of the run's corpora, `at-once` of them at a time, then time each: nothing beside it.

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
    running: Running = Running(
        run,
        store,
        plan,
        sizing.Slots(plan.cpus, plan.memory),
        sizing.watcher(),
        {entry.port: threading.Lock() for entry in entries if entry.port},
    )
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(run.at_once) as pool:
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
