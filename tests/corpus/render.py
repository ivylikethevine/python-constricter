# SPDX-License-Identifier: MIT
"""A run's outputs, each made from its records alone (`pipeline.Store`), so no two can disagree.

- `json`: `report.json`, every record under its corpus, version and step, with the run's own facts;
  and `guesses.jsonl`, every fix a suite's type checks or traced tests could judge, a line each;
- `markdown`: `report.md`, the tables docs/RUNS.md has a section of for each version, and
  `census.md`, what `--fix` can't type and why, where the run took the census;
- `csv`: `tables/offences.csv`, `levels.csv`, `fixes.csv`, `census.csv`, `traced.csv`, `tests.csv`,
  `types.csv`, `type-errors.csv`, `coverage.csv`, `timing.csv` and `steps.csv`, a row a measurement.

`publish` puts the tables in docs/RUNS.md where the run file says: a section a version, or one
section of the whole run (`section`).
"""

import csv
import itertools
import json
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import Level
from tests.corpus import corpus_table, corpus_untyped
from tests.corpus.corpus_table import Corpus, Likely, Measured, Typed
from tests.corpus.pipeline import (
    CENSUS,
    CHECK,
    COVERAGE,
    FIX,
    GUESS,
    TESTS,
    TIMING,
    TRACED,
    TYPES,
    Record,
    Store,
    fixing,
    steps,
)
from tests.corpus.run_config import CERTAIN, CSV, JSON, LIKELY, MARKDOWN, UNSAFE, Run
from tests.corpus.sizing import USED
from tests.corpus.trees import Tree

_Row: TypeAlias = list[object]  # a table's cells, as `csv` writes them
_Rows: TypeAlias = list[_Row]
_Key: TypeAlias = tuple[str, int, str]  # a fix's file, line and name
_NO_RECORD: Final[Record] = {}
_SHAPE: Final = "shape"  # the census table's column for an unfixed binding's value
_CONSTRICTER: Final = "constricter"  # a table's second column: the version
_ERROR: Final = "error"  # in a fixed run's record: why its patch didn't apply
_SUITE: Final = frozenset({TESTS, TYPES})  # the steps whose records have a fixed run for each fix
_VERDICTS: Final = ("told", "held", "differed")  # a traced record's counts, each by tier
_COUNTS: Final = ("untyped", "guessed", "unfixed", "unparsed")  # a census record's counts
# The fix steps a second pass of which is to leave nothing: `--likely`'s is known to leave some.
_CONVERGING: Final = frozenset({f"{FIX}{CERTAIN}", f"{FIX}{UNSAFE}"})
_HEAVY: Final = 8  # gigabytes: a step that held more beside others is noted (a laptop has 16)
_VERSIONS: Final = "\n## constricter "  # `corpus_table.record`'s sections, which a run's goes before
_HEADING: Final = "\n## "
MINUTES: Final = "minutes"  # in a run's facts: how long it took, unless it resumed another


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
    return list(dict.fromkeys([*steps(run), *fixing(run), TRACED, TESTS, TYPES, TIMING]))


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
    head: _Row = ["corpus", "constricter", "tier", *_VERDICTS, "resting on the trace", "tests"]
    rows: _Rows = [[*head, "seconds", "untraced"]]
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


