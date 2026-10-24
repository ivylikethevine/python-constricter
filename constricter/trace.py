"""Record the types a run binds its functions' locals to, for `--fix --infer-from` to read.

  python -m constricter.trace [--output FILE] [--root DIR] (-m MODULE | -c CODE | SCRIPT) [ARG ...]

Runs the module, code or script as `python` would (`-m pytest`), and each time a statement of a
function defined in a file under DIR (default: the working directory; nothing installed there) ends,
notes the type of each name it binds (see `constricter.recording`). At exit it writes them to FILE
(default: `constricter-trace.json`).

Lines are followed by `sys.monitoring`, or `sys.settrace` on a Python without it (before 3.12). A
pytest process the run starts (pytest-xdist's workers) records itself the same way: the run names
this module in `PYTEST_PLUGINS`, and its trace has what each wrote as its session ended. A process
the run forks (`multiprocessing`'s `fork` workers: Django's `--parallel`) records on as it did, and
writes what it has as it ends. No other child process is recorded.
"""

import argparse
import atexit
import json
import os
import runpy
import shutil
import sys
import tempfile
import threading
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import partial
from multiprocessing import util as multiprocessing_util
from pathlib import Path
from types import CodeType, FrameType
from typing import Final, Protocol, TypeAlias, cast

from constricter.recording import Found, Recorder, merged, write

DEFAULT: Final = "constricter-trace.json"
# What tells a pytest process a traced run started it: the run's process, its root, and where to write.
ENVIRONMENT: Final = "CONSTRICTER_TRACE"
_PLUGINS: Final = "PYTEST_PLUGINS"  # the modules every pytest process loads, by name
_PLUGIN: Final = "constricter.trace"  # this one: `pytest_configure` and `pytest_unconfigure`
_PARTS: Final = "*.json"  # what those processes write
_LINE: Final = "line"  # `sys.settrace`'s events
_RETURN: Final = "return"
_EXCEPTION: Final = "exception"
_TOOL: Final = "constricter"  # to `sys.monitoring`
# Its ids no kind of tool has: this takes the first free. A profiler's is `cProfile`'s, which a run may start.
_TOOLS: Final = (4, 3)
_GETFRAME: Final = "_getframe"  # `sys`'s, which `inspect.currentframe` asks for each time
_OPTIONS: Final = frozenset({"--output", "--root"})
_MODULE: Final = "-m"
_CODE: Final = "-c"
_STRING: Final = "<string>"  # the file name `python -c` compiles its code under
_MAIN: Final = "__main__"
_Trace: TypeAlias = Callable[[FrameType, str, object], "_Trace | None"]  # a `sys.settrace` function
_Callback: TypeAlias = Callable[..., object]  # what `sys.monitoring` reports an event to
_Sentinel: TypeAlias = object  # what a callback answers to have an event reported no more


class Events(Protocol):  # pylint: disable=too-few-public-methods
    """`sys.monitoring.events`: the ones followed."""

    LINE: int
    PY_RETURN: int
    PY_START: int
    RAISE: int


class Monitoring(Protocol):
    """`sys.monitoring` (Python 3.12), as it's used here."""

    DISABLE: _Sentinel
    events: Events

    def get_tool(self, tool_id: int, /) -> str | None:
        """Name the tool that has an id, if one has."""

    def use_tool_id(self, tool_id: int, name: str, /) -> None:
        """Claim a tool's id, under a name."""

    def free_tool_id(self, tool_id: int, /) -> None:
        """Give a tool's id up."""

    def register_callback(self, tool_id: int, event: int, func: _Callback | None, /) -> object:
        """Set what one event is reported to, or nothing."""

    def set_events(self, tool_id: int, event_set: int, /) -> None:
        """Choose the events reported of every function."""

    def set_local_events(self, tool_id: int, code: CodeType, event_set: int, /) -> None:
        """Choose the events reported of one function besides."""


MONITORING: Final = cast("Monitoring | None", getattr(sys, "monitoring", None))


# What finds a frame, held as this module is loaded: a run may take it away (a test of code without it).
_frame: Final = cast("Callable[[int], FrameType]", getattr(sys, _GETFRAME))


