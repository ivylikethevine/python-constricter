# SPDX-License-Identifier: MIT
"""`--fix` writes a type only as vague as `vague` allows: none by default."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, Offence, check_source
from constricter.fix.core.known import Hints, Outside

# Each offence's fix and whether it's a guess.
_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_SOURCE: Final = """
from collections.abc import Callable
from typing import Any, cast


class Box:
    def vague(self) -> dict[str, Any]:
        return {}


def vague_dict() -> dict[str, Any]:
    return {}


def vague_pair() -> tuple[Any, Any]:
    return 1, 2


def anything() -> Any:
    return 1


def f(
    d: dict[str, Any], rows: list[dict[str, Any]], box: Box, make: Callable[[], Any], kind: type[Any]
) -> None:
    h = vague_dict()
    i = vague_pair()
    j = anything()
    k = d
    for row in rows:
        pass
    m = d.get("x")
    n, o = vague_pair()
    p = cast(Any, d)
    q = make()
    r = kind()
    s = box.vague()
    t = vague_dict(Box())
"""


def _fixes(level: int) -> _Fixes:
    found: list[Offence] = check_source(textwrap.dedent(_SOURCE), checks=Checks(vague=level))
    return {o.name: (o.fix, o.unsafe) for o in found if o.fix is not None}


def test_a_fix_is_written_only_as_vague_as_the_level_allows() -> None:
    """A declared return, a copy, an element, a `cast`, a callable's call: the same rule for each.

    A call of a function declaring a vague return is certain whatever its arguments are, as one
    declaring any other is.
    """
    assert _fixes(-1) == {}
    one_inside: _Fixes = dict.fromkeys(("h", "k", "row", "s", "t"), ("dict[str, Any]", False))
    assert _fixes(0) == one_inside
    assert _fixes(1) == {
        **one_inside,
        "i": ("tuple[Any, Any]", False),
        "j": ("Any", False),
        "m": ("Any | None", False),
        "n": ("Any", False),
        "o": ("Any", False),
        "p": ("Any", False),
        "q": ("Any", False),
        "r": ("Any", False),
    }


def test_what_only_a_vague_type_describes_is_typed_from_1() -> None:
    """`getattr`, by its default's type if it has one, and a standard-library function declaring `Any`.

    `Any` is named as the module can (here, imported). Not where the module binds `getattr`, for a
    default of no known type, or where `Any` can't be named; a guessed default makes a guess.
    """
    source: str = """
    import json


    def f(o: object, s: str, n: int) -> None:
        a = json.loads(s)
        b = getattr(o, "x")
        c = getattr(o, "x", None)
        d = getattr(o, "x", n)
        e = getattr(o, "x", unknown())
        g = getattr(o, "x", Box())
        h = getattr(o, "x", 1, 2)
    """
    found: list[Offence] = check_source(textwrap.dedent(source), checks=Checks(vague=1))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "a": ("Any", False),
        "b": ("Any", False),
        "c": ("Any | None", False),
        "d": ("Any | int", False),
        "e": (None, False),
        "g": ("Any | Box", True),
        "h": (None, False),
    }
    assert {o.edit.imports for o in found if o.edit is not None} == {("from typing import Any",)}
    assert [o.fix for o in check_source(textwrap.dedent(source)) if o.fix] == []
    shadowed: str = "def f(o, getattr) -> None:\n    a = getattr(o, 'x')\n"
    taken: str = "import json\nAny = typing = 1\ndef f(s: str) -> None:\n    a = json.loads(s)\n"
    assert [o.fix for o in check_source(shadowed, checks=Checks(vague=1))] == [None]
    assert [o.fix for o in check_source(taken, checks=Checks(vague=1))] == [None]


def test_a_hint_is_taken_only_as_vague_as_the_level_allows() -> None:
    """A type checker's `dict[str, Any]`: dropped by default, a fix at 0."""
    source: str = "from typing import Any\n\n\ndef f(q) -> None:\n    x = q.load()\n"
    hints: Hints = Hints("basedpyright", {(5, 5): "dict[str, Any]"})
    found: list[list[str | None]] = [
        [o.fix for o in check_source(source, checks=Checks(vague=level), outside=Outside(hints=(hints,)))]
        for level in (-1, 0)
    ]
    assert found == [[None], ["dict[str, Any]"]]
