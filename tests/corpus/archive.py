"""A run's folder as later runs read it: its records and its listings, one file each.

As a run goes, each step keeps its record under `records/` (`pipeline.Store`), and some a listing
beside it, a corpus's. Once it ends, its report gathers the records into `report.json` and each
listing into one file of the whole run, a line a binding or a test with its corpus and version
(`gather`): what the folder commits. A folder with no report, a run stopped or under way, is read
from `records/`.
"""

import contextlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Final, TypeAlias, cast

from tests.corpus.run_config import scrubbed

Record: TypeAlias = dict[str, object]
Kept: TypeAlias = dict[tuple[str, str, str], Record]  # by a corpus's directory, a version and a step
_Steps: TypeAlias = dict[str, Record]  # a version's records, by step
_Nested: TypeAlias = dict[str, dict[str, _Steps]]  # a report's, by corpus and version
RECORDS: Final = "records"
REPORT: Final = "report.json"
# The listings a run's folder keeps, each a step's and its suffix: what the witness judged and
# what the trace saw of each binding, and the released tests by name.
LISTINGS: Final = (
    ("traced", ".verdicts.jsonl"),
    ("traced", ".seen.jsonl"),
    ("tests-released", ".tests.jsonl"),
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


def gather(folder: Path, corpora: Iterable[tuple[str, str]]) -> list[Path]:
    """Write each listing of the run in `folder` as one file of the whole run.

    `corpora`: each corpus's name and version, in the run's order. A line keeps its corpus and its
    version, first.

    Returns:
      The files written: none for a listing no corpus has.

    """
    written: list[Path] = []
    step: str
    suffix: str
    for step, suffix in LISTINGS:
        lines: list[str] = []
        corpus: str
        version: str
        for corpus, version in corpora:
            path: Path = folder / RECORDS / corpus.replace(" ", "-") / version / f"{step}{suffix}"
            text: str = path.read_text(encoding="utf-8") if path.is_file() else ""
            lines += [
                json.dumps({"corpus": corpus, "constricter": version} | cast("Record", json.loads(line)))
                for line in text.splitlines()
            ]
        if lines:
            written.append(folder / f"{step}{suffix}")
            _ = written[-1].write_text(scrubbed("".join(f"{line}\n" for line in lines)), encoding="utf-8")
    return written
