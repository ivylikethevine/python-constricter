# SPDX-License-Identifier: MIT
"""`--fix` where a type checker sees the value otherwise: narrowable unions, constants, `Self`, generics."""

import textwrap
from typing import Final

import pytest

from constricter import Checks, Offence, check_source


def _found(source: str, checks: Checks | None = None) -> dict[str, tuple[str | None, bool]]:
    return {
        o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(source), checks=checks or Checks())
    }


def test_a_read_of_a_union_may_be_narrowed_where_it_is_so_is_a_guess() -> None:
    """A copy, attribute or subscript of a union, and a filtered comprehension of one, are guesses.

    One of an `X | None` isn't offered at all: it's nearly always checked for `None` first. Nor is a
    bare `None`.
    """
    source: str = """
    class C:
        x: int | None

    def f(
        c: C,
        maybe: int | None,
        pairs: dict[str, int | None],
        items: list[int | str],
        either: int | str,
        options: list[int | None],
        spelled: "list[Optional[int]]",
        nothing: None,
    ) -> None:
        a = maybe
        b = c.x
        d = pairs["k"]
        e = [i for i in items if isinstance(i, int)]
        g = [i for i in items]
        h = [maybe]
        i = either
        j = [o for o in options if o]
        k = nothing
        m = [s for s in spelled if s]
    """
    assert _found(source) == {
        "a": (None, False),
        "b": (None, False),
        "d": (None, False),
        "e": ("list[int | str]", True),
        "g": ("list[int | str]", False),  # no condition to narrow it
        "h": ("list[int | None]", False),  # a container of one isn't narrowed with it
        "i": ("int | str", True),
        "j": (None, False),
        "k": (None, False),
        "m": (None, False),
    }


def test_a_read_of_what_the_function_tests_may_be_narrowed_so_is_a_guess() -> None:
    """`isinstance`, a `TypeGuard`, an `assert`, a `match`: a read of what's tested is a guess."""
    source: str = """
    class C:
        x: object

    def is_int(o: object) -> bool:
        return isinstance(o, int)

    def f(o: object, p: object, c: C, q: object, r: object, s: object) -> None:
        if isinstance(o, int):
            a = o
        b = p if is_int(p) else None
        assert c.x
        d = c.x
        match q:
            case int():
                e = q
        g = [i for i in [r] if i]
        h = r
        k = s
    """
    assert {name: fix for name, fix in _found(source).items() if len(name) == 1} == {
        "a": ("object", True),
        "b": (None, False),
        "d": ("object", True),
        "e": ("object", True),
        "g": ("list[object]", False),
        "h": ("object", False),  # `r`'s test is on the comprehension's `i`, not on `r`
        "k": ("object", False),
    }


def test_after_a_rebinding_a_name_is_what_it_was_bound_to() -> None:
    """A checker narrows a name to its value: a member of its declared union for certain, else a guess."""
    source: str = """
    def f(maybe: int | None, items: tuple[str, ...], n: int, u) -> None:
        maybe = 1
        a = maybe
        items = [s for s in items]
        for b in items:
            pass
        n = u
        c = n
        n = 2
        d = n
    """
    assert {name: fix for name, fix in _found(source).items() if len(name) == 1} == {
        "a": ("int", False),
        "b": ("str", True),  # `items` is a `list[str]` now: mypy doesn't narrow a `tuple`'s annotation to it
        "c": ("int", True),  # an unknown value may be anything
        "d": ("int", True),  # a guess, from `c` on
    }


def test_an_all_caps_module_literal_is_a_constant_to_pyright_so_is_a_guess() -> None:
    """To pyright an ALL_CAPS module name is a constant: it keeps its `Literal` type, which `str` widens.

    One passed to a call is declared `Final`, which keeps it (a guess still); one bound again isn't.
    """
    source: str = """
    MODE = "r"
    _LIMIT = -3
    FLAG = True
    RATE = 0.5
    lower = "x"
    NAMES = ["a"]
    UNUSED = "x"
    AGAIN = "a"
    AGAIN = "b"

    def f(limit: int = _LIMIT, *, flag: bool = FLAG) -> None:
        LOCAL = "x"
        open("f", MODE)
        g(rate=RATE, lower=lower, names=NAMES, again=AGAIN)
    """
    assert _found(source, Checks(all_scopes=True)) == {
        "MODE": ("Final", True),
        "_LIMIT": ("Final", True),
        "FLAG": ("Final", True),
        "AGAIN": (None, False),
        "RATE": ("float", False),  # no `Literal` of a float
        "lower": ("str", False),
        "NAMES": ("list[str]", False),
        "UNUSED": ("str", False),  # passed to nothing here: no parameter to narrow it for
        "LOCAL": ("str", False),  # a function's local is narrowed to its literal where it's read
    }


