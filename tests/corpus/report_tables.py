"""The tables of a run's report, each built from the run's records alone (`Records`), a row a corpus.

Which go in `report.md` and which each version's section of docs/RUNS.md has (`SECTIONS`), and
the CSV files (`TABLES`).
"""

from collections import Counter
from collections.abc import Callable, Iterator, Sequence
from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast

from constricter import Level
from tests.corpus import corpus_guesses, corpus_suite, jsonl
from tests.corpus.corpus_table import Typed
from tests.corpus.pipeline import (
    CENSUS,
    CHECK,
    COVERAGE,
    FIX,
    FIX_UNSAFE,
    FROM,
    GUESS,
    IMPLIED,
    INFER_UNION,
    LOOP,
    RELEASED,
    ROWS,
    TESTED,
    TESTS,
    TIMING,
    TRACED,
    TYPES,
    UNION,
    Record,
    Store,
    fixing,
    united,
)
from tests.corpus.run_config import CERTAIN, LIKELY, Run
from tests.corpus.sizing import USED
from tests.corpus.trees import Tree

if TYPE_CHECKING:
    from pathlib import Path

_Row: TypeAlias = list[object]  # a table's cells, as `csv` writes them
Rows: TypeAlias = list[_Row]


_NO_RECORD: Final[Record] = {}
_SHAPE: Final = "shape"  # the census table's column for an unfixed binding's value


_VERDICTS: Final = ("told", "held", "differed")  # a traced record's counts, each by tier
_COUNTS: Final = ("untyped", "guessed", "unfixed", "unparsed")  # a census record's counts
_FIXES: Final = ".fixes.jsonl"  # a fix step's list of its fixes, a line each
_Bound: TypeAlias = tuple[str, int, str]  # a fix's file, line and name


class Records(NamedTuple):
    """A run's records, read once: each step's by its corpus, version and name."""

    run: Run
    trees: Sequence[Tree]
    versions: list[str]  # as the run records them, in its order
    found: dict[tuple[str, str, str], Record]
    store: Store | None = None  # the run's folder, for the lists its fix steps wrote

    def of(self, tree: Tree, version: str, step: str) -> Record:
        """Find a step's record.

        Returns:
          It, or an empty one if the step didn't run.

        """
        return self.found.get((tree.name, version, step), _NO_RECORD)

    def each(self, step: str) -> Iterator[tuple[Tree, str, Record]]:
        """Walk a step's records, each corpus's in turn, each version's in the run's order.

        Yields:
          Each corpus, version and record, where the step ran.

        """
        tree: Tree
        version: str
        record: Record
        for tree in self.trees:
            for version in self.versions:
                if record := self.of(tree, version, step):
                    yield tree, version, record

    def listed(self, tree: Tree, version: str, step: str) -> dict[_Bound, str]:
        """Read the fixes a fix step made.

        Returns:
          Each one's annotation, by its file, line and name; none without the run's folder.

        """
        if self.store is None:
            return {}
        path: Path = self.store.path(tree.name, version, step, _FIXES)
        return {
            (str(fix["path"]), cast("int", fix["line"]), str(fix["name"])): str(fix["annotation"])
            for fix in jsonl.read(path)
        }


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
    version: str
    record: Record
    for tree, version, record in records.each(TYPES):
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
    version: str
    record: Record
    for tree, version, record in records.each(TRACED):
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


def _one_type(records: Records) -> Rows:
    """Hold each binding with neither a fix nor a guess to what the traced tests saw it hold, by its shape.

    Those a test reached, and those it saw hold one type: what any inference could type at most,
    and where a binding the run bound otherwise is worth a look. Read from the census's rows and the
    traced step's (`traced.seen.jsonl`), where a run kept both.

    Returns:
      A row a shape, the most bindings first, with the commonest source of those of one type.

    """
    rows: Rows = [["corpus", "constricter", "shape", "no fix", "traced", "one type", "commonest source"]]
    tree: Tree
    for tree in records.trees if records.store is not None else ():
        store: Store = cast("Store", records.store)
        version: str
        for version in records.versions:
            seen: dict[_Bound, list[str]] = {
                _bound(each): cast("list[str]", each["seen"])
                for each in jsonl.read(store.path(tree.name, version, TRACED, corpus_guesses.SEEN))
            }
            shape: str
            counts: list[int]
            common: str
            for shape, counts, common in _held(
                jsonl.read(store.path(tree.name, version, CENSUS, ROWS)),
                seen,
            ):
                rows.append([tree.name, version, shape, *counts, common])
    return rows


