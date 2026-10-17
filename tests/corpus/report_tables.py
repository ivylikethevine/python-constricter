# SPDX-License-Identifier: MIT
"""The tables of a run's report, each built from the run's records alone (`Records`), a row a corpus.

Which go in `report.md` and which each version's section of docs/RUNS.md has (`SECTIONS`), and
the CSV files (`TABLES`).
"""

from collections import Counter
from collections.abc import Callable, Sequence
from typing import Final, NamedTuple, TypeAlias, cast

from constricter import Level
from tests.corpus.corpus_table import Typed
from tests.corpus.pipeline import (
    CENSUS,
    CHECK,
    COVERAGE,
    FIX,
    FROM,
    GUESS,
    IMPLIED,
    LOOP,
    TESTS,
    TIMING,
    TRACED,
    TYPES,
    Record,
    fixing,
)
from tests.corpus.run_config import CERTAIN, LIKELY, Run
from tests.corpus.sizing import USED
from tests.corpus.trees import Tree

_Row: TypeAlias = list[object]  # a table's cells, as `csv` writes them
Rows: TypeAlias = list[_Row]


_NO_RECORD: Final[Record] = {}
_SHAPE: Final = "shape"  # the census table's column for an unfixed binding's value


_VERDICTS: Final = ("told", "held", "differed")  # a traced record's counts, each by tier
_COUNTS: Final = ("untyped", "guessed", "unfixed", "unparsed")  # a census record's counts


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


def typed_share(record: Record) -> Typed | None:
    """Read what a record says of the copy's typed bindings.

    Returns:
      Its count, or `None` where it has none.

    """
    counts: list[int] | None = cast("list[int] | None", record.get("typed"))
    return Typed(counts[0], counts[1]) if counts else None


def _summary(outcome: Record) -> str:
    counts: dict[str, int] = cast("dict[str, int]", outcome.get("counts", {}))
    return ", ".join(f"{count:,} {kind}" for kind, count in counts.items()) or str(outcome.get("error", ""))


def _types(records: Records) -> Rows:
    rows: Rows = [["corpus", "constricter", "run", "errors", "new", "gone", "change"]]
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


def _type_errors(records: Records) -> Rows:
    head: _Row = ["corpus", "constricter", "run", "mechanisms", "path", "line", "message"]
    rows: Rows = [[*head, "fix", "annotation", "fix line"]]
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


