# SPDX-License-Identifier: MIT
"""`--fix` on small shapes typed from their parts: unions, displays that unpack, `type(x)`, and the like."""

import textwrap
from typing import Final, TypeAlias

from constricter import Offence, check_source

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
UNIONS: Final = """
from typing import Final, Literal


class Node:
    name: str | None
    kind: Literal["a", "b"]
    size: int | str


def is_int(o: object) -> bool:
    return isinstance(o, int)


def f(
    n: int,
    maybe: int | None,
    either: int | str,
    node: Node,
    odd: Final,
    names: list[str],
    c: bool,
    q,
) -> None:
    a = n if c else None
    b = None if c else names
    d = maybe if c else None
    e = None if c else None
    g = q if c else None
    h = either if c else None
    i = node.kind if c else None
    j = odd if c else None
    o = maybe or n
    p = n or maybe
    r = node.name or "anon"
    s = n and n
    t = maybe and n
    u = n or q
    v = n or "x"
    w = node.size or 3
    x = odd or odd
    y = Node() if c else None
    z = n or n or 0


def g(n: int, names: list[str]) -> None:
    k = n if is_int(n) else None
    m = len(names) if names else None
"""
PARTS: Final = """
import os
from os import environ


class Node:
    pass


def f(
    n: int,
    node: Node,
    either: int | str,
    nothing: None,
    names: list[str],
    pairs: dict[str, int],
    q,
) -> None:
    a = [*names, "z"]
    b = {*names}
    c = (*names, "a")
    d = {**pairs, "k": 1}
    e = [*names, n]
    g = {**pairs, "k": "v"}
    h = {**names, "k": 1}
    i = {**q}
    j = [*q, "z"]
    k = type(node)
    m = type(either)
    o = type(nothing)
    p = type(q)
    r = type(*names)
    s = type("Made", (), {})
    t = type(Node())
    u = os.environ["HOME"]
    v = environ["HOME"]
    w = os.environ["a":"b"]
    x = q["HOME"]
    y = pairs.get("k", Node())
"""


def _fixed(source: str) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source))
    return {o.name: (o.fix, o.unsafe) for o in found if len(o.name) == 1}


def test_a_union_the_author_would_write() -> None:
    """`a if c else None` is `T | None`; `a or b` of one type is that type, an earlier `None` dropped."""
    assert _fixed(UNIONS) == {
        "a": ("int | None", False),
        "b": ("list[str] | None", False),
        "d": ("int | None", False),  # `None` already
        "e": (None, False),  # nothing but `None`
        "g": (None, False),
        "h": (None, False),  # a read of a union of two types may be narrowed to one
        "i": (None, False),  # a `Literal`'s string can't take `| None`
        "j": (None, False),  # a qualifier names no type
        "k": (None, False),  # the conditional's own test narrows it
        "m": ("int | None", False),
        "o": ("int", False),
        "p": ("int | None", False),  # the last operand's own `None` stays
        "r": ("str", False),
        "s": ("int", False),
        "t": (None, False),  # `and` gives its first operand when it's false: `None`, here
        "u": (None, False),
        "v": (None, False),  # two types
        "w": (None, False),
        "x": (None, False),
        "y": ("Node | None", True),  # a guess, as its side is
        "z": ("int", False),
    }


def test_a_read_in_a_union_the_function_tests_is_a_guess() -> None:
    """A side read as its declared type is narrowed where the function tests it, as a copy is."""
    source: str = """
    def f(n: int, name: str | None, c: bool) -> None:
        if name:
            pass
        assert n
        a = n if c else None
        b = name or "x"
    """
    assert _fixed(source) == {"a": ("int | None", True), "b": ("str", True)}


