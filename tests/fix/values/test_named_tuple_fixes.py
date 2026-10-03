# SPDX-License-Identifier: MIT
"""`--fix` for what's unpacked by its parts: a named tuple's fields, and a `with` statement's target."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import project
from constricter.fix.values import entered, targets

# Each offence's fix and whether it's a guess.
_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_TUPLES: Final = """
from typing import Any, Generic, NamedTuple, TypeVar

T = TypeVar("T")


class Pair(NamedTuple):
    left: dict[str, int]
    right: "str"

    def swapped(self) -> "Pair":
        return self


class Loose(NamedTuple):
    data: dict[str, Any]
    name: str


class One(NamedTuple):
    only: int


class Boxed(NamedTuple, Generic[T]):
    item: T
    count: int


class Twice(NamedTuple):
    a: int
    b: int


class Twice(NamedTuple):
    a: str
    b: str


class Holder:
    @property
    def pair(self) -> Pair:
        return Pair({}, "")


def make() -> Pair:
    return Pair({}, "")


def loose() -> Loose:
    return Loose({}, "")


def f(holder: Holder, pair: Pair, pairs: list[Pair], one: One, twice: Twice) -> None:
    a, b = holder.pair
    c, d = make()
    e, *g = pair
    data, name = loose()
    (only,) = one
    h, i = twice
    j, k, m = pair
    whole = pair
    for n, (o, p) in enumerate(pairs):
        pass
    q = [s for r, s in pairs]
"""
_ENTERED: Final = """
from collections.abc import Generator, Iterator
from contextlib import contextmanager
from typing import Any, NamedTuple, Self


class Pair(NamedTuple):
    left: int
    right: str


class Defs:
    @contextmanager
    def entry(self, key: str) -> Generator[tuple[str, int | None]]:
        yield key, None

    @contextmanager
    def itself(self) -> Iterator[Self]:
        yield self

    def __enter__(self) -> tuple[str, dict[str, Any]]:
        return "", {}


class More(Defs):
    def __enter__(self) -> Pair:
        return Pair(1, "")


class Again:
    @contextmanager
    def entry(self) -> Iterator[int]:
        yield 1


class Again:
    pass


class Owner:
    def __init__(self) -> None:
        self.defs = Defs()

    async def later(self, more: More) -> None:
        async with more as (soon, enough):
            pass

    def run(self, defs: Defs, more: More, again: Again, other) -> None:
        with self.defs.entry("k") as (ref, found):
            pass
        with defs.entry("k") as both, more.entry("k") as (key, value):
            pass
        with defs as (text, vague), more as (left, right):
            pass
        with defs.itself() as same, again.entry() as count, other.entry() as unknown:
            pass
        with defs.entry("k") as (a, b, c):
            pass
"""
_SHAPES: Final = """
from typing import NamedTuple, TypeAlias, TypeVar

T = TypeVar("T")
Pair: TypeAlias = tuple[int, str]
Plain = tuple[bytes, float]
Generic = tuple[T, T]
Twice = tuple[int, int]
Twice = tuple[str, str]
if T:
    Nested = tuple[float, float]


def pair() -> Pair:
    return 1, ""


class Namespaces(NamedTuple):
    globals: dict[str, int]
    locals: list[str]


class Resolver:
    @property
    def namespaces(self) -> Namespaces:
        return Namespaces({}, [])
"""
_USING: Final = """
from pkg.shapes import Resolver


def f(resolver: Resolver) -> None:
    globalns, localns = resolver.namespaces
"""
_SPELLING: Final = """
import pkg.shapes as shapes
from pkg.shapes import Namespaces, Plain, pair


def f(pair: shapes.Namespaces, other: Namespaces, plain: Plain) -> None:
    first, second = pair
    third, fourth = other
    left, right = pair()
    raw, ratio = plain
"""
_SMALL: Final = """
class _stack:
    pass


class Config:
    pass


def helper() -> None:
    pass


def f(config: Config | None = None) -> None:
    made = _stack()
    called = helper()
    config = config or Config()
    copied = config
