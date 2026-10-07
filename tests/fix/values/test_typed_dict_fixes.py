# SPDX-License-Identifier: MIT
"""`--fix` for a `TypedDict`'s key, read by a literal: `d["key"]`, `d.get("key")`."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import project
from constricter.rules import annotations

_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_LOCAL: Final = """
import typing
from typing import Generic, NotRequired, ReadOnly, Required, TypedDict, TypeVar

T = TypeVar("T")


class Base(TypedDict):
    name: str
    tags: list[str]


class Movie(Base, total=False):
    year: Required[int]
    score: NotRequired[ReadOnly[float]]
    parent: "Base"


class Loose(typing.TypedDict):
    extra: dict[str, typing.Any]


class Boxed(TypedDict, Generic[T]):
    item: T
    count: int


class Plain:
    name: str


def use(m: Movie, loose: Loose, boxed: Boxed[int], plain: Plain, key: str, maybe: Movie | None) -> None:
    name = m["name"]
    year = m["year"]
    score = m["score"]
    parent = m["parent"]
    for tag in m["tags"]:
        print(tag)
    got = m.get("year")
    kept = m.get("name", "")
    none = m.get("score", None)
    other = m.get("year", "")
    missing = m["missing"]
    computed = m[key]
    extra = loose["extra"]
    for word in loose["extra"]:
        print(word)
    count = boxed["count"]
    attribute = plain["name"]
    narrowed = maybe["name"]
    made = Movie(name="", tags=[], year=1)
    guessed = made["year"]
"""
_SHAPES: Final = """
from typing import Literal, TypedDict


class Shape(TypedDict):
    kind: Literal["circle", "square"]
    sides: int
    inner: "Shape"
"""
_MAIN: Final = """
import pkg.shapes as s
from pkg.shapes import Shape


class Solid(Shape):
    depth: int


def f(shape: Shape, other: s.Shape, solid: Solid) -> None:
    sides = shape["sides"]
    again = other.get("sides")
    inner = shape["inner"]
    kind = shape["kind"]
    inherited = solid["sides"]
    own = solid["depth"]
"""


def test_a_literal_key_of_a_typed_dict_is_its_declared_type() -> None:
    """Its own or a base's, less `Required` and its like; `get` is that or `None`, or its default's."""
    fixes: _Fixes = {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_LOCAL))}
    assert fixes == {
        "name": ("str", False),
        "year": ("int", False),
        "score": ("float", False),
        "parent": ("Base", False),
        "tag": ("str", False),
        "got": ("int | None", False),
        "kept": ("str", False),
        "none": ("float | None", False),
        "word": ("str", False),  # a vague key's elements
        "narrowed": ("str", False),
        "made": ("Movie", True),
        "guessed": ("int", True),  # of a guessed receiver
        **dict.fromkeys(("other", "missing", "computed", "extra", "count", "attribute"), (None, False)),
    }
    kinds: dict[str, frozenset[str]] = {
        o.name: o.edit.kinds for o in check_source(textwrap.dedent(_LOCAL)) if o.edit is not None
    }
    assert kinds["year"] == {"subscript"}
    assert kinds["tag"] == {"loop", "subscript"}
    assert kinds["got"] == {"method"}
    assert kinds["kept"] == {"literal", "method"}


def test_a_typed_dicts_annotations_are_its_keys() -> None:
    """Under `TypedDict` or one of the module's; a generic one's, and a plain class's, are attributes."""
    found: dict[str, dict[str, str]] = annotations.classes(ast.parse(textwrap.dedent(_LOCAL)))
    assert found == {
        "Base": {"[name]": "str", "[tags]": "list[str]"},
        "Movie": {"[year]": "int", "[score]": "float", "[parent]": "Base"},
        "Loose": {"[extra]": "dict[str, typing.Any]"},
        "Boxed": {"item": "T", "count": "int"},
        "Plain": {"name": "str"},
    }


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def test_another_files_typed_dict_is_keyed_too(tmp_path: Path) -> None:
    """However it's spelled, by the keys the file reads; a class under it has its keys, not its own."""
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "shapes.py", _SHAPES)
    main: Path = _write(tmp_path / "main.py", _MAIN)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    imported: project.Imported = project.imported(catalog, main)
    assert imported.classes.attributes["s.Shape"] == {
        "[kind]": "Literal['circle', 'square']",
        "[sides]": "int",
        "[inner]": "s.Shape",
    }
    assert imported.classes.attributes["Shape"] == {
        **imported.classes.attributes["s.Shape"],
        "[inner]": "Shape",
    }
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, main, {}),
    )
    assert {o.name: o.fix for o in found} == {
        "sides": "int",
        "again": "int | None",
        "inner": "Shape",
        "kind": "Literal['circle', 'square']",
        "inherited": "int",
        "own": None,
    }
