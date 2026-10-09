# SPDX-License-Identifier: MIT
"""`--fix --unsafe-fixes` where a guess, once declared, makes an error of what's done with the name."""

import textwrap

from constricter import Checks, check_source


def _found(source: str, checks: Checks | None = None) -> dict[str, tuple[str | None, bool]]:
    return {
        o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(source), checks=checks or Checks())
    }


_OPTIONS: str = """
class Option:
    cb: int = 0

OPTIONS: dict[str, Option] = {}

def registered(key: str):
    return OPTIONS.get(key)
"""


def test_a_guessed_union_used_where_nothing_narrows_it_has_no_fix() -> None:
    """A checker takes an unannotated function's call for anything: declared, `opt.cb` is an error."""
    source: str = """
    def f(key: str, keys: list[str]) -> None:
        a = registered(key)
        a.cb
        b = registered(key)
        b[0]
        c = registered(key)
        d = registered(key)
        d = registered(key)
        d.cb
    """
    assert _found(_OPTIONS + textwrap.dedent(source)) == {
        "a": (None, False),
        "b": (None, False),  # an item of it
        "c": ("Option | None", True),  # nothing is taken of it
        "d": ("Option | None", True),  # bound again: a checker narrows it to what it's bound to
    }


def test_a_guessed_union_is_kept_where_every_use_is_narrowed() -> None:
    """By the test around the use, on its own lines, or before it in its block."""
    source: str = """
    def f(key: str, keys: list[str]) -> None:
        a = registered(key)
        if a:
            a.cb
        b = registered(key)
        if b and b.cb:
            pass
        c = registered(key)
        c.cb if c else 0
        d = registered(key)
        print(d and d.cb)
        e = registered(key)
        assert e is not None
        e.cb
        g = registered(key)
        print([g.cb for _ in keys if g])
        h = registered(key)
        while h:
            h.cb
        i = registered(key)
        if i is None:
            return
        i.cb
    """
    assert _found(_OPTIONS + textwrap.dedent(source)) == dict.fromkeys(
        "abcdeghi",
        ("Option | None", True),
    )


def test_a_union_a_checker_held_already_is_kept() -> None:
    """A declared type's union, or a library's, is an error as released, if at all."""
    source: str = """
    import re

    def f(text: str, either: int | str) -> None:
        a = either
        a.real
        b = re.match("x", text)
        b.group()
    """
    assert _found(source) == {"a": ("int | str", True), "b": ("re.Match[str] | None", False)}


def test_an_attribute_its_class_hasnt_leaves_a_returned_class_no_fix() -> None:
    """A class of the module's, every attribute in sight, of which the function takes another."""
    source: str = """
    class Config:
        pass

    class Slotted:
        __slots__ = ("expr",)

    class Base(object):
        kind: int = 0

        def reset(self) -> None:
            self.count = 0

    class Sub(Base):
        from os import sep

        class Inner:
            pass

    def config():
        made = Config()
        made.verbose = True
        return made

    def slotted():
        return Slotted()

    def sub():
        return Sub()

    def f() -> None:
        a = config()
        a.verbose
        b = config()
        b.__class__
        c = slotted()
        c.expr
        d = slotted()
        d.other
        e = sub()
        print(e.kind, e.count, e.reset, e.sep, e.Inner)
        g = sub()
        g.missing
        h = sub()
        h[0]
    """
    assert _found(source) == {
        "made": ("Config", True),
        "a": (None, False),
        "b": ("Config", True),  # every object has it
        "c": ("Slotted", True),
        "d": (None, False),
        "e": ("Sub", True),  # its own, and its base's
        "g": (None, False),
        "h": ("Sub", True),  # an item, not an attribute
    }


def test_a_certain_returned_class_is_held_to_its_attributes_too() -> None:
    """Certain once the function's own local is declared, as a first pass of `--fix` leaves it."""
    source: str = """
    class Config:
        pass

    def config():
        made: Config = Config()
        return made

    def f() -> None:
        a = config()
        a.verbose
        b = config()
    """
    assert _found(source) == {"a": (None, False), "b": ("Config", False)}


