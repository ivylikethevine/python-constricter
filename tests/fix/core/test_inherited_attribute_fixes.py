# SPDX-License-Identifier: MIT
"""`--fix` for an attribute a class doesn't declare: the base's that does, in method resolution order."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import project
from constricter.rules.tables import module_tables

_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_SOURCE: Final = """
import other
from typing import Generic, Self, TypeVar

T = TypeVar("T")


class Base:
    limit: int = 3
    label: str
    hidden: str

    def __init__(self) -> None:
        self.size: float = 1.0

    @property
    def twin(self) -> Self:
        return self

    @property
    def text(self) -> bytes:
        return b""


class Middle(Base):
    label: bytes

    def hidden(self):
        return 1


class Child(Middle):
    def f(self) -> None:
        child_limit = self.limit
        child_label = self.label
        child_hidden = self.hidden
        child_size = self.size
        child_twin = self.twin
        child_text = self.text
        child_missing = self.missing

    @classmethod
    def g(cls) -> None:
        side_limit = cls.limit
        side_label = cls.label


class Boxed(Generic[T]):
    count: int


class Under(Boxed[int]):
    def f(self) -> None:
        under_count = self.count


class Far(other.Base):
    def f(self) -> None:
        far_limit = self.limit


def use(child: Child, middle: Middle) -> None:
    used_size = child.size
    used_label = middle.label
    used_twin = middle.twin
"""
_BASE: Final = """
class Base:
    limit: int

    def __init__(self) -> None:
        self.size: float = 1.0

    @property
    def twin(self) -> "Base":
        return self


class Mixed(Base):
    extra: str
"""
_MAIN: Final = """
from pkg.base import Base, Mixed


class Child(Base):
    def f(self) -> None:
        limit = self.limit
        size = self.size
        twin = self.twin


class Grand(Child):
    limit = 5

    def f(self) -> None:
        size = self.size


def use(mixed: Mixed) -> None:
    inherited = mixed.limit
    own = mixed.extra
"""


def test_an_inherited_attribute_is_the_base_class_one() -> None:
    """An annotation's, a `self.x: T`'s or a property's, of the first base that declares it."""
    fixes: _Fixes = {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_SOURCE))}
    assert fixes == {
        "child_limit": ("int", False),
        "child_label": ("bytes", False),  # `Middle` comes before `Base`
        "child_size": ("float", False),
        "child_twin": ("Child", False),  # `Self`: the receiver's own class
        "child_text": ("bytes", False),
        "side_limit": ("int", False),
        "used_size": ("float", False),
        "used_label": ("bytes", False),
        "used_twin": ("Middle", False),
        # `Middle` binds `hidden` another way; a class's attribute needs a value (`label` has none).
        **dict.fromkeys(("child_hidden", "child_missing", "side_label"), (None, False)),
        # A generic base's members depend on its arguments, and a base out of sight has its own.
        **dict.fromkeys(("under_count", "far_limit"), (None, False)),
    }


def test_a_modules_classes_hold_their_bases_attributes() -> None:
    """Each class's own first, then its bases' that nothing before them binds."""
    found: dict[str, dict[str, str]] = module_tables(ast.parse(textwrap.dedent(_SOURCE))).classes
    assert found["Middle"] == {
        "label": "bytes",
        "limit": "int",
        "size": "float",
        "twin": "Middle",
        "text": "bytes",
    }
    assert found["Child"] == {**found["Middle"], "twin": "Child"}
    assert found["Under"] == {}


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def test_another_files_base_gives_its_attributes(tmp_path: Path) -> None:
    """Its own and those it takes from its module's classes; not one typed as the base itself."""
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "base.py", _BASE)
    main: Path = _write(tmp_path / "main.py", _MAIN)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, main, {}),
    )
    assert {(o.line, o.name): o.fix for o in found} == {
        (7, "limit"): "int",
        (8, "size"): "float",
        (9, "twin"): None,  # the base's own class, or its `Self`
        (16, "size"): "float",  # through `Child`
        (20, "inherited"): "int",
        (21, "own"): "str",
    }


_REBOUND: Final = """
from functools import cached_property


class Base:
    suffix: str = ""
    limit: int = 3


class Own(Base):
    def read(self) -> None:
        text = self.suffix
        size = self.limit

    @cached_property
    def suffix(self):
        return "" if self.limit else " FROM DUAL"
"""


def test_a_name_the_class_binds_itself_isnt_its_bases() -> None:
    """A method of that name is the class's own: the base's annotation, once written, changes nothing."""
    found: list[Offence] = check_source(textwrap.dedent(_REBOUND))
    assert {o.name: o.fix for o in found} == {"text": None, "size": "int"}
