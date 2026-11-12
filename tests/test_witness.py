"""`python -m constricter.trace --check`: a run's values held to the annotations its functions declare."""

import collections.abc
import inspect
import json
import os
import runpy
import sys
import typing
from pathlib import Path
from types import FrameType, ModuleType
from typing import TYPE_CHECKING, Final, Protocol, TypeAlias, cast

import pytest

from constricter import recording, trace, witness
from constricter.overrides import override

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from types import GeneratorType

# A script whose functions are called with what they declare, and with something else.
_CHECKED: Final = """\
import pathlib
import typing
from typing import Protocol

if typing.TYPE_CHECKING:
    from pathlib import Path
    from nowhere import Missing


class Named(Protocol):
    name: str


class Odd:
    __module__ = "tests.stand_ins"


def same(function):
    return function


@same
def double(value: int, where: "Path", who: Named, *rest: int, **more: int) -> str:
    total: int = value * 2
    names: list[str] = [1, "a"]
    plain = total
    later: int
    total = "x"
    return total


def lost(value: "Missing", other: "1 / 0" = 1, quoted: "'int'" = 2, odd: Odd = None) -> "Missing":
    return value


def spun(values: list[int]):
    for value in values:
        yield value


def gone(value: int) -> int:
    del value
    return "a"


def __annotate__(format: int) -> int:
    return "a"


def unannotated(value):
    return value


double(2, pathlib.Path("."), pathlib.Path("x"))
double("a", "p", 3)
lost(1)
lost(1, odd=Odd())
list(spun(["a"]))
gone(1)
__annotate__("a")
unannotated(1)
"""
_HOLDS: Final = """\
import sys


def double(value: int) -> int:
    return value * 2


double(2)
sys.exit({status})
"""
_MANY: Final = """\
def taken(value: int) -> None:
    held: int = value


def spun(value: int):
    yield value
"""
_TEXT: Final = "a"  # a value no `int` annotation holds
_OF: Final = "__module__"  # where a class says what module it's of
_Judged: TypeAlias = list[str | int | list[int] | list[str]]
_Case: TypeAlias = tuple[object, object, bool | None]  # a value, an annotation, and whether it holds
_Verdict: TypeAlias = tuple[int, list[int], list[str]]  # a binding's line, its counts, what differed
_Counted: TypeAlias = tuple[list[int], list[str]]  # a binding's counts in every process, and what differed


