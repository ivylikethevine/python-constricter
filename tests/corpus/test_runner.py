# SPDX-License-Identifier: MIT
"""The corpus runner's own parts that need no corpus: its run file, and how it runs and sizes its steps."""

import os
import shutil
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Final, cast

import pytest

from constricter import Level
from tests.corpus import __main__ as runner
from tests.corpus import catalog, corpus_suite, pipeline, sizing, suite_steps
from tests.corpus.pipeline import Record, Store
from tests.corpus.recorded import SHARE, USED
from tests.corpus.run_config import CERTAIN, CSV, DEV, LIKELY, Run, Steps, parse
from tests.corpus.trees import Tree

_SLICED: Final = "--slice=constricter-corpus.slice"  # `systemd-run`'s, for a run with a share
_SET: Final = "set-property"  # `systemctl`'s, setting the slice's limits
_BASE: Final = "base"  # a version that names another Python
_PYREFLY: Final = "pyrefly"
_WINDOWS: Final = "nt"  # `os.name`'s


def test_a_run_file_is_read_with_defaults_for_what_it_leaves_out() -> None:
    """Each table's keys are read; a key, a format or a fix this doesn't know is an error."""
    assert parse({}) == Run()
    run: Run = parse(
        {
            "run": {
                "label": "0.3.6-rc.1",
                "output": "out",
                "versions": ["0.3.1", DEV],
                "formats": [CSV],
                "jobs": 4,
                "at-once": 2,
            },
            "corpora": {"include": ["pydantic"]},
            "steps": {
                "check": False,
                "fix": ["unsafe"],
                "coverage": False,
                "infer-with": ["ty"],
                "census": False,
            },
        },
    )
    assert run == Run(
        "0.3.6-rc.1",
        Path("out"),
        ("0.3.1", DEV),
        (CSV,),
        4,
        ("pydantic",),
        Steps(check=False, fix=("unsafe",), coverage=False, infer=("ty",), census=False),
        at_once=2,
    )
    assert [run.recorded(version) for version in run.versions] == ["0.3.1", "0.3.6-rc.1+dev"]
    assert run.recorded(f"{_BASE}=local/base/bin/python") == _BASE
    with pytest.raises(ValueError, match=r"\[steps\] lint"):
        _ = parse({"steps": {"lint": True}})
    with pytest.raises(ValueError, match="checker 'mypy'"):
        _ = parse({"steps": {"infer-with": ["mypy"]}})
    with pytest.raises(ValueError, match=r"\[publish\] where"):
        _ = parse({"publish": {"where": "x"}})
    with pytest.raises(ValueError, match="format 'html'"):
        _ = parse({"run": {"formats": ["html"]}})
    with pytest.raises(ValueError, match="fix 'all'"):
        _ = parse({"steps": {"fix": ["all"]}})


def test_a_step_waits_for_the_cpus_and_the_memory_it_wants() -> None:
    """One that fits starts beside those running; one that wants all the memory runs alone."""
    slots: sizing.Slots = sizing.Slots(4, 10)
    held: int = slots.take(sizing.Wanted(2, 6))
    assert (held, slots.free, slots.held) == (2, 2, 6)
    second: int = slots.take(sizing.Wanted(2, 4))
    assert sizing.Slots(4, 10).take(sizing.Wanted(9, 0)) == slots.cpus  # more CPUs than there are: every one
    started: threading.Event = threading.Event()

    def alone() -> None:
        slots.give(slots.take(sizing.Wanted(1, 10)), 10)
        started.set()

    waiting: threading.Thread = threading.Thread(target=alone, daemon=True)
    waiting.start()
    assert not started.wait(0.2)
    slots.give(held, 6)
    assert not started.wait(0.2)
    slots.give(second, 4)
    assert started.wait(5)
    waiting.join()
    assert (slots.free, slots.held, slots.running) == (4, 0, 0)
    assert parse({"run": {"suite-seconds": 900, "suite-workers": 4, "cpus": 8, "memory": 12}})[-6:-1] == (
        900,
        4,
        8,
        12.0,
        0,
    )
    switched: Record = {"tests-hinted": False, "every-level": True, "tests-released": False}
    asked: Steps = parse({"steps": switched}).steps
    assert (asked.tests_hinted, asked.every_level, asked.tests_released) == (False, True, False)
    assert (Steps().tests_hinted, Steps().every_level, Steps().tests_released) == (True, False, True)