def test_displays_that_unpack_and_other_shapes() -> None:
    """A starred element gives what it unpacks; `type(x)`, `os.environ[k]` and `d.get(k, v)` their parts'."""
    assert _fixed(PARTS) == {
        "a": ("list[str]", False),
        "b": ("set[str]", False),
        "c": ("tuple[str, ...]", False),  # of unknown length
        "d": ("dict[str, int]", False),
        "e": ("list[str | int]", True),  # two types, joined: a guess
        "g": ("dict[str, int | str]", True),
        "h": (None, False),  # `**` of what isn't a `dict`
        "i": (None, False),
        "j": (None, False),
        "k": ("type[Node]", False),
        "m": (None, False),  # a union's is a union of types
        "o": (None, False),
        "p": (None, False),
        "r": (None, False),
        "s": (None, False),  # the three-argument form makes a class
        "t": ("type[Node]", True),  # a guess, as its argument is
        "u": ("str", False),
        "v": ("str", False),
        "w": (None, False),  # a slice
        "x": (None, False),
        "y": (None, False),  # a default of another type
    }
    rebound: str = "def g(type, pairs: dict[str, int]) -> None:\n    a = type(pairs)\n"
    assert _fixed(rebound) == {"a": (None, False)}  # not the builtin


def test_a_type_fixed_whatever_its_parts_stays_certain() -> None:
    """`x.kind is None` is a `bool` whatever `x.kind` is: a guess there doesn't make it one."""
    source: str = """
    class Box:
        def __init__(self) -> None:
            self.kind = make()

    def make() -> int:
        return 1

    def f(box: Box) -> None:
        a = box.kind
        b = box.kind is None
        c = f"{box.kind}"
        d = not box.kind
    """
    assert _fixed(source) == {
        "a": ("int", True),
        "b": ("bool", False),
        "c": ("str", False),
        "d": ("bool", False),
    }


def test_type_of_self_is_self_where_the_method_says_so() -> None:
    """`type(self)` is `type[Self]` in a method whose signature says `Self`, its class's elsewhere."""
    source: str = """
    from typing import Self

    class Point:
        def copy(self) -> Self:
            a = type(self)
            return a()

        def plain(self) -> None:
            b = type(self)
    """
    assert _fixed(source) == {"a": ("type[Self]", False), "b": ("type[Point]", False)}
    assert _fixed(source.replace("from typing import Self", "")) == {
        "a": (None, False),  # no `Self` to write it with
        "b": ("type[Point]", False),
    }


def test_a_self_method_on_the_instance_or_its_class_is_self() -> None:
    """Called on `self` or `type(self)`, the class's own or one it inherits; and a conditional of two."""
    source: str = """
    from typing import Self

    class Base:
        def clone(self) -> Self:
            return self

    class Point(Base):
        @classmethod
        def build(cls) -> Self:
            return cls()

        def other(self) -> "Point":
            return self

        def copy(self, inplace: bool) -> Self:
            a = type(self).build()
            b = self.clone()
            c = self if inplace else self.clone()
            d = self if inplace else self.other()
            e = self.other()
            return a

        def plain(self, inplace: bool) -> None:
            g = type(self).build()
            h = self if inplace else self.clone()
    """
    assert _fixed(source) == {
        "a": ("Self", False),
        "b": ("Self", False),  # `Base`'s
        "c": ("Self", False),
        "d": ("Point", False),  # one side is declared the class
        "e": ("Point", False),
        "g": ("Point", False),  # where the signature doesn't say `Self`, `self` is its class
        "h": ("Point", False),
    }