def _script(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str) -> Path:
    """Write `source` where a run finds it, the interpreter's state restored after the test.

    Returns:
      Its path.

    """
    path: Path = tmp_path / "checked.py"
    _ = path.write_text(source, encoding="utf-8", newline="\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [*sys.argv])
    monkeypatch.setattr(sys, "path", [*sys.path])
    return path


def _at(source: str, text: str, name: str = "") -> str:
    """Find where the line of `source` starting with `text` binds `name`.

    Returns:
      Its place as a report gives it: the line, then `name`'s column (1 with no name).

    """
    lines: list[str] = source.splitlines()
    line: int = next(at for at, each in enumerate(lines) if each.lstrip().startswith(text))
    return f"{line + 1}:{lines[line].index(name) + 1 if name else 1}"


def _said(text: str, name: str, annotation: str, seen: str) -> str:
    """Write the line a report gives `name`, bound on `_CHECKED`'s line starting with `text`.

    Returns:
      It.

    """
    where: str = _at(_CHECKED, text, name)
    return (
        f"checked.py:{where}: error: LVA016 '{name}', annotated `{annotation}`, "
        f"was bound to `{seen}` in a traced run"
    )


def test_a_checked_run_lists_each_binding_a_value_differed_from(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A parameter, a local at each line it's bound, and a return: with the type seen, and exits 1.

    An annotation is evaluated where it runs, a name imported for type checking alone imported for
    it, a quoted one's text read; one that can't be, a test's class and a generator's return say
    nothing. Not a `*args`, a `**kwargs`, an unannotated name, or Python 3.14's `__annotate__`.
    """
    path: Path = _script(tmp_path, monkeypatch, _CHECKED)
    assert trace.main(["--check", f"--root={tmp_path}", path.name]) == 1
    last: str = _at(_CHECKED, 'return "a"')
    returned: str = f"checked.py:{last}: error: LVA016 a function annotated"
    assert capsys.readouterr().out.splitlines() == [
        _said("def double", "value", "int", "str"),
        _said("def double", "where", "Path", "str"),
        _said("def double", "who", "Named", "int"),
        _said("total: int", "total", "int", "str"),
        _said("names: list", "names", "list[str]", "list[int | str]"),
        _said("total = ", "total", "int", "str"),
        _said("def spun", "values", "list[int]", "list[str]"),
        f"{returned} to return `int` returned `str` in a traced run",
        "14 annotated bindings held to a run's values: 8 differed, 4 couldn't be told",
    ]
    assert not (tmp_path / trace.DEFAULT).exists()


@pytest.mark.parametrize("status", [0, 3])
def test_what_a_checked_run_left_with_stands(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    *,
    status: int,
) -> None:
    """0 where nothing differed, its own status otherwise; the trace is written where it's named."""
    path: Path = _script(tmp_path, monkeypatch, _HOLDS.format(status=status))
    left: pytest.ExceptionInfo[SystemExit]
    if status:
        with pytest.raises(SystemExit) as left:
            _ = trace.main(["--check", "--output", "out.json", path.name])
        assert left.value.code == status
    else:
        assert trace.main(["--check", "--output", "out.json", path.name]) == 0
    assert capsys.readouterr().out.endswith(": 0 differed, 0 couldn't be told\n")
    assert (tmp_path / "out.json").is_file()


# A script whose functions call a hook where the interpreter would report to a recorder: `tell` on a
# line it arrives at, `leave` as it returns what it's given.
_TOLD: Final = """\
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


class Odd:
    __module__ = "tests.stand_ins"


def same(function):
    return function


@same
def bound(tell, leave, value: int, other: "Path" = None, odd: Odd = None, *rest: int) -> int:
    held: int = (tell(), value)[1]
    plain = (tell(), value)[1]
    item: int
    for item in (tell(), [])[1]:
        pass
    del other
    return leave((tell(), held)[1])


def silent(tell, leave, value):
    kept = (tell(), value)[1]
    return leave(kept)


def spun(tell, leave, value: int):
    yield (tell(), value)[1]
"""
_Functions: TypeAlias = "Mapping[str, Callable[..., object]]"  # a script's, by name
_Spun: TypeAlias = "GeneratorType[str, None, None]"  # what a call of `spun` answers


class _Told:
    """A witness told of a script's functions by the hooks they call, and those functions."""

    def __init__(self, tmp_path: Path) -> None:
        """Run `_TOLD` under `tmp_path`."""
        self.path: Path = tmp_path / "told.py"
        _ = self.path.write_text(_TOLD, encoding="utf-8", newline="\n")
        self.witness: witness.Witness = witness.Witness(tmp_path)
        self.functions: _Functions = cast("_Functions", runpy.run_path(str(self.path)))

    def tell(self) -> None:
        """Tell the witness its caller arrived at a line."""
        _ = self.witness.line(_caller())

    def leave(self, value: object) -> object:
        """Tell the witness its caller returns `value`.

        Returns:
          `value`.

        """
        _ = self.witness.left(_caller(), finished=True, returned=True, value=value)
        return value

    def call(self, name: str, *args: object) -> object:
        """Call one of the script's functions with the hooks, then `args`.

        Returns:
          What it returns.

        """
        return self.functions[name](self.tell, self.leave, *args)

    def judged(self) -> dict[str, _Verdict]:
        """Read the witness's verdicts.

        Returns:
          Each binding's line, counts and what differed, by its name; a return's by `<return>`.

        """
        return {
            cast("str", each[3]): (
                cast("int", each[1]),
                cast("list[int]", each[5]),
                cast("list[str]", each[6]),
            )
            for each in self.witness.judged()
        }


def _caller(depth: int = 2) -> FrameType:
    """Find the frame of what called this function's caller.

    Returns:
      It.

    """
    frame: FrameType = cast("FrameType", inspect.currentframe())
    for _ in range(depth):
        frame = cast("FrameType", frame.f_back)
    return frame


def test_a_statements_names_are_held_as_it_ends_and_parameters_as_the_function_returns(
    tmp_path: Path,
) -> None:
    """Each to what the function declares of it; not an undeclared name, an unbound one, or a `*args`."""
    told: _Told = _Told(tmp_path)
    assert told.call("bound", _TEXT, Path()) == _TEXT
    assert told.call("silent", 1) == 1
    assert told.judged() == {
        "held": (17, [0, 1, 0], ["str"]),
        "value": (16, [0, 1, 0], ["str"]),
        "odd": (16, [0, 0, 1], []),
        recording.RETURN: (23, [0, 1, 0], ["str"]),
    }
    assert not told.witness.left(_caller(1))


def test_a_binding_is_judged_a_few_times_and_told_of_by_its_first_values(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """As many times as `_MOST` (50), and of the first 3 types that differed, each once."""
    monkeypatch.setattr(witness, "_MOST", 6)
    told: _Told = _Told(tmp_path)
    value: str | bytes | float | list[int]
    for value in ("a", "b", b"b", 1.5, [1], 2, 3, 4):
        _ = told.call("bound", value)
    assert told.judged()["held"] == (17, [1, 5, 0], ["str", "bytes", "float"])
    assert told.judged()[recording.RETURN][1] == [1, 5, 0]


def test_a_generators_parameters_are_held_as_its_suspended_too(tmp_path: Path) -> None:
    """A follower that can't tell a `yield` from a return (`sys.settrace`) tells of each."""
    told: _Told = _Told(tmp_path)
    made: _Spun = cast("_Spun", told.call("spun", _TEXT))
    assert told.witness.left(cast("FrameType", made.gi_frame))
    assert told.witness.left(cast("FrameType", made.gi_frame), finished=True)
    assert told.judged() == {"value": (31, [0, 2, 0], ["str"])}


def test_a_file_that_cant_be_read_again_says_nothing(tmp_path: Path) -> None:
    """Gone since the recorder read it: its functions are recorded on, and none judged."""
    told: _Told = _Told(tmp_path)
    assert told.call("bound", _TEXT) == _TEXT
    before: dict[str, _Verdict] = told.judged()
    told.path.unlink()
    told.witness.read.clear()
    told.witness.declared.clear()
    assert told.call("bound", _TEXT) == _TEXT
    assert told.judged() == before
    assert told.witness.read == {"told.py": {}}


class _Fake:  # pylint: disable=too-few-public-methods
    """A class that says it's a test module's."""

    __module__ = "tests.fake"


def test_an_annotation_is_evaluated_where_its_function_runs() -> None:
    """Its quoted text too, and with the module's guarded imports where a name's missing; else it's unset."""
    module: ModuleType = ModuleType("pkg.core")
    odd: type[_Fake] = _Fake
    vars(module)["Odd"] = odd
    exec("import sys\nframe = sys._getframe()\n", vars(module))  # ruff: ignore[exec-builtin]  # pylint: disable=exec-used
    frame: FrameType = cast("FrameType", vars(module)["frame"])
    assert witness.patched(odd, witness.module_of(frame))
    assert witness.evaluated("Odd", frame, ()) is odd
    assert witness.evaluated("'int'", frame, ()) is int
    assert witness.evaluated("1 / 0", frame, ()) is witness.UNSET
    assert witness.evaluated("Missing", frame, ("import nowhere",)) is witness.UNSET
    assert witness.evaluated("Missing", frame, ("import nowhere", "from typing import Any as Missing"))


class _Unchecked(Protocol):  # pylint: disable=too-few-public-methods
    """A protocol `isinstance` can't check."""

    name: str

    def close(self) -> None:
        """Close it."""


class _Whole:  # pylint: disable=too-few-public-methods
    """What has an unchecked protocol's members, and isn't declared one."""

    name: str = "a"

    def close(self) -> None:
        """Close it."""


class _Refusing(type):
    """A class's class that can't say what its instances are, or what module it's of."""

    @override
    def __instancecheck__(cls, instance: object) -> bool:
        """Refuse to say.

        Raises:
          TypeError: as an unchecked protocol does.

        """
        raise TypeError(instance)

    @override
    def __getattribute__(cls, name: str) -> object:
        """Refuse to say what module the class is of.

        Returns:
          Any other attribute.

        Raises:
          RuntimeError: for its module.

        """
        if name == _OF:
            raise RuntimeError(name)
        return cast("object", super().__getattribute__(name))


class _Failing(type):
    """A class's class whose check of an instance fails."""

    @override
    def __instancecheck__(cls, instance: object) -> bool:
        """Fail.

        Raises:
          RuntimeError: always.

        """
        raise RuntimeError(instance)


_Count = typing.NewType("_Count", int)


class _Row(typing.TypedDict):
    """A row of one name."""

    name: str


_FORMS: Final[tuple[_Case, ...]] = (
    (1, typing.Annotated[int, "a count"], True),
    ("a", typing.Annotated[int, "a count"], False),
    ("a", typing.Literal["a", "b"], True),
    (int, type[int], True),
    (1, type[int], False),
    (len, collections.abc.Callable[..., int], True),
    (1, collections.abc.Callable[..., int], False),
    (1, _Count, True),
    ({"name": "a"}, _Row, True),
    (1, _Row, False),
    (1, "int", None),
)


@pytest.mark.parametrize(("value", "hint", "held"), _FORMS)
def test_a_special_form_is_held_to_what_it_stands_for(
    value: object,
    hint: object,
    held: bool | None,  # ruff: ignore[boolean-type-hint-positional-argument]
) -> None:
    """What it wraps, its values, a class, a callable, a supertype, a `dict`; text says nothing."""
    assert witness.holds(value, hint) is held


def test_a_protocol_isinstance_cant_check_is_held_to_its_members_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each of them, as `isinstance` asks of a checkable one; a class that names none says nothing."""
    assert witness.holds(_Whole(), _Unchecked) is True
    assert witness.holds(Path(), _Unchecked) is False
    assert witness.holds(1, _Refusing("Refusing", (), {})) is None
    marked: _Refusing = _Refusing("Marked", (), {"_is_protocol": True, "name": ""})
    assert witness.holds(_Whole(), marked) is True  # as Python 3.11's protocols are read
    monkeypatch.setattr(witness, "_attributes", None)
    assert witness.holds(_Whole(), marked) is None


def test_what_a_value_raises_of_being_asked_reaches_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Its class's check, its class's module, or its spelling: it can't be told, or is `?`."""
    assert witness.fits(1, _Failing("Failing", (), {})) is None
    assert witness.fits(1, witness.UNSET) is None
    assert witness.fits(1, int) is True
    assert witness.kind_of(_Refusing("Refusing", (), {})()) == recording.UNKNOWN
    assert witness.seen([]) == witness.kind_of([]).replace(recording.SEPARATOR, ".")

    def failing(_value: object) -> str:
        raise RuntimeError

    monkeypatch.setattr(recording, "spelled", failing)
    assert witness.seen(1) == witness.kind_of(1).replace(recording.SEPARATOR, ".")


def test_a_runs_processes_verdicts_are_joined(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A pytest process a checked run started writes its own beside its trace; one cut short is left out."""
    script: Path = tmp_path / "many.py"
    _ = script.write_text(_MANY, encoding="utf-8", newline="\n")
    monkeypatch.setenv(trace.ENVIRONMENT, json.dumps(["0", str(tmp_path), str(tmp_path), "check"]))
    trace.pytest_configure()
    try:
        _ = cast("_Functions", runpy.run_path(str(script)))["taken"]("a")
    finally:
        trace.pytest_unconfigure()
    part: Path = tmp_path / f"{os.getpid()}{witness.VERDICTS}"
    key: list[str | int] = ["many.py", 2, 5, "held", "int"]
    assert [*key, [0, 1, 0], ["str"]] in cast("list[_Judged]", json.loads(part.read_text(encoding="utf-8")))
    _ = (tmp_path / f"0{witness.VERDICTS}").write_text("[", encoding="utf-8")
    other: list[_Judged] = [
        [*key, [1, 2, 0], ["str", "bytes", "float"]],
        [*key, [0, 1, 0], ["list[int]"]],
        ["many.py", 9, 1, "other", "int", [0, 0, 2], []],
    ]
    found: dict[witness.Key, _Counted] = witness.gathered(tmp_path, other)
    assert found["many.py", 2, 5, "held", "int"] == ([1, 4, 0], ["str", "bytes", "float"])
    assert witness.report(found)[-1].endswith(": 2 differed, 1 couldn't be told")
