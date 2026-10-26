"""What a suite's traced tests say of its fixes: whether each fixed binding's value was what the fix says.

The tests run traced by `tests/corpus/witness/constricter_witness.py`, which is told each fix (the
annotation, where, and the imports it adds) and holds the value to the annotation as its statement
ends, where it ran: an instance of the class, or of one of a union's, a subscripted class held to
the class alone. `expected` writes what it's told, `verdicts` reads what its processes wrote, and
`Verdict` is one binding's: how many times its value fit, didn't, and couldn't be told (an
annotation that can't be evaluated there, a protocol nothing checks at run time).

`seen` reads the trace itself, for the files that are still what was traced: the types each
binding held, as the trace spells them. They say what a value that didn't fit was.
"""

import hashlib
import json
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final, NamedTuple, Protocol, TypeAlias, cast

if TYPE_CHECKING:
    from tests.corpus.catalog import Suite
    from tests.corpus.pipeline import Job

_Names: TypeAlias = dict[str, tuple[str, ...]]  # a line's bindings: each name's types held
# Each traced file's bindings: by its path in the checkout, then the line.
Seen: TypeAlias = Mapping[str, Mapping[int, _Names]]
_Lines: TypeAlias = dict[str, dict[str, list[str]]]  # a file's bindings, as a trace file writes them
_File: TypeAlias = dict[str, str | _Lines]  # a traced file: its `path` and its `bindings`
_Key: TypeAlias = tuple[str, int, str]  # a binding: its file's path, its line and its name
# A binding as a process writes it: its key, its counts, and the first values that differed.
_Written: TypeAlias = tuple[str, int, str, list[int], list[str]]
_TOLD: Final = 3  # how many of a binding's differing values a verdict tells of, the first
_Told: TypeAlias = dict[str, dict[str, list[str]]]  # what's expected of a file: by line, then name

WITNESS: Final = Path(__file__).parent / "witness" / "constricter_witness.py"
# What `corpus_suite.TRACER_VARIABLE` is to be, for a run the witness traces: its name, and where it is.
TRACER: Final = os.pathsep.join((WITNESS.stem, str(WITNESS.parent)))
WITNESS_VARIABLE: Final = (
    "CORPUS_WITNESS"  # what the witness reads: where its expectations are, and where to write
)
_EXPECTED: Final = ".venv/corpus-suite-expected.json"  # out of a checkout's source's way, as its trace is
_VERDICTS: Final = ".venv/corpus-suite-verdicts"
SEEN: Final = ".seen.jsonl"  # beside the traced step's record: the types the trace saw, a binding a line
_TRACED: Final = "traced"  # the step (`pipeline.TRACED`)


class Fixed(Protocol):
    """A fix, as `corpus_suite.Fix` has one."""

    @property
    def line(self) -> int:
        """The line of the binding it annotates, as released."""
        raise NotImplementedError

    @property
    def name(self) -> str:
        """The name bound."""
        raise NotImplementedError

    @property
    def annotation(self) -> str:
        """What it writes."""
        raise NotImplementedError

    @property
    def imports(self) -> tuple[str, ...]:
        """The import statements it adds."""
        raise NotImplementedError


class Verdict(NamedTuple):
    """How a binding's values stood to its fix's annotation, each time a traced test bound it."""

    fit: int = 0
    differ: int = 0
    unknown: int = 0
    differed: tuple[str, ...] = ()  # the first values that differed, each its class and the annotation's

    @property
    def held(self) -> bool:
        """Whether every value that could be told fit, and one could."""
        return bool(self.fit) and not self.differ

    @property
    def told(self) -> bool:
        """Whether any value could be told."""
        return bool(self.fit or self.differ)


Verdicts: TypeAlias = Mapping[str, Mapping[int, Mapping[str, Verdict]]]  # by path, line, then name
_Judged: TypeAlias = dict[int, dict[str, Verdict]]  # a file's, as they're gathered


