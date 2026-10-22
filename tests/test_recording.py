"""What a recorder keeps by class, and how it spells a value as an annotation would write its type."""

import collections
import fractions
import importlib.util
import io
import pathlib
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast
from unittest import mock

import pytest

from constricter import recording

if TYPE_CHECKING:
    from importlib.machinery import ModuleSpec
    from types import ModuleType

_KEPT: list[str] = ["int", "int", recording.UNKNOWN, recording.UNKNOWN, "Odd", "Odd"]
_ASKED: list[str] = ["int", "float", "float", "Odd", "Odd"]
# A class that can't be hashed: its class of classes has no `__hash__`.
_ODD: Final = type("Unhashed", (type,), {"__hash__": None})("Odd", (), {})


def test_what_a_class_says_is_kept_but_for_one_that_cant_be() -> None:
    """Not a class no annotation names yet, which its module may bind later; nor one with no hash."""
    asked: list[str] = []

    @recording.by_class
    def kept(cls: type) -> str:
        asked.append(cls.__name__)
        return recording.UNKNOWN if cls is float else cls.__name__

    assert [kept(int), kept(int), kept(float), kept(float), kept(_ODD), kept(_ODD)] == _KEPT
    assert asked == _ASKED


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