def _traced(records: Records) -> Rows:
    head: _Row = ["corpus", "constricter", "tier", *_VERDICTS, "resting on the trace", "tests"]
    rows: Rows = [[*head, "seconds", "untraced"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TRACED):
                said: str = str(record.get("summary", record.get("error", "")))
                summary: str = ", ".join(
                    line.strip() for line in said.splitlines()
                )  # pytest-pretty's: a count a line
                took: _Row = [record.get("seconds", ""), records.of(tree, version, TESTS).get("seconds", "")]
                rows.append([tree.name, version, "", "", "", "", record.get("resting", ""), summary, *took])
                tier: str
                for tier in (CERTAIN, LIKELY, GUESS) if _VERDICTS[0] in record else ():
                    counts: _Row = [cast("dict[str, int]", record[key]).get(tier, 0) for key in _VERDICTS]
                    rows.append([tree.name, version, tier, *counts, "", "", "", ""])
    return rows


def _tests(records: Records) -> Rows:
    head: _Row = ["corpus", "constricter", "run", "same as released", "summary", "new failures"]
    rows: Rows = [[*head, "gone", "named"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TESTS):
                released: str = _summary(cast("Record", record["released"]))
                whose: str = f" (from {record[FROM]})" if FROM in record else ""
                rows.append([tree.name, version, f"released{whose}", "", released, "", "", ""])
                step: str
                ran: Record
                for step, ran in cast("dict[str, Record]", record["fixed"]).items():
                    more: _Row = [
                        len(cast("list[str]", ran.get(key, []))) for key in ("new", "gone", "named")
                    ]
                    summary: str = f"as {ran[IMPLIED]}'s (implied)" if IMPLIED in ran else _summary(ran)
                    rows.append([tree.name, version, step, not differs(record, ran), summary, *more])
    return rows


def differs(record: Record, ran: Record) -> bool:
    """Check whether a fixed run of a `tests` record differs from the released tests by the fix's doing.

    Returns:
      What `suite_steps.weighed` found; for a record from before it weighed, whether the run
      isn't the released one's and the released tests don't vary.

    """
    return bool(ran.get("differs", ran.get("same") is False and not record.get("varies")))


def _steps(records: Records) -> Rows:
    head: _Row = ["corpus", "constricter", "step", "seconds", "CPU seconds", "CPUs", "GB held"]
    rows: Rows = [[*head, "CPUs given", "GB given", "alone"]]
    key: tuple[str, str, str]
    record: Record
    for key, record in records.found.items():
        used: Record
        if used := cast("Record", record.get(USED, {})):
            seconds: float = cast("float", used["seconds"])
            busy: float = round(cast("float", used["cpu"]) / seconds, 1) if seconds else 0.0
            given: Record = cast("Record", used["given"])
            took: _Row = [seconds, used["cpu"], busy, used["memory"]]
            rows.append([*key, *took, given["cpus"], given["memory"], used["alone"]])
    return rows


def _counted(records: Records) -> Rows:
    return [row[:-2] for row in _census(records) if row[-2] in {"", _SHAPE}]


def _timing(records: Records) -> Rows:
    rows: Rows = [
        [
            *("corpus", "constricter", "jobs", "one process", "with jobs", "runs"),
            *("G instructions, one process", "with jobs", "timed by"),
        ],
    ]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TIMING):
                medians: _Row = [record["median one"], record["median every"]]
                runs: int = len(cast("list[float]", record["one"]))
                instructions: _Row = [
                    round(cast("int", record[key]) / 1e9, 1) if key in record else ""
                    for key in ("median one instructions", "median every instructions")
                ]
                timed: _Row = [
                    *medians,
                    runs,
                    *instructions,
                    record.get("by", LOOP),  # a record from before `by` was timed in a loop
                ]
                rows.append([tree.name, version, record["jobs"], *timed])
    return rows


def _offences(records: Records) -> Rows:
    codes: list[str] = sorted(
        {
            code
            for record in records.found.values()
            for code in cast("dict[str, int]", record.get("codes", {}))
        },
    )
    rows: Rows = [["corpus", "corpus version", "constricter", "files", *codes, "total"]]
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


def _levels(records: Records) -> Rows:
    rows: Rows = [["corpus", "constricter", "level", "errors", "warnings"]]
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


def _fixes(records: Records) -> Rows:
    head: _Row = ["corpus", "constricter", "fix", "fixed", CERTAIN, LIKELY, GUESS, "broken", "left"]
    rows: Rows = [[*head, "typed", "bindings", "seconds"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            mode: str
            for mode in fixing(records.run):
                record: Record
                if record := records.of(tree, version, mode):
                    tiers: dict[str, int] = cast("dict[str, int]", record.get("tiers", {}))
                    typed: Typed | None = typed_share(record)
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


def _mechanisms(records: Records, most: int | None = None) -> Rows:
    """Count each fix's fixes by their whole set of mechanisms and by tier, the corpora together.

    `most`: only that many sets of each fix, those that made the most.

    Returns:
      The rows, a fix's sets from the one that made the most.

    """
    rows: Rows = [["fix", "constricter", "mechanisms", "fixed", CERTAIN, LIKELY, GUESS]]
    version: str
    for version in records.versions:
        mode: str
        for mode in fixing(records.run):
            sets: dict[str, Counter[str]] = {}
            tiers: dict[str, int]
            tree: Tree
            for tree in records.trees:
                counted: dict[str, dict[str, int]] = cast(
                    "dict[str, dict[str, int]]",
                    records.of(tree, version, mode).get("sets", {}),
                )
                kinds: str
                for kinds, tiers in counted.items():
                    sets.setdefault(kinds, Counter()).update(tiers)
            rows.extend(
                [
                    *(mode.removeprefix(FIX), version, each, sets[each].total()),
                    *(sets[each].get(tier, "") for tier in (CERTAIN, LIKELY, GUESS)),
                ]
                for each in _ranked(sets)[:most]
            )
    return rows


def _ranked(sets: dict[str, Counter[str]]) -> list[str]:
    """Order sets of mechanisms from the one that made the most fixes.

    Returns:
      Their names.

    """
    return sorted(sets, key=lambda each: (-sets[each].total(), each))


def _most_mechanisms(records: Records) -> Rows:
    return _mechanisms(records, _MOST_SETS)


def _census(records: Records) -> Rows:
    rows: Rows = [["corpus", "constricter", *_COUNTS, _SHAPE, "bindings"]]
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


def _coverage(records: Records) -> Rows:
    rows: Rows = [["corpus", "constricter", "typed", "bindings"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            typed: Typed | None
            if typed := typed_share(records.of(tree, version, COVERAGE)):
                rows.append([tree.name, version, *typed])
    return rows


_MOST_SETS: Final = 12  # the sets of mechanisms `report.md` lists for each fix
Table: TypeAlias = Callable[[Records], Rows]
# What `report.md` has under each version's tables: a note, the table, and its columns of words.
_Section: TypeAlias = tuple[str, Table, int]
SECTIONS: Final[tuple[_Section, ...]] = (
    ("Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:", _fixes, 3),
    (
        (
            f"Each fix's {_MOST_SETS} sets of mechanisms that made the most fixes, the corpora together, "
            "by tier (a guess is likely by its whole set: every set is in `tables/mechanisms.csv`):"
        ),
        _most_mechanisms,
        3,
    ),
    ("The untyped bindings: with only a guess, with no fix, and in files that don't parse:", _counted, 2),
    (
        (
            "A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`, and "
            "the billions of instructions they took, where `hyperfine` counted them:"
        ),
        _timing,
        2,
    ),
    (
        (
            "The fixes a traced test could tell of, those whose every value fit, and those one didn't; "
            "and the traced tests' seconds, beside the released tests' untraced:"
        ),
        _traced,
        3,
    ),
    (
        (
            "Each package's own tests, as released and after each fix: the failures every fixed run has "
            "and no released run, those gone, and the differences in tests its catalog entry names:"
        ),
        _tests,
        5,
    ),
    ("Each package's own type checks: its errors as released, then those new and gone:", _types, 3),
    (
        (
            "Each step's process tree: its seconds, its CPU seconds and the CPUs they kept busy, the most "
            "memory it held at once, and what it was given (`sizing`):"
        ),
        _steps,
        3,
    ),
)
TABLES: Final[dict[str, Table]] = {
    "offences": _offences,
    "levels": _levels,
    "fixes": _fixes,
    "mechanisms": _mechanisms,
    "census": _census,
    "traced": _traced,
    "tests": _tests,
    "types": _types,
    "type-errors": _type_errors,
    "coverage": _coverage,
    "timing": _timing,
    "steps": _steps,
}
