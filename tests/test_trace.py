# SPDX-License-Identifier: MIT
"""`python -m constricter.trace`: the types a run binds its functions' locals to, recorded."""

import collections
import fractions
import hashlib
import importlib.util
import inspect
import io
import json
import os
import pathlib
import runpy
import subprocess  # runs a traced pytest, whose workers are processes of its own
import sys
import threading
from functools import partial
from pathlib import Path
from types import CodeType, FrameType
from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast
from unittest import mock

import pytest

from constricter import recording, trace

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from importlib.machinery import ModuleSpec
    from types import ModuleType

# A script whose functions call a hook where the interpreter would report to a recorder: `tell` on a
# line it arrives at, `leave` as it returns, `fail` before it raises.
_STEPS: Final = """
def same(function):
    return function


class Odd:
    __module__ = None


@same
def bound(tell, leave, value):
    held = (tell(), value)[1]
    held = (tell(), [held])[1]
    other = (
        tell(),
        tell(),
        1.5,
    )[2]
    if other: flag = bool(tell())
    leave()


def spun(tell, leave, values):
    while values:
        each = (tell(), values.pop())[1]
        tell()
    for item in (tell(), "ab")[1]: last = item
    leave()


def failed(tell, leave, fail):
    first = (tell(), 1)[1]
    try:
        first = (tell(), fail(), int("x"))[2]
    except ValueError:
        tell()
    leave()


def suspended(tell, leave):
    held = (tell(), 1)[1]
    leave()
    yield held


def scoped(tell, leave, values):
    def inner():
        deep = 1
        return deep

    doubled = (tell(), [each * 2 for each in values])[1]
    leave()
    return inner


def begun(tell):
    began = tell()
    return began


def shared(tell, leave):
    global elsewhere
    elsewhere = (tell(), 1)[1]
    leave()


def nameless(tell):
    return tell(), (lambda: tell())()
"""
# A module of classes, with what's made of each.
_SHAPES: Final = """
from typing import Generic, TypeVar

K = TypeVar("K")
T = TypeVar("T")


class Outer:
    class Inner:
        pass

    class Renamed:
        pass

    Renamed.__qualname__ = "Outer.Other"


class Stack(list[T]):
    pass


class Table(dict[K, T]):
    pass


class Names(list[str]):
    pass


class Keyed(dict[str, T]):
    pass


class Pair(Generic[K, T], list[T]):
    pass


class Box(Generic[T]):
    pass


def local():
    class Local(list[T]):
        pass

    return Local([1])


ASKED = []


class Lazy:
    __slots__ = ()

    def __getattr__(self, name):
        ASKED.append(name)
        raise RuntimeError(name)

    @property
    def __class__(self):
        ASKED.append("__class__")
        return type


class Slotted:
    __slots__ = ()


MADE = {
    "nested": Outer.Inner(),
    "nested class": Outer.Inner,
    "stack": Stack([1]),
    "table": Table({"a": 1.5}),
    "box of int": Box[int](),
    "box": Box(),
    "box of lists": Box[list[int]](),
    "names": Names(["a"]),
    "keyed": Keyed({"a": 1}),
    "pair": Pair([1]),
    "local": local(),
    "renamed": Outer.Renamed(),
    "empty": Stack(),
    "lazy": Lazy(),
    "slotted": Slotted(),
}
"""
_MODULE: Final = """
import sys


class Local:
    pass


def run(argv):
    made = Local()
    count = len(argv)
    for arg in argv:
        size = len(arg)
    try:
        count = int(argv[0])
    except ValueError:
        pass
    count = str(
        count,
    )
    return made


if __name__ == "__main__":
    run(sys.argv)
    raise SystemExit(3)
"""
# A script that tells what a traced run's environment says, and writes as two of its pytest processes
# would: one killed as it wrote, and one that recorded a file `w.py`.
_CHILD: Final = """
import json
import os
from pathlib import Path

told = json.loads(os.environ["CONSTRICTER_TRACE"])
Path("told.json").write_text(json.dumps([*told, os.environ["PYTEST_PLUGINS"]]))
(Path(told[2]) / "killed.json").write_text("{")
files = {"d": {"path": "w.py", "bindings": {"1": {"x": ["int"]}}}}
(Path(told[2]) / "worker.json").write_text(json.dumps({"version": 2, "files": files, "modules": {"w": "d"}}))
"""
_WORKER: Final = {
    "version": recording.VERSION,
    "files": {"d": {"path": "w.py", "bindings": {"1": {"x": ["int"]}}}},
    "modules": {"w": "d"},
}
_WORKED: Final = "def f(x):\n    y = x\n    return y\n\n\nf(1)\n"  # what a pytest process runs
# Tests for pytest-xdist's workers to share out: `double` binds one type in each.
_TESTS: Final = """
import pytest


def double(value):
    result = value * 2
    return result


@pytest.mark.parametrize("value", [1, "a", 1.5, b"x"])
def test_double(value):
    assert double(value) == value * 2
"""
_PLUGINS: Final = "PYTEST_PLUGINS"
_STATUS: Final = 3  # what it exits with
_NOTHING: Final = "nothing to run"
_OUTPUT: Final = "out.json"
_RUN_PATH: Final = "<run_path>"  # the name `runpy.run_path` runs a file under
_HELD: Final = "    held = (tell(), value)[1]"
_HELD_AGAIN: Final = "    held = (tell(), [held])[1]"
_OTHER: Final = "    other = ("
_FLAG: Final = "    if other: flag = bool(tell())"
_EACH: Final = "        each = (tell(), values.pop())[1]"
_ITEM: Final = '    for item in (tell(), "ab")[1]: last = item'
_ONE: Final = ["int"]
_Hook: TypeAlias = "Callable[[], object]"
_Callback: TypeAlias = "Callable[..., object]"
_Functions: TypeAlias = "Mapping[str, _Callback]"  # a script's, by name
_Found: TypeAlias = "Mapping[str, object]"  # what a recorder writes
_Files: TypeAlias = dict[str, dict[str, object]]  # its files' entries
_Bindings: TypeAlias = dict[str, dict[str, list[str]]]  # each binding's spellings, by its line and name
_Asked: TypeAlias = list[tuple[object, ...]]
_Sentinel: TypeAlias = object  # `sys.monitoring.DISABLE`'s type
_Tracing: TypeAlias = tuple[object, object]  # what traces this thread, and those `threading` starts


