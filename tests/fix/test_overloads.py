# SPDX-License-Identifier: MIT
"""`--fix` for standard-library calls whose arguments decide their type, by the signatures they match."""

import textwrap
from typing import Final

import pytest

from constricter import Checks, Offence, check_source
from constricter.fix import stdlib
from constricter.fix.stdlib import Accepts, Signature

UNANNOTATED: Final = "LVA001"
SOURCE: Final = """
import ast
import os
import re
from re import compile as rc


def f(fd: int, data: bytes, unknown, parts: list[str], options: dict[str, str]) -> None:
    a = os.listdir()
    b = os.listdir(data)
    c = os.listdir(fd)
    d = os.listdir(unknown)
    e = re.compile("x")
    g = rc(b"x")
    h = ast.parse("x")
    i = ast.parse("x", mode="eval")
    j = os.path.join(*parts)
    k = os.path.join("a", **options)
    m = os.listdir(path=".")
    n = os.listdir(".", ".")
    p = os.listdir(nothing=".")
    q = os.path.split("a/b")
    r = os.getenv("X", None)
"""
SHADOWED: Final = """
import os


def f(list) -> None:
    a = os.listdir()
"""
_EVERY: Final = "y" * 9
_T: Final = Accepts(v=_EVERY, var={"LiteralString": ["T", "str"], "bytes": ["T", "bytes"]})
FAKE: Final = [
    [
        Signature(params=[("a", "e", False, _T), ("b", "e", False, _T)], returns="T"),
    ],
]
RECEIVERS: Final = """
import re
from typing import Any


def g(p: re.Pattern[Any], q: re.Pattern[str], s: str) -> None:
    t = p.match(s)
    u = q.match(s)
"""
GENERIC: Final = """
import io
import logging
from collections import OrderedDict as OD


def f(p: str) -> None:
    a = logging.StreamHandler()
    b = OD()
    c = io.BufferedReader(io.FileIO(p))
"""
UNBOUND: Final = [[Signature(params=[("a", "e", False, None)], returns="tuple[U, ...]")]]
MADE_UP: Final = """
import os


def f() -> None:
    a = os.made_up("x", "y")
    b = os.made_up("x", b"y")
    c = os.unbound(1)
"""


def _fixes(source: str) -> dict[str, str | None]:
    found: list[Offence] = check_source(textwrap.dedent(source))
    return {o.name: o.fix for o in found if o.code == UNANNOTATED}


def test_a_call_is_typed_by_the_signature_its_arguments_match() -> None:
    """The first signature taking them, if every one before certainly refuses them; classes imported.

    A call that unpacks its arguments, or passes one no signature has, is left alone; a literal
    argument picks a `Literal` overload; a type variable takes the argument's type.
    """
    assert _fixes(SOURCE) == {
        "a": "list[str]",
        "b": "list[bytes]",
        "c": "list[str]",
        "d": None,  # `str` or `bytes`: unknown
        "e": "re.Pattern[str]",
        "g": "re.Pattern[bytes]",  # through `import re`
        "h": "ast.Module",
        "i": "ast.Expression",
        "j": None,
        "k": None,
        "m": "list[str]",
        "n": None,
        "p": None,
        "q": "tuple[str, str]",
        "r": "str | None",
    }


def test_a_generic_receiver_binds_its_class_type_parameters() -> None:
    """`Pattern[str]`'s methods declared for `self: Pattern[str]` apply; with `Pattern[Any]` none is sure."""
    assert _fixes(RECEIVERS) == {"t": None, "u": "re.Match[str] | None"}


def test_a_standard_library_generic_class_isnt_written_bare() -> None:
    """Unless every type parameter it has has a default (`io.BufferedReader`'s)."""
    assert _fixes(GENERIC) == {"a": None, "b": None, "c": "io.BufferedReader"}


def test_a_builtin_the_module_rebinds_isnt_written() -> None:
    """`list[str]` means something else where `list` is a parameter."""
    assert _fixes(SHADOWED) == {"a": None}


def test_type_variables_bind_to_one_type_or_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two arguments binding one type variable must agree; one no argument binds leaves the call alone."""
    monkeypatch.setitem(stdlib.OVERLOADS, "os.made_up", FAKE)
    monkeypatch.setitem(stdlib.OVERLOADS, "os.unbound", UNBOUND)
    assert _fixes(MADE_UP) == {"a": "str", "b": None, "c": None}


GENERICS: Final = """
import array
import collections
import copy
import itertools
import weakref


class Foo:
    pass


