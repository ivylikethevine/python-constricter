# SPDX-License-Identifier: MIT
"""A run's outputs, each made from its records alone (`pipeline.Store`), so no two can disagree.

- `json`: `report.json`, every record under its corpus, version and step, with the run's own facts;
- `markdown`: `report.md`, the tables docs/RUNS.md has a section of for each version;
- `csv`: `tables/offences.csv`, `levels.csv`, `fixes.csv`, `census.csv`, `traced.csv`, `tests.csv`,
  `types.csv`, `type-errors.csv` and `coverage.csv`, a row a measurement.
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
from tests.corpus.corpus_table import Corpus, Likely, Measured, Typed
from tests.corpus.pipeline import (
    CENSUS,
    CHECK,
    COVERAGE,
    FIX,
    GUESS,
    INFER,
    TESTS,
    TRACED,
    TYPES,
    Record,
    Store,
    fixing,
    steps,
)
from tests.corpus.run_config import CERTAIN, CSV, JSON, LIKELY, MARKDOWN, UNSAFE, Run
from tests.corpus.trees import Tree

_Row: TypeAlias = "list[object]"  # a table's cells, as `csv` writes them
_Rows: TypeAlias = "list[_Row]"
_NO_RECORD: Final[Record] = {}
_VERDICTS: Final = ("told", "held", "differed")  # a traced record's counts, each by tier
_COUNTS: Final = ("untyped", "guessed", "unfixed", "unparsed")  # a census record's counts
_INFERRED: Final = "`--fix --unsafe-fixes --infer-with` each type checker, on a copy:"
_COUNTED: Final = "The untyped bindings, by the fix they have:"
_TESTED: Final = "Each package's own tests, as released and after each fix:"
_TOLD: Final = "The fixes a traced test could tell of, those whose every value fit, and those one didn't:"
_CHECKED: Final = (
    "Each package's own type checks: its errors as released, and those new and gone after each fix:"
)


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


def _every(run: Run) -> list[str]:
    """List every step a run may have a record of.

    Returns:
      Their names, each once.

    """
    return list(dict.fromkeys([*steps(run), *fixing(run), TRACED, TESTS, TYPES]))


def gathered(run: Run, store: Store, trees: Sequence[Tree]) -> Records:
    """Read every record the run's steps wrote on `trees`.

    Returns:
      Them.

    """
    versions: list[str] = [run.recorded(version) for version in run.versions]
    found: dict[tuple[str, str, str], Record] = {}
    key: tuple[str, str, str]
    record: Record | None
    for key in itertools.product([tree.name for tree in trees], versions, _every(run)):
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
        parts += [f"## constricter {version}", "", corpus_table.tables(rows), "", *_more(records, version)]
    return "\n".join(parts)


def _summary(outcome: Record) -> str:
    counts: dict[str, int] = cast("dict[str, int]", outcome.get("counts", {}))
    return ", ".join(f"{count:,} {kind}" for kind, count in counts.items()) or str(outcome.get("error", ""))


def _types(records: Records) -> _Rows:
    rows: _Rows = [["corpus", "constricter", "run", "errors", "new", "gone", "change"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TYPES):
                rows.append([tree.name, version, "released", record["released"], "", "", ""])
                step: str
                ran: Record
                for step, ran in cast("dict[str, Record]", record["fixed"]).items():
                    errors: list[Record] | None = cast("list[Record] | None", ran.get("new"))
                    new: int | str = "" if errors is None else len(errors)
                    counts: _Row = [ran.get("errors", ""), new, ran.get("gone", "")]
                    rows.append([tree.name, version, step, *counts, ran.get("change", ran.get("error", ""))])
    return rows


def _type_errors(records: Records) -> _Rows:
    head: _Row = ["corpus", "constricter", "run", "mechanisms", "path", "line", "message"]
    rows: _Rows = [[*head, "fix", "annotation", "fix line"]]
    key: tuple[str, str, str]
    record: Record
    for key, record in records.found.items():
        step: str
        ran: Record
        for step, ran in cast("dict[str, Record]", record["fixed"]).items() if key[2] == TYPES else ():
            new: Record
            for new in cast("list[Record]", ran.get("new", [])):
                fix: Record = cast("Record", new["fix"] or {})
                where: _Row = [new["kind"], new["path"], new["line"], new["message"]]
                about: _Row = [fix.get(each, "") for each in ("name", "annotation", "line")]
                rows.append([*key[:2], step, *where, *about])
    return rows


def _traced(records: Records) -> _Rows:
    rows: _Rows = [["corpus", "constricter", "tier", *_VERDICTS, "resting on the trace", "tests"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TRACED):
                summary: str = str(record.get("summary", record.get("error", "")))
                rows.append([tree.name, version, "", "", "", "", record.get("resting", ""), summary])
                tier: str
                for tier in (CERTAIN, LIKELY, GUESS) if _VERDICTS[0] in record else ():
                    counts: _Row = [cast("dict[str, int]", record[key]).get(tier, 0) for key in _VERDICTS]
                    rows.append([tree.name, version, tier, *counts, "", ""])
    return rows


def _tests(records: Records) -> _Rows:
    rows: _Rows = [["corpus", "constricter", "run", "same as released", "summary", "new failures"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TESTS):
                released: str = _summary(cast("Record", record["released"]))
                rows.append([tree.name, version, "released", "", released, ""])
                step: str
                ran: Record
                for step, ran in cast("dict[str, Record]", record["fixed"]).items():
                    new: list[str] = cast("list[str]", ran.get("new", []))
                    rows.append([tree.name, version, step, ran.get("same", False), _summary(ran), len(new)])
    return rows


def _more(records: Records, version: str) -> list[str]:
    """Write what the tables of `corpus_table` haven't: the type checkers' fixes, and the census.

    Returns:
      The Markdown's lines, for one version.

    """
    inferred: _Rows = [["Corpus", "Checker", "Fixed", "Broken", "Left", "Typed after"]]
    counted: _Rows = [["Corpus", "Untyped", "A guess only", "No fix", "In files that don't parse"]]
    tree: Tree
    record: Record
    for tree in records.trees:
        step: str
        for step in fixing(records.run):
            if step.startswith(INFER) and (record := records.of(tree, version, step)):
                typed: Typed | None = _typed(record)
                share: str = (
                    f"{typed.typed / typed.total:.1%}" if typed and typed.total else corpus_table.NONE
                )
                counts: list[str] = [f"{record.get(key) or 0:,}" for key in ("fixed", "broken", "left")]
                inferred.append([tree.name, step.removeprefix(INFER), *counts, share])
        if record := records.of(tree, version, CENSUS):
            counted.append([tree.name, *(f"{record[key]:,}" for key in _COUNTS)])
    lines: list[str] = []
    if len(inferred) > 1:
        lines += [_INFERRED, "", *corpus_table.table(inferred, right=2), ""]
    if len(counted) > 1:
        lines += [_COUNTED, "", *corpus_table.table(counted, right=1), ""]
    tested: _Rows = [row[:1] + row[2:] for row in _tests(records) if row[1] in {version, "constricter"}]
    if len(tested) > 1:
        lines += [_TESTED, "", *corpus_table.table(tested, right=4), ""]
    told: _Rows = [row[:1] + row[2:] for row in _traced(records) if row[1] in {version, "constricter"}]
    if len(told) > 1:
        lines += [_TOLD, "", *corpus_table.table(told, right=2), ""]
    checked: _Rows = [row[:1] + row[2:] for row in _types(records) if row[1] in {version, "constricter"}]
    if len(checked) > 1:
        lines += [_CHECKED, "", *corpus_table.table(checked, right=2), ""]
    return lines


def publish(records: Records, root: Path) -> None:
    """Record the run's per-version tables where its run file says: a section a version of RUNS.md.

    `corpus_table.record` refuses to write over a section that's there, unless the run file says to
    replace it.
    """
    target: Path | None
    if (target := records.run.publish.runs_md) is not None:
        rows: list[Measured] = [
            measured(records, tree, version) for version in records.versions for tree in records.trees
        ]
        corpus_table.record(rows, root / target, replace=records.run.publish.replace)


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
            for mode in fixing(records.run):
                record: Record
                if record := records.of(tree, version, mode):
                    tiers: dict[str, int] = cast("dict[str, int]", record.get("tiers", {}))
                    typed: Typed | None = _typed(record)
                    rows.append(
                        [
                            *(tree.name, version, mode.removeprefix(FIX), record.get("fixed", "")),
                            *(tiers.get(each, "") for each in (CERTAIN, LIKELY, GUESS)),
                            *(record.get("broken", ""), record.get("left", "")),
                            *(typed or ("", "")),
                            record.get("seconds", ""),
                        ],
                    )
    return rows


def _census(records: Records) -> _Rows:
    rows: _Rows = [["corpus", "constricter", *_COUNTS, "shape", "bindings"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, CENSUS):
                rows.append([tree.name, version, *(record[key] for key in _COUNTS), "", ""])
                blank: _Row = [tree.name, version, *("" for _ in _COUNTS)]
                shapes: dict[str, int] = cast("dict[str, int]", record["shapes"])
                rows.extend([*blank, shape, count] for shape, count in shapes.items())
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
    "census": _census,
    "traced": _traced,
    "tests": _tests,
    "types": _types,
    "type-errors": _type_errors,
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