def _tests(records: Records) -> _Rows:
    head: _Row = ["corpus", "constricter", "run", "same as released", "summary", "new failures"]
    rows: _Rows = [[*head, "gone", "named"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TESTS):
                released: str = _summary(cast("Record", record["released"]))
                rows.append([tree.name, version, "released", "", released, "", "", ""])
                step: str
                ran: Record
                for step, ran in cast("dict[str, Record]", record["fixed"]).items():
                    more: _Row = [
                        len(cast("list[str]", ran.get(key, []))) for key in ("new", "gone", "named")
                    ]
                    rows.append([tree.name, version, step, not _differs(record, ran), _summary(ran), *more])
    return rows


def _differs(record: Record, ran: Record) -> bool:
    """Check whether a fixed run of a `tests` record differs from the released tests by the fix's doing.

    Returns:
      What `suite_steps.weighed` found; for a record from before it weighed, whether the run
      isn't the released one's and the released tests don't vary.

    """
    return bool(ran.get("differs", ran.get("same") is False and not record.get("varies")))


def _steps(records: Records) -> _Rows:
    head: _Row = ["corpus", "constricter", "step", "seconds", "CPU seconds", "CPUs", "GB held"]
    rows: _Rows = [[*head, "CPUs given", "GB given", "alone"]]
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


def notes(records: Records) -> list[str]:
    """List what a run says of itself that no fix broke: the steps that held much memory beside others.

    Returns:
      Each, a line: a step that held over `_HEAVY` gigabytes and wasn't run alone.

    """
    found: list[str] = []
    key: tuple[str, str, str]
    record: Record
    for key, record in records.found.items():
        used: Record = cast("Record", record.get(USED, {}))
        if cast("float", used.get("memory", 0.0)) > _HEAVY and not used.get("alone"):
            found.append(f"{', '.join(key)}: held {used['memory']} GB beside other steps")
    return found


def _more(records: Records, version: str) -> list[str]:
    """Write what the tables of `corpus_table` haven't, each as the CSV table of it is, for one version.

    Returns:
      The Markdown's lines.

    """
    lines: list[str] = []
    note: str
    table: _Table
    right: int
    for note, table, right in _SECTIONS:
        rows: _Rows = [
            [f"{cell:,}" if isinstance(cell, int) and not isinstance(cell, bool) else cell for cell in row]
            for row in table(records)
            if row[1] in {version, _CONSTRICTER}
        ]
        if len(rows) > 1:
            laid: list[str] = corpus_table.table([row[:1] + row[2:] for row in rows], right=right - 1)
            lines += [*corpus_table.filled(note), "", *laid, ""]
    return lines


def _counted(records: Records) -> _Rows:
    return [row[:-2] for row in _census(records) if row[-2] in {"", _SHAPE}]


def problems(records: Records) -> list[str]:
    """List what the run's fixes broke: what a run exits 1 for, beside a step that failed.

    A file that compiled before a fix and doesn't after; what a second pass of the certain fixes
    or of every guess would still fix; a fix whose patch a suite's checkout refuses; a suite's
    tests stopped for running too long, traced or not; and its tests that differ after a fix by more than
    the tests its catalog entry names, both times they ran (`suite_steps.weighed`).

    Returns:
      Each, a line.

    """
    found: list[str] = []
    key: tuple[str, str, str]
    record: Record
    for key, record in records.found.items():
        where: str = f"{key[0]}, {key[1]}, {key[2]}"
        if key[2].startswith(FIX) and record.get("broken"):
            found.append(f"{where}: {record['broken']} file(s) no longer compile")
        if key[2] in _CONVERGING and record.get("left"):
            found.append(f"{where}: a second pass would still fix {record['left']}")
        step: str
        ran: Record
        fixed: dict[str, Record] = cast("dict[str, Record]", record["fixed"] if key[2] in _SUITE else {})
        if record.get("stopped"):
            found.append(f"{where}: its tests were stopped as released: they ran too long")
        for step, ran in fixed.items():
            if _ERROR in ran:
                found.append(f"{where}: {step}'s patch didn't apply: {ran[_ERROR]}")
            elif _differs(record, ran):
                new: int = len(cast("list[str]", ran["new"]))
                found.append(f"{where}: the tests differ after {step}: {new} new")
    return found


def _timing(records: Records) -> _Rows:
    rows: _Rows = [["corpus", "constricter", "jobs", "one process", "with jobs", "runs"]]
    tree: Tree
    for tree in records.trees:
        version: str
        for version in records.versions:
            record: Record
            if record := records.of(tree, version, TIMING):
                medians: _Row = [record["median one"], record["median every"]]
                runs: int = len(cast("list[float]", record["one"]))
                rows.append([tree.name, version, record["jobs"], *medians, runs])
    return rows


def census_report(records: Records, store: Store) -> str:
    """Write the census as `corpus_untyped.report` lays it out, a section a version, from the bindings kept.

    Returns:
      The Markdown; nothing where the run took no census.

    """
    parts: list[str] = []
    version: str
    for version in records.versions:
        bindings: list[corpus_untyped.Binding] = []
        seen: list[str] = []
        tree: Tree
        for tree in records.trees:
            rows: Path = store.path(tree.name, version, CENSUS, ".rows.jsonl")
            if rows.exists():
                seen.append(tree.name)
                bindings += [
                    corpus_untyped.Binding(**json.loads(line))
                    for line in rows.read_text(encoding="utf-8").splitlines()
                ]
        if seen:
            parts += [f"# What constricter {version} can't type", "", corpus_untyped.report(bindings, seen)]
    return "\n".join(parts)


def _lines(path: Path) -> list[Record]:
    text: str = path.read_text(encoding="utf-8") if path.exists() else ""
    return [json.loads(line) for line in text.splitlines()]


def _key(path: object, about: Record) -> _Key:
    return str(path), cast("int", about["line"]), str(about["name"])


def _blames(checked: Record) -> Counter[_Key]:
    """Count the new type errors of a fixed run's record that are traced to each fix.

    Returns:
      The count, by the fix's file, line and name.

    """
    new: list[Record] = cast("list[Record]", checked.get("new", []))
    return Counter(_key(each["path"], cast("Record", each["fix"])) for each in new if each["fix"])


def guesses(records: Records, store: Store) -> list[Record]:
    """Gather every fix of each corpus's `fix-unsafe` step, with what blames it or bears it out.

    The new type errors its suite's checks traced to it (`errors`; `checked`: whether the suite has
    checks that ran), and how its binding's values stood to its annotation as the traced tests ran
    (`verdict`: how many fit, didn't, and couldn't be told; `seen`: the types the trace spells).
    What a set of mechanisms is measured by, to be likely (docs/LIKELY.md).

    Returns:
      Them, a record a fix; none of a corpus whose suite ran neither its checks nor its tests traced.

    """
    found: list[Record] = []
    step: str = f"{FIX}{UNSAFE}"
    tree: Tree
    version: str
    for tree, version in itertools.product(records.trees, records.versions):
        fixed: Record = cast("Record", records.of(tree, version, TYPES).get("fixed", {}))
        checked: Record = cast("Record", fixed.get(step, {}))
        judged: list[Record] = _lines(store.path(tree.name, version, TRACED, ".verdicts.jsonl"))
        if tree.base is None or not (checked or judged):
            continue
        source: str = tree.root.relative_to(tree.base).as_posix()
        errors: Counter[_Key] = _blames(checked)
        told: dict[_Key, Record] = {_key(each["path"], each): each for each in judged}
        fix: Record
        for fix in _lines(store.path(tree.name, version, step, ".fixes.jsonl")):
            key: _Key = _key(f"{source}/{fix['path']}", fix)
            verdict: Record = told.get(key, {})
            found.append(
                {
                    "package": tree.name,
                    "constricter": version,
                    "path": key[0],
                    "line": key[1],
                    "name": key[2],
                    "annotation": fix["annotation"],
                    "kinds": "+".join(cast("list[str]", fix["kinds"])),
                    "unsafe": fix["tier"] != CERTAIN,
                    "likely": fix["tier"] == LIKELY,
                    "errors": errors[key],
                    "checked": bool(checked),
                    "seen": verdict.get("seen") or None,
                    "verdict": verdict.get("verdict", [0, 0, 0]),
                },
            )
    return found


def section(records: Records, facts: Record) -> str:
    """Write the whole run as one section of docs/RUNS.md: its machine, and its last version's tables.

    Returns:
      The Markdown, from its heading on, laid out as Prettier does.

    """
    version: str = records.versions[-1]
    took: str = f" The run took {facts[MINUTES]} minutes." if MINUTES in facts else ""
    intro: str = (
        f"The run `{records.run.label}` (`python -m tests.corpus`) on {', '.join(records.run.include)}: "
        f"constricter {facts.get('constricter', '')} (`{facts.get('commit', '')}`), Python "
        f"{facts.get('python', '')}, on {facts.get('machine', '')} ({facts.get('cpus', '')} CPUs, "
        f"{facts.get('gigabytes', '')} GB, {facts.get('system', '')}): `--jobs={records.run.jobs}`, each "
        f"step a process of its own, started once the CPUs it's expected to keep busy and the memory "
        f"it's expected to hold are free.{took} Timings don't compare across machines."
    )
    rows: list[Measured] = [measured(records, tree, version) for tree in records.trees]
    broke: list[str] = [f"- {each}" for each in (*problems(records), *notes(records))]
    parts: list[str] = [
        f"## {records.run.publish.section}",
        "",
        *corpus_table.filled(intro),
        "",
        corpus_table.tables(rows),
        "",
        *_more(records, version),
        *(line for each in broke for line in corpus_table.filled(each, "  ")),
    ]
    return "\n".join(parts).rstrip() + "\n"


def _placed(text: str, heading: str, runs: Path) -> None:
    """Write a section into `runs`, in place of the one of its `heading`, before the versions' sections."""
    whole: str = runs.read_text(encoding="utf-8") if runs.exists() else ""
    head: str
    versions: str
    rest: str
    head, versions, rest = whole.partition(_VERSIONS)
    after: str = ""
    if heading in head:
        old: str
        head, _, old = head.partition(heading)
        following: int = old.find(_HEADING)
        after = "" if following < 0 else old[following:].strip() + "\n"
    body: str = f"{head.rstrip()}\n\n{text}".lstrip() + (f"\n{after}" if after else "")
    _ = runs.write_text(f"{body}{versions}{rest}", encoding="utf-8")


def publish(records: Records, root: Path, facts: Record) -> None:
    """Record the run's tables where its run file says, in docs/RUNS.md.

    A section a version, of the per-version tables: `corpus_table.record` refuses to write over
    one that's there, unless the run file says to replace it. Or, where the run file names a
    `section`, that one alone, of the whole run (`section`), in place of the one that's there.
    """
    target: Path | None
    if (target := records.run.publish.runs_md) is None:
        return
    if records.run.publish.section:
        _placed(section(records, facts), f"## {records.run.publish.section}\n", root / target)
        return
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
    rows: _Rows = [["corpus", "constricter", *_COUNTS, _SHAPE, "bindings"]]
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


_Table: TypeAlias = Callable[[Records], _Rows]
# What `report.md` has under each version's tables: a note, the table, and its columns of words.
_Section: TypeAlias = tuple[str, _Table, int]
_SECTIONS: Final[tuple[_Section, ...]] = (
    ("Each fix on a copy: by tier, and with `--infer-with` each type checker or a trace:", _fixes, 3),
    ("The untyped bindings: with only a guess, with no fix, and in files that don't parse:", _counted, 2),
    ("A check at `suffocate`: the median seconds of its runs, in one process and with `jobs`:", _timing, 2),
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
    "timing": _timing,
    "steps": _steps,
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
        "problems": problems(records),
        "notes": notes(records),
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
        guessed: list[Record]
        if guessed := guesses(records, Store(folder)):
            written.append(folder / "guesses.jsonl")
            _ = written[-1].write_text("".join(f"{json.dumps(each)}\n" for each in guessed), encoding="utf-8")
    if MARKDOWN in records.run.formats:
        written.append(folder / "report.md")
        _ = written[-1].write_text(markdown(records), encoding="utf-8")
        counted: str
        if counted := census_report(records, Store(folder)):
            written.append(folder / "census.md")
            _ = written[-1].write_text(counted, encoding="utf-8")
    if CSV in records.run.formats:
        (folder / "tables").mkdir(exist_ok=True)
        name: str
        rows: Callable[[Records], _Rows]
        for name, rows in _TABLES.items():
            table: _Rows = rows(records)
            if len(table) > 1:  # a step the run didn't ask for has no table
                written.append(folder / "tables" / f"{name}.csv")
                file: IO[str]
                with written[-1].open("w", encoding="utf-8", newline="") as file:
                    csv.writer(file).writerows(table)
    return written