def _one_type_counts(records: Records) -> Rows:
    """`_one_type` without its sources: Python, which Markdown tables and spell checks misread.

    Returns:
      Its rows, less their last column, each shape a code span (`builtin __import__()`).

    """
    rows: Rows = _one_type(records)
    return [rows[0][:-1], *([*row[:2], f"`{row[2]}`", *row[3:-1]] for row in rows[1:])]


def _bound(each: Record) -> _Bound:
    return str(each["path"]), cast("int", each["line"]), str(each["name"])


def _held(census: list[Record], seen: dict[_Bound, list[str]]) -> list[tuple[str, list[int], str]]:
    """Count, by shape, the bindings with neither a fix nor a guess, those `seen`, and those seen one type.

    Returns:
      Each shape's counts and the commonest source of those of one type, the most bindings first;
      none where nothing was seen.

    """
    counts: dict[str, list[int]] = {}
    sources: dict[str, Counter[str]] = {}
    row: Record
    for row in census if seen else ():
        if row["fixed"] or row["unsafe"]:
            continue
        held: list[str] = seen.get(_bound(row), [])
        count: list[int] = counts.setdefault(str(row["shape"]), [0, 0, 0])
        count[0] += 1
        count[1] += bool(held)
        count[2] += len(held) == 1
        if len(held) == 1:
            sources.setdefault(str(row["shape"]), Counter())[str(row.get("source", ""))] += 1
    return [
        (shape, count, next((source for source, _ in sources.get(shape, Counter()).most_common(1)), ""))
        for shape, count in sorted(counts.items(), key=lambda each: -each[1][0])
    ]


def _tests(records: Records) -> Rows:
    head: _Row = ["corpus", "constricter", "run", "same as released", "summary", "new failures"]
    rows: Rows = [[*head, "gone", "named", "skipped anew", "skipped no more"]]
    tree: Tree
    version: str
    record: Record
    for tree, version, record in records.each(TESTS):
        released: str = _summary(cast("Record", record["released"]))
        whose: str = f" (from {record[FROM]})" if FROM in record else ""
        rows.append([tree.name, version, f"released{whose}", "", released, "", "", "", "", ""])
        step: str
        ran: Record
        for step, ran in cast("dict[str, Record]", record["fixed"]).items():
            # An implied part's skips are the union's, whose run stands for it.
            more: _Row = [*_counts(ran), *_moved(records, tree, version, record, str(ran.get(IMPLIED, step)))]
            summary: str = f"as {ran[IMPLIED]}'s (implied)" if IMPLIED in ran else _summary(ran)
            rows.append([tree.name, version, step, not differs(record, ran), summary, *more])
        if UNION in record:  # the union's own run, listed as the parts it stands for are
            union: Record = cast("Record", record[UNION])
            more = [*_counts(union), *_moved(records, tree, version, record, INFER_UNION)]
            rows.append([tree.name, version, INFER_UNION, not differs(record, union), _summary(union), *more])
    return rows


def _counts(ran: Record) -> _Row:
    return [len(cast("list[str]", ran.get(key, []))) for key in ("new", "gone", "named")]


def _moved(records: Records, tree: Tree, version: str, record: Record, step: str) -> _Row:
    """Count the tests a fixed run skipped where the tests as released ran them, and the reverse.

    By name, from both runs' tests (`corpus_suite.skips`), as the run's folder holds them; the
    released tests' from the earlier run's folder they were taken from (`FROM`), where this one
    doesn't hold them (`_released`).

    Returns:
      The two counts; blanks where a run wrote no tests, or the folder isn't there.

    """
    store: Store | None
    if (store := records.store) is None:
        return ["", ""]
    released: Path = store.path(tree.name, version, f"{TESTS}-{RELEASED}", TESTED)
    if not released.is_file() and FROM in record:
        released = _released(Store(store.root.parent / str(record[FROM])), tree.name, version)
    moved: tuple[list[str], list[str]] | None = corpus_suite.skips(
        released,
        store.path(tree.name, version, f"{TESTS}-{step}", TESTED),
    )
    return ["", ""] if moved is None else [len(moved[0]), len(moved[1])]


