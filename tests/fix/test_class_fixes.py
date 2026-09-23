# SPDX-License-Identifier: MIT
"""`--fix` through a class: `@property` returns, `cls` in a classmethod, and `typing.cast`."""

import json
import textwrap
from pathlib import Path
from typing import Final, TypeAlias, cast

import pytest

from constricter import Checks, FixPolicy, Offence, check_source
from constricter.cli import command as cli

# Each offence's name, fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"
_Object: TypeAlias = dict[str, _Json]
REDUNDANT: Final = "LVA007"
UNANNOTATED: Final = "LVA001"
EDITS: Final = 2  # a declaration, and its type comment dropped
PROPERTIES: Final = """
from functools import cached_property
from typing import Self


class Box:
    @property
    def size(self) -> int:
        return 1

    @size.setter
    def size(self, value: int) -> None:
        pass

    @cached_property
    def label(self) -> str:
        return ""

    @property
    def me(self) -> Self:
        return self

    @property
    def vague(self):
        return 1

    def use(self) -> None:
        a = self.size
        b = self.label
        c = self.me


def outside(box: Box) -> None:
    d = box.size
    e = box.vague
"""
CLASSMETHODS: Final = """
from typing import ClassVar


class Config:
    limit: int = 3
    names: ClassVar[list[str]]
    field: str

    @classmethod
    def make(cls) -> "Config":
        return cls()

    @staticmethod
    def default_name() -> str:
        return ""

    @property
    def size(self) -> int:
        return 1

    @classmethod
    def build(klass, n: int) -> None:
        a = klass.limit
        b = klass.names
        c = klass.make()
        d = klass.default_name()
        e = klass
        f = klass.field
        g = klass.size
        h = klass()

    def instance(cls) -> None:
        i = cls.limit
"""
CASTS: Final = """
import typing
import typing as t
from typing import Any, cast
from typing import cast as c
from other import cast as not_typing


def f(x: object) -> None:
    a = cast(int, x)
    b = cast("list[str]", x)
    d = typing.cast(bytes, x)
    e = t.cast(float, x)
    g = c(str, x)
    h = cast(Any, x)
    i = not_typing(int, x)
    j = cast("not an expression(", x)
"""


def _fixed(source: str) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source))
    return {o.name: (o.fix, o.unsafe) for o in found if o.code == UNANNOTATED}


def test_a_property_is_its_declared_return() -> None:
    """A property (or cached one) with a setter still types `obj.prop`; an undeclared one doesn't."""
    assert _fixed(PROPERTIES) == {
        "a": ("int", False),
        "b": ("str", False),
        "c": ("Box", False),
        "d": ("int", False),
        "e": (None, False),
    }


def test_cls_is_its_class_in_a_classmethod() -> None:
    """Class attributes and class-side methods resolve; instance-only ones and `cls()` don't."""
    assert _fixed(CLASSMETHODS) == {
        "a": ("int", False),
        "b": ("list[str]", False),
        "c": ("'Config'", False),  # a string annotation stays one, as a method's does
        "d": ("str", False),
        "e": ("type[Config]", False),
        "f": (None, False),
        "g": (None, False),
        "h": (None, False),
        "i": (None, False),
    }


def test_cast_is_its_target() -> None:
    """`typing.cast(T, x)` however it's spelled is `T`; a vague `T`, or another `cast`, isn't."""
    assert _fixed(CASTS) == {
        "a": ("int", False),
        "b": ("list[str]", False),
        "d": ("bytes", False),
        "e": ("float", False),
        "g": ("str", False),
        "h": (None, False),
        "i": (None, False),
        "j": (None, False),
    }


def test_a_repeated_annotation_is_dropped(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """LVA007's fix drops the repeat's annotation; a bare one, a class body's, or an ignored kind keep it."""
    source: str = (
        "def f() -> None:\n    x: int = 1\n    x: int = 2\n    y: str = ''\n    y: str\n\n\n"
        "class C:\n    z: int = 1\n    z: int = 2\n"
    )
    found: list[Offence] = [o for o in check_source(source) if o.code == REDUNDANT]
    assert [(o.name, o.edit is not None) for o in found] == [("x", True), ("y", False), ("z", False)]
    ignored: list[Offence] = check_source(
        source,
        checks=Checks(fixes=FixPolicy(ignore=frozenset({"redundant"}))),
    )
    assert all(o.edit is None for o in ignored if o.code == REDUNDANT)
    path: Path = tmp_path / "again.py"
    _ = path.write_text(source, encoding="utf-8", newline="\n")
    assert cli.main(["--fix", "-q", "--level=suffocate", str(path)]) == cli.EXIT_FOUND
    assert path.read_text(encoding="utf-8") == source.replace("x: int = 2", "x = 2")
    _ = capsys.readouterr()


def test_sarif_and_rdjson_carry_both_edits_of_a_declaration(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    """LVA003's fix is two edits (the declaration, and the comment dropped): both are in each report."""
    path: Path = tmp_path / "loop.py"
    _ = path.write_text(
        "def f(items: list[int]) -> None:\n    for x in items:  # type: int\n        pass\n",
        encoding="utf-8",
        newline="\n",  # the edits' text is compared exactly, line ending included
    )
    assert cli.main(["--format=rdjson", "--level=suffocate", str(path)]) == cli.EXIT_FOUND
    rdjson: _Object = cast("_Object", json.loads(capsys.readouterr().out))
    diagnostics: list[_Object] = cast("list[_Object]", rdjson["diagnostics"])
    assert [cast("_Object", s)["text"] for s in cast("list[_Json]", diagnostics[0]["suggestions"])] == [
        "    x: int\n",
        "",
    ]
    assert cli.main(["--format=sarif", "--level=suffocate", str(path)]) == cli.EXIT_FOUND
    sarif: _Object = cast("_Object", json.loads(capsys.readouterr().out))
    run: _Object = cast("list[_Object]", sarif["runs"])[0]
    result: _Object = cast("list[_Object]", run["results"])[0]
    fix: _Object = cast("list[_Object]", result["fixes"])[0]
    change: _Object = cast("list[_Object]", fix["artifactChanges"])[0]
    assert len(cast("list[_Json]", change["replacements"])) == EDITS