class _Hooks(NamedTuple):
    """What a recorded function calls: at a line, as it returns, and before it raises."""

    tell: _Hook
    leave: _Hook
    fail: _Hook


class _Events:  # pylint: disable=too-few-public-methods
    """A `sys.monitoring.events`."""

    LINE: int = 1
    PY_RETURN: int = 2
    PY_START: int = 4
    RAISE: int = 8


class _Monitoring:
    """A `sys.monitoring` that lists what it's asked."""

    DISABLE: _Sentinel = "disable"
    events: trace.Events = _Events()

    def __init__(self) -> None:
        self.asked: _Asked = []

    def get_tool(self, tool_id: int, /) -> str | None:
        """Name the tool that has an id.

        Returns:
          One, for the first id a monitor asks of.

        """
        self.asked.append(("get", tool_id))
        return "other" if len(self.asked) == 1 else None

    def use_tool_id(self, tool_id: int, name: str, /) -> None:
        """List a tool's id claimed."""
        self.asked.append(("use", tool_id, name))

    def free_tool_id(self, tool_id: int, /) -> None:
        """List a tool's id given up."""
        self.asked.append(("free", tool_id))

    def register_callback(self, tool_id: int, event: int, func: "_Callback | None", /) -> None:
        """List what an event is to be reported to."""
        self.asked.append(("register", tool_id, event, func))

    def set_events(self, tool_id: int, event_set: int, /) -> None:
        """List the events chosen for every function."""
        self.asked.append(("events", tool_id, event_set))

    def set_local_events(self, tool_id: int, code: CodeType, event_set: int, /) -> None:
        """List the events chosen for one function."""
        self.asked.append(("local", tool_id, code, event_set))


def _caller() -> FrameType:
    """Find the frame of what called a hook: this function's caller's caller.

    Returns:
      It.

    """
    frame: FrameType | None = inspect.currentframe()
    assert frame is not None
    assert frame.f_back is not None
    assert frame.f_back.f_back is not None
    return frame.f_back.f_back


