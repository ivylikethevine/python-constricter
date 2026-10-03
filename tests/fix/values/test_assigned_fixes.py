# SPDX-License-Identifier: MIT
"""`--fix` for reads of unannotated instance attributes whose every `self.x = value` decides their type."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
_ASSIGNED: Final = FixPolicy(unsafe_select=frozenset({"assigned"}))
SOURCE: Final = """
def filled():
    items = []
    items.append(1)
    return items


class Box:
    limit = 3

    def use(self):
        a = self.name
        b = self.name.upper()
        c = self.size
        d = self.mixed
        e = self.counted
        f = self.empty
        g = self.limit
        h = self.declared
        i = self.made
        j = self.closed
        k = self.split
        m = self.deleted
        n = self.late
        q = self.filled

    def __init__(self, n: int, flag: bool):
        self.name = "box"
        self.size = 1
        self.mixed = 1
        self.counted = 0
        self.empty = None
        self.limit = 4
        self.declared: float = 1
        self.made = Thing()
        self.split, self.other = 1, 2
        self.deleted = 1
        late = None
        if flag:
            late = n
        self.late = late
        self.filled = filled()

        def inner():
            self.closed = 2

        self.closed = 1

    def grow(self):
        self.size = 2.5
        self.mixed = "x"
        self.counted += 1
        del self.deleted


def outside(box: Box, other) -> None:
    p = box.name
    s = box.name if other.name else ""
"""


def _fixed(checks: Checks | None = None, source: str = SOURCE) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if len(o.name) == 1}


def test_an_attribute_is_typed_by_its_assignments() -> None:
    """Every `self.x = value` in the class giving one known type: its reads are typed, as guesses."""
    assert _fixed() == {
        "a": ("str", True),
        "b": ("str", True),  # a chain goes on from it
        "c": ("float", True),  # `int`, then `float`: the widest
        "d": (None, False),  # two types
        "e": (None, False),  # `+=`
        "f": (None, False),  # `None`: no type of its own
        "g": (None, False),  # a class attribute too
        "h": ("float", False),  # its annotation, as before
        "i": ("Thing", True),
        "j": (None, False),  # a nested function assigns it too
        "k": (None, False),  # an unpacking assigns it
        "m": (None, False),  # deleted
        "n": (None, False),  # a local bound twice: what reaches `self.late` isn't known
        "q": ("list[int]", True),  # `filled` is typed late (in a round), and then so is it
        "p": ("str", True),  # outside the class, through a typed receiver
        "s": ("str", True),  # `other.name` decides nothing: `other` could be anything
    }


def test_trusting_assigned_makes_it_certain() -> None:
    """Trusting `assigned` makes an attribute's type certain, unless its value is itself a guess."""
    trusted: _Fixed = _fixed(Checks(fixes=_ASSIGNED))
    assert (trusted["a"], trusted["b"], trusted["i"]) == (("str", False), ("str", False), ("Thing", True))
    both: FixPolicy = FixPolicy(unsafe_select=frozenset({"assigned", "constructor"}))
    assert _fixed(Checks(fixes=both))["i"] == ("Thing", False)


def test_a_class_named_twice_types_nothing() -> None:
    """Two classes of one name: whose attribute a read is can't be told, so it isn't typed."""
    source: str = """
    class Box:
        def __init__(self):
            self.name = "box"

        def use(self):
            a = self.name


    def make():
        class Box:
            def __init__(self):
                self.name = 1
    """
    assert _fixed(source=source) == {"a": (None, False)}


def test_a_module_body_read_is_typed_with_all_scopes() -> None:
    """With `all-scopes`, a module-level read is checked again once the attributes are typed."""
    source: str = """
    class Box:
        def __init__(self):
            self.name = "box"


    def make():
        return Box()


    NAME = make().name
    """
    fixed: list[tuple[str, str | None]] = [
        (o.name, o.fix) for o in check_source(textwrap.dedent(source), checks=Checks(all_scopes=True))
    ]
    assert fixed == [("NAME", "str")]


def test_a_static_methods_self_is_not_the_instance() -> None:
    """A static method's `self.name = 1` isn't one of the instance's own assignments: nothing is typed."""
    source: str = """
    class Box:
        def __init__(self):
            self.name = "box"

        def use(self):
            a = self.name

        @staticmethod
        def build(self):
            self.name = 1
    """
    assert _fixed(source=source) == {"a": (None, False)}
