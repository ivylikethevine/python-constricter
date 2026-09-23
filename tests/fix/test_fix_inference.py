# SPDX-License-Identifier: MIT
"""`--fix`: which values decide an annotation, and which are only guesses (`--unsafe-fixes`)."""

import textwrap
from typing import Final

import pytest

from constricter import (
    Checks,
    Offence,
    check_source,
)

ANY_LENGTH: Final = "tuple[int, ...]"


@pytest.mark.parametrize(
    ("value", "fix"),
    [
        ("0", "int"),
        ("-1.5", "float"),
        ("+2", "int"),
        ("True", "bool"),
        ("-True", None),
        ("not y", "bool"),
        ("1j", "complex"),
        ("'text'", "str"),
        ("b'raw'", "bytes"),
        ("f'{0}'", "str"),
        ("Path('x')", "Path"),
        ("ast.Name('x')", "ast.Name"),
        ("len([1])", "int"),
        ("isinstance(1, int)", "bool"),
        ("any([1])", "bool"),
        ("hex(1)", "str"),
        ("dir()", "list[str]"),
        ("range(3)", "range"),
        ("bytearray(2)", "bytearray"),
        ("', '.join([])", "str"),
        ("b''.join([])", "bytes"),
        ("f'{0}'.upper()", "str"),
        ("'a=b'.partition('=')", "tuple[str, str, str]"),
        ("b'a'.rpartition(b'=')", "tuple[bytes, bytes, bytes]"),
        ("(1).bit_length()", None),
        ("TypeVar('T')", None),
        ("Counter()", None),
        ("path()", None),
        ("None", None),
        ("[1]", "list[int]"),
        ("[]", None),
        ("[1, 'a']", None),
        ("[[1], [2]]", "list[list[int]]"),
        ("{1, 2}", "set[int]"),
        ("(1, 'a', b'')", "tuple[int, str, bytes]"),
        ("(1, *[])", None),
        ("{'a': 1}", "dict[str, int]"),
        ("{'a': 1, 'b': 'c'}", None),
        ("{**{}}", None),
        ("{}", None),
    ],
)
def test_fixes_are_offered_only_where_the_value_decides_the_type(value: str, fix: str | None) -> None:
    """A literal or a capitalised constructor call offers its annotation; anything else doesn't."""
    offences: list[Offence] = check_source(f"def f() -> None:\n  x = {value}\n")
    assert [(o.name, o.fix) for o in offences] == [("x", fix)]