def test_an_empty_display_takes_the_type_of_the_container_beside_it() -> None:
    """`a or []` and `a if c else {}` are `a`'s `list` or `dict`; a read that may be `None`, a guess."""
    source: str = """
    def f(
        n: int,
        names: list[str],
        maybe: list[str] | None,
        ages: dict[str, int],
        either: list[str] | list[int],
        c: bool,
        q,
    ) -> None:
        a = names or []
        b = maybe or []
        d = ages or {}
        e = names or {}
        g = n or []
        h = q or []
        i = names and []
        j = either or []
        k = maybe or names or []
        m = [] if c else names
        o = ages if c else {}
        p = maybe if maybe else []
        r = maybe if maybe is not None else []
        s = [] if maybe else maybe
        t = [] if c else maybe
        u = [] if c else {}
        v = n if c else []
        w = q if c else []
        x = names if c else {}
        y = [n][:1] or []
    """
    assert _fixed(source) == {
        "a": ("list[str]", False),
        "b": ("list[str]", True),  # never `None`: `or` passes it over
        "d": ("dict[str, int]", False),
        "e": (None, False),  # a `dict` display beside a `list`
        "g": (None, False),
        "h": (None, False),
        "i": (None, False),  # `and` gives the display itself
        "j": (None, False),  # a union of two types may be narrowed to one
        "k": ("list[str]", True),
        "m": ("list[str]", False),
        "o": ("dict[str, int]", False),
        "p": ("list[str]", True),  # where it's true, it isn't `None`
        "r": (None, False),  # tested another way: narrowed there
        "s": (None, False),
        "t": ("list[str] | None", True),
        "u": (None, False),
        "v": (None, False),
        "w": (None, False),
        "x": (None, False),
        "y": ("list[int]", False),
    }


def test_a_modules_own_file_and_name_are_text() -> None:
    """`__file__` and `__name__` are `str`s, and type what's made of them; not where the module binds one."""
    source: str = """
    import os


    def f() -> None:
        a = __file__
        b = __name__
        c = os.path.dirname(os.path.abspath(__file__))
        d = __doc__
    """
    assert _fixed(source) == {
        "a": ("str", False),
        "b": ("str", False),
        "c": ("str", False),
        "d": (None, False),
    }
    bound: str = "__file__ = None\n\n\ndef f() -> None:\n    a = __file__\n    b = __name__\n"
    assert _fixed(bound) == {"a": (None, False), "b": ("str", False)}


def test_the_name_of_a_class_is_text_whatever_its_instance_is() -> None:
    """`type(x).__name__` and `x.__class__.__name__` are `str`s; `x.__class__` is `type[C]` by `x`'s `C`."""
    source: str = """
    class Box:
        def label(self) -> str:
            a = self.__class__
            b = self.__class__.__name__
            return b


    def f(s: str, box: Box, kind: type[Box], maybe: Box | None, q) -> None:
        c = type(q).__name__
        d = q.__class__.__qualname__
        e = type(s).__module__
        g = q.__class__
        h = s.__class__
        i = kind.__class__
        j = maybe.__class__
        k = type(q).__doc__
        m = q.__name__
        n = box.__class__.__name__.upper()
    """
    assert _fixed(source) == {
        "a": ("type[Box]", False),
        "b": ("str", False),
        "c": ("str", False),
        "d": ("str", False),
        "e": ("str", False),
        "g": (None, False),
        "h": ("type[str]", False),
        "i": (None, False),  # a class's own class is its metaclass
        "j": (None, False),  # `None` has a class too
        "k": (None, False),
        "m": (None, False),  # not a class's, for all `--fix` knows
        "n": ("str", False),
    }


def test_a_member_of_an_optional_value_is_the_values_own() -> None:
    """A member of an `X | None` is `X`'s: a checker has narrowed it there, or reports the access."""
    source: str = """
    import re
    from typing import Optional


    class Box:
        size: int
        label: str | None

        def name(self) -> str:
            return "box"


    def f(s: str, box: Box | None, other: Optional[Box], early: None | Box, either: Box | str | None) -> None:
        m = re.match(s, s)
        a = m.start()
        b = m.string
        c = box.size
        d = box.name()
        e = other.size
        g = early.size
        h = either.size
        i = box.label
        j = box.name().upper()
    """
    assert _fixed(source) == {
        "m": ("re.Match[str] | None", False),
        "a": ("int", False),
        "b": ("str", False),
        "c": ("int", False),
        "d": ("str", False),
        "e": ("int", False),
        "g": ("int", False),
        "h": (None, False),  # a union of two types has no one member
        "i": (None, False),  # itself an `X | None`: narrowed before it's used
        "j": ("str", False),
    }