"""


def _fixes(source: str) -> _Fixes:
    found: list[Offence] = check_source(textwrap.dedent(source))
    return {o.name: (o.fix, o.unsafe) for o in found}


def test_a_named_tuple_is_unpacked_by_its_fields() -> None:
    """Each name takes its field's type, in order: but a vague field's, or a count that doesn't match.

    Not a class with one field, a generic one, or one defined twice.
    """
    tree: ast.Module = ast.parse(textwrap.dedent(_TUPLES))
    assert targets.named_tuples(tree) == {
        "Pair": "tuple[dict[str, int], str]",
        "Loose": "tuple[dict[str, Any], str]",
    }
    assert _fixes(_TUPLES) == {
        "a": ("dict[str, int]", False),
        "b": ("str", False),
        "c": ("dict[str, int]", False),
        "d": ("str", False),
        "e": ("dict[str, int]", False),
        "g": ("list[str]", False),
        "name": ("str", False),
        "whole": ("Pair", False),
        "n": ("int", False),
        "o": ("dict[str, int]", False),
        "p": ("str", False),
        "q": ("list[str]", False),
        **dict.fromkeys(("data", "only", "h", "i", "j", "k", "m"), (None, False)),
    }


def test_a_with_target_that_unpacks_is_split_as_an_unpacking_is() -> None:
    """Over what the manager's `__enter__` returns, or a `@contextmanager` method declares it yields.

    Such a method types its call on a receiver of a known type (a guess, where that is one), a
    class's own or the base's that defines it; not one yielding `Self`, nor a class defined twice.
    A vague part's name gets no fix, and an `async with`'s target none.
    """
    tree: ast.Module = ast.parse(textwrap.dedent(_ENTERED))
    assert entered.managers(tree) == {"Defs.entry": "tuple[str, int | None]"}
    found: list[Offence] = check_source(textwrap.dedent(_ENTERED))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "ref": ("str", True),  # `self.defs`, typed by its assignment
        "found": ("int | None", True),
        "both": ("tuple[str, int | None]", False),
        "key": ("str", False),  # the base's method
        "value": ("int | None", False),
        "text": ("str", False),
        "left": ("int", False),  # a named tuple's fields
        "right": ("str", False),
        **dict.fromkeys(
            ("vague", "same", "count", "unknown", "a", "b", "c", "soon", "enough"),
            (None, False),
        ),
    }
    kinds: dict[str, frozenset[str]] = {o.name: o.edit.kinds for o in found if o.edit is not None}
    assert kinds["ref"] == {"assigned", "method", "unpack"}
    assert kinds["both"] == {"method"}
    assert kinds["left"] == {"method", "unpack"}


def test_another_files_named_tuple_is_unpacked_too(tmp_path: Path) -> None:
    """One the file imports, however it spells it, and one a type written for it names."""
    name: str
    source: str
    files: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/shapes.py": _SHAPES,
        "using.py": _USING,
        "spelling.py": _SPELLING,
    }
    for name, source in files.items():
        path: Path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(source, encoding="utf-8")
    using: Path = tmp_path / "using.py"
    spelling: Path = tmp_path / "spelling.py"
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    fields: str = "tuple[dict[str, int], list[str]]"
    assert schedule.outside(catalog, using, {}).tuples == {"Namespaces": fields}
    assert schedule.outside(catalog, spelling, {}).tuples == {
        "shapes.Namespaces": fields,
        "Namespaces": fields,
        "Plain": "tuple[bytes, float]",
        "shapes.Pair": "tuple[int, str]",
        "shapes.Plain": "tuple[bytes, float]",
        "shapes.Nested": "tuple[float, float]",
    }
    found: list[Offence] = check_source(_USING, outside=schedule.outside(catalog, using, {}))
    assert {o.name: o.fix for o in found} == {"globalns": "dict[str, int]", "localns": "list[str]"}
    found = check_source(_SPELLING, outside=schedule.outside(catalog, spelling, {}))
    assert {o.name: o.fix for o in found} == {
        "first": "dict[str, int]",
        "second": "list[str]",
        "third": "dict[str, int]",
        "fourth": "list[str]",
        "left": "int",
        "right": "str",
        "raw": "bytes",
        "ratio": "float",
    }
    assert targets.named_tuples(ast.parse(textwrap.dedent(_SHAPES))) == {
        "Namespaces": fields,
        "Pair": "tuple[int, str]",
        "Plain": "tuple[bytes, float]",
        "Nested": "tuple[float, float]",
    }


def test_a_call_to_a_class_the_module_defines_constructs_it() -> None:
    """Whatever its name's case (a guess, as a capitalised call is); a function's call doesn't.

    And a name bound again to a guessed value is that value's type from there on, as a guess
    (`config or Config()`, declared `Config | None`).
    """
    assert _fixes(_SMALL) == {"made": ("_stack", True), "called": (None, False), "copied": ("Config", True)}