def _direct(recorder: recording.Recorder) -> _Hooks:
    """Make hooks that tell `recorder` themselves.

    Returns:
      Them.

    """

    def tell() -> None:
        recorder.line(_caller())

    def leave() -> None:
        recorder.left(_caller())

    def fail() -> None:
        recorder.raised(_caller())

    return _Hooks(tell, leave, fail)


def _traced(recorder: recording.Recorder) -> _Hooks:
    """Make hooks that tell `recorder` as `sys.settrace`'s functions do.

    Returns:
      Them.

    """
    tracer: trace.Tracer = trace.Tracer(recorder)

    def report(event: str) -> None:
        frame: FrameType = _caller()
        if tracer.entered(frame, "call", None) is not None:
            assert tracer.within(frame, event, None) == tracer.within

    return _Hooks(partial(report, "line"), partial(report, "return"), partial(report, "exception"))


def _monitored(recorder: recording.Recorder) -> _Hooks:
    """Make hooks that tell `recorder` as `sys.monitoring`'s callbacks do.

    Returns:
      Them: each a callback itself, called from the frame its event is in.

    """
    monitor: trace.Monitor = trace.Monitor(recorder, _Monitoring())
    code: CodeType = _caller.__code__  # no callback looks at it
    return _Hooks(
        partial(monitor.line, code, 0),
        partial(monitor.returned, code, 0, None),
        partial(monitor.raised, code, 0, ValueError()),
    )


class _Run(NamedTuple):
    """A recorder of the files under a directory, hooks that tell it, and `_STEPS`'s functions there."""

    recorder: recording.Recorder
    hooks: _Hooks
    functions: _Functions
    root: Path


def _steps(path: Path) -> _Functions:
    """Write `_STEPS` to `path`, and run it.

    Returns:
      Its functions.

    """
    path.parent.mkdir(exist_ok=True)
    _ = path.write_text(_STEPS, encoding="utf-8", newline="\n")
    return cast("_Functions", runpy.run_path(str(path)))


@pytest.fixture(name="run", params=[_direct, _traced, _monitored])
def _recorded(request: pytest.FixtureRequest, tmp_path: Path) -> _Run:
    """Record `_STEPS`'s functions, told each way a recorder is.

    Returns:
      The run.

    """
    recorder: recording.Recorder = recording.Recorder(tmp_path)
    hooks: _Hooks = cast("Callable[[recording.Recorder], _Hooks]", request.param)(recorder)
    return _Run(recorder, hooks, _steps(tmp_path / "steps.py"), tmp_path)


def _digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def _line(source: str, text: str) -> str:
    """Find the line of `source` that's `text`.

    Returns:
      Its number, as a trace writes it.

    """
    return str(source.splitlines().index(text) + 1)


def _files(found: _Found) -> _Files:
    return cast("_Files", found["files"])


def _bindings(recorder: recording.Recorder, source: str = _STEPS) -> _Bindings:
    """Read what `recorder` holds of the file holding `source`.

    Returns:
      Its bindings.

    """
    return cast("_Bindings", _files(recorder.found())[_digest(source)]["bindings"])


@pytest.mark.parametrize(
    ("value", "spelling"),
    [
        (None, "None"),
        (True, "bool"),
        (1, "int"),
        (1.5, "float"),
        ("a", "str"),
        (b"a", "bytes"),
        ([1, 2], "list[int]"),
        ([1, "a", None], "list[int | str | None]"),
        ({1}, "set[int]"),
        (frozenset({"a"}), "frozenset[str]"),
        ({"a": 1}, "dict[str, int]"),
        (collections.deque([1]), "collections:deque[int]"),
        (collections.Counter("ab"), "collections:Counter[str]"),
        (collections.defaultdict(list, {"a": [1]}), "collections:defaultdict[str, list[int]]"),
        (collections.OrderedDict({"a": 1.5}), "collections:OrderedDict[str, float]"),
        ((1, "a"), "tuple[int, str]"),
        ((1,), "tuple[int, ...]"),  # of any length
        ((1, 2, 3, 4, 5), "tuple[int, ...]"),
        (int, "type[int]"),
        (fractions.Fraction, "type[fractions:Fraction]"),
        (fractions.Fraction(1), "fractions:Fraction"),
        (ValueError("no"), "ValueError"),
        (pathlib.PurePosixPath("a"), "pathlib:PurePath"),  # one platform's class, as any's
        (Path("a"), "pathlib:Path"),
        (io.StringIO(), "io:StringIO"),  # `_io`'s, as the public module names it
    ],
)
def test_a_value_is_spelled_as_its_annotation(value: object, spelling: str) -> None:
    """A scalar, a container by its elements, a tuple by its parts, a class, an instance by its class."""
    assert recording.spelled(value) == spelling


