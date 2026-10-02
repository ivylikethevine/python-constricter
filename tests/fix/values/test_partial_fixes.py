# SPDX-License-Identifier: MIT
"""`--fix` for an unpacked call whose declared return is a tuple with a vague part: the other parts."""

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


def test_partial_returns_are_tuples_with_a_vague_part() -> None:
    """Not one all vague, of any length, or with none: those are no return, or a plain one."""
    tree: ast.Module = ast.parse(textwrap.dedent(_LOCAL))
    assert annotations.partial_returns(tree) == {"collect": "tuple[list[str], dict[str, Any]]"}
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