def expected(root: Path, fixes: Mapping[str, Sequence[Fixed]]) -> str:
    """Write what the witness is to expect of the checkout at `root`: each of `fixes`, by its file.

    And empty the directory its processes write to.

    Returns:
      What `WITNESS_VARIABLE` is to be, for a traced run of the checkout.

    """
    told: dict[str, _Told] = {}
    path: str
    listed: Sequence[Fixed]
    for path, listed in fixes.items():
        fix: Fixed
        for fix in listed:
            told.setdefault(path, {}).setdefault(str(fix.line), {})[fix.name] = [fix.annotation, *fix.imports]
    _ = (root / _EXPECTED).write_text(json.dumps(told), encoding="utf-8")
    out: Path = root / _VERDICTS
    out.mkdir(exist_ok=True)
    stale: Path
    for stale in out.glob("*.json"):
        stale.unlink()
    return json.dumps([str(root / _EXPECTED), str(out)])


def verdicts(root: Path) -> Verdicts:
    """Read what the witness's processes wrote of the checkout at `root`, their counts added up.

    Returns:
      Each judged binding's verdict.

    """
    counts: dict[_Key, list[int]] = {}
    told: dict[_Key, list[str]] = {}
    part: Path
    for part in sorted((root / _VERDICTS).glob("*.json")):
        written: _Written
        for written in cast("list[_Written]", json.loads(part.read_text(encoding="utf-8"))):
            key: _Key = (written[0], written[1], written[2])
            had: list[int] = counts.setdefault(key, [0, 0, 0])
            counts[key] = [one + other for one, other in zip(had, written[3], strict=True)]
            told.setdefault(key, []).extend(written[4])
    found: dict[str, _Judged] = {}
    path: str
    line: int
    name: str
    each: list[int]
    for (path, line, name), each in counts.items():
        differed: tuple[str, ...] = tuple(dict.fromkeys(told.get((path, line, name), ())))[:_TOLD]
        found.setdefault(path, {}).setdefault(line, {})[name] = Verdict(each[0], each[1], each[2], differed)
    return found


def verdict(judged: Verdicts, path: str, line: int, name: str) -> Verdict:
    """Find the verdict on the binding of `name` on `line` of `path`.

    Returns:
      It; one of no values where no traced test reached the binding.

    """
    return judged.get(path, {}).get(line, {}).get(name, Verdict())


def seen(root: Path, trace: str) -> Seen:
    """Read the checkout's tests' trace: the file `trace` under `root`.

    Returns:
      Each file's bindings, for the files whose text is what was traced; none where there's no trace.

    """
    path: Path = root / trace
    if not path.exists():
        return {}
    found: dict[str, dict[int, _Names]] = {}
    files: dict[str, _File] = cast("dict[str, _File]", json.loads(path.read_text(encoding="utf-8"))["files"])
    digest: str
    each: _File
    for digest, each in files.items():
        name: str = cast("str", each["path"])
        file: Path = root / name
        if file.exists() and hashlib.sha256(file.read_bytes()).hexdigest() == digest:
            found[name] = {
                int(line): {bound: tuple(types) for bound, types in names.items()}
                for line, names in cast("_Lines", each["bindings"]).items()
            }
    return found


def held(traced: Seen, path: str, line: int, name: str) -> tuple[str, ...]:
    """Find the types the binding of `name` on `line` of `path` held.

    Returns:
      Them; none where no traced test reached it.

    """
    return traced.get(path, {}).get(line, {}).get(name, ())


def kept(job: "Job", root: Path, trace: str) -> Seen:
    """Read the checkout's tests' trace (`seen`), and keep what each of the package's bindings held.

    A line each (`traced.seen.jsonl`), by the path the census gives the binding, under the suite's
    `source`: the report holds each binding with no fix to what the run saw (`report_tables`).

    Returns:
      The trace's bindings, as `seen` reads them.

    """
    found: Seen = seen(root, trace)
    prefix: str = f"{cast('Suite', job.tree.suite).source.rstrip('/')}/"
    lines: list[str] = [
        json.dumps({"path": file.removeprefix(prefix), "line": line, "name": name, "seen": list(types)})
        for file, traced in found.items()
        if file.startswith(prefix)
        for line, names in traced.items()
        for name, types in names.items()
    ]
    written: Path = job.store.path(job.tree.name, job.recorded, _TRACED, SEEN)
    _ = written.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
    return found
