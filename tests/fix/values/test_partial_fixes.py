# SPDX-License-Identifier: MIT
"""`--fix` for an unpacked call whose declared return is a tuple with a vague part: the other parts."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Checks, Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import project
from constricter.rules import annotations

_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_LOCAL: Final = """
from typing import Any, Tuple


def collect(n: int) -> tuple[list[str], dict[str, Any]]:
    return [], {}


def anything() -> tuple[Any, ...]:
    return ()


def all_vague() -> Tuple[Any, dict[str, Any]]:
    return 1, {}


def plain() -> tuple[int, str]:
    return 1, ""


class Schema:
    def common(self) -> tuple[int, dict[str, Any]]:
        return 1, {}

    @staticmethod
    def info() -> "Tuple[Any, bool]":
        return 1, True

    def same(self) -> "Schema":
        return self

    def run(self) -> None:
        schema, metadata = self.common()
        value, flag = self.info()
        whole = self.common()


class Child(Schema):
    pass


def use(gen: Schema, child: Child) -> None:
    names, extra = collect(1)
    a, b = anything()
    c, d = all_vague()
    e, g = gen.common()
    h = collect(1)
    i, j, k = collect(1)
    m, n = Box().common()
    o, p = child.common()
    q, r = gen.same().common()
    made = Schema()
    s, t = made.common()
    u, v = unknown.common()
"""
_UTIL: Final = """
from typing import Any


def collect(n: int) -> tuple[list[str], dict[str, Any]]:
    return [], {}


class Schema:
    def common(self) -> tuple[int, dict[str, Any]]:
        return 1, {}

    def whole(self) -> int:
        return 1
"""
_MAIN: Final = """
import pkg.util as u
from pkg.util import Schema, collect


def f(gen: Schema) -> None:
    names, extra = collect(1)
    again, more = u.collect(2)
    size, metadata = gen.common()
    whole = gen.common()
"""
_HELD: Final = """
from typing import Any, Callable, cast


def hints(obj: object) -> dict[str, Any]:
    return {}


def anything() -> Any:
    return 1


def pair() -> tuple[dict[str, Any], int]:
    return {}, 1


class Schema:
    @property
    def extra(self) -> dict[str, Any]:
        return {}

    def fields(self) -> dict[str, list[Any]]:
        return {}


def use(schema: Schema, raw: object, make: Callable[[], list[Any]]) -> None:
    found = hints(raw)
    for name in found:
        print(name)
    for key, value in hints(raw).items():
        print(key, value)
    count = len(found)
    names = sorted(found)
    extra = schema.extra
    for word in extra:
        print(word)
    for field in schema.fields():
        print(field)
    cast_to = cast("dict[str, Any]", raw)
    for part in cast_to:
        print(part)
    made = make()
    size = len(made)
    first, second = pair()
    for inner in first:
        print(inner)
    whatever = anything()
    copied = whatever
    total = {"a": 1}
    total = hints(raw)
    declared: dict[str, int] = hints(raw)
    for later in total:
        print(later)
"""


def test_a_vague_type_is_the_names_and_no_fix() -> None:
    """What's read of it is typed: a `dict[str, Any]`'s keys; a later binding to one stays unknown."""
    found: list[Offence] = check_source(textwrap.dedent(_HELD))
    assert {o.code for o in found} == {"LVA001", "LVA002"}  # the value fits what `declared` says
    fixes: _Fixes = {o.name: (o.fix, o.unsafe) for o in found}
    assert fixes == {
        "name": ("str", False),
        "key": ("str", False),
        "count": ("int", False),
        "names": ("list[str]", False),
        "word": ("str", False),
        "field": ("str", False),
        "part": ("str", False),
        "size": ("int", False),
        "second": ("int", False),
        "inner": ("str", False),
        "total": ("dict[str, int]", True),  # bound again to a value of no certain type
        "later": ("str", True),
        **dict.fromkeys(
            ("found", "value", "extra", "cast_to", "made", "first", "whatever", "copied"),
            (None, False),
        ),
    }
    allowed: _Fixes = {
        o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_HELD), checks=Checks(vague=0))
    }
    assert allowed["found"] == ("dict[str, Any]", False)
    assert allowed["name"] == ("str", False)


def test_an_unpacked_call_takes_the_parts_that_arent_vague() -> None:
    """A function's or a method's declared tuple; the vague parts, and the call whole, stay untyped."""
    fixes: _Fixes = {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_LOCAL))}
    assert fixes == {
        "schema": ("int", False),
        "flag": ("bool", False),
        "names": ("list[str]", False),
        "e": ("int", False),
        "o": ("int", False),  # the base's method
        "q": ("int", False),
        "made": ("Schema", True),
        "s": ("int", True),  # of a guessed receiver
        **dict.fromkeys(
            ("metadata", "value", "whole", "extra", "a", "b", "c", "d", "g", "h", "i", "j", "k"),
            (None, False),
        ),
        **dict.fromkeys(("m", "n", "p", "r", "t", "u", "v"), (None, False)),
    }
    kinds: dict[str, frozenset[str]] = {
        o.name: o.edit.kinds for o in check_source(textwrap.dedent(_LOCAL)) if o.edit is not None
    }
    assert kinds["names"] == {"call", "unpack"}
    assert kinds["e"] == {"method", "unpack"}
    assert kinds["q"] == {"method", "unpack"}


def test_partial_returns_are_those_with_a_vague_part() -> None:
    """Of any shape, all vague or in part; one with none is a plain return."""
    tree: ast.Module = ast.parse(textwrap.dedent(_LOCAL))
    assert annotations.partial_returns(tree) == {
        "collect": "tuple[list[str], dict[str, Any]]",
        "all_vague": "Tuple[Any, dict[str, Any]]",
        "anything": "tuple[Any, ...]",
    }
    assert annotations.partial_method_returns(tree) == {
        "Schema": {"common": "tuple[int, dict[str, Any]]", "info": "Tuple[Any, bool]"},
        "Child": {},
    }
    assert annotations.returns(tree) == {"plain": "tuple[int, str]"}


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def test_another_files_partial_return_is_unpacked_too(tmp_path: Path) -> None:
    """An imported function's, however it's spelled, and an imported class's method's."""
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "util.py", _UTIL)
    main: Path = _write(tmp_path / "main.py", _MAIN)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    imported: project.Imported = project.imported(catalog, main)
    assert imported.partial.calls == {
        "collect": "tuple[list[str], dict[str, Any]]",
        "u.collect": "tuple[list[str], dict[str, Any]]",
    }
    assert imported.partial.methods == {
        "Schema": {"common": "tuple[int, dict[str, Any]]"},
        "u.Schema": {"common": "tuple[int, dict[str, Any]]"},
    }
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, main, {}),
    )
    assert {o.name: o.fix for o in found} == {
        "names": "list[str]",
        "again": "list[str]",
        "size": "int",
        **dict.fromkeys(("extra", "more", "metadata", "whole")),
    }
