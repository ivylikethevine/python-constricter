# SPDX-License-Identifier: MIT
"""The corpus runner's own parts that need no corpus: its run file, its catalog, its records and outputs."""

import csv
import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

import pytest

from tests.corpus import catalog, corpus_suite, pipeline, render, sizing, suite_steps
from tests.corpus.corpus_suite import Outcome
from tests.corpus.pipeline import Record, Store
from tests.corpus.run_config import CERTAIN, CSV, DEV, JSON, LIKELY, MARKDOWN, Run, Steps, parse
from tests.corpus.trees import Tree

_Nested: TypeAlias = dict[str, dict[str, dict[str, Record]]]  # corpus, version, step
_Rows: TypeAlias = list[list[str]]  # a CSV table, read back
_WARNING: Final = "a warning\n"
_PUBLISHED: Final = "\n## constricter rc\n"  # in RUNS.md: `dev` under the run's label
_BASE: Final = "base"  # a version that names another Python
_SECTION: Final = "## constricter rc+dev"
# The Markdown's cells for what was fixed, likely and guessed on top, broken, and left by each second pass.
_FIXES: Final = "| 2 (33.3%) | 1 (16.7%) | 2 (33.3%) |      0 |    0 |            1 |"
_COUNTED: Final[Record] = {"untyped": 6, "guessed": 2, "unfixed": 2, "unparsed": 0, "shapes": {"call": 2}}
_INFERRED: Final = "| standard library | infer-ty |     5 |       2 |      1 |     2 |      0 |    0 |"
_TESTED_ROW: Final = "| fix-unsafe | False            | 1 failed, 8 passed  |            1 |    0 |     0 |"
_USED: Final[Record] = {
    "seconds": 10.0,
    "cpu": 25.0,
    "memory": 9.5,
    "given": {"cpus": 2, "memory": 5.0},
    "alone": False,
}
_SUPER: Final = "## Super corpora\n"
_PROSE: Final = 100  # the width Prettier fills prose to
_OLD: Final = "\nold\n"  # a section a run's replaces
_MACHINE: Final = "constricter 0.3.6 (`abc`), Python 3.14.7, on a CPU (16 CPUs, 60 GB, Linux): `--jobs=0`"
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
    held: int = slots.take(2, 6)
    assert (held, slots.free, slots.held) == (2, 2, 6)
    second: int = slots.take(2, 4)
    assert sizing.Slots(4, 10).take(9) == slots.cpus  # more CPUs than there are: every one
    started: threading.Event = threading.Event()

    def alone() -> None:
        slots.give(slots.take(1, 10), 10)
        started.set()

    waiting: threading.Thread = threading.Thread(target=alone)
    waiting.start()
    assert not started.wait(0.2)
    slots.give(held, 6)
    assert not started.wait(0.2)
    slots.give(second, 4)
    assert started.wait(5)
    waiting.join()
    assert (slots.free, slots.held, slots.running) == (4, 0, 0)
    assert parse({"run": {"suite-seconds": 900, "suite-workers": 4, "cpus": 8, "memory": 12}})[-4:] == (
        900,
        4,
        8,
        12.0,
    )


def test_a_step_is_given_what_it_took_in_the_last_run(tmp_path: Path) -> None:
    """Its CPUs and its memory, a margin over; unmeasured, by what it is; the timed ones, every CPU."""
    known: catalog.Catalog = catalog.load()
    celery: catalog.Entry = known.entries["celery"]
    assert celery.suite is not None
    assert not celery.heavy
    assert len(celery.suite.parts) > 1
    tree: Tree = Tree("celery", "1", tmp_path, tmp_path, suite=celery.suite)
    Store(tmp_path / "earlier").write("celery", "rc+dev", pipeline.TESTS, {"used": _USED})
    Store(tmp_path / "earlier").write("celery", "rc+dev", pipeline.CHECK, {})
    before: dict[tuple[str, str], sizing.Before] = sizing.before(tmp_path, tmp_path / "this")
    assert before == {("celery", pipeline.TESTS): sizing.Before(2.5, 10.0, int(9.5 * sizing.GIB))}
    assert not sizing.before(tmp_path, tmp_path / "earlier")
    plan: sizing.Plan = sizing.Plan(parse({"run": {"jobs": 2}}), 8, 16 * sizing.GIB, before)
    measured: sizing.Wanted = plan.wanted(tree, pipeline.TESTS)
    assert measured == sizing.Wanted(3, int(9.5 * sizing.GIB * 1.25), 10.0)
    assert plan.wanted(tree, pipeline.TRACED)[:2] == (1, measured.memory)  # as its tests', unmeasured
    assert plan.wanted(tree, pipeline.TYPES).memory == 16 * sizing.GIB // 3
    assert plan.wanted(tree, pipeline.CHECK) == sizing.Wanted(2, 2 * (sizing.GIB + sizing.GIB // 4))
    assert plan.wanted(tree, pipeline.TIMING).cpus == plan.cpus
    unmeasured: sizing.Plan = plan._replace(before={})
    assert unmeasured.wanted(tree, pipeline.TESTS) == sizing.Wanted(1, sizing.GIB)
    assert unmeasured.wanted(tree, pipeline.TESTS, heavy=True).memory == plan.memory
    assert plan.workers(celery.suite._replace(most=32)) == plan.cpus // 2
    sized: sizing.Plan = sizing.plan(
        parse({"run": {"cpus": 3, "memory": 2, "output": "."}}),
        tmp_path,
        tmp_path,
    )
    assert (sized.cpus, sized.memory, sized.before) == (3, 2 * sizing.GIB, before)


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
    assert known.names(["pydantic", "seven"])[:2] == ["pydantic", "standard library"]
    assert len(known.names(["seven", "pip"])) == len(known.sets["seven"])
    assert all(name in known.entries for name in known.sets["seven"])
    here: catalog.Entry = known.entry(str(Path(__file__).parent))
    assert (here.name, here.suite, known.names([here.path])) == ("corpus", None, [here.path])
    assert known.entry("pip") is known.entries["pip"]
    with pytest.raises(ValueError, match="'numpy' is no directory, and no corpus or set"):
        _ = known.names(["numpy"])


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
        "census.csv",
        "traced.csv",
        "tests.csv",
        "types.csv",
        "type-errors.csv",
        "coverage.csv",
        "timing.csv",
        "steps.csv",
    ]
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
    assert tables["timing"][1] == ["standard library", "rc+dev", "0", "3.0", "1.0", "2"]
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
    facts |= {"python": "3.14.7", "machine": "a CPU", "system": "Linux"}
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
