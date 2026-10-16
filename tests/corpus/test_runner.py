# SPDX-License-Identifier: MIT
"""The corpus runner's own parts that need no corpus: its run file, its catalog, its records and outputs."""

import csv
import json
import os
import threading
import time
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import IO, Final, TypeAlias, cast

import pytest

from constricter import Level
from tests.corpus import __main__ as runner
from tests.corpus import catalog, corpus_sources, corpus_suite, pipeline, render, sizing, suite_steps, trees
from tests.corpus.corpus_sources import Source
from tests.corpus.corpus_suite import Outcome
from tests.corpus.pipeline import Measured, Record, Store
from tests.corpus.run_config import CERTAIN, CSV, DEV, JSON, LIKELY, MARKDOWN, Run, Steps, parse
from tests.corpus.trees import Tree

_Nested: TypeAlias = dict[str, dict[str, dict[str, Record]]]  # corpus, version, step
_Rows: TypeAlias = list[list[str]]  # a CSV table, read back
_WARNING: Final = "a warning\n"
_CRLF: Final = b"\r\n"  # a line's end that git keeps as LF
SHARE: Final = 75  # percent of the machine
_GROUPS: Final = ("fast-small", "fast-large", "slow-small", "slow-large")  # by size and time
_SLICED: Final = "--slice=constricter-corpus.slice"  # `systemd-run`'s, for a run with a share
_SET: Final = "set-property"  # `systemctl`'s, setting the slice's limits
_PUBLISHED: Final = "\n## constricter rc\n"  # in RUNS.md: `dev` under the run's label
_BASE: Final = "base"  # a version that names another Python
_SECTION: Final = "## constricter rc+dev"
# The Markdown's cells for what was fixed, likely and guessed on top, broken, and left by each second pass.
_FIXES: Final = "| 2 (33.3%) | 1 (16.7%) | 2 (33.3%) |      0 |    0 |            1 |"
_COUNTED: Final[Record] = {"untyped": 6, "guessed": 2, "unfixed": 2, "unparsed": 0, "shapes": {"call": 2}}
_INFERRED: Final = "| standard library | infer-ty |     5 |       2 |      1 |     2 |      0 |    0 |"
_TESTED_ROW: Final = (
    "| fix-unsafe  | False            | 1 failed, 8 passed        |            1 |    0 |     0 |"
)
_USED: Final[Record] = {
    "seconds": 10.0,
    "cpu": 25.0,
    "memory": 9.5,
    "given": {"cpus": 2, "memory": 5.0},
    "alone": False,
}
_SUPER: Final = "## Super corpora\n"
_SET_ROW: Final = "| unsafe  | constructor |     2 |         |      2 |       |"
_PROSE: Final = 100  # the width Prettier fills prose to
_OLD: Final = "\nold\n"  # a section a run's replaces
_MACHINE: Final = "constricter 0.3.6 (`abc`), Python 3.14.7, on 16CPU/60GB (Linux): `--jobs=0`"
_TOOK: Final = "The run took 25 minutes."
_STEP_ROW: Final = "| standard library | check |    10.0 |        25.0 |  2.5 |     9.5 |"
_DIFFERS: Final = "- standard library, rc+dev, tests: the tests differ after fix-unsafe: 1 new"
_TYPED_ROW: Final = "| standard library | fix-unsafe |      8 |   1 |    0 |      1 file changed |"
_COUNTED_ROW: Final = "| standard library |       6 |       2 |       2 |        0 |"
_FAILED: Final = "tests/test_a.py::test_a"
_TESTED: Final[Record] = {
    "seconds": 8.0,
    "released": {"counts": {"passed": 9, "skipped": 1}, "failed": []},
    "fixed": {
        "fix-unsafe": {
            "counts": {"passed": 8, "failed": 1},
            "failed": [_FAILED],
            "same": False,
            "new": [_FAILED],
        },
        "infer-ty": {"error": "error: patch failed"},
        "fix-certain": {
            "counts": {"passed": 9, "skipped": 1},
            "same": True,
            "new": [],
            "implied": "fix-unsafe",
        },
    },
}
_NEW: Final[Record] = {
    "path": "a.py",
    "line": 3,
    "message": "no",
    "kind": "copy (guess)",
    "fix": {"name": "x", "annotation": "int", "line": 2},
}
_TYPED: Final[Record] = {
    "released": 7,
    "fixed": {
        "fix-unsafe": {
            "change": "1 file changed",
            "errors": 8,
            "gone": 0,
            "new": [_NEW],
            "kinds": {"copy (guess)": 1},
        },
        "infer-ty": {"error": "error: patch failed"},
    },
}
_TRACED: Final[Record] = {
    "seconds": 40.0,
    "summary": "9 passed",
    "resting": 3,
    "told": {"certain": 2, "guess": 1},
    "held": {"certain": 2},
    "differed": {"guess": 1},
}
_TIMED: Final[Record] = {
    "jobs": 0,
    "one": [2.0, 4.0],
    "every": [1.0, 1.0],
    "median one": 3.0,
    "median every": 1.0,
}
_COUNTED_TIMING: Final[Record] = {
    "by": "hyperfine",
    "one instructions": [1_400_000_000, 1_600_000_000],
    "median one instructions": 1_500_000_000,
    "every instructions": [2_000_000_000, 2_000_000_000],
    "median every instructions": 2_000_000_000,
}
_SHAPE: Final = "empty list"  # an unfixed binding's value, as the census names it
_BINDING: Final = json.dumps(
    {
        "corpus": "standard library",
        "path": "a.py",
        "line": 1,
        "name": "x",
        "code": "LVA001",
        "fixed": False,
        "unsafe": False,
        "scope": "function",
        "annotated": True,
        "binding": "assign",
        "shape": _SHAPE,
        "dotted": "",
        "origin": "",
        "source": "[]",
    },
)
_CHECKED: Final[Record] = {
    "files": 2,
    "codes": {"LVA001": 5, "LVA004": 1},
    "levels": {"relaxed": [0, 6], "strict": [5, 1], "constrict": [6, 0], "suffocate": [6, 0]},
    "offered": {"certain": 2, "likely": 1, "guess": 1},
    "seconds": 0.1,
}