def test_a_suites_tests_start_with_half_the_cpus_they_want_and_take_whats_free() -> None:
    """With as much memory for each CPU as they wanted, the more they hold."""
    slots: sizing.Slots = sizing.Slots(8, 16)
    first: int = slots.take(sizing.Wanted(5, 5))
    held: int = slots.take(sizing.Wanted(8, 16, least=2))
    assert (held, slots.share(8, 16, held)) == (3, 6)
    assert (slots.free, slots.held) == (0, 11)
    slots.give(held, 6)
    slots.give(first, 5)
    assert slots.take(sizing.Wanted(8, 16, least=2)) == slots.cpus


def test_a_suites_parts_run_side_by_side(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """As many at once as it has workers, each with one process; their outcomes added up."""
    tests: tuple[str, ...] = (*catalog.PYTEST, "-n", catalog.WORKERS)
    suite: catalog.Suite = catalog.Suite("", "", "", (), tests, parts=("a", "b", "c"))
    both: threading.Barrier = threading.Barrier(2, timeout=5)  # two of them at once, or it breaks
    ran: list[list[str]] = []

    def workers(_suite: catalog.Suite) -> int:
        return both.parties

    def completed(args: list[str], *_args: object, **_options: object) -> SimpleNamespace:
        ran.append(args)
        if len(ran) <= both.parties:
            _ = both.wait()
        return SimpleNamespace(stdout="1 passed in 0.1s", stderr="")

    monkeypatch.setattr(corpus_suite, "workers", workers)
    monkeypatch.setattr(corpus_suite, "_completed", completed)
    assert corpus_suite.tested(tmp_path, suite, None).counts == {"passed": 3}
    assert sorted(command[-1] for command in ran) == ["a", "b", "c"]
    assert all(command[-3:-1] == ["-n", "1"] for command in ran)


def test_a_steps_record_says_when_it_started_and_how_long_it_waited(tmp_path: Path) -> None:
    """With its control group's count, the workers its tests took, and a line in the run's log."""
    run: Run = parse({})
    store: Store = Store(tmp_path)
    plan: sizing.Plan = sizing.Plan(run, 8, 16 * sizing.GIB, {})
    slots: sizing.Slots = sizing.Slots(8, 16)
    running: runner.Running = runner.Running(run, store, plan, slots, None, {}, threading.Semaphore())
    job: pipeline.Job = pipeline.Job(run, store, Tree("celery", "1", tmp_path), DEV)
    store.write("celery", job.recorded, pipeline.TESTS, {"scope": {"cpu": 30.0, "memory": 2 * sizing.GIB}})
    took: tuple[float, float] = (12.0, 60.0)
    before: float = time.time()
    assert running.recorded(job, pipeline.TESTS, sizing.Wanted(4, 8 * sizing.GIB), sizing.Used(1.0, 1), took)
    record: Record | None = store.read("celery", job.recorded, pipeline.TESTS)
    assert record is not None
    assert sizing.SCOPE not in record
    used: Record = cast("Record", record["used"])
    assert before - 61 <= cast("float", used.pop("started")) <= time.time() - 59
    assert used == {
        "by": sizing.SCOPE,
        "waited": 12.0,
        "seconds": 60.0,
        "cpu": 30.0,
        "memory": 2.0,
        "given": {"cpus": 4, "memory": 8.0},
        "alone": False,
        "workers": 4,
    }
    said: str = (tmp_path / "runner.log").read_text(encoding="utf-8")
    assert said.endswith(": tests: 60s, 30 CPU seconds, 2.0 GB (given 4 CPUs, 8.0 GB; waited 12s)\n")


def _waited(slots: sizing.Slots) -> bool:
    """Wait for a step to be waiting for `slots`, 5 seconds at most.

    Returns:
      Whether one is.

    """
    for _ in range(500):
        if slots.waiting:
            return True
        time.sleep(0.01)
    return False


def test_a_step_that_waited_long_has_whats_free_kept_for_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """None after it starts, though it fits, but one whose last run took `_BESIDE` seconds at most."""
    monkeypatch.setattr(sizing, "_PATIENCE", 0.0)
    slots: sizing.Slots = sizing.Slots(4, 10)
    held: int = slots.take(sizing.Wanted(2, 0))
    started: list[str] = []

    def step(name: str, cpus: int, seconds: float = 0.0) -> None:
        slots.give(slots.take(sizing.Wanted(cpus, 0, seconds=seconds)))
        started.append(name)

    threads: dict[str, threading.Thread] = {
        name: threading.Thread(target=step, args=(name, cpus, seconds), daemon=True)
        for name, cpus, seconds in (("large", 3, 0), ("small", 1, 0), ("long", 1, 600), ("brief", 1, 20))
    }
    threads["large"].start()
    assert _waited(slots)
    name: str
    for name in ("small", "long", "brief"):
        threads[name].start()
    threads["brief"].join(5)
    threads["small"].join(0.3)
    assert started == ["brief"]
    slots.give(held)
    each: threading.Thread
    for each in threads.values():
        each.join()
    assert sorted(started) == ["brief", "large", "long", "small"]
    assert (slots.free, slots.running) == (4, 0)


def test_a_running_steps_hold_follows_what_it_uses() -> None:
    """Unmeasured, it gives back what it isn't using; measured, it keeps its last run's, or takes more."""
    plan: sizing.Plan = sizing.Plan(parse({}), 8, 16 * sizing.GIB, {})
    unmeasured: sizing.Wanted = sizing.Wanted(4, 8 * sizing.GIB)
    assert plan.fitted(unmeasured, (4, 8 * sizing.GIB), 0.4, sizing.GIB) == (1, 2 * sizing.GIB)
    assert plan.fitted(unmeasured, (1, 2 * sizing.GIB), 5.2, 7 * sizing.GIB) == (6, int(8.75 * sizing.GIB))
    measured: sizing.Wanted = unmeasured._replace(measured=True)
    assert plan.fitted(measured, (4, 8 * sizing.GIB), 0.4, sizing.GIB) == (4, 8 * sizing.GIB)
    assert plan.fitted(measured, (4, 8 * sizing.GIB), 20.0, 8 * sizing.GIB) == (8, 10 * sizing.GIB)
    alone: tuple[int, int] = (8, 4 * sizing.GIB)
    assert plan.fitted(sizing.Wanted(8, 4 * sizing.GIB), alone, 1.0, sizing.GIB) == alone
    slots: sizing.Slots = sizing.Slots(8, 16)
    now: tuple[int, int] = slots.resize((slots.take(sizing.Wanted(4, 8)), 8), (6, 12))
    assert (now, slots.free, slots.held) == ((6, 12), 2, 12)
    slots.give(*now)
    assert (slots.free, slots.held) == (8, 0)


def _grouped(root: Path, process: str, group: str, counts: tuple[str, str] | None = None) -> None:
    """Put a process in a control group under `root`, which counts `cpu.stat` and `memory.peak`."""
    (root / "proc" / process).mkdir(parents=True)
    said: str = f"1:name=systemd:/other\n0::/{group}\n"  # a hybrid hierarchy's line first
    _ = (root / "proc" / process / "cgroup").write_text(said, encoding="ascii")
    if counts is not None:
        folder: Path = root / "cgroup" / group
        folder.mkdir(parents=True)
        _ = (folder / "cpu.stat").write_text(f"usage_usec {counts[0]}\nuser_usec 1\n", encoding="ascii")
        _ = (folder / "memory.peak").write_text(f"{counts[1]}\n", encoding="ascii")


def test_a_scope_is_counted_by_its_control_group(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Its CPU seconds and peak memory, as it runs and once it ends; not the runner's group's."""
    monkeypatch.setattr(sizing, "_PROC", tmp_path / "proc")
    monkeypatch.setattr(sizing, "_CGROUPS", tmp_path / "cgroup")
    _grouped(tmp_path, "self", "app.slice/terminal.scope", ("9000000", str(8 * sizing.GIB)))
    _grouped(tmp_path, "42", "app.slice/run-42.scope", ("2500000", str(sizing.GIB)))
    _grouped(tmp_path, "43", "app.slice/run-43.scope")
    assert sizing.counted(sizing.group(42)) == sizing.Used(2.5, sizing.GIB)
    assert sizing.counted(sizing.group(43)) is None
    assert sizing.group(44) is None
    watched: sizing.Grouped = sizing.Grouped()
    watched.watch(42)
    watched.watch(44)
    assert watched.seen(42) == sizing.Used(2.5, sizing.GIB)
    (tmp_path / "proc" / "42" / "cgroup").unlink()  # it ended: what was last read stands
    assert watched.used(42) == sizing.Used(2.5, sizing.GIB)
    _grouped(tmp_path, "44", "app.slice/terminal.scope")  # not moved to a scope of its own yet
    assert watched.used(44) == sizing.Used()


def test_a_step_starts_in_a_scope_only_where_one_is_counted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where `systemd-run` starts a scope whose control group counts it; nowhere else."""
    installed: list[str] = []
    started: list[list[str]] = []

    def which(name: str) -> str | None:
        return f"/usr/bin/{name}" if installed else None

    def probed(command: list[str], **_: object) -> SimpleNamespace:
        started.append(command)
        return SimpleNamespace(returncode=len(started) - 1)  # the first probe's scope counts it

    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr("shutil.which", which)
    monkeypatch.setattr("subprocess.run", probed)
    assert not sizing.scope(Path())
    installed.append("systemd-run")
    scope: tuple[str, ...] = sizing.scope(Path())
    assert scope[:3] == ("systemd-run", "--user", "--scope")
    assert started[0][: len(scope)] == list(scope)
    assert isinstance(sizing.watcher(scoped=True), sizing.Grouped)
    assert not sizing.scope(Path())


def test_a_run_takes_a_share_of_the_machine(monkeypatch: pytest.MonkeyPatch) -> None:
    """Its CPUs and its memory, no more than so much of what's free; refused past the whole of it."""
    monkeypatch.setattr("os.cpu_count", lambda: 16)
    monkeypatch.setattr(sizing, "available", lambda: 40 * sizing.GIB)
    monkeypatch.setattr("constricter.rules.parsed.memory", lambda: 60 * sizing.GIB)
    shared: Run = parse({"run": {"share": 75, "output": "."}})
    assert runner.commanded(Run(), ["--share", "75"]).share == shared.share == SHARE
    plan: sizing.Plan = sizing.plan(shared, Path(), Path())
    assert (plan.cpus, plan.memory) == (12, 32 * sizing.GIB)  # 45 GB is 75%: 80% of the free 40 holds less
    halved: sizing.Plan = sizing.plan(shared._replace(share=25), Path(), Path())
    assert (halved.cpus, halved.memory) == (4, 15 * sizing.GIB)
    whole: sizing.Plan = sizing.plan(Run(output=Path()), Path(), Path())
    assert (whole.cpus, whole.memory) == (16, 32 * sizing.GIB)
    wrong: int | str
    for wrong in (101, -1, True, "75"):
        with pytest.raises(ValueError, match="share must be a percent"):
            _ = parse({"run": {"share": wrong}})


def test_a_runs_steps_are_held_to_its_share_in_a_slice(monkeypatch: pytest.MonkeyPatch) -> None:
    """Of the CPUs and memory its plan has, where systemd sets them; else only sized to it."""
    asked: list[list[str]] = []
    refused: list[bool] = []

    def run(command: list[str], **_options: object) -> SimpleNamespace:
        asked.append(command)
        if refused and _SET in command:
            raise OSError
        return SimpleNamespace(returncode=0)

    def which(name: str) -> str:
        return f"/usr/bin/{name}"

    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setattr("shutil.which", which)
    monkeypatch.setattr("subprocess.run", run)
    plan: sizing.Plan = sizing.Plan(parse({"run": {"share": 75}}), 12, 32 * sizing.GIB, {})
    scope: tuple[str, ...] = sizing.scope(Path(), plan)
    assert scope[-1] == _SLICED
    assert asked[-1][-2:] == ["CPUQuota=1200%", f"MemoryHigh={32 * sizing.GIB}"]
    refused.append(True)
    assert _SLICED not in sizing.scope(Path(), plan)


def test_a_check_at_suffocate_counts_every_level() -> None:
    """A level chooses the codes it reports and which are errors: the rest of a check is the same."""
    entries: list[Record] = [
        {"code": "LVA001", "severity": "error"},
        {"code": "LVA002", "severity": "error"},
        {"code": "LVA005", "severity": "error"},
    ]
    counted: list[list[int]] = [pipeline.counted(entries, level) for level in (None, *Level)]
    assert counted == [[3, 0], [0, 2], [1, 2], [2, 1], [3, 0]]
    made: list[Record] = [
        {"kinds": ["call"], "unsafe": False},
        {"kinds": ["call"], "unsafe": False},
        {"kinds": ["constructor"], "unsafe": True, "likely": True},
        {"kinds": ["copy", "returned"], "unsafe": True, "likely": False},
    ]
    assert pipeline.sets(made) == {
        "call": {"certain": 2},
        "constructor": {"likely": 1},
        "copy+returned": {"guess": 1},
    }


def test_a_traced_run_finds_constricter_alone(tmp_path: Path) -> None:
    """Its path has a directory with the package linked, not this checkout's root and its `tests`."""
    first: Path = corpus_suite.tracer_path(tmp_path)
    assert [each.name for each in first.iterdir()] == ["constricter"]
    assert (first / "constricter" / "trace.py").is_file()
    assert corpus_suite.tracer_path(tmp_path) == first


def test_a_step_is_given_what_it_took_in_the_last_run(tmp_path: Path) -> None:
    """Its CPUs and its memory, a margin over; unmeasured, by what it is; the timed ones, every CPU."""
    known: catalog.Catalog = catalog.load()
    celery: catalog.Entry = known.entries["celery"]
    assert celery.suite is not None
    assert not celery.heavy
    assert (celery.suite.most, celery.suite.worker_memory) == (len(celery.suite.parts), 4.6)
    tree: Tree = Tree("celery", "1", tmp_path, tmp_path, suite=celery.suite)
    Store(tmp_path / "earlier").write("celery", "rc+dev", pipeline.TESTS, {"used": USED | {"workers": 2}})
    Store(tmp_path / "earlier").write("celery", "rc+dev", pipeline.CHECK, {})
    before: dict[tuple[str, str], sizing.Before] = sizing.before(tmp_path, tmp_path / "this")
    assert before == {("celery", pipeline.TESTS): sizing.Before(2.5, 10.0, int(9.5 * sizing.GIB), 2)}
    assert not sizing.before(tmp_path, tmp_path / "earlier")
    plan: sizing.Plan = sizing.Plan(parse({"run": {"jobs": 2}}), 8, 16 * sizing.GIB, before)
    # A suite's tests: a worker each for as many as half the run's memory holds, each worker's memory
    # as in the last run, on the CPUs they kept busy then, a margin over; fewer CPUs, fewer workers.
    roomy: sizing.Plan = plan._replace(memory=64 * sizing.GIB)
    measured: sizing.Wanted = roomy.wanted(tree, pipeline.TESTS)
    assert measured == sizing.Wanted(
        4,
        int(9.5 * sizing.GIB * 1.25 * 6 / 2),
        10.0,
        measured=True,
        least=4,
        seconds=10.0,
        workers=6,
    )
    assert (measured.started(4), measured.started(2), sizing.Wanted(3, 0).started(3)) == (6, 3, 3)
    # As its tests', unmeasured, a CPU a worker; and its tests wait for it: their seconds are behind it.
    assert roomy.wanted(tree, pipeline.TRACED) == measured._replace(
        cpus=6,
        measured=False,
        seconds=0.0,
        workers=0,
    )
    # A record that doesn't say how many workers ran: each its `worker-memory`.
    legacy: sizing.Plan = roomy._replace(
        before={("celery", pipeline.TESTS): before["celery", pipeline.TESTS]._replace(workers=0)},
    )
    assert legacy.wanted(tree, pipeline.TESTS) == sizing.Wanted(
        6,
        int(6 * 4.6 * sizing.GIB),
        10.0,
        least=4,
        seconds=10.0,
    )
    assert plan.wanted(tree, pipeline.TYPES) == sizing.Wanted(2, 16 * sizing.GIB // 3)
    assert plan.wanted(tree, pipeline.CHECK) == sizing.Wanted(2, 2 * (sizing.GIB + sizing.GIB // 4), 10.0)
    assert plan.wanted(tree._replace(suite=None), pipeline.CHECK).lasting == 0
    assert plan.wanted(tree, pipeline.TIMING).cpus == plan.cpus
    # The check and the census share one check: the one that only read it is held as the one that ran it.
    read: sizing.Before = sizing.Before(0.7, 0.4, sizing.GIB // 50)
    ran: sizing.Before = sizing.Before(2.2, 74.0, 4 * sizing.GIB)
    shared: sizing.Plan = plan._replace(
        before={("celery", pipeline.CHECK): read, ("celery", pipeline.CENSUS): ran},
    )
    assert (shared.wanted(tree, pipeline.CHECK), shared.wanted(tree, pipeline.CENSUS)) == (
        sizing.Wanted(3, 5 * sizing.GIB, 0.4, measured=True, seconds=74.0),
        sizing.Wanted(3, 5 * sizing.GIB, 74.0, measured=True, seconds=74.0),
    )
    alone: sizing.Plan = plan._replace(before={("celery", pipeline.CENSUS): ran})
    assert alone.wanted(tree, pipeline.CHECK) == sizing.Wanted(3, 5 * sizing.GIB, measured=True, seconds=74.0)
    unmeasured: sizing.Plan = plan._replace(before={})
    assert unmeasured.wanted(tree, pipeline.TESTS) == sizing.Wanted(1, int(4.6 * sizing.GIB), least=1)
    assert unmeasured.wanted(tree, pipeline.TESTS, heavy=True).memory == plan.memory
    assert plan.workers(celery.suite._replace(most=32, worker_memory=1.0)) == plan.cpus
    assert (
        plan.workers(celery.suite._replace(most=32, worker_memory=2.0)) == plan.cpus // 2
    )  # half the memory
    sized: sizing.Plan = sizing.plan(
        parse({"run": {"cpus": 3, "memory": 2, "output": "."}}),
        tmp_path,
        tmp_path,
    )
    assert (sized.cpus, sized.memory, sized.before) == (3, 2 * sizing.GIB, before)


def test_a_step_is_sized_by_a_run_of_its_own_label_first(tmp_path: Path) -> None:
    """A later run under another label sizes only the steps this label's runs didn't measure."""
    probe: Store = Store(tmp_path / "probe-10-13-2026-0900")
    probe.write("celery", "rc+dev", pipeline.TESTS, {"used": USED | {"memory": 0.1}})
    probe.write("celery", "rc+dev", pipeline.TYPES, {"used": USED})
    Store(tmp_path / "full-10-12-2026-0800").write("celery", "rc+dev", pipeline.TESTS, {"used": USED})
    os.utime(tmp_path / "full-10-12-2026-0800" / "records", (0, 0))
    labelled: dict[tuple[str, str], sizing.Before] = sizing.before(
        tmp_path,
        tmp_path / "full-10-13-2026-1000",
    )
    assert labelled["celery", pipeline.TESTS].memory == int(9.5 * sizing.GIB)
    assert ("celery", pipeline.TYPES) in labelled


def test_each_execution_has_a_folder_named_by_its_label_and_time() -> None:
    """`<output>/<label>-<month>-<day>-<year>-<hour><minute>`."""
    run: Run = parse({"run": {"label": "0.3.6-rc.1", "output": "data"}})
    started: datetime = datetime(2026, 10, 9, 10, 52, tzinfo=UTC)
    assert run.folder(started) == Path("data/0.3.6-rc.1-10-09-2026-1052")


def test_a_fix_is_certain_likely_or_a_guess() -> None:
    """By `--format=json`'s `unsafe` and `likely`."""
    assert pipeline.tier({"unsafe": False}) == CERTAIN
    assert pipeline.tier({"unsafe": True, "likely": True}) == LIKELY
    assert pipeline.tier({"unsafe": True, "likely": False}) == pipeline.GUESS


def test_the_tests_as_released_are_an_earlier_runs_record_where_one_may_be_taken(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Written as the step's, not run, and said in the run's output; else the step runs."""
    run: Run = parse({"steps": {"tests": True}})
    store: Store = Store(tmp_path)
    plan: sizing.Plan = sizing.Plan(run, 8, 16 * sizing.GIB, {})
    running: runner.Running = runner.Running(
        run,
        store,
        plan,
        sizing.Slots(8, 16),
        None,
        {},
        threading.Semaphore(),
    )
    job: pipeline.Job = pipeline.Job(run, store, Tree("celery", "1", tmp_path), DEV)
    entry: catalog.Entry = catalog.load().entry("celery")
    ran: list[str] = []
    found: Record = {"counts": {"passed": 1}, "failed": [], "from": "old", "confirmed": "traced"}

    def step(_self: runner.Running, _entry: catalog.Entry, _job: pipeline.Job, name: str) -> bool:
        ran.append(name)
        return True

    def none(_job: pipeline.Job) -> Record | None:
        return None

    def some(_job: pipeline.Job) -> Record | None:
        return found

    monkeypatch.setattr(runner.Running, "step", step)
    monkeypatch.setattr(suite_steps, "taken", none)
    assert running.steps(entry, job, ["tests-released"]) == []
    monkeypatch.setattr(suite_steps, "taken", some)
    assert running.steps(entry, job, ["tests-fix-unsafe"]) == []
    assert ran == ["tests-released", "tests-fix-unsafe"]
    assert running.steps(entry, job, ["tests-released"]) == []
    assert store.read("celery", job.recorded, "tests-released") == found
    assert ran == ["tests-released", "tests-fix-unsafe"]


def test_a_runs_facts_name_each_checkers_version_and_the_parsers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The first line of `--version`, with the checker's name; `(not found)` where it isn't installed."""
    run: Run = parse({"steps": {"infer-with": ["ty", "pyrefly"]}})
    # A batch file on Windows: `CreateProcess` runs no shebang script.
    windows: bool = os.name == _WINDOWS
    fake: Path = tmp_path / (f"{_PYREFLY}.cmd" if windows else _PYREFLY)
    script: str = "@echo pyrefly 0.40.0\n" if windows else "#!/bin/sh\necho 'pyrefly 0.40.0'\n"
    _ = fake.write_text(script, encoding="utf-8")
    fake.chmod(0o755)

    def which(name: str, **_kwargs: object) -> str | None:
        return str(fake) if name == _PYREFLY else None

    monkeypatch.setattr(shutil, "which", which)
    assert runner.checkers(run) == ["ty (not found)", "pyrefly 0.40.0"]
    facts: Record = runner.run_facts(run, datetime(2026, 10, 16, tzinfo=UTC))
    assert facts["checkers"] == ["ty (not found)", "pyrefly 0.40.0"]
    assert facts["parser"] == corpus_suite.parser()
