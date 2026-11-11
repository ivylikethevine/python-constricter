"""Trace a run as `constricter.trace` does, and hold each fixed binding's value to the fix's annotation.

  python -m constricter_witness [--output FILE] [--root DIR] (-m MODULE | SCRIPT) [ARG ...]

Run with this file's directory and this checkout's root on the path (`corpus_suite.traced`, where
`CORPUS_TRACER` names it): a module of its own name, not one of `tests`, which a traced package's
own tests are a package of too. `WITNESS_VARIABLE` names two paths, as JSON: a file of what to
expect, and a directory to write to. The file maps each traced file's path, then the line of a
binding a fix annotates, then the name, to each annotation a fix gives it (the guesses' fix's, a
checker's hints'), each with the import statements its fix adds.

As a statement that binds such a name ends, each annotation is evaluated where the statement is (its
function's globals and locals, with the fix's imports), once, and the value is held to it as
`constricter.witness.holds` holds one: it's an instance of the class, or of one of a union's. A
builtin container is held to its annotation's
arguments too, by its first elements (`_elements`); any other subscripted class to the class alone.
Each process writes, for each binding and annotation, how many times the value fit, didn't, and
couldn't be told (`FIT`, `DIFFER`, `UNKNOWN`): an annotation that can't be evaluated there, a protocol no
`isinstance`
checks, a type variable with no bound, a value that's a test's mock, a `SimpleNamespace`, an
in-memory file where `io`'s or `typing`'s file class is named (`_in_memory`) or of a class a test
module defines (`_stand_in`; a package's `pytest` plugin module is one), and an annotation that names
such a class: a module's name a test has patched (`humanize.datetime = MockDateTime`), as the
annotation was evaluated. `typing`'s file classes, which nothing is an instance of, take any value
that reads, writes and closes. A class
made again, by a function at each call or by a module imported anew, is the annotation's class where
its module and its qualified name are (`_redefined`).
"""

import json
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import CodeType, FrameType
from typing import Final, Protocol, TypeAlias, cast

from constricter import recording, trace
from constricter.overrides import override
from constricter.witness import DIFFER, FIT, UNKNOWN, UNSET, fits, kind_of, module_of, patched, read

WITNESS_VARIABLE: Final = "CORPUS_WITNESS"
_MOST: Final = 50  # how many times one binding is judged against one annotation
_TOLD: Final = 3  # how many of a binding's differing values are told of, the first
# What to expect of a file: by the line, then the name, each annotation with its fix's imports.
_Expected: TypeAlias = dict[str, dict[str, list[list[str]]]]
_Key: TypeAlias = tuple[str, int, str, str]  # a binding and an annotation: its file's path, line, name, text
_Judged: TypeAlias = list[str | int | list[int] | list[str]]  # a binding's key, its counts, what differed


class _Statement(Protocol):  # pylint: disable=too-few-public-methods
    """What a recorder keeps of a statement."""

    @property
    def stores(self) -> list[tuple[int, str]]:
        """The names it binds, each with its line."""
        raise NotImplementedError


def _settings() -> tuple[dict[str, _Expected], Path | None]:
    """Read `WITNESS_VARIABLE`.

    Returns:
      What to expect of each file, and where to write; nothing and `None` where it isn't set.

    """
    told: list[str]
    if not (told := cast("list[str]", json.loads(os.environ.get(WITNESS_VARIABLE, "[]")))):
        return {}, None
    expected: dict[str, _Expected] = cast(
        "dict[str, _Expected]",
        json.loads(Path(told[0]).read_text(encoding="utf-8")),
    )
    return expected, Path(told[1])