def test_fixes_are_offered_only_for_a_single_plain_name() -> None:
    """Chained `=`, `:=` and class bodies are never fixed; module bodies are, and so is unpacking."""
    source: str = textwrap.dedent(
        """
    LIMIT = 3


    def f() -> None:
      a, b = 1, 2
      c = d = 3
      if (e := 4):
        pass


    class C:
      size = 1
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source, checks=Checks(all_scopes=True))] == [
        ("LIMIT", "int"),
        ("a", "int"),  # declared before the statement: see tests/fix/test_declarations.py
        ("b", "int"),
        ("c", None),
        ("d", None),
        ("e", None),
        ("size", None),
    ]


def test_fixes_use_same_module_return_types() -> None:
    """A call to a plain module function offers its declared return type; unsafe ones don't."""
    source: str = textwrap.dedent(
        """
    from typing import Any, TypeVar
    T = TypeVar("T")


    def count() -> int: ...
    def rows() -> list[tuple[int, str]]: ...
    def nothing() -> None: ...
    def vague() -> Any: ...
    def same(value: T) -> T: ...
    def untyped(): ...
    async def later() -> int: ...
    @cache
    def cached() -> int: ...
    def twice() -> int: ...
    def twice() -> str: ...


    def f() -> None:
      a = count()
      b = [rows(), rows()]
      c = nothing()
      d = vague()
      e = same(1)
      g = untyped()
      h = later()
      i = cached()
      j = twice()
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [
        ("a", "int"),
        ("b", "list[list[tuple[int, str]]]"),
        ("c", None),
        ("d", None),
        ("e", None),
        ("g", None),
        ("h", None),
        ("i", None),
        ("j", None),
    ]


def test_fixes_copy_an_already_typed_locals_type() -> None:
    """A plain `x = y` offers `y`'s type: its annotation, an earlier fix, or its parameter's."""
    source: str = textwrap.dedent(
        """
    def f(n: int) -> None:
      a: int = 1
      b = a
      c = 2
      d = c
      e = n
      g = h
    """,
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("b", "int", False),
        ("c", "int", False),
        ("d", "int", False),
        ("e", "int", False),
        ("g", None, False),
    ]


def test_a_copy_of_a_guessed_fix_is_guessed_too() -> None:
    """A copy of an unsafely-fixed local is offered too, but it's no more certain than its source."""
    source: str = "def f() -> None:\n  a = Box(1)\n  b = a\n"
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("a", "Box", True),
        ("b", "Box", True),
    ]


@pytest.mark.parametrize(
    ("param", "subscript", "fix"),
    [
        ("nums: list[int]", "nums[0]", "int"),
        ("nums: list[int]", "nums[1:2]", "list[int]"),
        ("pairs: dict[str, int]", "pairs['x']", "int"),
        ("row: tuple[int, ...]", "row[0]", "int"),
        ("row: tuple[int, str]", "row[0]", None),  # which element varies with the index
        ("text: str", "text[0]", "str"),
        ("text: str", "text[1:3]", "str"),
        ("data: bytes", "data[0:1]", "bytes"),
        ("items: set[int]", "items[0]", None),  # a `set` isn't subscriptable
        ("nums: list[int]", "nums[i]", "int"),  # a non-literal index still gets the element type
    ],
)
def test_fixes_infer_a_typed_locals_subscript(param: str, subscript: str, fix: str | None) -> None:
    """A subscript of an already-typed local offers its element type, a slice its own type."""
    source: str = f"def f({param}, i: int) -> None:\n  x = {subscript}\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("x", fix)]


def test_a_subscript_of_a_guessed_fix_is_not_offered() -> None:
    """A subscript of an unsafely-fixed local (`Box` isn't a known container) offers nothing."""
    source: str = "def f() -> None:\n  a = Box([1])\n  b = a[0]\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", "Box"), ("b", None)]