class Monitor:
    """`sys.monitoring`'s callbacks: each recorded function's lines and returns, and every exception."""

    def __init__(self, recorder: Recorder, monitoring: Monitoring) -> None:
        """Tell `recorder` what `monitoring` reports."""
        self.recorder: Recorder = recorder
        self.monitoring: Monitoring = monitoring
        self.codes: list[CodeType] = []  # each recorded function's, its lines and returns reported
        self.tool: int = _TOOLS[0]  # its id, once started

    def start(self) -> None:
        """Have every function's start reported, and every exception."""
        events: Events = self.monitoring.events
        self.tool = next((tool for tool in _TOOLS if self.monitoring.get_tool(tool) is None), self.tool)
        self.monitoring.use_tool_id(self.tool, _TOOL)
        self._register(self.started, self.line, self.returned, self.raised)
        self.monitoring.set_events(self.tool, events.PY_START | events.RAISE)

    def stop(self) -> None:
        """Have nothing reported any more."""
        self.monitoring.set_events(self.tool, 0)
        code: CodeType
        for code in self.codes:
            self.monitoring.set_local_events(self.tool, code, 0)
        self._register(None, None, None, None)
        self.monitoring.free_tool_id(self.tool)

    def _register(self, *callbacks: _Callback | None) -> None:
        """Set the callbacks for a start, a line, a return and an exception."""
        events: Events = self.monitoring.events
        event: int
        callback: _Callback | None
        for event, callback in zip(
            (events.PY_START, events.LINE, events.PY_RETURN, events.RAISE),
            callbacks,
            strict=True,
        ):
            _ = self.monitoring.register_callback(self.tool, event, callback)

    def started(self, code: CodeType, _offset: int) -> object:
        """Have a recorded function's lines and returns reported, the first time it starts.

        Returns:
          `DISABLE`: no start of it is reported again.

        """
        if self.recorder.wanted(_frame(1)):
            self.codes.append(code)
            events: Events = self.monitoring.events
            self.monitoring.set_local_events(
                self.tool,
                code,
                events.LINE | events.PY_RETURN,
            )
        return self.monitoring.DISABLE

    def line(self, _code: CodeType, line: int) -> object:
        """Tell the recorder its caller has arrived at a line.

        Returns:
          `DISABLE` for a function no longer recorded: that line of it isn't reported again.

        """
        return None if self.recorder.line(_frame(1), line) else self.monitoring.DISABLE

    def returned(self, _code: CodeType, _offset: int, _value: object) -> object:
        """Tell the recorder its caller returns.

        Returns:
          `DISABLE` for a function no longer recorded.

        """
        return None if self.recorder.left(_frame(1), finished=True) else self.monitoring.DISABLE

    def raised(self, _code: CodeType, _offset: int, _error: BaseException) -> None:
        """Tell the recorder an exception is raised in its caller, or through it."""
        self.recorder.raised(_frame(1))


class Tracer:
    """`sys.settrace`'s functions: each recorded function's lines, returns and exceptions."""

    def __init__(self, recorder: Recorder) -> None:
        """Tell `recorder` what the interpreter reports."""
        self.recorder: Recorder = recorder
        self.previous: tuple[_Trace | None, _Trace | None] = (
            cast("_Trace | None", sys.gettrace()),
            cast("_Trace | None", threading.gettrace()),
        )

    def start(self) -> None:
        """Trace this thread, and those `threading` starts."""
        sys.settrace(self.entered)
        threading.settrace(self.entered)

    def stop(self) -> None:
        """Trace as before."""
        sys.settrace(self.previous[0])
        threading.settrace(cast("_Trace", self.previous[1]))

    def entered(self, frame: FrameType, _event: str, _arg: object) -> _Trace | None:
        """Choose what traces a function that starts, or resumes.

        Returns:
          `within` for one to record, or `None`.

        """
        return self.within if self.recorder.wanted(frame) else None

    def within(self, frame: FrameType, event: str, _arg: object) -> _Trace | None:
        """Tell the recorder what a recorded function's frame does.

        Returns:
          Itself: what traces the frame next.

        """
        if event == _LINE:
            _ = self.recorder.line(frame)
        elif event == _RETURN:
            _ = self.recorder.left(frame)
        elif event == _EXCEPTION:
            self.recorder.raised(frame)
        return self.within


