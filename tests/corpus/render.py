"""A run's outputs, each made from its records alone (`pipeline.Store`), so no two can disagree.

- `json`: `report.json`, every record under its corpus, version and step, with the run's own facts;
  and `guesses.jsonl`, every fix a suite's type checks or traced tests could judge, a line each;
- `markdown`: `report.md`, the tables docs/RUNS.md has a section of for each version, and
  `census.md`, what `--fix` can't type and why, where the run took the census;
- `csv`: `tables/offences.csv`, `levels.csv`, `fixes.csv`, `census.csv`, `traced.csv`, `tests.csv`,
  `types.csv`, `type-errors.csv`, `coverage.csv`, `timing.csv`, `steps.csv`, and where they have a
  row `unshared.csv`, `uncounted.csv` and `resampled.csv`, a row a measurement.

`publish` puts the tables in docs/RUNS.md where the run file says: a section a version, or one
section of the whole run (`section`).
"""

import csv
import itertools
import json
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

from constricter import Level
from tests.corpus import corpus_table, corpus_untyped
from tests.corpus.corpus_table import Corpus, Likely, Measured, Typed
from tests.corpus.pipeline import (
    CENSUS,
    CHECK,
    COVERAGE,
    FIX,
    INFER,
    TESTS,
    TIMING,
    TRACED,
    TYPES,
    UNION,
    Record,
    Store,
    fixing,
    steps,
    united,
)
from tests.corpus.pipeline import part as suite_part
from tests.corpus.pipeline import parts as suite_parts
from tests.corpus.report_tables import (
    SECTIONS,
    TABLES,
    Records,
    Rows,
    Table,
    differs,
    json_lines,
    typed_share,
)
from tests.corpus.run_config import CERTAIN, CSV, JSON, LIKELY, MARKDOWN, UNSAFE, Run
from tests.corpus.sizing import USED
from tests.corpus.trees import Tree

_Key: TypeAlias = tuple[str, int, str]  # a fix's file, line and name
_CONSTRICTER: Final = "constricter"  # a table's second column: the version
_ERROR: Final = "error"  # in a fixed run's record: why its patch didn't apply
_SUITE: Final = frozenset({TESTS, TYPES})  # the steps whose records have a fixed run for each fix
# The fix steps a second pass of which is to leave nothing: `--likely`'s is known to leave some.
_CONVERGING: Final = frozenset({f"{FIX}{CERTAIN}", f"{FIX}{UNSAFE}"})
_HEAVY: Final = 8  # gigabytes: a step that held more beside others is noted (a laptop has 16)
_VERSIONS: Final = "\n## constricter "  # `corpus_table.record`'s sections, which a run's goes before
_HEADING: Final = "\n## "
MINUTES: Final = "minutes"  # in a run's facts: how long it took, unless it resumed another


def _every(run: Run) -> list[str]:
    """List every step a run may have a record of.

    Returns:
      Their names, each once.

    """
    union: list[str] = [f"{INFER}{UNION}", suite_part(TESTS, f"{INFER}{UNION}")] if united(run) else []
    suited: list[str] = [TRACED, *suite_parts(run, TESTS), *union, TESTS, *suite_parts(run, TYPES), TYPES]
    return list(dict.fromkeys([*steps(run), *fixing(run), *suited, TIMING]))


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
    return Records(run, trees, versions, found, store)


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
        typed_share(certain),
        typed_share(unsafe),
        typed_share(records.of(tree, version, COVERAGE)) or Typed(0, 0),
        Likely(_count(likely, "fixed"), _count(likely, "left") or 0, typed_share(likely)),
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


