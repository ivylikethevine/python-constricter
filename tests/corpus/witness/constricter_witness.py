# SPDX-License-Identifier: MIT
"""Trace a run as `constricter.trace` does, and hold each fixed binding's value to the fix's annotation.

  python -m constricter_witness [--output FILE] [--root DIR] (-m MODULE | SCRIPT) [ARG ...]

Run with this file's directory and this checkout's root on the path (`corpus_suite.traced`, where
`CORPUS_TRACER` names it): a module of its own name, not one of `tests`, which a traced package's
own tests are a package of too. `WITNESS_VARIABLE` names two paths, as JSON: a file of what to
expect, and a directory to write to. The file maps each traced file's path, then the line of a
binding a fix annotates, then the name, to the annotation and the import statements it adds.

As a statement that binds such a name ends, the annotation is evaluated where the statement is (its
function's globals and locals, with the fix's imports), once, and the value is held to it: it's an
instance of the class, or of one of a union's; a subscripted class is held to the class alone, not
to its arguments. Each process writes, for each binding, how many times the value fit, didn't, and
couldn't be told (`FIT`, `DIFFER`, `UNKNOWN`): an annotation that can't be evaluated there, a
protocol no `isinstance` checks, a type variable with no bound, a value that's a test's mock.
"""

import collections.abc
import io
import json
import os
import sys
import types
import typing
from collections.abc import Mapping, Sequence
from pathlib import Path
from types import CodeType, FrameType
from typing import TYPE_CHECKING, Final, Protocol, TypeAlias, TypeVar, cast
from unittest import mock

from constricter import recording, trace

if TYPE_CHECKING:
    from typing_extensions import override
else:
    _F = TypeVar("_F")

    def override(method: _F) -> _F:
        """Mark a method as one of its base's: `typing.override`, where Python has none (3.11).

        Returns:
          It.

        """
        return method


WITNESS_VARIABLE: Final = "CORPUS_WITNESS"
FIT: Final = 0
DIFFER: Final = 1
UNKNOWN: Final = 2
_MOST: Final = 50  # how many times one binding is judged
_SUSPENDS: Final = 0x20 | 0x80 | 0x100 | 0x200  # a generator's or a coroutine's flags: it returns by yielding
# What an annotation's class takes besides its own instances: a number's narrower numbers, and any
# file object for `typing`'s, which none is an instance of.
_TAKEN: Final = {
    float: (int, float),
    complex: (int, float, complex),
    typing.IO: (io.IOBase,),
    typing.TextIO: (io.IOBase,),
    typing.BinaryIO: (io.IOBase,),
}
_UNSET: Final = object()
_ALIASED: Final = "__value__"  # where a `type` statement's alias keeps what it names
_CALLABLE: Final = collections.abc.Callable
# What makes a union: `X | Y`, and `Union[X, Y]` where that's another thing (before Python 3.14).
_UNIONS: Final = frozenset({types.UnionType, cast("object", vars(typing)["Union"])})
# What to expect of a file: by the line, then the name, the annotation and the fix's imports.
_Expected: TypeAlias = dict[str, dict[str, list[str]]]
_Key: TypeAlias = tuple[str, int, str]  # a binding: its file's path, its line and its name
_Judged: TypeAlias = list[str | int | list[int]]  # a binding's key, and its counts


class _Statement(Protocol):  # pylint: disable=too-few-public-methods
    """What a recorder keeps of a statement."""

    @property
    def stores(self) -> list[tuple[int, str]]:
        """The names it binds, each with its line."""
        raise NotImplementedError


class _File(Protocol):  # pylint: disable=too-few-public-methods
    """What a recorder keeps of a file."""

    @property
    def path(self) -> Path:
        """Its path under the root."""
        raise NotImplementedError


class _Function(Protocol):
    """What a recorder keeps of a function."""

    @property
    def file(self) -> _File:
        """Its file."""
        raise NotImplementedError

    @property
    def lines(self) -> Mapping[int, _Statement]:
        """The statement each of its lines is of."""
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


def holds(value: object, hint: object) -> bool | None:
    """Check whether `value` is what the evaluated annotation `hint` says.

    Returns:
      Whether it is; `None` where that can't be told.

    """
    if hint is typing.Any or hint is object:
        return True
    if isinstance(value, mock.NonCallableMock):  # a test's stand-in: it says nothing of the annotation
        return None
    if hint is None or hint is types.NoneType:
        return value is None
    return _held(value, hint, typing.get_origin(hint), typing.get_args(hint))


def _held(value: object, hint: object, origin: object, args: tuple[object, ...]) -> bool | None:
    """Check `value` against `hint`, by what it subscripts (`origin`: `None` for no subscript) with `args`.

    Returns:
      As `holds` does.

    """
    if origin in _UNIONS:
        found: list[bool | None] = [holds(value, each) for each in args]
        return True if True in found else None if None in found else False
    if origin is typing.Annotated or origin is typing.Final or origin is typing.ClassVar:
        return holds(value, args[0]) if args else None
    if origin is typing.Literal:
        return value in args
    if origin is type:
        return isinstance(value, type)
    if origin is _CALLABLE:
        return callable(value)
    return _instance(value, hint if origin is None else origin)


def _stood_for(hint: object) -> object:
    """Find what a type variable, a `type` statement's alias or a `NewType` stands for.

    Returns:
      Its bound (`None`: it has none), what it names, or its supertype; `_UNSET` for anything else.

    """
    if isinstance(hint, typing.TypeVar):
        return cast("object", hint.__bound__)
    if isinstance(hint, typing.NewType):
        return cast("object", hint.__supertype__)
    return cast("object", getattr(hint, _ALIASED, _UNSET))


