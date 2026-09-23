# SPDX-License-Identifier: MIT
"""`--fix` for an empty container filled later in its function (a guess)."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
UNANNOTATED: Final = "LVA001"
SOURCE: Final = """
def f(items: list[int], names: list[str], other) -> list[str]:
    a = []
    for i in items:
        a.append(i)
    b = {}
    for n in names:
        b[n] = len(n)
    c = set()
    c.add("x")
    c.discard("y")
    d = []
    d.append(1)
    d.append("x")
    e = []
    e.extend(items)
    g = []
    g.append(1)
    other(g)
    h = list()
    h.insert(0, "x")
    h.sort()
    k = []

    def inner() -> None:
        k.append(1)

    m = []
    m.append(1)
    p = dict()
    _ = p.setdefault("a", 1.5)
    q = {}
    q["a"] += 1
    r = []
    s = r
    t = []
    t[0:1] = [1]
    u = []
    v = []
    v.append(other)
    w = {}
    w[other] = 1
    x = []
    x.append(1, 2)
    z = []
    z.append(1)
    z = []
    print(len(m), ", ".join(h), sorted(a), c if c else None, f"{p}", not u, [y for y in m], m[0])
    return h
"""


def _fixed(checks: Checks | None = None) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(SOURCE), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if o.code == UNANNOTATED and len(o.name) == 1}


def test_an_empty_container_is_typed_by_what_is_added() -> None:
    """Every fill typed and agreeing, every other use unable to add: a guess; anything else, nothing."""
    fixed: _Fixed = _fixed()
    assert {name: fix for name, fix in fixed.items() if fix[0]} == {
        "a": ("list[int]", True),
        "b": ("dict[str, int]", True),
        "c": ("set[str]", True),
        "h": ("list[str]", True),
        "m": ("list[int]", True),
        "p": ("dict[str, float]", True),
    }
    # Mixed types (d), `extend` (e), passed elsewhere (g), a nested function (k), `+=` into it (q),
    # aliased (r), a slice (t), never filled (u), an unknown element (v) or key (w), a bad call (x),
    # rebound (z).
    assert {name for name, fix in fixed.items() if not fix[0]} >= set("degkqrtuvwxz")


def test_it_is_trusted_or_ignored_as_a_mechanism() -> None:
    """`unsafe-fix-select = ["filled"]` makes it certain; `fix-ignore = ["filled"]` drops it."""
    assert _fixed(Checks(fixes=FixPolicy(unsafe_select=frozenset({"filled"}))))["a"] == ("list[int]", False)
    assert _fixed(Checks(fixes=FixPolicy(ignore=frozenset({"filled"}))))["a"] == (None, False)