@pytest.mark.parametrize(
    "value",
    [
        len,  # a builtin class `builtins` doesn't name
        type("Inner", (), {"__qualname__": "Outer.Inner"}),
        mock.Mock(),
        [1, "a", None, 2.5],  # more types than a union is written with
        [len],
        (len, 1),
        (1, "a", None, 2.5, b""),
        [[[1]]],  # nested too deep
        [[(1,)]],
    ],
)
def test_what_no_annotation_names_is_unknown(value: object) -> None:
    """A class nothing reaches by its name, a mock, a container of too many types or too deep."""
    assert recording.spelled(value) == recording.UNKNOWN


@pytest.mark.parametrize("value", [[], {}, (), [[]], ([],), ([], [], [], [], [])])
def test_an_empty_container_says_nothing(value: object) -> None:
    """Nor does what holds one."""
    assert recording.spelled(value) is None


@pytest.mark.parametrize(
    ("made", "spelling"),
    [
        ("nested", "shapes:Outer.Inner"),
        ("nested class", "type[shapes:Outer.Inner]"),
        ("stack", "shapes:Stack[int]"),  # by its elements
        ("table", "shapes:Table[str, float]"),
        ("box of int", "shapes:Box[int]"),  # as it was made
        ("box", "shapes:Box"),  # bare: nothing says
        ("box of lists", "shapes:Box"),
        ("names", "shapes:Names"),
        ("keyed", "shapes:Keyed"),
        ("pair", "shapes:Pair"),
        ("local", recording.UNKNOWN),
        ("renamed", recording.UNKNOWN),
        ("empty", None),
        ("lazy", "shapes:Lazy"),  # none of its code runs
        ("slotted", "shapes:Slotted"),
    ],
)
def test_a_modules_class_is_spelled_as_its_annotation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    made: str,
    spelling: str | None,
) -> None:
    """One defined in another by both names; a generic one with the arguments that can be told.

    A value isn't asked what it is: its `__getattr__` and its properties aren't run.
    """
    path: Path = tmp_path / "shapes.py"
    _ = path.write_text(_SHAPES, encoding="utf-8", newline="\n")
    spec: ModuleSpec | None = importlib.util.spec_from_file_location(path.stem, path)
    assert spec is not None
    assert spec.loader is not None
    module: ModuleType = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, path.stem, module)
    spec.loader.exec_module(module)
    assert recording.spelled(cast("dict[str, object]", module.MADE)[made]) == spelling
    assert not cast("list[str]", module.ASKED)


def test_each_binding_has_what_its_statement_left(run: _Run) -> None:
    """Noted as another statement's line is reached, or the function returns."""
    _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, 1)
    found: _Found = run.recorder.found()
    assert found["version"] == recording.VERSION
    assert _files(found)[_digest(_STEPS)] == {
        "path": "steps.py",
        "bindings": {
            _line(_STEPS, _HELD): {"held": _ONE},
            _line(_STEPS, _HELD_AGAIN): {"held": ["list[int]"]},
            _line(_STEPS, _OTHER): {"other": ["float"]},
            _line(_STEPS, _FLAG): {"flag": ["bool"]},
        },
    }
    assert found["modules"] == {_RUN_PATH: _digest(_STEPS)}


def test_a_loops_binding_has_every_type_it_held(run: _Run) -> None:
    """Each time round; statements sharing a line are noted together, as the line is left."""
    _ = run.functions["spun"](run.hooks.tell, run.hooks.leave, [1.5, "a", 1])
    assert _bindings(run.recorder) == {
        _line(_STEPS, _EACH): {"each": ["float", "int", "str"]},
        _line(_STEPS, _ITEM): {"item": ["str"], "last": ["str"]},
    }


def test_a_statement_with_nothing_new_is_no_longer_looked_at(run: _Run) -> None:
    """After 20 times in a row that add no type."""
    _ = run.functions["spun"](run.hooks.tell, run.hooks.leave, ["a", *([1] * 21)])
    assert _bindings(run.recorder)[_line(_STEPS, _EACH)] == {"each": _ONE}


