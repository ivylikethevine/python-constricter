# SPDX-License-Identifier: MIT
"""`python -m constricter.trace`: the types a run's functions' locals hold, recorded."""

import collections
import fractions
import hashlib
import inspect
import io
import json
import operator
import pathlib
import runpy
import sys
import types
from pathlib import Path
from types import FrameType
from typing import TYPE_CHECKING, Final, TypeAlias, cast
from unittest import mock

import pytest

from constricter import trace

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

_HERE: Final = Path(__file__).parent
_MODULE: Final = """
import inspect
import sys


class Local:
    pass


def run(argv):
    made = Local()
    count = len(argv)
    return inspect.currentframe()


if __name__ == "__main__":
    run(sys.argv)
    raise SystemExit(3)
"""
_STATUS: Final = 3  # what it exits with
_RUN: Final = _MODULE.splitlines().index("def run(argv):") + 1  # `run`'s line in it
_NOTHING: Final = "nothing to run"
_RETURN: Final = "return"
_OUTPUT: Final = "out.json"
_Functions: TypeAlias = dict[str, dict[str, list[str]]]  # each function's locals' spellings, by its line


def _returning(value: object, *, bind: bool = True) -> FrameType:
    frame: FrameType | None = inspect.currentframe()
    assert frame is not None
    if bind and frame is not value:
        count: int = 1
        assert count
    return frame


def _digest(path: Path | None = None) -> str:
    return hashlib.sha256((path or Path(__file__)).read_bytes()).hexdigest()


def _read(output: Path) -> "Mapping[str, object]":
    return cast("Mapping[str, object]", json.loads(output.read_text(encoding="utf-8")))


def _files(output: Path) -> dict[str, dict[str, str]]:
    """Read the files a trace has.

    Returns:
      Each one's entry, by its digest.

    """
    return cast("dict[str, dict[str, str]]", _read(output)["files"])


def _functions(output: Path, digest: str) -> _Functions:
    return cast("dict[str, dict[str, _Functions]]", _read(output)["files"])[digest]["functions"]


def _held(recorder: trace.Recorder, output: Path) -> dict[str, list[str]]:
    """Write what `recorder` holds, and read `_returning`'s locals back.

    Returns:
      Each one's spellings.

    """
    recorder.write(output)
    return _functions(output, _digest())[str(_returning.__code__.co_firstlineno)]


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
    assert trace.spelled(value) == spelling


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
    """A nested class, a mock, a container of too many types or too deep."""
    assert trace.spelled(value) == trace.UNKNOWN


@pytest.mark.parametrize("value", [[], {}, (), [[]], ([],), ([], [], [], [], [])])
def test_an_empty_container_says_nothing(value: object) -> None:
    """Nor does what holds one."""
    assert trace.spelled(value) is None


def test_a_returning_functions_locals_are_noted(tmp_path: Path) -> None:
    """On each return, every local it holds then; a `call` isn't one, nor an unbound local."""
    recorder: trace.Recorder = trace.Recorder(_HERE)
    recorder(_returning([1]), "call", None)
    assert not recorder.functions
    recorder(_returning([1]), _RETURN, None)
    recorder(_returning(["a"]), _RETURN, None)
    recorder(_returning(cast("list[int]", []), bind=False), _RETURN, None)
    output: Path = tmp_path / _OUTPUT
    assert _held(recorder, output) == {
        "bind": ["bool"],
        "count": ["int"],
        "frame": [trace.UNKNOWN],
        "value": ["list[int]", "list[str]"],
    }
    assert _read(output)["version"] == trace.VERSION
    assert _files(output)[_digest()]["path"] == Path(__file__).name
    assert _read(output)["modules"] == {__name__: _digest()}


def test_a_function_with_nothing_new_is_no_longer_looked_at(tmp_path: Path) -> None:
    """After 20 returns in a row that add no type."""
    recorder: trace.Recorder = trace.Recorder(_HERE)
    for _ in range(21):
        recorder(_returning(1), _RETURN, None)
    recorder(_returning("a"), _RETURN, None)
    assert _held(recorder, tmp_path / _OUTPUT)["value"] == ["int"]


def test_two_functions_on_one_line_share_their_locals(tmp_path: Path) -> None:
    """A function compiled twice is one function."""
    again: types.FunctionType = types.FunctionType(_returning.__code__.replace(co_name="again"), globals())
    again.__kwdefaults__ = {"bind": True}
    recorder: trace.Recorder = trace.Recorder(_HERE)
    recorder(_returning(1), _RETURN, None)
    recorder(cast("FrameType", operator.call(again, 1.5)), _RETURN, None)
    assert _held(recorder, tmp_path / _OUTPUT)["value"] == ["float", "int"]


def test_a_value_that_cant_be_read_ends_its_functions_recording(tmp_path: Path) -> None:
    """A class that isn't one as Python makes them: nothing of its function is written."""
    recorder: trace.Recorder = trace.Recorder(_HERE)
    recorder(_returning(1), _RETURN, None)
    recorder(_returning(cast("object", type("Odd", (), {"__module__": None})())), _RETURN, None)
    recorder(_returning("a"), _RETURN, None)
    recorder.write(tmp_path / _OUTPUT)
    assert not _files(tmp_path / _OUTPUT)


def test_only_the_roots_own_functions_are_recorded(tmp_path: Path) -> None:
    """Not another directory's, an installed package's, a generator expression's, or a file's gone since."""
    output: Path = tmp_path / _OUTPUT
    here: trace.Recorder = trace.Recorder(_HERE)
    here(cast("FrameType", next(inspect.currentframe() for _ in (0,))), _RETURN, None)
    here.write(output)
    assert not _files(output)
    recorder: trace.Recorder = trace.Recorder(tmp_path)
    recorder(_returning(1), _RETURN, None)
    name: str
    for name in ("site-packages/installed.py", "gone.py", "kept.py"):
        path: Path = tmp_path / name
        path.parent.mkdir(exist_ok=True)
        _ = path.write_text(_MODULE, encoding="utf-8", newline="\n")
        run: Callable[[list[str]], FrameType] = cast(
            "Callable[[list[str]], FrameType]",
            runpy.run_path(str(path))["run"],
        )
        recorder(run(["a"]), _RETURN, None)
    (tmp_path / "gone.py").unlink()
    recorder.write(output)
    assert [entry["path"] for entry in _files(output).values()] == ["kept.py"]


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
def test_a_module_or_a_script_is_run_and_recorded(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: list[str],
) -> None:
    """As `python` runs it, with its arguments; the trace is written though it exits."""
    path: Path = _module(tmp_path, monkeypatch)
    exited: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exited:
        _ = trace.main(["--output", _OUTPUT, f"--root={tmp_path}", *target, "a", "b"])
    assert exited.value.code == _STATUS  # the run's own
    assert sys.getprofile() is None
    assert _functions(tmp_path / _OUTPUT, _digest(path)) == {
        str(_RUN): {"argv": ["list[str]"], "count": ["int"], "made": ["__main__:Local"]},
    }
    assert _read(tmp_path / _OUTPUT)["modules"] == {"__main__": _digest(path)}


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