def test_fixes_infer_a_typed_locals_attribute() -> None:
    """A class-level annotated attribute of a locally-constructed instance offers its type."""
    source: str = textwrap.dedent(
        """
    class Point:
      x: int
      y: int
      label = "origin"  # not class-level annotated: not offered

    def f() -> None:
      p = Point()
      a = p.x
      b = p.y
      c = p.z
      d = p.label
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [
        ("p", "Point"),
        ("a", "int"),
        ("b", "int"),
        ("c", None),
        ("d", None),
    ]


def test_an_attribute_of_a_guessed_fix_is_guessed_too() -> None:
    """A class attribute of an unsafely-fixed local is no more certain than its source."""
    source: str = textwrap.dedent(
        """
    class Point:
      x: int

    def f() -> None:
      p = Point()
      a = p.x
    """,
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("p", "Point", True),
        ("a", "int", True),
    ]


def test_fixes_infer_a_methods_self_attribute() -> None:
    """`self.attr` in a method offers its type: class-level, or `self.attr: T = ...` in any method."""
    source: str = textwrap.dedent(
        """
    class Counter:
      total: int

      def __init__(self) -> None:
        self.name: str = "x"

      def read(self) -> None:
        a = self.total
        b = self.name
        c = self.missing
    """,
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source, checks=Checks(all_scopes=True))] == [
        ("a", "int", False),
        ("b", "str", False),
        ("c", None, False),
    ]


def test_a_nested_functions_self_is_not_typed() -> None:
    """A function nested in a method isn't itself a method: its closed-over `self` isn't typed."""
    source: str = textwrap.dedent(
        """
    class C:
      x: int

      def method(self) -> None:
        def helper() -> None:
          a = self.x
        helper()
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", None)]


def test_a_classmethods_cls_is_not_typed_as_self() -> None:
    """Only a `self`-named first parameter is typed as the class; `cls` (classmethods) isn't."""
    source: str = textwrap.dedent(
        """
    class C:
      x: int

      @classmethod
      def make(cls) -> "C":
        return cls()

      @classmethod
      def read(cls) -> None:
        a = cls.x
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", None)]


@pytest.mark.parametrize(
    ("param", "call", "fix"),
    [
        ("s: str", "s.strip()", "str"),
        ("s: str", "s.split(',')", "list[str]"),
        ("s: str", "s.startswith('x')", "bool"),
        ("s: str", "s.count('x')", "int"),
        ("s: str", "s.encode()", "bytes"),
        ("b: bytes", "b.decode()", "str"),
        ("b: bytes", "b.hex()", "str"),
        ("b: bytes", "b.strip()", "bytes"),
        ("s: str", "s.unknown_method()", None),
        ("n: int", "n.bit_length()", None),  # `int` isn't in `_METHOD_RETURNS`
    ],
)
def test_fixes_infer_a_typed_locals_method_call(param: str, call: str, fix: str | None) -> None:
    """A `str`/`bytes` method with a fixed return type, called on an already-typed local, offers it."""
    source: str = f"def f({param}) -> None:\n  x = {call}\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("x", fix)]


def test_a_method_call_on_a_guessed_fix_is_not_offered() -> None:
    """A method call on an unsafely-fixed local (`Box` isn't `str`/`bytes`) offers nothing."""
    source: str = "def f() -> None:\n  a = Box('x')\n  b = a.strip()\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", "Box"), ("b", None)]


def test_a_long_tuple_display_is_typed_by_its_element() -> None:
    """Past `max-length`, a tuple is `tuple[T, ...]` if its elements agree, else untyped (LVA011's).

    Found on pip's vendored chardet, whose frequency tables are tuples of thousands of `int`s.
    """
    source: str = (
        "def f() -> None:\n    a = (1, 2, 3, 4)\n    b = (1, 2, 3, 4, 5)\n    c = (1, 'x', 3, 4, 5)\n"
    )
    assert {o.name: o.fix for o in check_source(source)} == {
        "a": "tuple[int, int, int, int]",
        "b": ANY_LENGTH,
        "c": None,
    }
    shorter: dict[str, str | None] = {
        o.name: o.fix for o in check_source(source, checks=Checks(max_length=2))
    }
    assert shorter["a"] == ANY_LENGTH


def test_a_builtin_the_module_rebinds_is_not_typed_as_the_builtin() -> None:
    """A parameter, local or definition named like a builtin means that, not the builtin, anywhere."""
    source: str = textwrap.dedent(
        """\
        def f(format, sorted):
            a = format(1)
            b = sorted([1])
            for c in sorted([1]):
                pass
            d = len([])
        def g():
            e = format(2)
        """,
    )
    offences: list[Offence] = check_source(source)
    assert [(o.name, o.fix) for o in offences] == [
        ("a", None),
        ("b", None),
        ("c", None),
        ("d", "int"),
        ("e", None),
    ]


def test_a_fixed_return_method_on_a_literal_is_certain() -> None:
    """`", ".join(xs)` is a `str` whatever `xs` is, and `"{}".format(Box())` whatever `Box()` is."""
    source: str = "def f(xs: list[str]) -> None:\n  a = ', '.join(xs)\n  b = '{}'.format(Box())\n"
    offences: list[Offence] = check_source(source)
    assert [(o.name, o.fix, o.unsafe) for o in offences] == [("a", "str", False), ("b", "str", False)]
