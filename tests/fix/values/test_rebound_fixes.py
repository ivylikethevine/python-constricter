# SPDX-License-Identifier: MIT
"""`--fix` for a name later bound to another type: widened to the type every value fits, or dropped."""

import textwrap
from typing import Final

from constricter import Checks, FixPolicy, Offence, check_source
from constricter.fix.core import fixes

SOURCE: Final = """
class C:
    def m(self):
        return 2.5


def f(items: list[int], flag: bool, text: str, c: C, other) -> None:
    a = 1
    if flag:
        a = None
    total = 0
    total += 0.5
    on = True
    on = 1
    b = 1
    b = text
    copied = b
    l = [1]
    l = ["x"]
    h = 1
    h = c.m()
    u = "x"
    u = other
    s = "x"
    s += other
    s %= other
    for i in items:
        pass
    i = None
    g = 1

    def inner() -> None:
        nonlocal g
        g = "x"
"""


def _found(checks: Checks | None = None) -> dict[str, tuple[str | None, bool]]:
    found: list[Offence] = check_source(textwrap.dedent(SOURCE), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if o.name not in {"m", "inner"}}


def test_a_later_binding_widens_the_first_ones_type() -> None:
    """The widest of every value's type, if it takes them all, with `| None` for a `None`; else nothing."""
    assert _found() == {
        "a": ("int | None", False),
        "total": ("float", False),
        "on": ("int", False),
        "b": (None, False),  # `int`, then `str`: no one type
        "copied": ("str", True),  # narrowed to what it was last bound to, which mypy doesn't do
        "l": (None, False),  # a generic fits only the same type arguments
        "h": ("float", True),  # a later binding's guess (a method's `return`s) makes it a guess
        "u": ("str", True),  # an unknown later value may be anything
        "s": ("str", False),  # text stays text by `+=`, `%=` and `*=`, whatever's added
        "i": ("int | None", False),  # a loop target's declaration, then `None`
        "g": ("int", False),  # written from a nested function: out of sight, left alone
    }


def test_rebound_is_its_own_fix_kind() -> None:
    """Each widened fix says why (`rebound`, or `optional` for a `None`); `fix-ignore` turns them off."""
    found: list[Offence] = check_source(textwrap.dedent(SOURCE))
    kinds: dict[str, frozenset[str]] = {o.name: o.edit.kinds for o in found if o.edit is not None}
    assert kinds["total"] >= {"rebound"}
    assert kinds["a"] >= {"optional"}
    policy: FixPolicy = FixPolicy(ignore=frozenset({"rebound"}))
    ignored: dict[str, tuple[str | None, bool]] = _found(Checks(fixes=policy))
    assert ignored["total"] == (None, False)
    assert ignored["a"] == ("int | None", False)


def test_a_widened_fix_is_declared_before_the_first_binding() -> None:
    """Annotated where it's bound, mypy wouldn't narrow `x` to the `str` it's bound to; declared, it does."""
    source: str = textwrap.dedent(
        """\
        def f(flag: bool) -> str:
            x = "a"
            y = x.upper()
            if flag:
                x = None
            return y
        """,
    )
    offences: list[Offence] = [o for o in check_source(source) if o.fix]
    assert "".join(fixes.apply(source.splitlines(keepends=True), offences)) == textwrap.dedent(
        """\
        def f(flag: bool) -> str:
            x: str | None
            x = "a"
            y: str = x.upper()
            if flag:
                x = None
            return y
        """,
    )


def test_a_branch_rebinding_makes_later_copies_guesses() -> None:
    """`x = 1`, then `x = "a"` only under `if`: past it, `x` may be either, so a copy of it is a guess."""
    source: str = (
        "def f(flag: bool) -> None:\n    x = 1\n    if flag:\n        x = 'a'\n        y = x\n    z = x\n"
    )
    fixed: dict[str, tuple[str | None, bool]] = {o.name: (o.fix, o.unsafe) for o in check_source(source)}
    assert fixed["y"] == ("str", True)
    assert fixed["z"] == ("int", True)


def test_a_name_first_bound_to_no_known_type_is_a_guess_later() -> None:
    """It may still hold that value (another branch's): what's inferred from a later one's type is a guess."""
    source: str = textwrap.dedent(
        """\
        def f(index, flag, count):
            if flag:
                levels = index.multi()
            else:
                levels = ["a"]
            for lvl in levels:
                pass
            copy = levels
            item = index.first()
            for item in ["a"]:
                pass
            kept = item
            count = 3
            total = count
            if flag:
                size = 1
            else:
                size = 2
            same = size
        """,
    )
    found: list[Offence] = check_source(source)
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "levels": (None, False),
        "lvl": ("str", True),
        "copy": ("list[str]", True),
        "item": (None, False),
        "kept": ("str", True),  # a loop's target, bound before
        "total": ("int", True),  # a parameter no annotation types
        "size": ("int", False),
        "same": ("int", False),  # every binding typed: certain
    }
    trusting: Checks = Checks(fixes=FixPolicy(unsafe_select=frozenset({"rebound"})))
    assert {o.name: o.unsafe for o in check_source(source, checks=trusting) if o.fix} == {
        "lvl": False,
        "copy": False,
        "kept": False,
        "total": False,
        "size": False,
        "same": False,
    }


def test_a_name_bound_again_to_a_call_on_itself_has_no_fix() -> None:
    """`item = proper(item)` converts as often as not: a call on something else stays a guess."""
    source: str = """
    def g(text: str, proper, n: int) -> None:
        a = "x"
        a = proper(a)
        b = "x"
        b = proper(text)
        c = "x"
        c = proper(flag=c)
        d = 1
        d = abs(d)
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "a": (None, False),
        "b": ("str", True),
        "c": (None, False),
        "d": ("int", False),  # of a known type: it fits
    }


def test_a_later_with_or_loop_target_holds_the_first_bindings_fix() -> None:
    """Its known type fits the fix, or leaves none: `open(path)` then `open(path, "rb")` are two types."""
    source: str = """
    def g(path: str, names: list[str], counts: list[int]) -> None:
        with open(path) as a:
            print(a)
        with open(path, "rb") as a:
            print(a)
        with open(path) as b:
            print(b)
        with open(path) as b:
            print(b)
        for c in names:
            print(c)
        for c in counts:
            print(c)
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "a": (None, False),
        "b": ("TextIOWrapper", False),
        "c": (None, False),
    }
