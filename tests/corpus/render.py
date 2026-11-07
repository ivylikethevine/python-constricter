"""A run's outputs, each made from its records alone (`pipeline.Store`), so no two can disagree.

- `json`: `report.json`, every record under its corpus, version and step, with the run's own facts;
  and `guesses.jsonl`, every fix a suite's type checks or traced tests could judge, a line each;
- `markdown`: `report.md`, the tables docs/runs/ has a file of for each version, and
  `census.md`, what `--fix` can't type and why, where the run took the census;
- `csv`: `tables/offences.csv`, `levels.csv`, `fixes.csv`, `census.csv`, `traced.csv`, `tests.csv`,
  `types.csv`, `type-errors.csv`, `coverage.csv`, `timing.csv`, `steps.csv`, and where they have a
  row `unshared.csv`, `uncounted.csv` and `resampled.csv`, a row a measurement.

`publish` puts the tables in docs/runs/ where the run file says, linked from docs/RUNS.md: a file a
version, or one of the whole run (`section`).
"""

import csv
import itertools
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

from constricter import Level
from tests.corpus import archive, corpus_table, corpus_untyped, jsonl
from tests.corpus.corpus_table import Corpus, Likely, Measured, Typed
from tests.corpus.pipeline import (
    CENSUS,
    CHECK,
    COVERAGE,
    FIX,
    FIX_UNSAFE,
    INFER_UNION,
    TESTS,
    TIMING,
    TRACED,
    TYPES,
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
    typed_share,
)
from tests.corpus.run_config import CERTAIN, CSV, JSON, LIKELY, MARKDOWN, REPORT, Run, scrubbed
from tests.corpus.sizing import USED
from tests.corpus.trees import Tree

_Key: TypeAlias = tuple[str, int, str]  # a fix's file, line and name
_CONSTRICTER: Final = "constricter"  # a table's second column: the version
_ERROR: Final = "error"  # in a fixed run's record: why its patch didn't apply
_SUITE: Final = frozenset({TESTS, TYPES})  # the steps whose records have a fixed run for each fix
# The fix steps a second pass of which is to leave nothing: `--likely`'s is known to leave some.
_CONVERGING: Final = frozenset({f"{FIX}{CERTAIN}", FIX_UNSAFE})
_HEAVY: Final = 8  # gigabytes: a step that held more beside others is noted (a laptop has 16)
MINUTES: Final = "minutes"  # in a run's facts: how long it took, unless it resumed another