def notes(records: Records) -> list[str]:
    """List what a run says of itself that no fix broke: much memory held beside others, hints kept.

    Returns:
      Each, a line: a step that held over `_HEAVY` gigabytes and wasn't run alone, and a hinted
      step whose rounds' hints came from the store, which its seconds then don't count.

    """
    found: list[str] = []
    key: tuple[str, str, str]
    record: Record
    for key, record in records.found.items():
        used: Record = cast("Record", record.get(USED, {}))
        if cast("float", used.get("memory", 0.0)) > _HEAVY and not used.get("alone"):
            found.append(f"{', '.join(key)}: held {used['memory']} GB beside other steps")
        name: str
        rounds: list[int]
        for name, rounds in cast("dict[str, list[int]]", record.get("stored", {})).items():
            read: str = f"{name}'s hints for {rounds[0]} of {rounds[1]} rounds came from the store"
            found.append(f"{', '.join(key)}: {read}, so its seconds measure less of the checker")
    return found


def _more(records: Records, version: str) -> list[str]:
    """Write what the tables of `corpus_table` haven't, each as the CSV table of it is, for one version.

    Returns:
      The Markdown's lines.

    """
    lines: list[str] = []
    note: str
    table: Table
    right: int
    for note, table, right in SECTIONS:
        rows: Rows = [
            [f"{cell:,}" if isinstance(cell, int) and not isinstance(cell, bool) else cell for cell in row]
            for row in table(records)
            if row[1] in {version, _CONSTRICTER}
        ]
        if len(rows) > 1:
            laid: list[str] = corpus_table.table([row[:1] + row[2:] for row in rows], right=right - 1)
            lines += [*corpus_table.filled(note), "", *laid, ""]
    return lines


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
            elif differs(record, ran):
                new: int = len(cast("list[str]", ran["new"]))
                found.append(f"{where}: the tests differ after {step}: {new} new")
    return found


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
        judged: list[Record] = json_lines(store.path(tree.name, version, TRACED, ".verdicts.jsonl"))
        if tree.base is None or not (checked or judged):
            continue
        source: str = tree.root.relative_to(tree.base).as_posix()
        errors: Counter[_Key] = _blames(checked)
        told: dict[_Key, Record] = {_key(each["path"], each): each for each in judged}
        fix: Record
        for fix in json_lines(store.path(tree.name, version, step, ".fixes.jsonl")):
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


def _shared(facts: Record) -> str:
    """Say what share of the machine a run took, where it was given one.

    Returns:
      `, 75% of it`, or nothing.

    """
    share: int = cast("int", facts.get("share", 0))
    return f", {share}% of it" if share else ""


def staged(facts: Record) -> str:
    """Say what stages a run was made in, each with its commit, and which are left (`stages`).

    Returns:
      ` Made in stages: fixes on abc123def456, tests on ...; left: timed.`, or nothing for a run
      made in one sitting.

    """
    ran: list[str]
    if not (ran := list(cast("list[str]", facts.get("stages", [])))):
        return ""
    each: str = ", ".join(" on ".join(one.split(" ", 1)) for one in ran)
    left: list[str] = list(cast("list[str]", facts.get("stages-left", [])))
    return f" Made in stages: {each}" + (f"; left: {', '.join(left)}." if left else ".")


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
        f"{facts.get('python', '')}, on {facts.get('cpus', '')}CPU/{facts.get('gigabytes', '')}GB "
        f"({facts.get('system', '')}){_shared(facts)}: `--jobs={records.run.jobs}`, each "
        f"step a process of its own, started once the CPUs it's expected to keep busy and the memory "
        f"it's expected to hold are free.{took}{staged(facts)} Timings don't compare across machines."
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
        made: str = staged(facts).strip()
        _ = written[-1].write_text((f"{made}\n\n" if made else "") + markdown(records), encoding="utf-8")
        counted: str
        if counted := census_report(records, Store(folder)):
            written.append(folder / "census.md")
            _ = written[-1].write_text(counted, encoding="utf-8")
    if CSV in records.run.formats:
        (folder / "tables").mkdir(exist_ok=True)
        name: str
        rows: Callable[[Records], Rows]
        for name, rows in TABLES.items():
            table: Rows = rows(records)
            if len(table) > 1:  # a step the run didn't ask for has no table
                written.append(folder / "tables" / f"{name}.csv")
                file: IO[str]
                with written[-1].open("w", encoding="utf-8", newline="") as file:
                    csv.writer(file, lineterminator="\n").writerows(table)  # as git keeps text
    return written
