# SPDX-License-Identifier: MIT
"""A run's outputs, each made from its records alone (`pipeline.Store`), so no two can disagree.

- `json`: `report.json`, every record under its corpus, version and step, with the run's own facts;
- `markdown`: `report.md`, the tables docs/RUNS.md has a section of for each version;
- `csv`: `tables/offences.csv`, `levels.csv`, `fixes.csv` and `coverage.csv`, a row a measurement.
"""

import csv
import itertools
import json
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import Level
from tests.corpus import corpus_table
from tests.corpus.catalog import Tree
from tests.corpus.corpus_table import Corpus, Likely, Measured, Typed
from tests.corpus.pipeline import CHECK, COVERAGE, FIX, GUESS, Record, Store, steps
from tests.corpus.run_config import CERTAIN, CSV, FIXES, JSON, LIKELY, MARKDOWN, UNSAFE, Run

_Row: TypeAlias = "list[object]"  # a table's cells, as `csv` writes them
_Rows: TypeAlias = "list[_Row]"
_NO_RECORD: Final[Record] = {}


class Records(NamedTuple):
    """A run's records, read once: each step's by its corpus, version and name."""

    run: Run
    trees: Sequence[Tree]
    versions: list[str]  # as the run records them, in its order
    found: dict[tuple[str, str, str], Record]

    def of(self, tree: Tree, version: str, step: str) -> Record:
        """Find a step's record.

        Returns:
          It, or an empty one if the step didn't run.

        """
        return self.found.get((tree.name, version, step), _NO_RECORD)


def gathered(run: Run, store: Store, trees: Sequence[Tree]) -> Records:
    """Read every record the run's steps wrote on `trees`.

    Returns:
      Them.

    """
    versions: list[str] = [run.recorded(version) for version in run.versions]
    found: dict[tuple[str, str, str], Record] = {}
    key: tuple[str, str, str]
    record: Record | None
    for key in itertools.product([tree.name for tree in trees], versions, steps(run)):
        if (record := store.read(*key)) is not None:
            found[key] = record
    return Records(run, trees, versions, found)


def _typed(record: Record) -> Typed | None:
    counts: list[int] | None = cast("list[int] | None", record.get("typed"))
    return Typed(counts[0], counts[1]) if counts else None


def _count(record: Record, key: str) -> int | None:
    return cast("int | None", record.get(key))


def measured(records: Records, tree: Tree, version: str) -> Measured:
    """Lay one corpus's records with one version out as a row of `corpus_table`'s tables.

    Returns:
      The row.

    """
    checked: Record = records.of(tree, version, CHECK)
    certain: Record = records.of(tree, version, f"{FIX}{CERTAIN}")
    likely: Record = records.of(tree, version, f"{FIX}{LIKELY}")
    unsafe: Record = records.of(tree, version, f"{FIX}{UNSAFE}")
    fixed: int | None = _count(certain, "fixed")
    every: int | None = _count(unsafe, "fixed")
    levels: dict[str, list[int]] = cast("dict[str, list[int]]", checked.get("levels", {}))
    return Measured(
        Corpus(tree.name, tree.version, tree.root),
        version,
        cast("int", checked.get("files", 0)),
        Counter(cast("dict[str, int]", checked.get("codes", {}))),
        {level: cast("tuple[int, int]", tuple(levels.get(level.name.lower(), (0, 0)))) for level in Level},
        fixed,
        None if fixed is None or every is None else every - fixed,
        _count(unsafe, "broken") or 0,
        _count(unsafe, "left") or 0,
        _typed(certain),
        _typed(unsafe),
        _typed(records.of(tree, version, COVERAGE)) or Typed(0, 0),
        Likely(_count(likely, "fixed"), _count(likely, "left") or 0, _typed(likely)),
    )


def markdown(records: Records) -> str:
    """Write the run's tables as Markdown, a section a version.

    Returns:
      The text.

    """
    parts: list[str] = [f"# Corpus run {records.run.label}", ""]
    version: str
    for version in records.versions:
        rows: list[Measured] = [measured(records, tree, version) for tree in records.trees]
        parts += [f"## constricter {version}", "", corpus_table.tables(rows), ""]
    return "\n".join(parts)


