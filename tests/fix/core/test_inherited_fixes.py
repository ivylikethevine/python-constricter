# SPDX-License-Identifier: MIT
"""`--fix` for a method a class doesn't define: the base's that does, in method resolution order."""

import ast
import textwrap
from itertools import starmap
from typing import Final, TypeAlias

import pytest

from constricter import check_source
from constricter.fix.core import inherited

_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_SOURCE: Final = """
import abc
import other
from typing import Generic, Self, TypeVar

T = TypeVar("T")


class Base:
    limit = 3

    def size(self) -> int:
        return 1

    def clone(self) -> Self:
        return self

    def label(self):
        return "x"

    def me(self):
        return self

    def made(self):
        return [Base()]


class Mixin(abc.ABC):
    def extra(self) -> float:
        return 1.0

    def size(self) -> bool:
        return True


class Child(Base, object):
    def own(self):
        return b"y"

    def f(self) -> None:
        child_size = self.size()
        child_clone = self.clone()
        child_label = self.label()
        child_me = self.me()
        child_made = self.made()
        child_own = self.own()
        child_limit = self.limit()
        child_missing = self.missing()


class Grand(Mixin, Child):
    def g(self) -> None:
        grand_size = self.size()
        grand_extra = self.extra()
        grand_label = self.label()
        grand_own = self.own()


class Shadow(Child):
    if other.FLAG:
        size = None
    else:
        import label

    def h(self) -> None:
        shadow_size = self.size()
        shadow_label = self.label()
        shadow_own = self.own()


class Hidden(other.Thing, Base):
    def i(self) -> None:
        hidden_size = self.size()


class After(Base, other.Thing):
    def j(self) -> None:
        after_size = self.size()
        after_else = self.other()


class Box(Generic[T]):
    def get(self):
        return 1


class Crate(Box):
    def k(self) -> None:
        crate_get = self.get()


class Twice:
    def one(self):
        return 1


class Twice:
    pass


class Later(Twice):
    def m(self) -> None:
        later_one = self.one()


def use(child: Child, grand: Grand) -> None:
    used_size = child.size()
    used_clone = grand.clone()
    used_label = grand.label()
"""


def _fixes(source: str) -> _Fixes:
    """Check `source`.

    Returns:
      Each function's untyped local's fix, and whether it's a guess.

    """
    return {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(source))}


def test_an_inherited_method_is_the_base_class_one() -> None:
    """A declared return is certain, `return`s a guess; `Self` is the receiver's own class."""
    assert _fixes(_SOURCE) == {
        "child_size": ("int", False),
        "child_clone": ("Child", False),
        "child_label": ("str", True),
        "child_me": (None, False),  # `Base`, by its `return`s: but a `Child` here
        "child_made": (None, False),
        "child_own": ("bytes", True),
        "child_limit": (None, False),  # not a method
        "child_missing": (None, False),
        "grand_size": ("bool", False),  # `Mixin` comes before `Child`
        "grand_extra": ("float", False),
        "grand_label": ("str", True),
        "grand_own": ("bytes", True),
        "shadow_size": (None, False),  # its body binds `size`, and `label`
        "shadow_label": (None, False),
        "shadow_own": ("bytes", True),
        "hidden_size": (None, False),  # a base out of sight comes first
        "after_size": ("int", False),
        "after_else": (None, False),
        "crate_get": (None, False),  # a generic base's members depend on its arguments
        "later_one": (None, False),  # a name two classes share is neither
        "used_size": ("int", False),
        "used_clone": ("Grand", False),
        "used_label": ("str", True),
    }


@pytest.mark.parametrize(
    ("source", "order"),
    [
        ("class A: pass\nclass B(A): pass\nclass C(B): pass", {"A": (), "B": ("A",), "C": ("B", "A")}),
        (
            "class O: pass\nclass A(O): pass\nclass B(O): pass\nclass C(A, B): pass",
            {"O": (), "A": ("O",), "B": ("O",), "C": ("A", "B", "O")},
        ),
        ("class A(x.Y): pass\nclass B(A, z.W): pass", {"A": (), "B": ("A",)}),
        ("class A(B): pass\nclass B(A): pass", {"A": (), "B": ()}),  # each the other's base
        (
            "class A: pass\nclass B: pass\nclass X(A, B): pass\nclass Y(B, A): pass\nclass Z(X, Y): pass",
            {"A": (), "B": (), "X": ("A", "B"), "Y": ("B", "A"), "Z": ()},  # `Z`'s bases disagree
        ),
        ("class A: pass\nclass A: pass\nclass B(A): pass", {"B": ()}),
    ],
)
def test_the_order_of_a_class_is_pythons(source: str, order: dict[str, tuple[str, ...]]) -> None:
    """Python's own linearisation, as far as the module sees."""
    assert inherited.lineage(ast.parse(source), {}, frozenset()).order == order


def test_a_class_binds_what_its_body_stores() -> None:
    """Through its compound statements, not its methods' own."""
    source: str = textwrap.dedent(
        """\
        class A:
            a = b = 1
            c: int
            import d.e, f as g
            from h import i
            for j in ():
                with k as l:
                    m = 2
            def n(self):
                o = 3
            class P:
                q = 4
        """,
    )
    assert inherited.lineage(ast.parse(source), {}, frozenset()).bound == {
        "A": frozenset("abcdgijlmn") | {"P"},
        "P": frozenset({"q"}),
    }