def test_a_class_with_attributes_out_of_sight_keeps_its_fix() -> None:
    """Defined twice, decorated, with a metaclass or a base that isn't the module's, or dynamic."""
    source: str = """
    import abc
    import enum

    def decorated(cls):
        return cls

    class Twice:
        pass

    class Twice:
        pass

    @decorated
    class Decorated:
        pass

    class Meta(metaclass=abc.ABCMeta):
        pass

    class Outside(enum.Enum):
        pass

    class Unknown(Elsewhere):
        pass

    class Under(Outside):
        pass

    class Dynamic:
        def __getattr__(self, name: str) -> int:
            return 1

    class Follows(Dynamic):
        pass

    class Setting:
        def fill(self) -> None:
            setattr(self, "x", 1)

    class Round(Trip):
        pass

    class Trip(Round):
        pass

    def twice():
        return Twice()

    def decorate():
        return Decorated()

    def meta():
        return Meta()

    def outside():
        return Outside()

    def unknown():
        return Unknown()

    def under():
        return Under()

    def dynamic():
        return Dynamic()

    def follows():
        return Follows()

    def setting():
        return Setting()

    def trip():
        return Trip()

    def f() -> None:
        a = twice()
        a.x
        b = decorate()
        b.x
        c = meta()
        c.x
        d = outside()
        d.x
        e = unknown()
        e.x
        g = under()
        g.x
        h = dynamic()
        h.x
        i = follows()
        i.x
        j = setting()
        j.x
        k = trip()
        k.x
    """
    found: dict[str, tuple[str | None, bool]] = _found(source)
    assert {name: found[name][1] for name in "abcdeghijk"} == dict.fromkeys("abcdeghijk", True)
    assert found["a"] == ("Twice", True)
    assert found["k"] == ("Trip", True)


def test_a_name_of_no_known_type_has_none_past_a_branch_that_types_it() -> None:
    """It may still hold what it held before the branch."""
    source: str = """
    import os

    def numeric(flag: bool, x):
        if flag:
            x = float(x)
            inside = x
        after = x
        return x

    def loaded(path):
        for part in path:
            part = str(part)
            within = part
        past = part
        try:
            path = os.fspath(path)
        except TypeError:
            pass
        left = path

    def use(flag: bool, value) -> None:
        a = numeric(flag, value)
    """
    assert _found(source) == {
        "inside": ("float", True),
        "after": (None, False),
        "part": (None, False),
        "within": ("str", True),
        "past": (None, False),
        "left": (None, False),
        "a": (None, False),
    }


def test_a_return_of_what_the_function_alone_can_name_types_no_call() -> None:
    """A class it imports or defines in its own body."""
    source: str = """
    def table():
        from decimal import Decimal

        return Decimal(1)

    def aliased():
        import decimal as d

        return d.Decimal(1)

    def local():
        class Row:
            pass

        return Row()

    def f() -> None:
        a = table()
        b = local()
        c = aliased()
    """
    assert _found(source) == {"a": (None, False), "b": (None, False), "c": (None, False)}


def test_a_union_isnt_split_over_several_names() -> None:
    """`name, length` of `[["prefix", 24], ...]` are a `str` and an `int`, not each either."""
    source: str = """
    from typing import NamedTuple

    class Size(NamedTuple):
        width: int | None
        height: int | None

    def split(rows: list[list[str | int]], sizes: list[tuple[int | None, int | None]], size: Size) -> None:
        parts = [["prefix", 24], ["version", 8]]
        for name, length in parts:
            pass
        first, second = parts[0]
        for one in parts:
            pass
        for key, count in rows:
            pass
        for width, height in sizes:
            pass
        wide, high = size
    """
    assert _found(source) == {
        "parts": ("list[list[str | int]]", True),
        "name": (None, False),
        "length": (None, False),
        "first": (None, False),
        "second": (None, False),
        "one": ("list[str | int]", True),
        "key": (None, False),  # declared or not: a second pass sees the first's guess declared
        "count": (None, False),
        "width": ("int | None", False),  # a tuple of that many says which is which
        "height": ("int | None", False),
        "wide": ("int | None", False),
        "high": ("int | None", False),
    }


def test_a_display_of_a_narrowed_attribute_has_no_fix() -> None:
    """`[self.offset]` under `isinstance(self.offset, list)` holds the narrowed type."""
    source: str = """
    class Holiday:
        offset: int | list[int] | None = None

        def dates(self, other: int | list[int]) -> None:
            if not isinstance(self.offset, list):
                offsets = [self.offset]
                others = [other]
    """
    assert _found(source) == {"offsets": (None, False), "others": ("list[int | list[int]]", False)}


def test_a_name_bound_in_another_arm_to_an_unknown_type_has_no_fix() -> None:
    """Only one arm runs: a checker that knows the other's type holds it to the first's."""
    source: str = """
    def arms(flag: bool, thing, text: str) -> None:
        if flag:
            a = "None"
        else:
            a = thing.dtype
        if flag:
            b = 1
        elif text:
            b = thing.size
        try:
            c = int(text)
        except ValueError:
            c = thing
        match text:
            case "a":
                d = 1
            case _:
                d = thing
        e = 1
        if flag:
            e = thing
        for _ in text:
            g = 1
        else:
            g = thing
        with thing:
            h = 1
        h = thing
        if flag:
            i: int = 1
            j = 1

            def inner() -> None:
                k = thing

        else:
            i = thing
            j += 1
    """
    assert _found(source) == {
        "a": (None, False),
        "b": (None, False),
        "c": (None, False),
        "d": (None, False),
        "e": ("int", True),  # one after the other: a guess still
        "g": ("int", True),
        "h": ("int", True),
        "j": ("int", False),
        "k": (None, False),
    }