class Witness(recording.Recorder):
    """A recorder that holds what a statement bound to what a fix says of it, as it notes it."""

    def __init__(self, root: Path) -> None:
        """Record the functions of the files under `root`, and judge the bindings the settings name."""
        super().__init__(root)
        self.expected: dict[str, _Expected]
        self.out: Path | None
        self.expected, self.out = _settings()
        self.hints: dict[_Key, object] = {}  # each annotation, evaluated; `UNSET`: it can't be
        self.verdicts: dict[_Key, list[int]] = {}  # each key's counts: fit, differing, unknown
        self.differed: dict[_Key, list[str]] = {}  # the first values that differed: their type, the hint's
        # What's expected of each function's file (see `_told`), by the function's id, kept with it.
        self.told: dict[int, tuple[recording.Function, tuple[str, _Expected] | None]] = {}

    @override
    def ended(self, frame: FrameType, function: recording.Function) -> None:
        """Judge what the statement `frame` was in bound, as it ends; then note it."""
        told: tuple[str, _Expected] | None
        if (told := self._told(function)) is not None:
            self._judge(frame, *told)
        super().ended(frame, function)

    def _told(self, function: recording.Function) -> tuple[str, _Expected] | None:
        """Find what the settings expect of a function's file, read once a function.

        Returns:
          The file's path and its bindings' annotations; `None` for a file with none.

        """
        if id(function) not in self.told:
            path: str = function.file.path.as_posix()
            expected: _Expected | None = self.expected.get(path)
            self.told[id(function)] = (function, None if expected is None else (path, expected))
        return self.told[id(function)][1]

    def _judge(self, frame: FrameType, path: str, expected: _Expected) -> None:
        # Hold each name the pending statement bound to each annotation expected of it.
        pending: tuple[CodeType | None, _Statement] | None = self.pending.get(id(frame))
        if pending is None or pending[0] is not frame.f_code:
            return
        line: int
        name: str
        for line, name in pending[1].stores:
            said: list[str]
            for said in expected.get(str(line), {}).get(name, []):
                key: _Key = (path, line, name, said[0])
                if sum(self.verdicts.get(key, ())) < _MOST:
                    self._weighed(frame, key, said, frame.f_locals)

    def _weighed(self, frame: FrameType, key: _Key, said: list[str], bound: Mapping[str, object]) -> None:
        # Hold what a name is bound to in `frame` to its annotation `said`, and count the verdict.
        if key[2] in bound:
            if key not in self.hints:
                self.hints[key] = _evaluated(said, frame)
            fit: bool | None = fits(bound[key[2]], self.hints[key])
            if patched(self.hints[key], module_of(frame)):  # evaluated again once the test's done
                fit = None
                del self.hints[key]
            self.verdicts.setdefault(key, [0, 0, 0])[UNKNOWN if fit is None else FIT if fit else DIFFER] += 1
            told: list[str] = self.differed.setdefault(key, [])
            if fit is False and len(told) < _TOLD:  # what to read a verdict by: the value's, the hint's
                told.append(f"{kind_of(bound[key[2]])} against {self.hints.get(key, UNSET)!r}")

    @override
    def found(self) -> recording.Found:
        """Gather what was recorded, having written this process's verdicts where they're read.

        Returns:
          The trace.

        """
        if self.out is not None:
            self.out.mkdir(parents=True, exist_ok=True)
            judged: list[_Judged] = [
                [*key, counts, self.differed.get(key, [])] for key, counts in self.verdicts.items()
            ]
            _ = (self.out / f"{os.getpid()}.json").write_text(json.dumps(judged), encoding="utf-8")
        return super().found()


def _evaluated(said: list[str], frame: FrameType) -> object:
    """Evaluate a fix's annotation where its statement is: `said` is it, then the imports it adds.

    Returns:
      What it names, or `UNSET` where it can't be evaluated there.

    """
    try:
        return read(said[0], _imported(dict(frame.f_globals), said[1:]), dict(frame.f_locals))
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        return UNSET


def _imported(scope: dict[str, object], imports: Sequence[str]) -> dict[str, object]:
    """Run `imports` among `scope`'s names, a copy of a module's.

    Returns:
      `scope`.

    """
    statement: str
    for statement in imports:
        exec(statement, scope)  # ruff: ignore[exec-builtin]  # pylint: disable=exec-used
    return scope


# Every recorder `constricter.trace` makes in a process that has this module is a witness: the
# run's own, and each pytest process it starts, which loads this module as the plugin that records
# it, in `constricter.trace`'s place: pytest takes no plugin a process has already imported.
trace.__dict__["Recorder"] = Witness
trace.__dict__["_PLUGIN"] = Path(__file__).stem
pytest_configure: Final = trace.pytest_configure
pytest_unconfigure: Final = trace.pytest_unconfigure


if __name__ == "__main__":
    sys.exit(trace.main())