SELFISH: Final = """
{imports}
class Node:
    def clone(self) -> Self:
        return self

    @classmethod
    def make(cls) -> Self:
        return cls()

    def parent(self) -> Node:
        return self

    def walk(self, other: Node) -> Self:
        a = self
        b = self.clone()
        c = self.parent()
        d = other.clone()
        return a

    @classmethod
    def build(cls) -> Self:
        e = cls.make()
        return e

    def plain(self) -> None:
        h = self
        i = self.clone()

    @staticmethod
    def other(self: Node) -> None:
        g = self
"""


@pytest.mark.parametrize(
    ("imports", "spelled"),
    [
        ("from typing import Self", "Self"),
        ("from typing_extensions import Self", "Self"),
        ("import typing as t", "t.Self"),
        ("from typing import Self as S", "S"),
    ],
)
def test_self_and_its_self_methods_are_self(imports: str, spelled: str) -> None:
    """`self`, and a `Self` method called on `self` or `cls`, are `Self`, as the module imports it."""
    found: dict[str, tuple[str | None, bool]] = _found(SELFISH.format(imports=imports))
    assert {name: fix for name, (fix, _) in found.items() if len(name) == 1} == {
        "a": spelled,
        "b": spelled,
        "c": "Node",  # declared to return `Node`: so it does
        "d": "Node",  # not on `self`: its own class
        "e": spelled,
        "g": "Node",  # a staticmethod's first parameter is just a parameter
        "h": "Node",  # a signature without `Self`: mypy takes `self` for its class
        "i": "Node",
    }


def test_without_self_imported_a_self_is_not_offered() -> None:
    """`typing.Self` is Python 3.11's: no import is added for it, and without one there's no fix."""
    found: dict[str, tuple[str | None, bool]] = _found(SELFISH.format(imports="import os"))
    assert found["a"] == (None, False)
    assert found["b"] == (None, False)
    assert found["c"] == ("Node", False)


def test_a_self_takes_nothing_else() -> None:
    """A `Self` later bound to anything but `Self` (the class itself, say) has no one type: no fix."""
    source: str = """
    from typing import Self

    class Node:
        def clone(self) -> Self:
            return self

        def walk(self, other: Node, flag: bool) -> Self:
            a = self
            if flag:
                a = other
            b = self
            b = self.clone()
            return b
    """
    found: dict[str, tuple[str | None, bool]] = _found(source)
    assert (found["a"], found["b"]) == ((None, False), ("Self", False))


def test_a_generic_class_is_never_written_bare() -> None:
    """`[self]` in a generic class would be `list[Box]`, missing its type arguments: nothing is offered."""
    source: str = """
    from typing import Generic, TypeVar

    T = TypeVar("T")

    class Box(Generic[T]):
        def all(self) -> None:
            a = [self]
            b = {"k": [1]}

    class Plain:
        def all(self) -> None:
            c = [self]
    """
    found: dict[str, tuple[str | None, bool]] = _found(source)
    assert {name: found[name] for name in "abc"} == {
        "a": (None, False),
        "b": ("dict[str, list[int]]", False),
        "c": ("list[Plain]", False),
    }


def test_a_typing_type_variable_is_never_a_calls_type() -> None:
    """`AnyStr`, however `typing` is imported, depends on the arguments."""
    source: str = """
    import typing
    from typing import AnyStr

    def pad(x: AnyStr) -> AnyStr:
        return x

    def pad2(x: typing.AnyStr) -> typing.AnyStr:
        return x

    def f() -> None:
        a = pad("x")
        b = pad2("x")
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert [(o.name, o.fix) for o in found] == [("a", None), ("b", None)]


def test_a_chained_read_of_a_union_or_of_what_is_tested_is_a_guess() -> None:
    """Through any receiver (`self.a.b`), as through a local: what the function tests is a guess.

    An `X | None` isn't offered at all.
    """
    source: str = """
    class Inner:
        x: int | None
        y: object
        z: int

    class Outer:
        inner: Inner

        def f(self) -> None:
            a = self.inner.x
            if isinstance(self.inner.y, int):
                b = self.inner.y
            d = self.inner.z
    """
    assert _found(source) == {"a": (None, False), "b": ("object", True), "d": ("int", False)}