def _every(run: Run) -> list[str]:
    """List every step a run may have a record of.

    Returns:
      Their names, each once.

    """
    union: list[str] = [INFER_UNION, suite_part(TESTS, INFER_UNION)] if united(run) else []
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
    unsafe: Record = records.of(tree, version, FIX_UNSAFE)
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
    """Gather every fix of each corpus's `fix-unsafe` and `infer-union` steps, with what judges it.

    The new type errors its suite's checks traced to it (`errors`; `checked`: whether the suite has
    checks that ran after the step), and how its binding's values stood to its annotation as the
    traced tests ran (`verdict`: how many fit, didn't, and couldn't be told; `seen`: the types the
    trace spells), the step's own verdicts (`<step>.verdicts.jsonl`, by annotation). What a set of
    mechanisms is measured by, to be likely (docs/LIKELY.md): the guesses' sets by `fix-unsafe`'s
    rows, and those the union alone makes (`agreed+checker`) by `infer-union`'s (`fix`), which
    hold the guesses' fixes again.

    Returns:
      Them, a record a fix; none of a step its corpus's suite ran neither its checks nor its tests
      traced after.

    """
    found: list[Record] = []
    step: str
    tree: Tree
    version: str
    for tree, version, step in itertools.product(records.trees, records.versions, (FIX_UNSAFE, INFER_UNION)):
        fixed: Record = cast("Record", records.of(tree, version, TYPES).get("fixed", {}))
        checked: Record = cast("Record", fixed.get(step, {}))
        judged: list[Record] = jsonl.read(
            store.path(tree.name, version, TRACED if step == FIX_UNSAFE else step, ".verdicts.jsonl"),
        )
        if tree.base is None or not (checked or judged):
            continue
        source: str = tree.root.relative_to(tree.base).as_posix()
        errors: Counter[_Key] = _blames(checked)
        told: dict[tuple[_Key, str], Record] = {
            (_key(each["path"], each), str(each["annotation"])): each for each in judged
        }
        fix: Record
        for fix in jsonl.read(store.path(tree.name, version, step, ".fixes.jsonl")):
            key: _Key = _key(f"{source}/{fix['path']}", fix)
            verdict: Record = told.get((key, str(fix["annotation"])), {})
            found.append(
                {
                    "package": tree.name,
                    "constricter": version,
                    "fix": step,
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


def _beside(records: Records) -> str:
    """Say that the timed checks ran beside the other steps, where they did (`timing-beside`).

    Returns:
      The clause, or nothing.

    """
    if not records.run.steps.timing_beside:
        return ""
    return ", nor their seconds across runs, taken beside the other steps: their instructions do"


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
    """Write the whole run as one file of docs/runs/: its machine, and its last version's tables.

    Returns:
      The Markdown below its heading, laid out as Prettier does.

    """
    version: str = records.versions[-1]
    took: str = f" The run took {facts[MINUTES]} minutes." if MINUTES in facts else ""
    intro: str = (
        f"The run `{records.run.label}` (`python -m tests.corpus`) on {', '.join(records.run.include)}: "
        f"constricter {facts.get('constricter', '')} (`{facts.get('commit', '')}`), Python "
        f"{facts.get('python', '')}, on {facts.get('cpus', '')}CPU/{facts.get('gigabytes', '')}GB "
        f"({facts.get('system', '')}){_shared(facts)}: `--jobs={records.run.jobs}`, each "
        f"step a process of its own, started once the CPUs it's expected to keep busy and the memory "
        f"it's expected to hold are free.{took}{staged(facts)} Timings don't compare across machines"
        f"{_beside(records)}."
    )
    rows: list[Measured] = [measured(records, tree, version) for tree in records.trees]
    broke: list[str] = [f"- {each}" for each in (*problems(records), *notes(records))]
    parts: list[str] = [
        *corpus_table.filled(intro),
        "",
        corpus_table.tables(rows),
        "",
        *_more(records, version),
        *(line for each in broke for line in corpus_table.filled(each, "  ")),
    ]
    return "\n".join(parts).rstrip() + "\n"


def publish(records: Records, root: Path, facts: Record) -> None:
    """Record the run's tables where its run file says, in files beside docs/RUNS.md, its index.

    A file a version, of the per-version tables: `corpus_table.record` refuses to write over one
    that's there, unless the run file says to replace it. Or, where the run file names a `section`,
    that one alone, of the whole run (`section`), in place of its file that's there.
    """
    target: Path | None
    if (target := records.run.publish.runs_md) is None:
        return
    title: str
    if title := records.run.publish.section:
        name: str = title.lower().replace(" ", "-")
        corpus_table.written(root / target, name, title, section(records, facts))
        return
    rows: list[Measured] = [
        measured(records, tree, version) for version in records.versions for tree in records.trees
    ]
    corpus_table.record(rows, root / target, replace=records.run.publish.replace)


def report(records: Records, facts: Record, tables: Mapping[str, Rows] | None = None) -> Record:
    """Gather the run's records under each corpus, version and step, with the run's own `facts`.

    `tables`: each of its tables by name, kept as the CSV files have them (`TABLES`).

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
        "tables": {
            name: [["" if cell is None else str(cell) for cell in row] for row in rows]
            for name, rows in (tables or {}).items()
        },
    }


def _tables(records: Records) -> dict[str, Rows]:
    """Make each of the run's tables (`TABLES`).

    Returns:
      Them, by name: none for a step the run didn't ask for.

    """
    found: dict[str, Rows] = {}
    name: str
    rows: Table
    for name, rows in TABLES.items():
        table: Rows = rows(records)
        if len(table) > 1:
            found[name] = table
    return found


def write(records: Records, folder: Path, facts: Record) -> list[Path]:
    """Write each of the run's formats into its folder.

    Returns:
      The files written.

    """
    written: list[Path] = []
    tables: dict[str, Rows] = _tables(records)
    guessed: list[Record] = []
    if JSON in records.run.formats:
        written.append(folder / REPORT)
        reported: str = scrubbed(json.dumps(report(records, facts, tables), indent=2))
        _ = written[-1].write_text(reported + "\n", encoding="utf-8")
        if guessed := guesses(records, Store(folder)):
            written.append(folder / "guesses.jsonl")
            _ = written[-1].write_text(jsonl.text(guessed), encoding="utf-8")
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
        table: Rows
        for name, table in tables.items():
            written.append(folder / "tables" / f"{name}.csv")
            file: IO[str]
            with written[-1].open("w", encoding="utf-8", newline="") as file:
                csv.writer(file, lineterminator="\n").writerows(table)  # as git keeps text
    corpora: dict[tuple[str, str], None] = dict.fromkeys(
        (corpus, version) for corpus, version, _ in records.found
    )
    return written + archive.gather(folder, corpora, guessed)