def _instance(value: object, hint: object) -> bool | None:
    """Check whether `value` is an instance of what `hint` names, itself no subscript or union.

    Returns:
      Whether it is; `None` where that can't be told.

    """
    if _stood_for(hint) is not _UNSET:
        return None if _stood_for(hint) is None else holds(value, _stood_for(hint))
    if typing.is_typeddict(hint):
        return isinstance(value, dict)
    if not isinstance(hint, type):
        return None
    try:
        return isinstance(value, _TAKEN.get(hint, hint))
    except TypeError:  # a protocol that isn't checked at run time
        return None


class Witness(recording.Recorder):
    """A recorder that holds what a statement bound to what a fix says of it, as it notes it."""

    def __init__(self, root: Path) -> None:
        """Record the functions of the files under `root`, and judge the bindings the settings name."""
        super().__init__(root)
        self.expected: dict[str, _Expected]
        self.out: Path | None
        self.expected, self.out = _settings()
        self.hints: dict[_Key, object] = {}  # each binding's annotation, evaluated; `_UNSET`: it can't be
        self.verdicts: dict[_Key, list[int]] = {}  # each binding's counts: fit, differing, unknown

    @override
    def line(self, frame: FrameType) -> None:
        """Judge what the statement `frame` was in bound, as it arrives at another's line; then note it."""
        function: _Function | None
        if (function := self.functions.get(id(frame.f_code))) is not None:
            at: _Statement | None = function.lines.get(frame.f_lineno)
            if self.pending.get(id(frame), (None, at))[1] is not at:
                self._judge(frame, function)
        super().line(frame)

    @override
    def left(self, frame: FrameType) -> None:
        """Judge what `frame`'s last statement bound, as its function returns; then note it."""
        function: _Function | None = self.functions.get(id(frame.f_code))
        if function is not None and not frame.f_code.co_flags & _SUSPENDS:
            self._judge(frame, function)
        super().left(frame)

    def _judge(self, frame: FrameType, function: _Function) -> None:
        # Hold each name the pending statement bound to its annotation, where one's expected.
        path: str = function.file.path.as_posix()
        expected: _Expected | None = self.expected.get(path)
        pending: tuple[CodeType | None, _Statement] | None = self.pending.get(id(frame))
        if expected is None or pending is None or pending[0] is not frame.f_code:
            return
        line: int
        name: str
        for line, name in pending[1].stores:
            said: list[str] | None = expected.get(str(line), {}).get(name)
            key: _Key = (path, line, name)
            if said is None or name not in frame.f_locals or sum(self.verdicts.get(key, ())) >= _MOST:
                continue
            if key not in self.hints:
                self.hints[key] = _evaluated(said, frame)
            fits: bool | None = _fits(cast("object", frame.f_locals[name]), self.hints[key])
            self.verdicts.setdefault(key, [0, 0, 0])[
                UNKNOWN if fits is None else FIT if fits else DIFFER
            ] += 1

    @override
    def found(self) -> recording.Found:
        """Gather what was recorded, having written this process's verdicts where they're read.

        Returns:
          The trace.

        """
        if self.out is not None:
            self.out.mkdir(parents=True, exist_ok=True)
            judged: list[_Judged] = [
                [path, line, name, counts] for (path, line, name), counts in self.verdicts.items()
            ]
            _ = (self.out / f"{os.getpid()}.json").write_text(json.dumps(judged), encoding="utf-8")
        return super().found()


def _fits(value: object, hint: object) -> bool | None:
    """Hold `value` to `hint`, whatever its class raises of being asked: nothing of it reaches the run.

    Returns:
      As `holds` does; `None` for a `hint` that couldn't be evaluated.

    """
    try:
        return None if hint is _UNSET else holds(value, hint)
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        return None


def _evaluated(said: list[str], frame: FrameType) -> object:
    """Evaluate a fix's annotation where its statement is: `said` is it, then the imports it adds.

    Returns:
      What it names, or `_UNSET` where it can't be evaluated there.

    """
    try:
        return _read(said[0], _imported(dict(frame.f_globals), said[1:]), dict(frame.f_locals))
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        return _UNSET


def _imported(scope: dict[str, object], imports: Sequence[str]) -> dict[str, object]:
    """Run `imports` among `scope`'s names, a copy of a module's.

    Returns:
      `scope`.

    """
    statement: str
    for statement in imports:
        exec(statement, scope)  # ruff: ignore[exec-builtin]  # pylint: disable=exec-used
    return scope


def _read(text: object, scope: dict[str, object], local: dict[str, object]) -> object:
    """Evaluate `text`, an annotation, among `scope`'s and `local`'s names; a quoted one's text too.

    Returns:
      What it names; `text` itself if it isn't text.

    """
    if not isinstance(text, str):
        return text
    return _read(_named(text, scope, local), scope, local)


def _named(text: str, scope: dict[str, object], local: dict[str, object]) -> object:
    # What the expression `text` gives there.
    return cast(
        "object",
        eval(text, scope, local),  # ruff: ignore[suspicious-eval-usage]  # pylint: disable=eval-used
    )


# Every recorder `constricter.trace` makes in a process that has this module is a witness: the
# run's own, and each pytest process it starts, which loads this module as the plugin that records
# it, in `constricter.trace`'s place: pytest takes no plugin a process has already imported.
trace.__dict__["Recorder"] = Witness
trace.__dict__["_PLUGIN"] = Path(__file__).stem
pytest_configure: Final = trace.pytest_configure
pytest_unconfigure: Final = trace.pytest_unconfigure


if __name__ == "__main__":
    sys.exit(trace.main())
