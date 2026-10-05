# SPDX-License-Identifier: MIT
"""`--fix` for reads of an instance attribute bound to an empty container its class's methods fill."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
SOURCE: Final = """
class Thing: ...


class Box:
    def __init__(self, names: list[str], other):
        self.items = []
        self.sizes = {}
        self.seen = set()
        self.made = list()
        self.merged = dict()
        self.loaded = []
        self.passed = []
        self.mixed = []
        self.unknown = []
        self.closed = []
        self.never = []
        self.things = []
        self.twice = []
        self.kinds = []
        self.bound = []
        self.copied = []
        self.differs = []
        other.items = []
        other.box.items = []
        spare = []

    def add(self, n: int, s: str, other, sizes: dict[str, int]):
        self.items.append(n)
        self.sizes[s] = n
        self.seen.add(s)
        self.made.extend(s.split())
        self.merged.update(sizes)
        self.mixed.append(n)
        self.mixed.append(s)
        self.unknown.append(other)
        self.closed.append(n)
        self.things.append(Thing())
        other(self.passed)
        self.passed.append(1)
        x = None
        if n:
            x = 1
        self.twice.append(x)
        self.kinds = {}
        self.differs.append(n)
        return lambda: self.closed

    def reset(self, names: list[str]):
        self.items = []
        self.items.sort()
        self.loaded = names
        self.differs = names

    def use(self):
        a = self.items.pop()
        for b in self.items:
            pass
        c = self.sizes.get("k")
        d = self.merged["k"]
        e = sorted(self.seen)
        f = self.made[0]
        g = self.loaded[0]
        h = self.passed[0]
        i = self.mixed[0]
        j = self.unknown[0]
        k = self.closed[0]
        m = self.never[0]
        n = self.things[0]
        p = self.twice[0]
        q = self.kinds[0]
        r = self.bound[0]
        t = self.copied[0]
        u = self.differs[0]
        copy = self.copied

    def bound(self):
        self.bound.append(1)


def outside(box: Box) -> None:
    v = box.items[0]
    w = box.items
    box.elsewhere = []
"""


def _fixed(checks: Checks | None = None) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(SOURCE), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if len(o.name) == 1}


def test_an_empty_containers_attribute_is_typed_by_what_its_class_adds() -> None:
    """`self.items = []`, then only fills of one type in its class's methods: its reads are guesses."""
    assert _fixed() == {
        "x": ("int | None", False),
        "a": ("int", True),
        "b": ("int", True),
        "c": ("int | None", True),  # a `dict`'s, by its keys and values
        "d": ("int", True),  # `update`: another `dict`'s entries
        "e": ("list[str]", True),
        "f": ("str", True),  # `extend`: its argument's elements
        "g": ("str", True),  # assigned a `list[str]` too, and never filled
        "h": (None, False),  # passed on: something else may add to it
        "i": (None, False),  # two types
        "j": (None, False),  # a value of no known type
        "k": (None, False),  # a lambda reads it
        "m": (None, False),  # nothing's added
        "n": ("Thing", True),
        "p": (None, False),  # a local bound twice: what's added isn't known
        "q": (None, False),  # bound empty as a `list`, then as a `dict`
        "r": (None, False),  # a method's name too
        "t": (None, False),  # aliased
        "u": (None, False),  # filled with `int`s, assigned a `list[str]`
        "v": ("int", True),  # outside the class, through a typed receiver
        "w": ("list[int]", True),
    }


def test_trusting_assigned_alone_leaves_it_a_guess() -> None:
    """It rests on `filled` too: trusting both makes it certain, unless what's added is itself a guess."""
    assigned: FixPolicy = FixPolicy(unsafe_select=frozenset({"assigned"}))
    assert _fixed(Checks(fixes=assigned))["a"] == ("int", True)
    both: FixPolicy = FixPolicy(unsafe_select=frozenset({"assigned", "filled"}))
    trusted: _Fixed = _fixed(Checks(fixes=both))
    assert (trusted["a"], trusted["g"], trusted["n"]) == (("int", False), ("str", False), ("Thing", True))
