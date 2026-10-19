# SPDX-License-Identifier: MIT
"""The corpus runner's records, and the outputs made from them: reports, tables and docs/RUNS.md."""

import csv
import json
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

import pytest

from tests.corpus import pipeline, render, report_tables
from tests.corpus.pipeline import Measured, Record, Store
from tests.corpus.recorded import SHARE, USED
from tests.corpus.run_config import CERTAIN, JSON, LIKELY, MARKDOWN, Run, parse
from tests.corpus.trees import Tree

_Nested: TypeAlias = dict[str, dict[str, dict[str, Record]]]  # corpus, version, step
_Rows: TypeAlias = list[list[str]]  # a CSV table, read back
_Named: TypeAlias = list[tuple[str, str]]  # a fix step's fixes, by name and annotation
_WARNING: Final = "a warning\n"
_CRLF: Final = b"\r\n"  # a line's end that git keeps as LF
_PUBLISHED: Final = "\n## constricter rc\n"  # in RUNS.md: `dev` under the run's label
_SECTION: Final = "## constricter rc+dev"
# The Markdown's cells for what was fixed, likely and guessed on top, broken, and left by each second pass.
_FIXES: Final = "| 2 (33.3%) | 1 (16.7%) | 2 (33.3%) |      0 |    0 |            1 |"
_COUNTED: Final[Record] = {"untyped": 6, "guessed": 2, "unfixed": 2, "unparsed": 0, "shapes": {"call": 2}}
_INFERRED: Final = "| standard library | infer-ty |     5 |       2 |      1 |     2 |      0 |    0 |"
_TESTED_ROW: Final = (
    "| fix-unsafe                  | False            | 1 failed, 8 passed        |"
    "            1 |    0 |     0 |"
)
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
    "from": "earlier-run",
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


def _recorded(root: Path) -> tuple[Store, Tree]:
    """Write a record of every step of one corpus with one version, `rc+dev`, under `root`.

    Returns:
      The store, and the corpus's tree.

    """
    tree: Tree = Tree("standard library", "3.14", root)
    store: Store = Store(root)
    assert store.read(tree.name, "rc+dev", pipeline.CHECK) is None
    store.write(tree.name, "rc+dev", pipeline.CHECK, _CHECKED | {"used": USED})
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
    records: report_tables.Records = render.gathered(run, store, [tree])
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
        ["standard library", "rc+dev", "released (from earlier-run)", "", "9 passed, 1 skipped", "", "", ""],
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
    store.write(tree.name, "rc+dev", pipeline.TESTS, stopped | {"used": USED | {"alone": True}})
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


def test_what_the_records_hold_beside_the_tables_is_tabled_where_it_differs(tmp_path: Path) -> None:
    """Likely fixes unsafe leaves out, a fix that typed nothing, and the traced tests beside the released."""
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    listed: dict[str, _Named] = {
        "fix-likely": [("x", "int"), ("y", "str"), ("z", "int")],
        "fix-unsafe": [("x", "int"), ("y", "bytes")],
    }
    step: str
    named: _Named
    for step, named in listed.items():
        fixes: list[Record] = [
            {"path": "a.py", "line": 1, "name": name, "annotation": annotation} for name, annotation in named
        ]
        _ = store.path(tree.name, "rc+dev", step, ".fixes.jsonl").write_text(
            "".join(f"{json.dumps(fix)}\n" for fix in fixes),
            encoding="utf-8",
        )
    store.write(tree.name, "rc+dev", "fix-certain", _fixed(2, {"certain": 2}) | {"typed": [5, 10]})
    traced: Record = {"counts": {"passed": 8, "failed": 1}, "failed": [_FAILED]}
    store.write(tree.name, "rc+dev", pipeline.TESTS, _TESTED | {"samples": {pipeline.TRACED: traced}})
    records: report_tables.Records = render.gathered(parse({"run": {"label": "rc"}}), store, [tree])
    assert report_tables.TABLES["unshared"](records)[1:] == [["standard library", "rc+dev", 3, 1, 1]]
    assert report_tables.TABLES["uncounted"](records)[1:] == [
        ["standard library", "rc+dev", "certain", 4, 2, 5, 1],
    ]
    assert report_tables.TABLES["resampled"](records)[1:] == [
        ["standard library", "rc+dev", "9 passed, 1 skipped", "1 failed, 8 passed", False],
    ]
    assert report_tables.TABLES["unshared"](
        report_tables.Records(records.run, records.trees, records.versions, records.found),
    ) == [
        ["corpus", "constricter", "likely", "absent from unsafe", "annotated otherwise"],
    ]


def test_a_hinted_step_whose_rounds_came_from_the_store_is_noted(tmp_path: Path) -> None:
    """Its seconds measure less of the checker, and the run's notes say so."""
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    kept: Record = _fixed(5, {"certain": 2, "likely": 1, "guess": 2}) | {"stored": {"ty": [1, 2]}}
    store.write(tree.name, "rc+dev", "infer-ty", kept)
    run: Run = parse({"run": {"label": "rc"}, "steps": {"infer-with": ["ty"]}})
    assert render.notes(render.gathered(run, store, [tree]))[1:] == [
        (
            "standard library, rc+dev, infer-ty: ty's hints for 1 of 2 rounds came from the store,"
            " so its seconds measure less of the checker"
        ),
    ]


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