def f(
    names: list[str],
    ids: set[int],
    table: dict[str, int],
    same: tuple[str, ...],
    mixed: tuple[str, int],
    empty: tuple[()],
    obj: Foo,
    unknown,
) -> None:
    a = itertools.chain(names, names)
    b = itertools.chain(names, ids)
    c = itertools.product(names, ids)
    d = itertools.groupby(names)
    e = collections.deque(names)
    g = collections.deque()
    h = array.array("i")
    i = copy.copy(obj)
    j = copy.deepcopy(names)
    k = weakref.ref(obj)
    m = itertools.chain("ab", "cd")
    n = collections.deque(table)
    o = itertools.chain(same)
    p = copy.copy(unknown)
    q = itertools.chain(mixed)
    r = collections.deque(obj)
    s = copy.copy(1)
    t = itertools.chain(empty)
    u = collections.deque(unknown)
"""
REBOUND: Final = """
import collections


def f(list, names: list[str]) -> None:
    a = collections.deque(names)
"""


def test_a_generic_class_is_typed_by_what_its_arguments_bind() -> None:
    """Its constructor's signatures, as a function's: containers bind by their elements, anything by its type.

    A tuple binds by its one element type (not several); a type variable nothing binds, or two
    arguments bind differently, leaves the call alone.
    """
    assert _fixes(GENERICS) == {
        "a": "itertools.chain[str]",
        "b": None,  # `str` and `int`
        "c": "itertools.product[tuple[str, int]]",
        "d": "itertools.groupby[str, str]",
        "e": "collections.deque[str]",
        "g": None,
        "h": "array.array[int]",
        "i": "Foo",
        "j": "list[str]",
        "k": "weakref.ReferenceType[Foo]",
        "m": "itertools.chain[str]",
        "n": "collections.deque[str]",  # a `dict`'s keys
        "o": "itertools.chain[str]",
        "p": None,
        "q": None,
        "r": None,  # not iterable, as far as the tables know
        "s": "int",
        "t": None,
        "u": None,
    }


def test_a_container_the_module_rebinds_binds_nothing() -> None:
    """`list[str]` isn't a builtin list where `list` is a parameter."""
    assert _fixes(REBOUND) == {"a": None}


MODULE_LEVEL: Final = """
import array
import itertools

counter = itertools.count()
chained = itertools.chain("a", "b")
codes = array.array("i")
"""


def test_a_module_annotation_a_python_cant_subscript_is_quoted() -> None:
    """A module's annotations are evaluated: `itertools.count[int]` raises, `itertools.chain[str]` doesn't.

    `array.array` can be subscripted from Python 3.12 only.
    """
    found: list[Offence] = check_source(textwrap.dedent(MODULE_LEVEL), checks=Checks(all_scopes=True))
    assert {o.name: o.fix for o in found} == {
        "counter": '"itertools.count[int]"',
        "chained": "itertools.chain[str]",
        "codes": '"array.array[int]"',
    }


TESTED: Final = """
import collections
from typing import TypeGuard


def is_str(value: object) -> TypeGuard[str]:
    return isinstance(value, str)


def f(item: int | str, other: int) -> None:
    if is_str(item):
        a = collections.deque([item])
    b = collections.deque([other])
"""


def test_a_read_the_function_tests_makes_a_type_it_binds_a_guess() -> None:
    """A type checker sees `item` narrowed where it's read, and the `deque` of that type."""
    found: list[Offence] = check_source(textwrap.dedent(TESTED))
    assert {o.name: (o.fix, o.unsafe) for o in found if o.code == UNANNOTATED} == {
        "a": ("collections.deque[int | str]", True),
        "b": ("collections.deque[int]", False),
    }


PROTOCOLS: Final = """
import functools
import math
import re
from re import Match as M


def helper(a: int, b: int) -> str:
    return str(a + b)


def f(x: float, n: int, m: re.Match[str], p: re.Pattern[bytes], bare: M, unknown) -> None:
    a = math.floor(x)
    b = math.ceil(n)
    c = functools.partial(helper, 1)
    d = m.string
    e = p.pattern
    g = m.pos
    h = m.re
    i = functools.partial(unknown, 1)
    j = math.floor(unknown)
    k = bare.string
    o = m.nothing
    q = unknown.string
"""


def test_generic_protocols_callables_and_attributes_bind_type_variables() -> None:
    """A scalar binds a protocol's parameter by its method (`float.__floor__`), a function its return.

    A generic class's attribute is typed by the receiver's type arguments; with none, one naming a
    type parameter isn't.
    """
    assert _fixes(PROTOCOLS) == {
        "a": "int",
        "b": "int",
        "c": "functools.partial[str]",
        "d": "str",
        "e": "bytes",
        "g": "int",
        "h": "re.Pattern[str]",
        "i": None,
        "j": None,
        "k": None,
        "o": None,
        "q": None,
    }
