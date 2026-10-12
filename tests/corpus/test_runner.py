# SPDX-License-Identifier: MIT
"""The corpus runner's own parts that need no corpus: its run file, its catalog, its records and outputs."""

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

import pytest

from tests.corpus import catalog, pipeline, render
from tests.corpus.pipeline import Record, Store
from tests.corpus.run_config import CERTAIN, CSV, DEV, JSON, LIKELY, MARKDOWN, Run, Steps, parse
from tests.corpus.trees import Tree

_Nested: TypeAlias = "dict[str, dict[str, dict[str, Record]]]"  # corpus, version, step
_Rows: TypeAlias = "list[list[str]]"  # a CSV table, read back
_WARNING: Final = "a warning\n"
_PUBLISHED: Final = "\n## constricter rc\n"  # in RUNS.md: `dev` under the run's label
_SECTION: Final = "## constricter rc+dev"
# The Markdown's cells for what was fixed, likely and guessed on top, broken, and left by each second pass.
_FIXES: Final = "| 2 (33.3%) | 1 (16.7%) | 2 (33.3%) |      0 |    0 |            1 |"
_COUNTED: Final[Record] = {"untyped": 6, "guessed": 2, "unfixed": 2, "unparsed": 0, "shapes": {"call": 2}}
_INFERRED: Final = "| standard library | ty      |     5 |      0 |    0 |       90.0% |"
_TESTED_ROW: Final = "| fix-unsafe | False            | 1 failed, 8 passed  |            1 |"
_TYPED_ROW: Final = "| standard library | fix-unsafe |      8 |   1 |    0 |      1 file changed |"
_COUNTED_ROW: Final = "| standard library |       6 |            2 |      2 |                         0 |"
_FAILED: Final = "tests/test_a.py::test_a"
_TESTED: Final[Record] = {
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
    "summary": "9 passed",
    "resting": 3,
    "told": {"certain": 2, "guess": 1},
    "held": {"certain": 2},
    "differed": {"guess": 1},
}
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
    with pytest.raises(ValueError, match=r"\[steps\] profile"):
        _ = parse({"steps": {"profile": True}})
    with pytest.raises(ValueError, match="checker 'mypy'"):
        _ = parse({"steps": {"infer-with": ["mypy"]}})
    with pytest.raises(ValueError, match=r"\[publish\] where"):
        _ = parse({"publish": {"where": "x"}})
    with pytest.raises(ValueError, match="format 'html'"):
        _ = parse({"run": {"formats": ["html"]}})
    with pytest.raises(ValueError, match="fix 'all'"):
        _ = parse({"steps": {"fix": ["all"]}})


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
    with pytest.raises(ValueError, match="'numpy' is no corpus or set"):
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
    store.write(tree.name, "rc+dev", pipeline.CHECK, _CHECKED)
    store.write(tree.name, "rc+dev", "fix-certain", _fixed(2, {"certain": 2}))
    store.write(tree.name, "rc+dev", "fix-likely", _fixed(3, {"certain": 2, "likely": 1}, left=1))
    store.write(tree.name, "rc+dev", "fix-unsafe", _fixed(4, {"certain": 2, "likely": 1, "guess": 1}))
    store.write(tree.name, "rc+dev", pipeline.COVERAGE, {"typed": [4, 10]})
    store.write(tree.name, "rc+dev", "infer-ty", _fixed(5, {"certain": 2, "likely": 1, "guess": 2}))
    store.write(tree.name, "rc+dev", pipeline.CENSUS, _COUNTED)
    store.write(tree.name, "rc+dev", pipeline.TESTS, _TESTED)
    store.write(tree.name, "rc+dev", pipeline.TYPES, _TYPED)
    store.write(tree.name, "rc+dev", pipeline.TRACED, _TRACED)
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
        "offences.csv",
        "levels.csv",
        "fixes.csv",
        "census.csv",
        "traced.csv",
        "tests.csv",
        "types.csv",
        "type-errors.csv",
        "coverage.csv",
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
    for path in written[2:]:
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
        ["standard library", "rc+dev", "released", "", "9 passed, 1 skipped", ""],
        ["standard library", "rc+dev", "fix-unsafe", "False", "1 failed, 8 passed", "1"],
        ["standard library", "rc+dev", "infer-ty", "False", "error: patch failed", "0"],
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
        ["standard library", "rc+dev", "", "", "", "", "3", "9 passed"],
        ["standard library", "rc+dev", "certain", "2", "2", "0", "", ""],
        ["standard library", "rc+dev", "likely", "0", "0", "0", "", ""],
        ["standard library", "rc+dev", "guess", "1", "0", "1", "", ""],
    ]
    assert tables["coverage"][1] == ["standard library", "rc+dev", "4", "10"]
    assert render.write(
        render.gathered(parse({"run": {"label": "rc", "formats": [JSON]}}), store, [tree]),
        tmp_path,
        {},
    ) == [
        tmp_path / "report.json",
    ]
    assert MARKDOWN not in parse({"run": {"formats": [JSON]}}).formats


def test_a_run_publishes_a_section_a_version(tmp_path: Path) -> None:
    """In the file its run file names, and over a section that's there only where it says to replace."""
    store: Store
    tree: Tree
    store, tree = _recorded(tmp_path)
    render.publish(render.gathered(parse({"run": {"label": "rc"}}), store, [tree]), tmp_path)
    assert not (tmp_path / "RUNS.md").exists()
    published: Run = parse({"run": {"label": "rc"}, "publish": {"runs-md": "RUNS.md"}})
    render.publish(render.gathered(published, store, [tree]), tmp_path)
    assert _PUBLISHED in (tmp_path / "RUNS.md").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="already has rc"):
        render.publish(render.gathered(published, store, [tree]), tmp_path)
    again: Run = parse({"run": {"label": "rc"}, "publish": {"runs-md": "RUNS.md", "replace": True}})
    render.publish(render.gathered(again, store, [tree]), tmp_path)