def following(recorder: Recorder) -> Monitor | Tracer:
    """Choose what tells `recorder` of the run's lines: `sys.monitoring` where there is one.

    Returns:
      It, not started.

    """
    return Tracer(recorder) if MONITORING is None else Monitor(recorder, MONITORING)


@dataclass
class _Worker:
    """A pytest process a traced run started: what records it, and where it writes, while it has a session."""

    sessions: int = 0
    recorder: Recorder | None = None
    follower: Monitor | Tracer | None = None
    output: Path = Path()


_WORKER: Final = _Worker()


def pytest_configure() -> None:
    """Record a pytest process a traced run started, from its first session: not the run's own."""
    told: list[str] = cast("list[str]", json.loads(os.environ.get(ENVIRONMENT, "[]")))
    if not told or told[0] == str(os.getpid()):
        return
    _WORKER.sessions += 1
    if _WORKER.recorder is None:
        _WORKER.recorder = Recorder(Path(told[1]))
        _WORKER.follower = following(_WORKER.recorder)
        _WORKER.output = Path(told[2]) / f"{os.getpid()}.json"
        _WORKER.follower.start()


def pytest_unconfigure() -> None:
    """Write what such a process recorded where the run reads it, as its last session ends."""
    if _WORKER.recorder is None or _WORKER.follower is None:
        return
    _WORKER.sessions -= 1
    if not _WORKER.sessions:
        _WORKER.follower.stop()
        _WORKER.recorder.write(_WORKER.output)
        _WORKER.recorder = _WORKER.follower = None


@dataclass
class _Forking:
    """A traced run's own process, for the children it forks: what records it, and where they write."""

    recorder: Recorder | None = None
    parts: Path = Path()
    hooked: bool = False  # `os.register_at_fork` takes no hook back: one, for every run of the process


_FORKING: Final = _Forking()


def forked() -> None:
    """Have a child the run forked write what it records where the run reads, as it ends.

    `os.register_at_fork`'s hook in the child. `sys.monitoring` (or `sys.settrace`) and the recorder
    are copied with it, so it records on; what its parent recorded before the fork is in its trace
    too, which the run's merge joins. A worker `multiprocessing` forks leaves by `os._exit`, after
    its finalizers alone, which it clears as it starts and then has its after-fork callbacks add to:
    one adds what writes it there. `atexit` writes any other child.
    """
    recorder: Recorder | None
    if (recorder := _FORKING.recorder) is None:
        return
    output: Path = _FORKING.parts / f"{os.getpid()}.json"
    _ = atexit.register(recorder.write, output)
    multiprocessing_util.register_after_fork(recorder, partial(_finalized, output=output))


def _finalized(recorder: Recorder, *, output: Path) -> None:
    """Have a `multiprocessing` worker write what `recorder` has to `output`, as it ends."""
    _ = multiprocessing_util.Finalize(None, recorder.write, args=(output,), exitpriority=0)


def _unforked(**_hooks: Callable[[], None]) -> None:
    """Register nothing: no process forks where there's no `os.register_at_fork` (Windows)."""


_at_fork: Final = cast("Callable[..., None]", getattr(os, "register_at_fork", _unforked))


def _forking(recorder: Recorder | None, parts: Path) -> None:
    """Have the children this process forks record themselves for `recorder`'s run, or none (`None`)."""
    _FORKING.recorder = recorder
    _FORKING.parts = parts
    if not _FORKING.hooked:
        _at_fork(after_in_child=forked)
        _FORKING.hooked = True