_LIBRARY: Final = """
import collections
import threading
import unittest
from asyncio.events import Handle
from pathlib import Path
from unittest import TestCase

import other


class Mixin:
    def id(self) -> int:
        return 1


class Case(unittest.TestCase):
    def test(self) -> None:
        case_id = self.id()
        case_result = self.defaultTestResult()
        case_message = self.longMessage
        case_missing = self.missing()
        case_nothing = self.nothing


class Mixed(Mixin, TestCase):
    def test(self) -> None:
        mixed_id = self.id()
        mixed_count = self.countTestCases()


class Later(Case):
    def test_more(self) -> None:
        later_id = self.id()


class Own(Path):
    def exists(self) -> int:
        return 1

    def f(self) -> None:
        own_resolved = self.resolve()
        own_exists = self.exists()
        own_name = self.name
        own_parent = self.parent


class Aliased(Handle):
    def f(self) -> None:
        aliased_cancelled = self.cancelled()


class Counted(collections.Counter):
    def f(self) -> None:
        counted_total = self.total()


class Elsewhere(other.Thing, unittest.TestCase):
    def test(self) -> None:
        elsewhere_id = self.id()


def use(case: Case, worker: threading.Thread) -> None:
    used_id = case.id()
    used_alive = worker.is_alive()


def shadowing(case: Case, unittest: int) -> None:
    shadowed_id = case.id()
"""


def test_a_member_of_a_standard_library_base_is_typed_by_the_tables() -> None:
    """Where no class before it binds the name; not one that is the base itself, which may be `Self`."""
    assert _fixes(_LIBRARY) == {
        "case_id": ("str", False),
        "case_result": ("unittest.TestResult", False),
        "case_message": ("bool", False),
        "case_missing": (None, False),
        "case_nothing": (None, False),
        "mixed_id": ("int", False),  # `Mixin` comes first
        "mixed_count": ("int", False),
        "later_id": ("str", False),
        "own_resolved": (None, False),  # a `Path`, or the class itself
        "own_exists": ("int", False),
        "own_name": ("str", False),
        "own_parent": (None, False),
        "aliased_cancelled": ("bool", False),
        "counted_total": (None, False),  # a generic base's members depend on its arguments
        "elsewhere_id": (None, False),  # a base out of sight comes first
        "used_id": ("str", False),
        "used_alive": ("bool", False),
        "shadowed_id": (None, False),  # `unittest` isn't the module there
    }


def test_a_class_out_of_sight_defines_its_own() -> None:
    """A receiver the module doesn't define is looked up as itself."""
    found: inherited.Lineage = inherited.lineage(
        ast.parse("class A: y = 1\nclass B(A): x = 1"),
        {},
        frozenset(),
    )
    asked: tuple[tuple[str, str], ...] = (("m.C", "x"), ("B", "x"), ("B", "y"), ("B", "z"))
    assert list(starmap(found.definer, asked)) == ["m.C", "B", "A", None]


_SEVERAL: Final = """
import collections
import threading
import unittest
from collections import UserDict
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


class Both(threading.Thread, unittest.TestCase):
    def run_it(self) -> None:
        ident = self.id()
        name = self.name
        alive = self.is_alive()
        missing = self.missing()


class Shared(unittest.TestCase, unittest.IsolatedAsyncioTestCase):
    def run_it(self) -> None:
        first = self.id()
        second = self.addAsyncCleanup(print)


class Ordered(collections.OrderedDict[str, int]):
    def total(self) -> None:
        item = self.popitem()
        for key in self:
            pass
        for k, v in self.items():
            pass


class Users(UserDict[str, bytes]):
    def total(self) -> None:
        data = self.data
        user = self["a"]


class Bare(collections.OrderedDict):
    def total(self) -> None:
        bare = self.popitem()


class Short(collections.OrderedDict[str]):
    def total(self) -> None:
        short = self.popitem()


class Under(Ordered):
    def total(self) -> None:
        under = self.popitem()


class Deep(collections.ChainMap[K, V]):
    def total(self) -> None:
        inside = self.maps


class Hidden(Ordered):
    def popitem(self):
        return self.missing

    def total(self) -> None:
        hidden = self.popitem()


def use(ordered: Ordered, users: Users, deep: Deep) -> None:
    outside = deep.maps
    taken = ordered.popitem()
    read = users["a"]
    for each in ordered:
        pass
"""


def test_an_order_goes_on_past_a_library_class_and_through_a_generic_one() -> None:
    """Past one held whole, to the next base's members; a generic one's, by the arguments it's given."""
    assert _fixes(_SEVERAL) == {
        "ident": ("str", False),  # the second library class's: the first has no `id`
        "name": ("str", False),
        "alive": ("bool", False),
        "first": ("str", False),
        "item": ("tuple[str, int]", False),
        "key": ("str", False),
        "k": ("str", False),
        "v": ("int", False),
        "data": ("dict[str, bytes]", False),
        "user": ("bytes", False),
        "under": ("tuple[str, int]", False),
        "taken": ("tuple[str, int]", False),
        "read": ("bytes", False),
        "each": ("str", False),
        # Two bases sharing an ancestor; a generic base without its arguments, or too few.
        **dict.fromkeys(("missing", "second", "bare", "short", "hidden"), (None, False)),
        # A base given type variables: they mean nothing outside the class.
        **dict.fromkeys(("inside", "outside"), (None, False)),
    }
