# SPDX-License-Identifier: MIT
"""`--fix` for a classmethod or staticmethod called on its class: `Box.make()`, by its declared return."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

import pytest

from constricter import Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import decorated, project
from constricter.rules import annotations
from constricter.rules.decorators import Held

_Fixes: TypeAlias = dict[str, str | None]
_LOCAL: Final = """
import functools
from abc import abstractmethod
from typing import Generic, Self, TypeVar

import other

T = TypeVar("T")
F = TypeVar("F")


def same(func: F) -> F:
    return func


class Box:
    @classmethod
    def make(cls, size: int) -> "Box":
        return cls()

    @classmethod
    def new(cls) -> Self:
        return cls()

    @staticmethod
    def count() -> int:
        return 1

    @classmethod
    @functools.cache
    @same
    def cached(cls) -> list[str]:
        return []

    @other.registered
    @staticmethod
    def registered() -> int:
        return 1

    @classmethod
    @staticmethod
    def twice() -> int:
        return 1

    @classmethod
    def nothing(cls) -> None:
        return None

    @property
    @abstractmethod
    def size(self) -> int: ...

    def plain(self) -> int:
        return 1

    class Inner:
        @staticmethod
        def deep() -> int:
            return 1


class Many(Generic[T]):
    @classmethod
    def make(cls) -> int:
        return 1


class Twice:
    @staticmethod
    def count() -> int:
        return 1


class Twice:
    @staticmethod
    def count() -> int:
        return 1


class Rebound:
    @staticmethod
    def count() -> int:
        return 1


def use(box: Box, Rebound) -> None:
    made = Box.make(1)
    new = Box.new()
    count = Box.count()
    cached = Box.cached()
    size = box.size
    registered = Box.registered()
    twice = Box.twice()
    nothing = Box.nothing()
    plain = Box.plain(box)
    deep = Inner.deep()
    many = Many.make()
    again = Twice.count()
    rebound = Rebound.count()
"""
_TYPING: Final = """
from typing import TypeVar

F = TypeVar("F")
"""
_MODELS: Final = """
import other
from pkg._typing import F
from typing import Self


def compat(method: F) -> F:
    return method


def boxed(method: int) -> int:
    return method


class Row:
    @classmethod
    def make(cls, size: int) -> "Row":
        return cls()

    @classmethod
    def new(cls) -> Self:
        return cls()

    @staticmethod
    def names() -> list[str]:
        return []

    @classmethod
    @compat
    def from_pairs(cls, pairs: list[tuple[int, int]]) -> "Row":
        return cls()

    @staticmethod
    @boxed
    def boxed() -> int:
        return 1

    @other.deco
    @classmethod
    def elsewhere(cls) -> int:
        return 1

    class Inner:
        @staticmethod
        @compat
        def deep() -> int:
            return 1


def own() -> None:
    made = Row.make(1)
    pairs = Row.from_pairs([])
    boxed = Row.boxed()
"""
_SHADOWED: Final = """
from pkg._typing import F


def compat(method: F) -> F:
    return method


class Row:
    @staticmethod
    @compat
    def count() -> int:
        return 1


def own(Row: int) -> None:
    count = Row.count()
"""
_MAIN: Final = """
import pkg
import pkg.models
import pkg.models as m
from pkg import Row
from pkg.models import Row as R, compat


def f(m: int) -> None:
    made = Row.make(1)
    new = R.new()
    names = pkg.Row.names()
    dotted = pkg.models.Row.make(2)
    pairs = Row.from_pairs([])
    boxed = Row.boxed()
    missing = Row.missing()
    shadowed = m.Row.make(3)
    function = compat.make()
    unknown = nowhere.Row.make()