def _announced(root: Path, parts: Path) -> dict[str, str | None]:
    """Tell the pytest processes this one starts to record themselves, and write to `parts`.

    Returns:
      The environment variables that say so, as they were.

    """
    before: dict[str, str | None] = {name: os.environ.get(name) for name in (ENVIRONMENT, _PLUGINS)}
    os.environ[ENVIRONMENT] = json.dumps([str(os.getpid()), str(root.resolve()), str(parts)])
    os.environ[_PLUGINS] = f"{before[_PLUGINS]},{_PLUGIN}" if before[_PLUGINS] else _PLUGIN
    return before


def _gathered(parts: Path, before: Mapping[str, str | None]) -> list[Found]:
    """Read what the processes this one started wrote to `parts`, the environment as it was `before`.

    Returns:
      Each one's trace: not one that can't be read (a process killed as it wrote).

    """
    name: str
    value: str | None
    for name, value in before.items():
        if value is None:
            del os.environ[name]
        else:
            os.environ[name] = value
    found: list[Found] = []
    path: Path
    for path in sorted(parts.glob(_PARTS)):
        try:
            found.append(cast("Found", json.loads(path.read_text(encoding="utf-8"))))
        except ValueError:
            continue
    return found


def _split(args: Sequence[str]) -> tuple[list[str], list[str]]:
    """Split the command line where what's to run starts: at `-m` or `-c`, or the first word no option's.

    Returns:
      This command's options, and the module or script with its arguments.

    """
    valued: bool = False
    at: int
    arg: str
    for at, arg in enumerate(args):
        if valued or arg in _OPTIONS:
            valued = not valued
        elif arg in {_MODULE, _CODE} or not arg.startswith("-"):
            return list(args[:at]), list(args[at:])
    return list(args), []


def _run(name: str, kind: str) -> None:
    """Run `name` as `python` would: a module (`kind` `-m`), code (`-c`), or a script (`""`)."""
    if kind == _MODULE:
        _ = runpy.run_module(name, run_name=_MAIN, alter_sys=True)
    elif kind == _CODE:
        sys.path[0] = ""  # the working directory, as `python -c` has it
        code: CodeType = compile(name, _STRING, "exec")
        # pylint: disable-next=exec-used
        exec(code, {"__name__": _MAIN, "__builtins__": __builtins__})  # ruff: ignore[exec-builtin]
    else:
        sys.path[0] = str(Path(name).resolve().parent)
        _ = runpy.run_path(name, run_name=_MAIN)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the module, code or script named on the command line, recording its functions' locals' types.

    Returns:
      0: the exit status, where what ran doesn't exit itself.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="python -m constricter.trace",
        usage="%(prog)s [--output FILE] [--root DIR] (-m MODULE | -c CODE | SCRIPT) [ARG ...]",
        description="Record the types a run binds its functions' locals to, for `constricter --infer-from`.",
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        default=Path(DEFAULT),
        metavar="FILE",
        help="where to write",
    )
    _ = parser.add_argument("--root", type=Path, default=Path(), metavar="DIR", help="whose files to record")
    own: list[str]
    target: list[str]
    own, target = _split(sys.argv[1:] if argv is None else argv)
    args: argparse.Namespace = parser.parse_args(own)
    kind: str = target[0] if target[:1] in ([_MODULE], [_CODE]) else ""
    if len(target) <= bool(kind):
        parser.error("nothing to run: name a script, a module after -m, or code after -c")
    name: str = target[bool(kind)]
    sys.argv = [_CODE if kind == _CODE else name, *target[bool(kind) + 1 :]]
    recorder: Recorder = Recorder(cast("Path", args.root))
    follower: Monitor | Tracer = following(recorder)
    # Not a `TemporaryDirectory`, whose finalizer a forked child runs too as it exits.
    parts: Path = Path(tempfile.mkdtemp(prefix=f"{_TOOL}-trace-"))
    started: int = os.getpid()
    before: dict[str, str | None] = _announced(recorder.root, parts)
    _forking(recorder, parts)
    follower.start()
    try:
        _run(name, kind)
    finally:
        follower.stop()
        _forking(None, Path())
        if os.getpid() == started:  # a forked child leaving this way writes its own part, as it exits
            write(cast("Path", args.output), merged([recorder.found(), *_gathered(parts, before)]))
            shutil.rmtree(parts, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