def _fixed(count: int, tiers: dict[str, int], left: int = 0) -> Record:
    return {
        "fixed": count,
        "tiers": tiers,
        "sets": {"call": {"certain": min(count, 2)}, "constructor": {"likely": count - min(count, 2)}},
        "broken": 0,
        "left": left,
        "typed": [4 + count, 10],
        "seconds": 0.1,
    }


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
    asked: Steps = parse({"steps": {"tests-hinted": False, "every-level": True}}).steps
    assert (asked.tests_hinted, asked.every_level) == (False, True)
    assert (Steps().tests_hinted, Steps().every_level) == (True, False)


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


def test_a_suite_traced_by_its_script_is_one_process(tmp_path: Path) -> None:
    """Its tests' workers aren't kept for it: it's given what any other step is."""
    celery: catalog.Entry = catalog.load().entries["celery"]
    assert celery.suite is not None
    suite: catalog.Suite = celery.suite._replace(script=("runtests.py",))
    plan: sizing.Plan = sizing.Plan(parse({"run": {"jobs": 2}}), 8, 64 * sizing.GIB, {})
    tree: Tree = Tree("celery", "1", tmp_path, tmp_path, suite=suite)
    assert plan.wanted(tree, pipeline.TRACED) == sizing.Wanted(2, 2 * (sizing.GIB + sizing.GIB // 4))


def test_a_step_is_given_what_it_took_in_the_last_run(tmp_path: Path) -> None:
    """Its CPUs and its memory, a margin over; unmeasured, by what it is; the timed ones, every CPU."""
    known: catalog.Catalog = catalog.load()
    celery: catalog.Entry = known.entries["celery"]
    assert celery.suite is not None
    assert not celery.heavy
    assert (celery.suite.most, celery.suite.worker_memory) == (len(celery.suite.parts), 4.6)
    tree: Tree = Tree("celery", "1", tmp_path, tmp_path, suite=celery.suite)
    Store(tmp_path / "earlier").write("celery", "rc+dev", pipeline.TESTS, {"used": _USED | {"workers": 2}})
    Store(tmp_path / "earlier").write("celery", "rc+dev", pipeline.CHECK, {})
    before: dict[tuple[str, str], sizing.Before] = sizing.before(tmp_path, tmp_path / "this")
    assert before == {("celery", pipeline.TESTS): sizing.Before(2.5, 10.0, int(9.5 * sizing.GIB), 2)}
    assert not sizing.before(tmp_path, tmp_path / "earlier")
    plan: sizing.Plan = sizing.Plan(parse({"run": {"jobs": 2}}), 8, 16 * sizing.GIB, before)
    # A suite's tests: a CPU for each worker, as many as half the run's memory holds; each worker's
    # memory as in the last run; starting with half the CPUs.
    roomy: sizing.Plan = plan._replace(memory=64 * sizing.GIB)
    measured: sizing.Wanted = roomy.wanted(tree, pipeline.TESTS)
    assert measured == sizing.Wanted(
        6,
        int(9.5 * sizing.GIB * 1.25 * 6 / 2),
        10.0,
        measured=True,
        least=4,
        seconds=10.0,
    )
    # As its tests', unmeasured; and its tests wait for it: their seconds are behind it.
    assert roomy.wanted(tree, pipeline.TRACED) == measured._replace(measured=False, seconds=0.0)
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
    probe.write("celery", "rc+dev", pipeline.TESTS, {"used": _USED | {"memory": 0.1}})
    probe.write("celery", "rc+dev", pipeline.TYPES, {"used": _USED})
    Store(tmp_path / "full-10-12-2026-0800").write("celery", "rc+dev", pipeline.TESTS, {"used": _USED})
    os.utime(tmp_path / "full-10-12-2026-0800" / "records", (0, 0))
    labelled: dict[tuple[str, str], sizing.Before] = sizing.before(
        tmp_path,
        tmp_path / "full-10-13-2026-1000",
    )
    assert labelled["celery", pipeline.TESTS].memory == int(9.5 * sizing.GIB)
    assert ("celery", pipeline.TYPES) in labelled


def test_hyperfines_runs_are_read_with_their_instructions_where_every_run_counted_them() -> None:
    """Read hyperfine 2's measurements as the seconds and the instructions, and 1's times as the seconds."""
    first: Measured = {"time_wall_clock": {"value": 1.001}, "instructions": {"value": 7.0}}
    second: Measured = {"time_wall_clock": {"value": 2.004}, "instructions": {"value": 9.0}}
    uncounted: Measured = {"time_wall_clock": {"value": 2.004}, "instructions": {"value": None}}
    measured: pipeline.Timed = pipeline.hyperfined({"results": [{"measurements": [first, second]}]})
    assert measured == pipeline.Timed([1.0, 2.0], [7, 9])
    assert pipeline.hyperfined({"results": [{"measurements": [first, uncounted]}]}).instructions == []
    assert pipeline.hyperfined({"results": [{"times": [1.004, 2.0]}]}) == pipeline.Timed([1.0, 2.0], [])


def test_the_timing_table_has_the_instructions_where_hyperfine_counted_them(tmp_path: Path) -> None:
    """Give a record of hyperfine's instructions' medians, in billions, and what timed it."""
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    store.write(tree.name, "rc+dev", pipeline.TIMING, _TIMED | _COUNTED_TIMING)
    run: Run = parse({"run": {"label": "rc"}})
    written: dict[str, Path] = {
        path.name: path for path in render.write(render.gathered(run, store, [tree]), tmp_path, {})
    }
    counted: Path = written["timing.csv"]
    file: IO[str]
    with counted.open(encoding="utf-8", newline="") as file:
        assert list(csv.reader(file))[1][6:] == ["1.5", "2.0", "hyperfine"]


def test_a_fixed_runs_failures_are_the_fixs_only_if_it_has_them_both_times() -> None:
    """And no released run does; a test the catalog names is listed apart, and is no difference."""
    released: Outcome = Outcome({"passed": 9, "skipped": 1}, frozenset())
    failing: Outcome = Outcome({"passed": 8, "failed": 1, "skipped": 1}, frozenset({_FAILED}))
    other: Outcome = Outcome({"passed": 8, "failed": 1, "skipped": 1}, frozenset({"tests/test_b.py::test_b"}))
    assert suite_steps.weighed([released], [released], frozenset()) == {
        "counts": released.counts,
        "failed": [],
        "same": True,
        "new": [],
    }
    twice: Record = suite_steps.weighed([failing, failing], [released, released], frozenset())
    assert (twice["same"], twice["new"], twice["differs"]) == (False, [_FAILED], True)
    once: Record = suite_steps.weighed([failing, other], [released, released], frozenset())
    assert (once["new"], once["differs"], len(cast("list[Record]", once["again"]))) == ([], False, 1)
    named: Record = suite_steps.weighed([failing, failing], [released, released], frozenset({_FAILED}))
    assert (named["new"], named["named"], named["differs"]) == ([], [_FAILED], False)
    theirs: Record = suite_steps.weighed([failing, failing], [released, failing], frozenset())
    assert (theirs["new"], theirs["gone"], theirs["differs"]) == ([], [], False)
    gone: Record = suite_steps.weighed([released, released], [failing, failing], frozenset())
    assert (gone["gone"], gone["differs"]) == ([_FAILED], True)
    skipping: Outcome = Outcome({"passed": 8, "skipped": 2}, frozenset())
    assert suite_steps.weighed([skipping, skipping], [released, released], frozenset())["differs"]
    black: catalog.Suite | None = catalog.load().entries["black"].suite
    assert black is not None
    assert [test.rpartition("::")[2] for test, _ in black.differs] == ["test_piping"]
    flaky: Outcome = Outcome({}, frozenset({"tests/test_black.py::BlackTestCase::test_piping", _FAILED}))
    whole: catalog.Suite = black._replace(differs=(("tests/test_black.py", "its tests come and go"),))
    assert suite_steps.told(black, [flaky]) == suite_steps.told(whole, [flaky]) == flaky.failed - {_FAILED}
    assert corpus_suite.read("ERROR - 2026-10-13 - logged\nFAILED tests/test_a.py::test_a - x\n").failed == {
        _FAILED,
    }


def test_each_execution_has_a_folder_named_by_its_label_and_time() -> None:
    """`<output>/<label>-<month>-<day>-<year>-<hour><minute>`."""
    run: Run = parse({"run": {"label": "0.3.6-rc.1", "output": "data"}})
    started: datetime = datetime(2026, 10, 9, 10, 52, tzinfo=UTC)
    assert run.folder(started) == Path("data/0.3.6-rc.1-10-09-2026-1052")


def test_the_catalog_expands_sets_and_refuses_a_name_it_hasnt() -> None:
    """A set stands for its corpora, each named once, in order."""
    known: catalog.Catalog = catalog.load()
    assert known.names(["pydantic", catalog.ORIGINAL])[:2] == ["pydantic", "standard library"]
    assert len(known.names([catalog.ORIGINAL, "pip"])) == len(known.sets[catalog.ORIGINAL])
    assert all(name in known.entries for name in known.sets[catalog.ORIGINAL])
    here: catalog.Entry = known.entry(str(Path(__file__).parent))
    assert (here.name, here.suite, known.names([here.path])) == ("corpus", None, [here.path])
    assert known.entry("pip") is known.entries["pip"]
    with pytest.raises(ValueError, match="'numpy' is no directory, and no corpus or set"):
        _ = known.names(["numpy"])


def test_the_tiers_hold_each_other_and_the_groups_split_every_corpus() -> None:
    """`original` within `super` within `mega`, every corpus; each corpus in one group of size and time."""
    known: catalog.Catalog = catalog.load()
    original: list[str] = known.names([catalog.ORIGINAL])
    fast: list[str] = known.names([catalog.SUPER])
    every: list[str] = known.names([catalog.MEGA])
    assert set(original) < set(fast) < set(every) == set(known.entries)
    grouped: list[str] = known.names(list(_GROUPS))
    assert sorted(grouped) == sorted(known.entries)
    assert sum(len(known.names([group])) for group in _GROUPS) == len(grouped)
    assert known.names([catalog.SUPER], [catalog.ORIGINAL]) == [name for name in fast if name not in original]


def test_a_set_that_names_itself_is_refused() -> None:
    """Through another set as well as directly."""
    looped: catalog.Catalog = catalog.Catalog({}, {"a": ["b"], "b": ["a"]})
    with pytest.raises(ValueError, match="names itself, by a > b > a"):
        _ = looped.names(["a"])


def test_a_command_leaves_out_a_corpus_a_set_or_a_run_files(tmp_path: Path) -> None:
    """`--minus NAME`, or `--minus RUN.toml`: that run's corpora."""
    assert runner.commanded(Run(), ["--minus", catalog.ORIGINAL]).minus == (catalog.ORIGINAL,)
    less: Path = tmp_path / "less.toml"
    _ = less.write_text('[corpora]\ninclude = ["pip", "twisted"]\n', encoding="utf-8")
    run: Run = runner.commanded(Run(include=(catalog.SUPER,)), ["--minus", str(less)])
    assert run.minus == ("pip", "twisted")
    known: catalog.Catalog = catalog.load()
    left: list[str] = [name for name in known.names([catalog.SUPER]) if name not in run.minus]
    assert known.names(list(run.include), list(run.minus)) == left
    assert len(left) == len(known.names([catalog.SUPER])) - len(run.minus)


def test_the_standard_library_is_cpythons_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Its `Lib`, fetched as an sdist is: not the running Python's, which may lack its tests."""
    entry: catalog.Entry = catalog.load().entry("standard library")
    source: Source = cast("Source", entry.source)
    assert source.url == f"https://www.python.org/ftp/python/{entry.version}/Python-{entry.version}.tar.xz"
    assert source.package == f"Python-{entry.version}/Lib"
    fetched: list[str] = []

    def fetch(name: str, *, sources: dict[str, Source]) -> Path:
        fetched.append(name)
        return tmp_path / sources[name].package

    monkeypatch.setattr(corpus_sources, "fetch", fetch)
    tree: Tree = trees.found(entry)
    assert (tree.root, tree.version, tree.base, fetched) == (
        tmp_path / source.package,
        "3.14.7",
        None,
        [entry.name],
    )
    assert corpus_sources.pinned()["pip"].url.startswith(corpus_sources.FILES)


def test_a_fix_is_certain_likely_or_a_guess() -> None:
    """By `--format=json`'s `unsafe` and `likely`."""
    assert pipeline.tier({"unsafe": False}) == CERTAIN
    assert pipeline.tier({"unsafe": True, "likely": True}) == LIKELY
    assert pipeline.tier({"unsafe": True, "likely": False}) == pipeline.GUESS


def _recorded(root: Path) -> tuple[Store, Tree]:
    """Write a record of every step of one corpus with one version, `rc+dev`, under `root`.

    Returns:
      The store, and the corpus's tree.

    """
    tree: Tree = Tree("standard library", "3.14", root)
    store: Store = Store(root)
    assert store.read(tree.name, "rc+dev", pipeline.CHECK) is None
    store.write(tree.name, "rc+dev", pipeline.CHECK, _CHECKED | {"used": _USED})
    store.write(tree.name, "rc+dev", "fix-certain", _fixed(2, {"certain": 2}))
    store.write(tree.name, "rc+dev", "fix-likely", _fixed(3, {"certain": 2, "likely": 1}, left=1))
    store.write(tree.name, "rc+dev", "fix-unsafe", _fixed(4, {"certain": 2, "likely": 1, "guess": 1}))
    store.write(tree.name, "rc+dev", pipeline.COVERAGE, {"typed": [4, 10]})
    store.write(tree.name, "rc+dev", "infer-ty", _fixed(5, {"certain": 2, "likely": 1, "guess": 2}))
    store.write(tree.name, "rc+dev", pipeline.CENSUS, _COUNTED)
    _ = store.path(tree.name, "rc+dev", pipeline.CENSUS, ".rows.jsonl").write_text(_BINDING, encoding="utf-8")
    store.write(tree.name, "rc+dev", pipeline.TESTS, _TESTED)
    store.write(tree.name, "rc+dev", pipeline.TYPES, _TYPED)
    store.write(tree.name, "rc+dev", pipeline.TRACED, _TRACED)
    store.write(tree.name, "rc+dev", pipeline.TIMING, _TIMED)
    return store, tree


def test_every_output_is_made_from_the_records(tmp_path: Path) -> None:
    """The JSON, the Markdown and each CSV table give the same counts: the records'."""
    run: Run = parse({"run": {"label": "rc"}, "steps": {"infer-with": ["ty"]}})
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    store.log(tree.name, "rc+dev", pipeline.CHECK, _WARNING)
    store.log(tree.name, "rc+dev", pipeline.CHECK, "  ")
    assert (tmp_path / "logs" / "standard-library" / "rc+dev" / "check.log").read_text(
        encoding="utf-8",
    ) == _WARNING
    records: render.Records = render.gathered(run, store, [tree])
    written: list[Path] = render.write(records, tmp_path, {"label": "rc"})
    assert [path.name for path in written] == [
        "report.json",
        "report.md",
        "census.md",
        "offences.csv",
        "levels.csv",
        "fixes.csv",
        "mechanisms.csv",
        "census.csv",
        "traced.csv",
        "tests.csv",
        "types.csv",
        "type-errors.csv",
        "coverage.csv",
        "timing.csv",
        "steps.csv",
    ]
    assert _CRLF not in (tmp_path / "tables" / "offences.csv").read_bytes()
    report: dict[str, _Nested] = cast(
        "dict[str, _Nested]",
        json.loads((tmp_path / "report.json").read_text(encoding="utf-8")),
    )
    assert report["records"] == {
        "standard library": {"rc+dev": {key[2]: record for key, record in records.found.items()}},
    }
    text: str = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert _SECTION in text
    assert _FIXES in text
    tables: dict[str, _Rows] = {}
    path: Path
    assert f"| assign: {_SHAPE} |     1 | 100.0% |" in written[2].read_text(encoding="utf-8")
    for path in written[3:]:
        file: IO[str]
        with path.open(encoding="utf-8", newline="") as file:
            tables[path.stem] = list(csv.reader(file))
    assert tables["offences"] == [
        ["corpus", "corpus version", "constricter", "files", "LVA001", "LVA004", "total"],
        ["standard library", "3.14", "rc+dev", "2", "5", "1", "6"],
    ]
    assert tables["levels"][1:] == [
        ["standard library", "rc+dev", "relaxed", "0", "6"],
        ["standard library", "rc+dev", "strict", "5", "1"],
        ["standard library", "rc+dev", "constrict", "6", "0"],
        ["standard library", "rc+dev", "suffocate", "6", "0"],
    ]
    assert tables["fixes"][3] == [
        "standard library",
        "rc+dev",
        "unsafe",
        "4",
        "2",
        "1",
        "1",
        "0",
        "0",
        "8",
        "10",
        "0.1",
    ]
    assert tables["fixes"][4][2:5] == ["infer-ty", "5", "2"]
    assert tables["census"][1:] == [
        ["standard library", "rc+dev", "6", "2", "2", "0", "", ""],
        ["standard library", "rc+dev", "", "", "", "", "call", "2"],
    ]
    assert _INFERRED in text
    assert _COUNTED_ROW in text
    assert tables["tests"][1:] == [
        ["standard library", "rc+dev", "released", "", "9 passed, 1 skipped", "", "", ""],
        ["standard library", "rc+dev", "fix-certain", "True", "as fix-unsafe's (implied)", "0", "0", "0"],
        ["standard library", "rc+dev", "fix-unsafe", "False", "1 failed, 8 passed", "1", "0", "0"],
        ["standard library", "rc+dev", "infer-ty", "True", "error: patch failed", "0", "0", "0"],
    ]
    assert _TESTED_ROW in text
    assert tables["types"][1:] == [
        ["standard library", "rc+dev", "released", "7", "", "", ""],
        ["standard library", "rc+dev", "fix-unsafe", "8", "1", "0", "1 file changed"],
        ["standard library", "rc+dev", "infer-ty", "", "", "", "error: patch failed"],
    ]
    assert tables["type-errors"][1] == [
        *("standard library", "rc+dev", "fix-unsafe", "copy (guess)", "a.py", "3", "no"),
        *("x", "int", "2"),
    ]
    assert _TYPED_ROW in text
    assert tables["traced"][1:] == [
        ["standard library", "rc+dev", "", "", "", "", "3", "9 passed", "40.0", "8.0"],
        ["standard library", "rc+dev", "certain", "2", "2", "0", "", "", "", ""],
        ["standard library", "rc+dev", "likely", "0", "0", "0", "", "", "", ""],
        ["standard library", "rc+dev", "guess", "1", "0", "1", "", "", "", ""],
    ]
    assert tables["steps"][1:] == [
        ["standard library", "rc+dev", "check", "10.0", "25.0", "2.5", "9.5", "2", "5.0", "False"],
    ]
    assert render.notes(records) == ["standard library, rc+dev, check: held 9.5 GB beside other steps"]
    stopped: Record = {"released": {}, "fixed": {}, "stopped": True}
    store.write(tree.name, "rc+dev", pipeline.TESTS, stopped | {"used": _USED | {"alone": True}})
    assert render.problems(render.gathered(run, store, [tree]))[0].endswith(
        "stopped as released: they ran too long",
    )
    assert len(render.notes(render.gathered(run, store, [tree]))) == 1
    store.write(tree.name, "rc+dev", pipeline.TESTS, _TESTED)
    assert tables["coverage"][1] == ["standard library", "rc+dev", "4", "10"]
    assert render.write(
        render.gathered(parse({"run": {"label": "rc", "formats": [JSON]}}), store, [tree]),
        tmp_path,
        {},
    ) == [
        tmp_path / "report.json",
    ]
    assert MARKDOWN not in parse({"run": {"formats": [JSON]}}).formats
    assert tables["timing"][1] == ["standard library", "rc+dev", "0", "3.0", "1.0", "2", "", "", "loop"]
    assert render.problems(records) == [
        "standard library, rc+dev, tests: the tests differ after fix-unsafe: 1 new",
        "standard library, rc+dev, tests: infer-ty's patch didn't apply: error: patch failed",
        "standard library, rc+dev, types: infer-ty's patch didn't apply: error: patch failed",
    ]
    store.write(tree.name, "rc+dev", "fix-unsafe", _fixed(4, {}, left=2) | {"broken": 1})
    assert render.problems(render.gathered(run, store, [tree]))[:2] == [
        "standard library, rc+dev, fix-unsafe: 1 file(s) no longer compile",
        "standard library, rc+dev, fix-unsafe: a second pass would still fix 2",
    ]


def test_fixes_are_counted_by_their_whole_set_of_mechanisms(tmp_path: Path) -> None:
    """Each fix's sets, the corpora together, by tier: every one in the CSV, the most in the Markdown."""
    run: Run = parse({"run": {"label": "rc"}})
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    written: list[Path] = render.write(render.gathered(run, store, [tree]), tmp_path, {"label": "rc"})
    file: IO[str]
    with (tmp_path / "tables" / "mechanisms.csv").open(encoding="utf-8") as file:
        rows: _Rows = list(csv.reader(file))
    assert rows[0] == ["fix", "constricter", "mechanisms", "fixed", CERTAIN, LIKELY, "guess"]
    assert rows[5:] == [
        ["unsafe", "rc+dev", "call", "2", "2", "", ""],
        ["unsafe", "rc+dev", "constructor", "2", "", "2", ""],
    ]
    assert _SET_ROW in written[1].read_text(encoding="utf-8")


def test_each_judged_fix_is_listed_with_what_blames_it_and_bears_it_out(tmp_path: Path) -> None:
    """A suite's corpus: its `fix-unsafe` fixes, the type errors traced to each, and the witness's verdict."""
    tree: Tree = Tree("pkg", "1.0", tmp_path / "src" / "pkg", tmp_path)
    store: Store = Store(tmp_path)
    listed: _Rows = [["a.py", "certain"], ["b.py", "guess"]]
    fixes: list[Record] = [
        {
            "path": path,
            "line": 2,
            "name": "x",
            "annotation": "int",
            "tier": tier,
            "kinds": ["copy"],
            "imports": [],
        }
        for path, tier in listed
    ]
    blamed: Record = _NEW | {"path": "src/pkg/b.py"}
    store.write(
        tree.name,
        "rc+dev",
        pipeline.TYPES,
        {"released": 0, "fixed": {"fix-unsafe": {"new": [blamed]}}},
    )
    _ = store.path(tree.name, "rc+dev", "fix-unsafe", ".fixes.jsonl").write_text(
        "".join(f"{json.dumps(fix)}\n" for fix in fixes),
        encoding="utf-8",
    )
    told: Record = {"path": "src/pkg/a.py", "line": 2, "name": "x", "verdict": [3, 0, 0], "seen": ["int"]}
    _ = store.path(tree.name, "rc+dev", pipeline.TRACED, ".verdicts.jsonl").write_text(
        f"{json.dumps(told)}\n",
        encoding="utf-8",
    )
    run: Run = parse({"run": {"label": "rc", "formats": [JSON]}})
    found: list[Record] = render.guesses(render.gathered(run, store, [tree]), store)
    assert [
        (each["path"], each["unsafe"], each["errors"], each["verdict"], each["seen"]) for each in found
    ] == [
        ("src/pkg/a.py", False, 0, [3, 0, 0], ["int"]),
        ("src/pkg/b.py", True, 1, [0, 0, 0], None),
    ]
    assert render.write(render.gathered(run, store, [tree]), tmp_path, {})[1] == tmp_path / "guesses.jsonl"


def test_a_run_publishes_a_section_a_version(tmp_path: Path) -> None:
    """In the file its run file names, and over a section that's there only where it says to replace."""
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    render.publish(render.gathered(parse({"run": {"label": "rc"}}), store, [tree]), tmp_path, {})
    assert not (tmp_path / "RUNS.md").exists()
    published: Run = parse({"run": {"label": "rc"}, "publish": {"runs-md": "RUNS.md"}})
    render.publish(render.gathered(published, store, [tree]), tmp_path, {})
    assert _PUBLISHED in (tmp_path / "RUNS.md").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="already has rc"):
        render.publish(render.gathered(published, store, [tree]), tmp_path, {})
    again: Run = parse({"run": {"label": "rc"}, "publish": {"runs-md": "RUNS.md", "replace": True}})
    render.publish(render.gathered(again, store, [tree]), tmp_path, {})


def test_a_run_publishes_one_section_of_itself(tmp_path: Path) -> None:
    """Before the versions' sections, in place of the one of its heading, with its machine and every table."""
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    runs: Path = tmp_path / "RUNS.md"
    _ = runs.write_text(f"# Corpus runs\n\n{_SUPER}{_OLD}\n## Other\n\nkept\n{_PUBLISHED}", encoding="utf-8")
    whole: Run = parse(
        {"run": {"label": "rc"}, "publish": {"runs-md": "RUNS.md", "section": "Super corpora"}},
    )
    facts: Record = {"constricter": "0.3.6", "commit": "abc", "cpus": 16, "gigabytes": 60, "minutes": 25}
    facts |= {"python": "3.14.7", "system": "Linux"}
    render.publish(render.gathered(whole, store, [tree]), tmp_path, facts)
    render.publish(render.gathered(whole, store, [tree]), tmp_path, facts)
    text: str = runs.read_text(encoding="utf-8")
    assert text.count(_SUPER) == 1
    assert _OLD not in text
    assert text.index(_SUPER) < text.index("## Other\n\nkept\n") < text.index(_PUBLISHED)
    prose: str = " ".join(text.split())
    assert _MACHINE in prose
    assert _TOOK in prose
    assert _FIXES in text
    assert _STEP_ROW in text
    assert _DIFFERS in text
    assert all(len(line) <= _PROSE or line.startswith("|") for line in text.splitlines())
    render.publish(render.gathered(whole, store, [tree]), tmp_path, facts | {"share": SHARE})
    shared: str = " ".join(runs.read_text(encoding="utf-8").split())
    assert _MACHINE.replace("(Linux)", "(Linux), 75% of it") in shared