def _released(earlier: Store, corpus: str, version: str) -> "Path":
    """Find a suite's released tests in an earlier run's folder, under whichever version it ran.

    The released tests run no constricter, so any version's are the same tests: an earlier run of
    another label keeps them under its own (`super+dev` for a mega run's `mega+dev`).

    Returns:
      This version's path where it's there, else the first version's that is; this version's if none.

    """
    path: Path = earlier.path(corpus, version, f"{TESTS}-{RELEASED}", TESTED)
    found: list[Path] = sorted(path.parent.parent.glob(f"*/{path.name}"))
    return path if path.is_file() or not found else found[0]


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
            *("G instructions, one process", "with jobs", "timed by", "beside other steps"),
        ],
    ]
    tree: Tree
    version: str
    record: Record
    for tree, version, record in records.each(TIMING):
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
            "yes" if record.get("beside") else "no",  # a record from before it was timed alone
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

    With every source's fix at once (`infer-union`) last, where the run makes it: the one fix
    whose hints can agree.

    `most`: only that many sets of each fix, those that made the most.

    Returns:
      The rows, a fix's sets from the one that made the most.

    """
    rows: Rows = [["fix", "constricter", "mechanisms", "fixed", CERTAIN, LIKELY, GUESS]]
    union: list[str] = [INFER_UNION] if united(records.run) else []
    version: str
    for version in records.versions:
        mode: str
        for mode in (*fixing(records.run), *union):
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
    version: str
    record: Record
    for tree, version, record in records.each(CENSUS):
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


def _unshared(records: Records) -> Rows:
    """Count each corpus's likely fixes the unsafe fixes leave out or write otherwise.

    The fixes interact (a guess changes what another binding's inference sees), so `--unsafe-fixes`
    isn't `--likely` with more.

    Returns:
      A row a corpus and version where they differ.

    """
    rows: Rows = [["corpus", "constricter", "likely", "absent from unsafe", "annotated otherwise"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            likely: dict[_Bound, str] = records.listed(tree, version, f"{FIX}{LIKELY}")
            unsafe: dict[_Bound, str] = records.listed(tree, version, FIX_UNSAFE)
            absent: int = len(likely.keys() - unsafe.keys())
            otherwise: int = sum(unsafe[key] != likely[key] for key in likely.keys() & unsafe.keys())
            if unsafe and (absent or otherwise):
                rows.append([tree.name, version, len(likely), absent, otherwise])
    return rows


def _uncounted(records: Records) -> Rows:
    """Find the fix steps whose bindings typed after aren't those typed before and those they fixed.

    A fix that didn't make its binding typed, or a binding typed that no fix names.

    Returns:
      A row a corpus, version and fix where the counts differ.

    """
    rows: Rows = [["corpus", "constricter", "fix", "typed before", "fixed", "typed after", "short"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            before: Typed | None = typed_share(records.of(tree, version, COVERAGE))
            mode: str
            short: int
            for mode in fixing(records.run):
                record: Record = records.of(tree, version, mode)
                after: Typed | None = typed_share(record)
                fixed: int | None = cast("int | None", record.get("fixed"))
                if before is None or after is None or fixed is None:
                    continue
                if short := before.typed + fixed - after.typed:
                    rows.append(
                        [tree.name, version, mode.removeprefix(FIX), before.typed, fixed, after.typed, short],
                    )
    return rows


def _resampled(records: Records) -> Rows:
    """Set each suite's traced tests beside its released tests, a sample of its flakiness for free.

    Returns:
      A row a corpus and version whose tests were traced: both runs' counts, and whether the same
      tests failed.

    """
    rows: Rows = [["corpus", "constricter", "released", "traced", "same failures"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record = records.of(tree, version, TESTS)
            samples: dict[str, Record] = cast("dict[str, Record]", record.get("samples", {}))
            traced: Record | None
            if (traced := samples.get(TRACED)) is not None:
                released: Record = cast("Record", record["released"])
                same: bool = sorted(cast("list[str]", released.get("failed", []))) == sorted(
                    cast("list[str]", traced.get("failed", [])),
                )
                rows.append([tree.name, version, _summary(released), _summary(traced), same])
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
            "The bindings with neither a fix nor a guess, by shape: those a traced test reached, and "
            "those it saw hold one type, the most any inference could type (each shape's commonest "
            "source is in `tables/one-type.csv`):"
        ),
        _one_type_counts,
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
    (
        (
            "The likely fixes the unsafe fixes leave out or write otherwise, where there are any (the "
            "fixes interact, so unsafe isn't likely with more):"
        ),
        _unshared,
        2,
    ),
    (
        (
            "The fixes whose bindings typed after aren't those typed before and those fixed, where they "
            "differ (a fix that didn't make its binding typed):"
        ),
        _uncounted,
        3,
    ),
    (
        "Each suite's traced tests beside its released tests, a sample of its flakiness:",
        _resampled,
        5,
    ),
)
TABLES: Final[dict[str, Table]] = {
    "offences": _offences,
    "levels": _levels,
    "fixes": _fixes,
    "mechanisms": _mechanisms,
    "census": _census,
    "traced": _traced,
    "one-type": _one_type,
    "tests": _tests,
    "types": _types,
    "type-errors": _type_errors,
    "coverage": _coverage,
    "timing": _timing,
    "steps": _steps,
    "unshared": _unshared,
    "uncounted": _uncounted,
    "resampled": _resampled,
}