def test_a_function_with_nothing_new_is_no_longer_looked_at(run: _Run) -> None:
    """After 20 returns in a row that add no type."""
    for _ in range(21):
        _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, 1)
    _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, "a")
    assert _bindings(run.recorder)[_line(_STEPS, _HELD)] == {"held": _ONE}


def test_a_statement_an_exception_ends_says_nothing(run: _Run) -> None:
    """Its name holds what an earlier statement bound it to."""
    _ = run.functions["failed"](*run.hooks)
    assert list(_bindings(run.recorder).values()) == [{"first": _ONE}]


def test_a_yield_isnt_a_return(run: _Run) -> None:
    """What the statement before it binds is noted at the next line: there's none here."""
    assert list(cast("list[int]", run.functions["suspended"](run.hooks.tell, run.hooks.leave))) == [1]
    assert not _files(run.recorder.found())


def test_only_a_functions_own_names_are_noted(run: _Run) -> None:
    """Not a comprehension's, those of a function defined in it, or a global it binds."""
    _ = run.functions["shared"](run.hooks.tell, run.hooks.leave)
    assert not _files(run.recorder.found())
    _ = run.functions["scoped"](run.hooks.tell, run.hooks.leave, [1])
    assert list(_bindings(run.recorder).values()) == [{"doubled": ["list[int]"]}]


def test_a_value_that_cant_be_read_ends_its_functions_recording(run: _Run) -> None:
    """A class that isn't one as Python makes them: nothing of its function is written."""
    _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, 1)
    _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, cast("type", run.functions["Odd"])())
    _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, "a")
    assert not _files(run.recorder.found())


class _BlockedError(Exception):
    """What a program that forbids reading a file where it's read raises."""


_IMPORTED: Final = "tell()\n\n\ndef kept(tell, leave):\n    held = (tell(), 1)[1]\n    leave()\n"


def test_a_file_that_cant_be_read_yet_is_asked_for_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """What reading it raises doesn't reach the program; the next function of the file has it read."""
    recorder: recording.Recorder = recording.Recorder(tmp_path)
    hooks: _Hooks = _direct(recorder)
    functions: _Functions = _steps(tmp_path / "steps.py")
    blocked: list[type[Exception]] = [_BlockedError]
    reading: Callable[[Path], bytes] = Path.read_bytes

    def read(path: Path) -> bytes:
        if blocked:
            raise blocked.pop()
        return reading(path)

    monkeypatch.setattr(Path, "read_bytes", read, raising=True)
    _ = functions["bound"](hooks.tell, hooks.leave, 1)
    assert not _files(recorder.found())
    _ = functions["spun"](hooks.tell, hooks.leave, [1])
    assert list(_files(recorder.found())) == [_digest(_STEPS)]


def test_a_file_is_read_as_its_module_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Before any call of its functions, which may come where it can't be read."""
    recorder: recording.Recorder = recording.Recorder(tmp_path)
    hooks: _Hooks = _direct(recorder)
    path: Path = tmp_path / "imported.py"
    _ = path.write_text(_IMPORTED, encoding="utf-8", newline="\n")
    functions: _Functions = cast("_Functions", runpy.run_path(str(path), {"tell": hooks.tell}))

    def read(_path: Path) -> bytes:
        raise _BlockedError

    monkeypatch.setattr(Path, "read_bytes", read)
    _ = functions["kept"](hooks.tell, hooks.leave)
    assert list(_files(recorder.found())) == [_digest(_IMPORTED)]


def test_an_empty_container_isnt_written(run: _Run) -> None:
    """Its binding has no type yet."""
    _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, [])
    assert list(_bindings(run.recorder)) == [_line(_STEPS, _OTHER), _line(_STEPS, _FLAG)]


