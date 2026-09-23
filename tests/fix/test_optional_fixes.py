# SPDX-License-Identifier: MIT
"""`--fix` for `x = None` later rebound to one known type: `T | None`."""

import textwrap
from typing import Final

from constricter import Checks, FixPolicy, Offence, check_source

UNANNOTATED: Final = "LVA001"
SOURCE: Final = """
def f(items: list[int], flag: bool, other, maybe: int | None, counts: dict[str, int]) -> None:
    a = None
    if flag:
        a = 1
    b = None
    b = "x"
    b = 2
    c = None
    c = other
    d = None
    e = None
    for e in items:
        pass
    g = None
    g = 3
    g += 1
    i = None
    i = maybe
    j = None
    j = counts.get("k")

    def inner() -> None:
        nonlocal h
        h = 5

    h = None
    h = 4
"""


def _fixed(checks: Checks | None = None) -> dict[str, str | None]:
    found: list[Offence] = check_source(textwrap.dedent(SOURCE), checks=checks or Checks())
    return {o.name: o.fix for o in found if o.code == UNANNOTATED}


def test_none_then_one_type_is_optional() -> None:
    """Only a `None` rebound, every time, to one certain type, and written nowhere else, is `T | None`."""
    assert _fixed() == {
        "a": "int | None",
        "b": None,  # two types
        "c": None,  # an unknown one
        "d": None,  # never rebound
        "e": None,  # a loop target
        "g": "int | None",
        "i": None,  # a copy of a union is never certain
        "j": None,  # a type that allows `None` already
        "h": None,  # written from a nested function
    }


def test_optional_is_its_own_fix_kind() -> None:
    """`fix-ignore = ["optional"]` turns it off."""
    fixed: dict[str, str | None] = _fixed(Checks(fixes=FixPolicy(ignore=frozenset({"optional"}))))
    assert fixed["a"] is None
