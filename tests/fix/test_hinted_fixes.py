# SPDX-License-Identifier: MIT
"""`--infer-with`: which of a type checker's hints become fixes, spelled how, and what they feed."""

import ast
import textwrap
from typing import Final, TypeAlias

import pytest

from constricter import Checks, Offence, check_source
from constricter.fix import fixes
from constricter.fix.known import Hints, Outside
from constricter.offences import Edit, FixPolicy

_CHECKER: Final = "basedpyright"
_DEFAULT: Final = Checks()
_Fixes: TypeAlias = list[tuple[str, str | None, bool]]


def _checked(source: str, hinted: dict[str, str], checks: Checks = _DEFAULT) -> list[Offence]:
    """Check `source`, the checker hinting each name's every binding as `hinted` says.

    Returns:
      The offences.

    """
    text: str = textwrap.dedent(source)
    types: dict[tuple[int, int], str] = {
        (node.lineno, node.end_col_offset or 0): hinted[node.id]
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id in hinted
    }
    return check_source(text, checks=checks, outside=Outside(hints=(Hints(_CHECKER, types),)))


def _fixes(source: str, hinted: dict[str, str]) -> _Fixes:
    """Check `source` with hints.

    Returns:
      Each offence's name, fix and whether it's a guess.

    """
    return [(o.name, o.fix, o.unsafe) for o in _checked(source, hinted)]


@pytest.mark.parametrize(
    ("hint", "fix"),
    [
        ("int", "int"),
        ("Literal[1]", "int"),
        ("Literal[-1, 2]", "int"),
        ("Literal['a', b'b']", "str | bytes"),
        ("Literal[True] | None", "bool | None"),
        ("None | Literal[1] | int", "int | None"),
        ("Literal[None, 1]", "int | None"),
        ("tuple[Literal[1], Literal['a']]", "tuple[int, str]"),
        ("list[LiteralString]", "list[str]"),
        ("Callable[[int], str]", "Callable[[int], str]"),
        ("Callable[..., None]", "Callable[..., None]"),
        ("Literal[Color.RED]", "Color"),
        ("os.stat_result", "os.stat_result"),
        ("stat_result", "os.stat_result"),
        ("Iterator[int]", "Iterator[int]"),
        ("Any", None),  # vague
        ("list[Unknown]", None),  # a name the file can't use
        ("OrderedDict[Any, Any]", None),
        ("None", None),  # says nothing
        ('Module("os")', None),  # not an annotation
        ("(x: int) -> str", None),  # a signature, not valid Python
        ("Self@C", None),
        ("Literal[f()]", None),
        ("list[Literal[f()]]", None),
        ("tuple[Literal[f()], int]", None),
        ("Literal['a'] | Literal[f()]", None),
        ('list["int"]', None),  # a string: its meaning isn't checked
        ("dict[str, dict[str, list[int]]]", None),  # as deep as LVA006 reports
        ("tuple[int, int, int, int, int]", None),  # as long as LVA011 reports
        ("_T", None),  # a type variable, or anything private
        ("list[<class 'int'> | <class 'Color'>]", "list[type[int] | type[Color]]"),  # ty's class objects
        ("<class '<unknown>'>", None),
        ("type[_]", None),  # `_` is gettext's, or a throwaway: never the checker's class
        ("dict[int, <class 'A'> | ... omitted 11 union elements]", None),  # cut short
    ],
)
def test_a_hint_is_widened_spelled_or_dropped(hint: str, fix: str | None) -> None:
    """A `Literal` is its values' types; what isn't a usable annotation is no fix."""
    source: str = """
    import os
    from enum import Enum
    from gettext import gettext as _
    from collections.abc import Callable, Iterator


    class Color(Enum):
        RED = 1


    def f(q) -> None:
        x = q.make()
    """
    assert _fixes(source, {"x": hint}) == [("x", fix, fix is not None)]


def test_a_well_known_class_is_imported() -> None:
    """A class a checker prints by its bare name is imported, unless the file has it already."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = q.make()\n"
    offences: list[Offence] = _checked(source, {"x": "Iterator[Path]", "y": "Iterator[Path]"})
    fixed: str = "".join(
        fixes.apply(source.splitlines(keepends=True), [o for o in offences if o.edit is not None]),
    )
    expected: str = (
        "from collections.abc import Iterator\n"
        "from pathlib import Path\n"
        "def f(q) -> None:\n"
        "    x: Iterator[Path] = q.make()\n"
        "    y: Iterator[Path] = q.make()\n"
    )
    assert fixed == expected


def test_a_taken_name_is_imported_by_its_module_or_not_at_all() -> None:
    """`Path` bound elsewhere gets `pathlib.Path`; with `pathlib` taken too, no fix.

    A name the module binds at its top level means what it binds there: the checker prints only a
    bare name, and a value of the module's own `Path` is as likely as one of `pathlib`'s.
    """
    source: str = "def g(Path, pathlib) -> None: ...\ndef f(q) -> None:\n    x = q.make()\n"
    assert _fixes(source.replace(", pathlib", ""), {"x": "Path"}) == [("x", "pathlib.Path", True)]
    assert _fixes(source, {"x": "Path"}) == [("x", None, False)]
    assert _fixes("from mine import Path\n" + source, {"x": "Path"}) == [("x", "Path", True)]


def test_a_module_body_uses_only_what_is_bound_before() -> None:
    """A module-level annotation is evaluated where it is: a class defined later can't be used."""
    source: str = """
    x = make()
    class Early: ...
    y = make()
    """
    offences: list[Offence] = _checked(source, {"x": "Early", "y": "Early"}, Checks(all_scopes=True))
    assert [(o.name, o.fix) for o in offences] == [("x", None), ("y", "Early")]


