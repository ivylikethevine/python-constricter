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
instance of the class, or of one of a union's. A builtin container is held to its annotation's
arguments too, by its first elements (`_elements`); any other subscripted class to the class alone.
Each process writes, for each binding, how many times the value fit, didn't, and couldn't be told
(`FIT`, `DIFFER`, `UNKNOWN`): an annotation that can't be evaluated there, a protocol no `isinstance`
checks, a type variable with no bound, a value that's a test's mock, a `SimpleNamespace`, an
in-memory file where `io`'s or `typing`'s file class is named (`_in_memory`) or of a class a test
module defines (`_stand_in`; a package's `pytest` plugin module is one), and an annotation that names
such a class: a module's name a test has patched (`humanize.datetime = MockDateTime`), as the
annotation was evaluated. `typing`'s file classes, which nothing is an instance of, take any value
that reads, writes and closes. A class
made again, by a function at each call or by a module imported anew, is the annotation's class where
its module and its qualified name are (`_redefined`).
"""

import collections
import collections.abc
import io
import itertools
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
# What an annotation's class takes besides its own instances: a number's narrower numbers.
_TAKEN: Final = {
    float: (int, float),
    complex: (int, float, complex),
}
# What `typing`'s file classes, which nothing is an instance of, take: a value that reads, writes
# and closes (`tempfile.NamedTemporaryFile`'s wrapper, which is no `io.IOBase`); see `_file_class`.
_FILE_METHODS: Final = ("read", "write", "close")
# An in-memory file: a test's stand-in for the file a fix's annotation names (`open`'s
# `TextIOWrapper`, `typing.IO`).
_IN_MEMORY: Final = (io.StringIO, io.BytesIO)
_FILE_MODULES: Final = frozenset({"io", "_io", "typing"})
_UNSET: Final = object()
_FIRST: Final = 100  # how many of an ordered container's elements are held to its annotation's arguments
# The containers read without running anything of the value's own: these classes themselves, no subclass.
_SETS: Final = (set, frozenset)
_SEQUENCES: Final = (list, collections.deque)
_MAPPINGS: Final = (dict, collections.defaultdict, collections.OrderedDict)
_TUPLES: Final = (tuple,)
_PAIR: Final = 2  # a mapping's arguments: its keys' type and its values'
_ALIASED: Final = "__value__"  # where a `type` statement's alias keeps what it names
# A test module's name, by any of its parts: pytest's and unittest's ways of naming them, and a
# package's pytest plugin (`pdm.pytest`), whose classes stand in for the package's own.
_TESTS: Final = frozenset({"test", "tests", "testing", "conftest", "pytest"})
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
    found_class: bool | None = _instance(value, hint if origin is None else origin)
    return _elements(value, origin, args) if found_class and origin is not None else found_class


def _elements(value: object, origin: object, args: tuple[object, ...]) -> bool | None:
    """Check a builtin container's elements against its annotation's arguments, `value` being of its class.

    Its first `_FIRST`, in its order; a set's every one, whose order is no two runs'. A tuple's
    parts one by one, where the annotation has them so. Not another class's (a subclass may run its
    own code as it's read), nor one whose arguments aren't its elements' types.

    Returns:
      Whether they all are; `None` where one can't be told and none isn't, `True` for a container
      this doesn't read.

    """
    found: list[bool | None]
    if (
        type(value) in _TUPLES and origin is tuple and args[-1:] != (Ellipsis,)
    ):  # `tuple[()]` has no arguments
        if len(cast("tuple[object, ...]", value)) != len(args):
            return False
        found = list(itertools.starmap(holds, zip(cast("tuple[object, ...]", value), args, strict=True)))
    elif type(value) in _MAPPINGS and len(args) == _PAIR:
        found = [
            holds(each, arg)
            for pair in itertools.islice(cast("dict[object, object]", value).items(), _FIRST)
            for each, arg in zip(pair, args, strict=True)
        ]
    elif (
        (type(value) in _SEQUENCES or type(value) in _SETS or type(value) in _TUPLES)
        and args
        and args[1:] in {(), (Ellipsis,)}
    ):
        most: int = len(cast("collections.abc.Sized", value)) if type(value) in _SETS else _FIRST
        found = [
            holds(each, args[0])
            for each in itertools.islice(cast("collections.abc.Iterable[object]", value), most)
        ]
    else:
        return True
    return False if False in found else None if None in found else True


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
    if _file_class(hint):
        return all(hasattr(value, name) for name in _FILE_METHODS)
    if not isinstance(hint, type):
        return None
    try:
        fit: bool = isinstance(value, _TAKEN.get(hint, hint)) or _redefined(type(value), hint)
    except TypeError:  # a protocol that isn't checked at run time
        return None
    return True if fit else None if _stand_in(type(value)) or _in_memory(type(value), hint) else False


def _redefined(kind: type, hint: type) -> bool:
    """Check whether `kind` or a base of it is `hint` made again: by a function, or a module imported anew.

    Returns:
      Whether one has `hint`'s module and qualified name.

    """
    return any(
        (base.__module__, base.__qualname__) == (hint.__module__, hint.__qualname__) for base in kind.__mro__
    )


def _stand_in(kind: type) -> bool:
    """Check whether `kind` is a test's stand-in, which says nothing of the annotation.

    Returns:
      Whether it's `SimpleNamespace`, or a test module's (`_testing`).

    """
    return kind is types.SimpleNamespace or _testing(kind.__module__)


def _file_class(hint: object) -> bool:
    """Check whether `hint` is one of `typing`'s file classes: `IO`, `TextIO` or `BinaryIO`.

    Returns:
      Whether it is.

    """
    return hint is typing.IO or hint is typing.TextIO or hint is typing.BinaryIO


def _in_memory(kind: type, hint: type) -> bool:
    """Check whether `kind` is an in-memory file held to a file class: a test's stand-in for the file.

    Returns:
      Whether it's a `StringIO` or `BytesIO` and `hint` is `io`'s or `typing`'s.

    """
    return issubclass(kind, _IN_MEMORY) and hint.__module__ in _FILE_MODULES


def _testing(module: str) -> bool:
    # Whether a part of a module's name is a test package's, or a test file's (`test_x`, `x_test`).
    return any(
        part in _TESTS or part.startswith("test_") or part.endswith("_test") for part in module.split(".")
    )


def patched(hint: object, module: str) -> bool:
    """Check whether an annotation in `module` names a test's class: a name of the module's a test patched.

    Returns:
      Whether it does, `module` being no test module, whose own annotations name its classes.

    """
    return isinstance(hint, type) and _testing(hint.__module__) and not _testing(module)


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
        # Hold each name the pending statement bound to its annotation, where one's expected.
        pending: tuple[CodeType | None, _Statement] | None = self.pending.get(id(frame))
        if pending is None or pending[0] is not frame.f_code:
            return
        line: int
        name: str
        for line, name in pending[1].stores:
            said: list[str] | None = expected.get(str(line), {}).get(name)
            key: _Key = (path, line, name)
            if said is not None and sum(self.verdicts.get(key, ())) < _MOST:
                self._weighed(frame, key, said, frame.f_locals)

    def _weighed(self, frame: FrameType, key: _Key, said: list[str], bound: Mapping[str, object]) -> None:
        # Hold what a name is bound to in `frame` to its annotation `said`, and count the verdict.
        if key[2] in bound:
            if key not in self.hints:
                self.hints[key] = _evaluated(said, frame)
            fits: bool | None = _fits(bound[key[2]], self.hints[key])
            if patched(self.hints[key], _module(frame)):  # evaluated again once the test's done
                fits = None
                del self.hints[key]
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


def _module(frame: FrameType) -> str:
    # The name of the module `frame` runs in.
    return str(cast("object", frame.f_globals.get("__name__", "")))


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
