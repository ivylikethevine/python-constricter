# SPDX-License-Identifier: MIT
"""`--fix` for `:=`: its name is declared on a line of its own before the statement."""

import ast
import textwrap
from typing import Final

from constricter import Checks, Offence, check_source, check_tree
from constricter.fix.core import fixes
from constricter.fix.core.known import Hints, Outside
from constricter.offences import Edit

SOURCE: Final = """
import re


def f(pattern: re.Pattern[str], s: str, xs: list[int], q) -> None:
    if (m := pattern.match(s)) is not None:
        print(m)
    elif (n := len(s)) > 3:
        print(n)
    elif (k := s.strip()):
        print(k)
    else:
        if (deep := len(xs)):
            pass
    while (u := q.read()):
        pass
    ys = [y for x in xs if (y := x)]
    total = len(z := xs)
    square = lambda v: (w := v * v)

    @print if (a := 1) else print
    def g(v: int = (b := 2)) -> None: ...

    if s: c = 1
    else: d = (e := 2)
"""
FIXED: Final = """
import re


def f(pattern: re.Pattern[str], s: str, xs: list[int], q) -> None:
    m: re.Match[str] | None
    n: int
    k: str
    if (m := pattern.match(s)) is not None:
        print(m)
    elif (n := len(s)) > 3:
        print(n)
    elif (k := s.strip()):
        print(k)
    else:
        deep: int
        if (deep := len(xs)):
            pass
    while (u := q.read()):
        pass
    ys = [y for x in xs if (y := x)]
    z: list[int]
    total: int = len(z := xs)
    square = lambda v: (w := v * v)

    @print if (a := 1) else print
    def g(v: int = (b := 2)) -> None: ...

    if s: c: int = 1
    else: d = (e := 2)
"""


def test_a_walrus_is_declared_before_its_statement() -> None:
    """Before the `if` an `elif` belongs to; typed as a plain assignment's name is.

    Not one in a comprehension (its value may read the comprehension's names), in a definition's
    decorators or defaults, or in a statement that doesn't start its line.
    """
    offences: list[Offence] = check_source(SOURCE)
    walruses: dict[str, str | None] = {
        o.name: o.fix for o in offences if o.name in set("mnkuyzabe") | {"deep"}
    }
    assert walruses == {
        "m": "re.Match[str] | None",
        "n": "int",
        "k": "str",
        "deep": "int",
        "u": None,
        "y": None,
        "z": "list[int]",
        "a": None,
        "b": None,
        "e": None,
    }
    assert {o.edit.edit for o in offences if o.edit is not None and o.name in walruses} == {Edit.DECLARE}
    assert "".join(fixes.apply(SOURCE.splitlines(keepends=True), offences)) == FIXED
    assert check_source(FIXED) == [o for o in check_source(FIXED) if o.fix is None]  # nothing left to fix


def test_a_walrus_without_its_source_lines_is_declared_too() -> None:
    """A tree checked without its lines can't say where a statement starts its line: it's taken to."""
    tree: ast.Module = ast.parse("def f(s: str) -> None:\n    if (n := len(s)):\n        pass\n")
    assert [(o.name, o.fix) for o in check_tree(tree)] == [("n", "int")]


def test_a_walrus_is_typed_as_an_assignment_would_see_it() -> None:
    """A read the function tests is a guess, and a type checker's hint types what `--fix` can't."""
    source: str = textwrap.dedent(
        """
    def f(o: object, q) -> None:
        if (a := o):
            pass
        if isinstance(o, int):
            pass
        if (b := q.make()):
            pass
    """,
    )
    hints: Hints = Hints("basedpyright", {(7, 9): "int"})
    offences: list[Offence] = check_source(source, checks=Checks(), outside=Outside(hints=(hints,)))
    assert [(o.name, o.fix, o.unsafe) for o in offences] == [("a", "object", True), ("b", "int", True)]