"""


def test_a_class_side_method_called_on_its_class_gives_its_declared_return() -> None:
    """A classmethod's or staticmethod's, under decorators that give it back; `Self` is the class."""
    fixes: _Fixes = {o.name: o.fix for o in check_source(textwrap.dedent(_LOCAL))}
    assert fixes == {
        "made": "Box",
        "new": "Box",
        "count": "int",
        "cached": "list[str]",
        "size": "int",
        **dict.fromkeys(
            ("registered", "twice", "nothing", "plain", "deep", "many", "again", "rebound"),
        ),
    }


def test_an_instance_and_a_subclass_have_the_class_side_methods_too() -> None:
    """`self.count()` is the staticmethod's return; a subclass takes its base's, `Self` as itself."""
    source: str = """
    from typing import Self


    class Base:
        @staticmethod
        def pair() -> tuple[str, bool]:
            return "", True

        @classmethod
        def make(cls) -> Self:
            return cls()

        @classmethod
        def base(cls) -> "Base":
            return cls()

        def run(self) -> None:
            name, flag = self.pair()


    class Sub(Base):
        def pair(self) -> int:
            return 1

        @classmethod
        def more(cls) -> None:
            own = cls.base()


    def use(base: Base, sub: Sub) -> None:
        both = base.pair()
        hidden = sub.pair()
        made = Sub.make()
        plain = Sub.base()
        mine = sub.make()
        theirs = base.make()
        shadowed = Sub.pair()
    """
    fixes: _Fixes = {o.name: o.fix for o in check_source(textwrap.dedent(source))}
    assert fixes == {
        "name": "str",
        "flag": "bool",
        "own": "Base",
        "both": "tuple[str, bool]",
        "hidden": "int",
        "made": "Sub",
        "plain": "Base",
        "mine": "Sub",
        "theirs": "Base",
        "shadowed": None,  # `Sub` binds `pair` itself, a plain method
    }


def test_class_side_methods_under_other_decorators_are_held() -> None:
    """Those the module can't vouch for alone, each with those decorators."""
    assert annotations.held_class_methods(ast.parse(textwrap.dedent(_LOCAL))) == {
        "Box": {"registered": Held("int", ("other.registered",))},
    }
    assert annotations.held_class_methods(ast.parse(textwrap.dedent(_MODELS))) == {
        "Row": {
            "from_pairs": Held("Row", ("compat",)),
            "boxed": Held("int", ("boxed",)),
            "elsewhere": Held("int", ("other.deco",)),
        },
        "Inner": {"deep": Held("int", ("compat",))},
    }


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


@pytest.fixture(name="catalog")
def _catalog(tmp_path: Path) -> project.Index:
    """Index a package whose class's class-side methods another file calls.

    Returns:
      The index, with the decorators it vouches for.

    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "from pkg.models import Row as Row\n")
    _ = _write(tmp_path / "pkg" / "_typing.py", _TYPING)
    _ = _write(tmp_path / "pkg" / "models.py", _MODELS)
    _ = _write(tmp_path / "pkg" / "shadowed.py", _SHADOWED)
    _ = _write(tmp_path / "main.py", _MAIN)
    return decorated.passed(project.index(sorted(tmp_path.rglob("*.py"))))


def test_another_files_class_side_method_types_its_calls(catalog: project.Index, tmp_path: Path) -> None:
    """Through imports and re-exports, however the class is spelled; not through a name bound as a value."""
    main: Path = tmp_path / "main.py"
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, main, {}),
    )
    assert {o.name: o.fix for o in found} == {
        "made": "Row",
        "new": "R",
        "names": "list[str]",
        "dotted": "pkg.models.Row",
        "pairs": "Row",
        **dict.fromkeys(("boxed", "missing", "shadowed", "function", "unknown")),
    }


def test_the_index_vouches_for_a_class_side_methods_decorators(
    catalog: project.Index,
    tmp_path: Path,
) -> None:
    """A decorator whose type variable is imported gives the method back, by the index."""
    assert catalog.modules["pkg.models"].vouched_sides == {("Row", "from_pairs"), ("Inner", "deep")}
    assert catalog.modules["pkg.models"].sides["Inner"] == {"deep": "int"}
    models: Path = tmp_path / "pkg" / "models.py"
    # A nested class's name isn't the module's, and neither is one a function binds as a value.
    assert decorated.own(catalog, models) == {"Row.from_pairs": "Row"}
    assert decorated.own(catalog, tmp_path / "pkg" / "shadowed.py") == {}
    found: list[Offence] = check_source(
        models.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, models, {}),
    )
    assert {o.name: o.fix for o in found} == {"made": "Row", "pairs": "Row", "boxed": None}