def test_a_function_uses_any_name_the_module_binds() -> None:
    """A local's annotation is never evaluated: a class the module defines after it will do."""
    source: str = "def f(q) -> None:\n    x = q.make()\nclass Late: ...\n"
    assert _fixes(source, {"x": "Late"}) == [("x", "Late", True)]


def test_constricters_own_inference_comes_first() -> None:
    """Where `--fix` types a value itself, its own type stands, a guess or not."""
    source: str = "def f() -> None:\n    x = 1\n    y = Box(1)\n"
    assert _fixes(source, {"x": "Literal[1]", "y": "Box[int]"}) == [("x", "int", False), ("y", "Box", True)]


def test_what_follows_from_a_hint_is_a_guess_too() -> None:
    """A copy of a hinted local is typed in the same pass, as a guess resting on the checker."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = x\n"
    offences: list[Offence] = _checked(source, {"x": "int"})
    assert [(o.name, o.fix, o.unsafe) for o in offences] == [("x", "int", True), ("y", "int", True)]
    trusted: list[Offence] = _checked(
        source,
        {"x": "int"},
        Checks(fixes=FixPolicy(unsafe_select=frozenset({"checker"}))),
    )
    assert [o.unsafe for o in trusted] == [False, False]
    ignored: list[Offence] = _checked(
        source,
        {"x": "int"},
        Checks(fixes=FixPolicy(ignore=frozenset({"checker"}))),
    )
    assert [o.fix for o in ignored] == [None, None]


def test_loop_with_and_unpacking_targets_are_declared() -> None:
    """A hinted name a statement binds some other way is declared before it."""
    source: str = """
    def f(q) -> None:
        for item in q:
            pass
        with q as held:
            pass
        first, second = q
    """
    offences: list[Offence] = _checked(source, {"item": "int", "held": "str", "first": "bytes"})
    assert [(o.name, o.fix, o.edit.edit if o.edit else None) for o in offences] == [
        ("item", "int", Edit.DECLARE),
        ("held", "str", Edit.DECLARE),
        ("first", "bytes", Edit.DECLARE),
        ("second", None, None),
    ]


def test_a_late_fix_replaces_a_hints() -> None:
    """`None` then one type, or an empty container filled, is typed by `--fix` itself, not the hint."""
    source: str = """
    def f(n: int) -> None:
        x = None
        x = n
        y = []
        y.append(n)
    """
    assert _fixes(source, {"x": "None", "y": "list[Unknown]"}) == [
        ("x", "int | None", False),
        ("y", "list[int]", True),
    ]
    assert _fixes(source, {"x": "int | None", "y": "list[int]"}) == [
        ("x", "int | None", False),
        ("y", "list[int]", True),
    ]


def test_none_then_a_guess_is_a_guess() -> None:
    """`x = None`, then only a hinted value: `T | None`, a guess resting on the checker."""
    source: str = "def f(q) -> None:\n    x = None\n    x = q.make()\n"
    offences: list[Offence] = _checked(source, {"x": "int"})
    assert [(o.fix, o.unsafe, o.edit.kinds if o.edit else None) for o in offences] == [
        ("int | None", True, frozenset({"optional", "checker"})),
    ]


def test_a_class_body_is_never_fixed() -> None:
    """A dataclass's annotation is a field: a class body's hints change nothing."""
    source: str = "class C:\n    x = make()\n"
    assert [o.fix for o in _checked(source, {"x": "int"}, Checks(all_scopes=True))] == [None]


def test_the_first_checker_whose_hint_is_usable_wins() -> None:
    """With two checkers, the first named whose hint the file can use types the name."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = q.make()\n"
    first: Hints = Hints("ty", {(2, 5): "Unknown", (3, 5): "int"})
    second: Hints = Hints(_CHECKER, {(2, 5): "str", (3, 5): "bytes"})
    offences: list[Offence] = check_source(source, outside=Outside(hints=(first, second)))
    assert [(o.name, o.fix, o.edit.reason if o.edit else None) for o in offences] == [
        ("x", "str", "basedpyright's inferred type"),
        ("y", "int", "ty's inferred type"),
    ]
