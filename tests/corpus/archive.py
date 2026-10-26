"""A run's folder as later runs read it: its report and its listings, a file each.

As a run goes, each step keeps its record under `records/` (`pipeline.Store`), and some a listing
beside it, a corpus's. Once it ends, its report gathers the records, the run's facts and its tables
into `report.json`, and every listing into `listings.jsonl.gz`, a line a guess, a binding or a test
with the listing it's from, its corpus and version (`gather`): the two files the folder commits.
A folder with no report, a run stopped or under way, is read from `records/`.
"""

import contextlib
import gzip
import json
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Final, TypeAlias, cast

from tests.corpus.run_config import REPORT, scrubbed

Record: TypeAlias = dict[str, object]
Kept: TypeAlias = dict[tuple[str, str, str], Record]  # by a corpus's directory, a version and a step
_Steps: TypeAlias = dict[str, Record]  # a version's records, by step
_Nested: TypeAlias = dict[str, dict[str, _Steps]]  # a report's, by corpus and version
RECORDS: Final = "records"
LISTED: Final = "listings.jsonl.gz"  # compressed: a large suite's tests by name alone run past 100 MB
LISTING: Final = "listing"  # in a line of it: the listing it's from
GUESSES: Final = "guesses"  # the listing of every fix-unsafe fix with what blames it or bears it out
# The listings each corpus keeps, each named, with the step's it is and its suffix: what the witness
# judged and what the trace saw of each binding, and the released tests by name.
LISTINGS: Final = (
    ("verdicts", "traced", ".verdicts.jsonl"),
    ("seen", "traced", ".seen.jsonl"),
    ("released-tests", "tests-released", ".tests.jsonl"),
)


def runs(output: Path) -> list[Path]:
    """List the run folders under `output`: those with a report or records.

    Returns:
      Them, in no order.

    """
    found: Iterable[Path] = output.iterdir() if output.is_dir() else ()
    return [each for each in found if (each / REPORT).is_file() or (each / RECORDS).is_dir()]


def kept(folder: Path) -> Kept:
    """Read every step's record the run in `folder` keeps: its report's, or else its records'.

    Returns:
      Each, by its corpus's directory (its name, a space a hyphen), its version and its step.

    """
    report: Path = folder / REPORT
    if report.is_file():
        nested: _Nested = cast("_Nested", json.loads(report.read_text(encoding="utf-8"))[RECORDS])
        return {
            (corpus.replace(" ", "-"), version, step): record
            for corpus, versions in nested.items()
            for version, steps in versions.items()
            for step, record in steps.items()
        }
    found: Kept = {}
    path: Path
    for path in sorted((folder / RECORDS).glob("*/*/*.json")):
        key: tuple[str, str, str] = (path.parts[-3], path.parts[-2], path.stem)
        with contextlib.suppress(OSError, ValueError):  # a record a stopped step left half written
            found[key] = cast("Record", json.loads(path.read_text("utf-8")))
    return found


def listed(folder: Path, name: str) -> list[Record]:
    """Read one listing of the run in `folder`, from its `listings.jsonl.gz`.

    Returns:
      Its lines, the `listing` field left out; none for a run with no such file.

    """
    path: Path = folder / LISTED
    text: str = gzip.decompress(path.read_bytes()).decode("utf-8") if path.is_file() else ""
    lines: list[str] = text.splitlines()
    rows: list[Record] = [cast("Record", json.loads(line)) for line in lines]
    return [
        {key: each for key, each in row.items() if key != LISTING} for row in rows if row[LISTING] == name
    ]


def gather(folder: Path, corpora: Iterable[tuple[str, str]], guessed: Sequence[Record] = ()) -> list[Path]:
    """Write every listing of the run in `folder` into its `listings.jsonl.gz`: `guessed`, then each corpus's.

    `corpora`: each corpus's name and version, in the run's order. A line keeps the listing it's from,
    then its corpus and version.

    Returns:
      The file written: none for a run with no listing.

    """
    lines: list[str] = [json.dumps({LISTING: GUESSES} | dict(row)) for row in guessed]
    pairs: list[tuple[str, str]] = list(corpora)
    name: str
    step: str
    suffix: str
    for name, step, suffix in LISTINGS:
        corpus: str
        version: str
        for corpus, version in pairs:
            path: Path = folder / RECORDS / corpus.replace(" ", "-") / version / f"{step}{suffix}"
            text: str = path.read_text(encoding="utf-8") if path.is_file() else ""
            head: Record = {LISTING: name, "corpus": corpus, "constricter": version}
            lines += [json.dumps(head | cast("Record", json.loads(line))) for line in text.splitlines()]
    if not lines:
        return []
    packed: bytes = scrubbed("".join(f"{line}\n" for line in lines)).encode("utf-8")
    _ = (folder / LISTED).write_bytes(gzip.compress(packed, compresslevel=9, mtime=0))  # the same bytes
    return [folder / LISTED]