def _offences(records: Records) -> _Rows:
    codes: list[str] = sorted(
        {
            code
            for record in records.found.values()
            for code in cast("dict[str, int]", record.get("codes", {}))
        },
    )
    rows: _Rows = [["corpus", "corpus version", "constricter", "files", *codes, "total"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            counts: dict[str, int] = cast("dict[str, int]", records.of(tree, version, CHECK).get("codes", {}))
            files: int = cast("int", records.of(tree, version, CHECK).get("files", 0))
            rows.append(
                [
                    tree.name,
                    tree.version,
                    version,
                    files,
                    *(counts.get(c, 0) for c in codes),
                    sum(counts.values()),
                ],
            )
    return rows


def _levels(records: Records) -> _Rows:
    rows: _Rows = [["corpus", "constricter", "level", "errors", "warnings"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            levels: dict[str, list[int]] = cast(
                "dict[str, list[int]]",
                records.of(tree, version, CHECK).get("levels", {}),
            )
            rows.extend(
                [tree.name, version, level.name.lower(), *levels[level.name.lower()]]
                for level in Level
                if level.name.lower() in levels
            )
    return rows


def _fixes(records: Records) -> _Rows:
    head: _Row = ["corpus", "constricter", "fix", "fixed", CERTAIN, LIKELY, GUESS, "broken", "left"]
    rows: _Rows = [[*head, "typed", "bindings", "seconds"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            mode: str
            for mode in FIXES:
                record: Record
                if record := records.of(tree, version, f"{FIX}{mode}"):
                    tiers: dict[str, int] = cast("dict[str, int]", record.get("tiers", {}))
                    typed: Typed | None = _typed(record)
                    rows.append(
                        [
                            *(tree.name, version, mode, record.get("fixed", "")),
                            *(tiers.get(each, "") for each in (CERTAIN, LIKELY, GUESS)),
                            *(record.get("broken", ""), record.get("left", "")),
                            *(typed or ("", "")),
                            record.get("seconds", ""),
                        ],
                    )
    return rows


def _coverage(records: Records) -> _Rows:
    rows: _Rows = [["corpus", "constricter", "typed", "bindings"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            typed: Typed | None
            if typed := _typed(records.of(tree, version, COVERAGE)):
                rows.append([tree.name, version, *typed])
    return rows


_Table: TypeAlias = "Callable[[Records], _Rows]"
_TABLES: Final[dict[str, _Table]] = {
    "offences": _offences,
    "levels": _levels,
    "fixes": _fixes,
    "coverage": _coverage,
}


def report(records: Records, facts: Record) -> Record:
    """Gather the run's records under each corpus, version and step, with the run's own `facts`.

    Returns:
      Them, as `report.json` has them.

    """
    nested: dict[str, dict[str, Record]] = {}
    corpus: str
    version: str
    step: str
    record: Record
    for (corpus, version, step), record in records.found.items():
        nested.setdefault(corpus, {}).setdefault(version, {})[step] = record
    return {
        "run": facts,
        "corpora": {tree.name: {"version": tree.version, "root": str(tree.root)} for tree in records.trees},
        "records": nested,
    }


def write(records: Records, folder: Path, facts: Record) -> list[Path]:
    """Write each of the run's formats into its folder.

    Returns:
      The files written.

    """
    written: list[Path] = []
    if JSON in records.run.formats:
        written.append(folder / "report.json")
        _ = written[-1].write_text(json.dumps(report(records, facts), indent=2) + "\n", encoding="utf-8")
    if MARKDOWN in records.run.formats:
        written.append(folder / "report.md")
        _ = written[-1].write_text(markdown(records), encoding="utf-8")
    if CSV in records.run.formats:
        (folder / "tables").mkdir(exist_ok=True)
        name: str
        rows: Callable[[Records], _Rows]
        for name, rows in _TABLES.items():
            written.append(folder / "tables" / f"{name}.csv")
            file: IO[str]
            with written[-1].open("w", encoding="utf-8", newline="") as file:
                csv.writer(file).writerows(rows(records))
    return written