def test_only_the_roots_own_functions_are_recorded(run: _Run) -> None:
    """Not another directory's, an installed package's, a lambda's, or one that binds nothing.

    Nor one whose file is gone, or no longer parses.
    """
    run.recorder.line(cast("FrameType", inspect.currentframe()))
    name: str
    for name in ("site-packages/installed.py", "gone.py", "broken.py"):
        functions: _Functions = _steps(run.root / name)
        (run.root / "gone.py").unlink(missing_ok=True)
        _ = (run.root / "broken.py").write_text("def (", encoding="utf-8")
        _ = functions["bound"](run.hooks.tell, run.hooks.leave, 1)
    _ = run.functions["nameless"](run.hooks.tell)
    assert not _files(run.recorder.found())
    assert not run.recorder.found()["modules"]
    assert set(run.recorder.functions.values()) == {None}


def test_a_files_copies_are_one_file(run: _Run) -> None:
    """Written by its SHA-256, under the first one's path."""
    _ = run.functions["bound"](run.hooks.tell, run.hooks.leave, 1)
    _ = _steps(run.root / "copy.py")["bound"](run.hooks.tell, run.hooks.leave, "a")
    found: _Files = _files(run.recorder.found())
    assert [entry["path"] for entry in found.values()] == ["steps.py"]
    assert _bindings(run.recorder)[_line(_STEPS, _HELD)] == {"held": ["int", "str"]}


def test_a_monitor_asks_for_its_functions_lines(tmp_path: Path) -> None:
    """Every start and exception first, then a recorded function's lines and returns; none once stopped.

    Under the first id no tool has.
    """
    monitoring: _Monitoring = _Monitoring()
    monitor: trace.Monitor = trace.Monitor(recording.Recorder(tmp_path), monitoring)
    functions: _Functions = _steps(tmp_path / "steps.py")
    begun: CodeType = functions["begun"].__code__
    events: trace.Events = monitoring.events
    callbacks: list[_Callback] = [monitor.started, monitor.line, monitor.returned, monitor.raised]
    registered: list[int] = [events.PY_START, events.LINE, events.PY_RETURN, events.RAISE]
    monitor.start()
    assert monitoring.asked == [
        ("get", 4),  # taken
        ("get", 3),
        ("use", 3, "constricter"),
        *(("register", 3, event, callback) for event, callback in zip(registered, callbacks, strict=True)),
        ("events", 3, events.PY_START | events.RAISE),
    ]
    monitoring.asked.clear()
    assert functions["begun"](partial(monitor.started, begun, 0)) == monitoring.DISABLE
    assert functions["nameless"](partial(monitor.started, begun, 0)) == (monitoring.DISABLE,) * 2
    assert monitoring.asked == [("local", 3, begun, events.LINE | events.PY_RETURN)]
    monitoring.asked.clear()
    monitor.stop()
    assert monitoring.asked == [
        ("events", 3, 0),
        ("local", 3, begun, 0),
        *(("register", 3, event, None) for event in registered),
        ("free", 3),
    ]


def test_a_monitor_disables_what_isnt_recorded(tmp_path: Path) -> None:
    """A line or a return of a function that isn't, or is no longer."""
    monitoring: _Monitoring = _Monitoring()
    monitor: trace.Monitor = trace.Monitor(recording.Recorder(tmp_path), monitoring)
    functions: _Functions = _steps(tmp_path / "steps.py")
    code: CodeType = _caller.__code__
    hook: _Hook
    for hook in (partial(monitor.line, code, 0), partial(monitor.returned, code, 0, None)):
        assert functions["begun"](hook) is None
        assert functions["nameless"](hook) == (monitoring.DISABLE,) * 2


def test_a_monitor_finds_its_frames_without_sys(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A run may patch `sys._getframe`, or take it away: a callback has what it was."""
    monitoring: _Monitoring = _Monitoring()
    monitor: trace.Monitor = trace.Monitor(recording.Recorder(tmp_path), monitoring)
    functions: _Functions = _steps(tmp_path / "steps.py")
    monkeypatch.delattr(sys, "_getframe")
    assert functions["begun"](partial(monitor.line, _caller.__code__, 0)) is None


def test_a_tracer_traces_until_stopped(tmp_path: Path) -> None:
    """Its thread and those started; then what traced them before does."""
    before: _Tracing = (sys.gettrace(), threading.gettrace())
    tracer: trace.Tracer = trace.Tracer(recording.Recorder(tmp_path))
    tracer.start()
    try:
        during: _Tracing = (sys.gettrace(), threading.gettrace())
    finally:
        tracer.stop()
    assert during == (tracer.entered, tracer.entered)
    assert (sys.gettrace(), threading.gettrace()) == before
    tracer.stop()  # again: nothing changes
    assert (sys.gettrace(), threading.gettrace()) == before
    frame: FrameType | None = inspect.currentframe()
    assert frame is not None
    assert tracer.entered(frame, "call", None) is None
    assert tracer.within(frame, "opcode", None) == tracer.within


def _module(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Write `_MODULE` where the run finds it, the interpreter's state restored after the test.

    Returns:
      Its path.

    """
    path: Path = tmp_path / "traced_module.py"
    _ = path.write_text(_MODULE, encoding="utf-8", newline="\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "path", [str(tmp_path), *sys.path])
    monkeypatch.setattr(sys, "argv", [*sys.argv])
    return path


@pytest.mark.parametrize("target", [["-m", "traced_module"], ["traced_module.py"]])
@pytest.mark.parametrize("monitored", [True, False])
def test_a_module_or_a_script_is_run_and_recorded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: list[str],
    *,
    monitored: bool,
) -> None:
    """As `python` runs it, by `sys.monitoring` or `sys.settrace`; the trace is written though it exits."""
    if monitored and trace.MONITORING is None:
        pytest.skip("no `sys.monitoring` before Python 3.12")
    if not monitored:
        monkeypatch.setattr(trace, "MONITORING", None)
    path: Path = _module(tmp_path, monkeypatch)
    before: _Tracing = (sys.gettrace(), threading.gettrace())
    exited: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exited:
        _ = trace.main(["--output", _OUTPUT, f"--root={tmp_path}", *target, "a", "b"])
    assert exited.value.code == _STATUS  # the run's own
    assert (sys.gettrace(), threading.gettrace()) == before
    found: _Found = cast("_Found", json.loads((tmp_path / _OUTPUT).read_text(encoding="utf-8")))
    assert _files(found)[_digest(_MODULE)]["bindings"] == {
        _line(_MODULE, "    made = Local()"): {"made": ["__main__:Local"]},
        _line(_MODULE, "    count = len(argv)"): {"count": _ONE},
        _line(_MODULE, "    for arg in argv:"): {"arg": ["str"]},
        _line(_MODULE, "        size = len(arg)"): {"size": _ONE},
        _line(_MODULE, "    count = str("): {"count": ["str"]},
    }
    assert found["modules"] == {"__main__": _digest(path.read_text(encoding="utf-8"))}


def test_what_ends_without_exiting_exits_0(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The default output is in the working directory."""
    path: Path = _module(tmp_path, monkeypatch)
    _ = path.write_text("def f():\n    x = 1\n    return x\n\n\nf()\n", encoding="utf-8", newline="\n")
    assert trace.main([path.name]) == 0
    assert (tmp_path / trace.DEFAULT).is_file()


def test_python_m_runs_the_command(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`python -m constricter.trace` reads the command line."""
    path: Path = _module(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", ["trace", f"--output={_OUTPUT}", path.name])
    monkeypatch.delitem(sys.modules, trace.__name__)  # run afresh, as `-m` does
    exited: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exited:
        _ = runpy.run_module(trace.__name__, run_name="__main__")
    assert exited.value.code == _STATUS
    assert (tmp_path / _OUTPUT).is_file()


@pytest.mark.parametrize("argv", [[], ["--output", _OUTPUT], ["-m"]])
def test_nothing_to_run_exits_2(argv: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    """With neither a script nor a module."""
    with pytest.raises(SystemExit):
        _ = trace.main(argv)
    assert _NOTHING in capsys.readouterr().err


def test_traces_are_joined() -> None:
    """Each binding has its spellings in them all; a file has the first path it's under."""
    one: recording.Found = {
        "version": recording.VERSION,
        "files": {"d": {"path": "a.py", "bindings": {"1": {"x": ["int"]}, "2": {"y": ["str"]}}}},
        "modules": {"a": "d"},
    }
    other: recording.Found = {
        "version": recording.VERSION,
        "files": {
            "d": {"path": "copy.py", "bindings": {"1": {"x": ["bytes", "int"], "z": ["float"]}}},
            "e": {"path": "b.py", "bindings": {"3": {"w": ["None"]}}},
        },
        "modules": {"b": "e"},
    }
    assert recording.merged([one, other]) == {
        "version": recording.VERSION,
        "files": {
            "d": {
                "path": "a.py",
                "bindings": {"1": {"x": ["bytes", "int"], "z": ["float"]}, "2": {"y": ["str"]}},
            },
            "e": {"path": "b.py", "bindings": {"3": {"w": ["None"]}}},
        },
        "modules": {"a": "d", "b": "e"},
    }


def test_a_run_tells_its_pytest_processes_and_reads_what_they_wrote(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """By the environment, as it was once the run ends; what one didn't finish writing is passed over."""
    path: Path = _module(tmp_path, monkeypatch)
    _ = path.write_text(_CHILD, encoding="utf-8", newline="\n")
    monkeypatch.setenv(_PLUGINS, "other")
    monkeypatch.delenv(trace.ENVIRONMENT, raising=False)
    assert trace.main([path.name]) == 0
    told: list[str] = cast("list[str]", json.loads((tmp_path / "told.json").read_text(encoding="utf-8")))
    assert told[:2] == [str(os.getpid()), str(tmp_path.resolve())]
    assert told[3] == f"other,{trace.__name__}"
    assert not Path(told[2]).exists()
    assert (os.environ.get(trace.ENVIRONMENT), os.environ[_PLUGINS]) == (None, "other")
    assert json.loads((tmp_path / trace.DEFAULT).read_text(encoding="utf-8")) == _WORKER


def test_a_pytest_process_a_run_started_records_itself(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """From its first session to its last, when it writes where the run reads."""
    script: Path = tmp_path / "worked.py"
    _ = script.write_text(_WORKED, encoding="utf-8", newline="\n")
    monkeypatch.setenv(trace.ENVIRONMENT, json.dumps(["0", str(tmp_path), str(tmp_path)]))
    part: Path = tmp_path / f"{os.getpid()}.json"
    trace.pytest_configure()
    trace.pytest_configure()  # a session in a session
    try:
        _ = runpy.run_path(str(script))
    finally:
        trace.pytest_unconfigure()
        early: bool = part.exists()
        trace.pytest_unconfigure()
    assert not early
    found: _Found = cast("_Found", json.loads(part.read_text(encoding="utf-8")))
    assert _files(found)[_digest(_WORKED)]["bindings"] == {"2": {"y": _ONE}}
    part.unlink()
    trace.pytest_unconfigure()  # no session left
    assert not part.exists()


@pytest.mark.parametrize("own", [True, False])
def test_the_runs_own_process_isnt_recorded_again(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    *,
    own: bool,
) -> None:
    """Nor a pytest process no traced run started."""
    monkeypatch.delenv(trace.ENVIRONMENT, raising=False)
    if own:
        monkeypatch.setenv(trace.ENVIRONMENT, json.dumps([str(os.getpid()), str(tmp_path), str(tmp_path)]))
    before: _Tracing = (sys.gettrace(), threading.gettrace())
    trace.pytest_configure()
    assert (sys.gettrace(), threading.gettrace()) == before
    trace.pytest_unconfigure()
    assert not list(tmp_path.iterdir())


def test_pytest_xdists_workers_are_recorded(tmp_path: Path) -> None:
    """Each records the tests it runs; the run's trace has them all."""
    if importlib.util.find_spec("xdist") is None:
        pytest.skip("pytest-xdist isn't installed")
    _ = (tmp_path / "test_double.py").write_text(_TESTS, encoding="utf-8", newline="\n")
    environment: dict[str, str] = {
        name: value for name, value in os.environ.items() if not name.startswith(("PYTEST_", "COV_"))
    }
    environment["PYTHONPATH"] = str(Path(trace.__file__).parent.parent)
    command: list[str] = [sys.executable, "-m", trace.__name__, "--output", _OUTPUT]
    ran: subprocess.CompletedProcess[str] = subprocess.run(
        [*command, "-m", "pytest", "-q", "-n", "2", "-p", "no:cacheprovider", "test_double.py"],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert ran.returncode == 0, ran.stdout + ran.stderr
    found: _Found = cast("_Found", json.loads((tmp_path / _OUTPUT).read_text(encoding="utf-8")))
    assert _files(found)[_digest(_TESTS)]["bindings"] == {
        _line(_TESTS, "    result = value * 2"): {"result": ["bytes", "float", "int", "str"]},
    }
