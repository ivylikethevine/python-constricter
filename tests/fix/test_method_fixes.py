# SPDX-License-Identifier: MIT
"""`--fix` on a method call: a `list`/`set`/`dict` method, or a method of a class the module defines."""

import textwrap

import pytest

from constricter import Offence, check_source


@pytest.mark.parametrize(
    ("param", "call", "fix"),
    [
        ("nums: list[int]", "nums.pop()", "int"),
        ("nums: list[int]", "nums.pop(0)", "int"),
        ("nums: list[int]", "nums.copy()", "list[int]"),
        ("nums: list[int]", "nums.index(1)", None),  # not in the table
        ("items: set[str]", "items.pop()", "str"),
        ("items: set[str]", "items.copy()", "set[str]"),
        ("pairs: dict[str, int]", "pairs.pop('k')", "int"),
        ("pairs: dict[str, int]", "pairs.pop('k', None)", None),  # the default can be any type
        ("pairs: dict[str, int]", "pairs.pop(key='k')", None),  # a keyword decides nothing
        ("pairs: dict[str, int]", "pairs.setdefault('k', 1)", "int"),
        ("pairs: dict[str, int]", "pairs.get('k')", "int | None"),
        ("pairs: dict[str, int]", "pairs.get('k', 0)", None),
        ("pairs: dict[str, 'Node']", "pairs.get('k')", None),  # `'Node' | None` fails where evaluated
        ("pairs: dict[str, int]", "pairs.popitem()", "tuple[str, int]"),
        ("pairs: dict[str, int]", "pairs.copy()", "dict[str, int]"),
        ("pairs: dict[str, int]", "pairs.keys()", None),  # a view, not in the table
    ],
)
def test_fixes_infer_a_typed_containers_method_call(param: str, call: str, fix: str | None) -> None:
    """A `list`/`set`/`dict` method whose return is the receiver's own element type offers it, as certain."""
    source: str = f"def f({param}) -> None:\n  x = {call}\n"
    offence: Offence
    [offence] = check_source(source)
    assert (offence.name, offence.fix) == ("x", fix)
    assert fix is None or not offence.unsafe


def test_fixes_infer_a_module_class_method_call() -> None:
    """`obj.method()` on a local typed as a module class offers the method's declared return type."""
    source: str = textwrap.dedent(
        """
    class Point:
      def norm(self) -> float:
        return 0.0

      def moved(self) -> "Self":
        return self

      def scaled(self) -> Self:
        return self

      def around(self) -> list[Self]:
        return [self]

      @property
      def size(self) -> int:
        return 0

      def twice(self) -> int:
        return 0

      def twice(self) -> str:
        return ""

    def f(p: Point) -> None:
      a = p.norm()
      b = p.scaled()
      c = p.moved()
      d = p.around()
      e = p.size()
      g = p.twice()
      h = p.missing()
    """,
    )
    assert [(o.name, o.fix, o.unsafe and o.fix is not None) for o in check_source(source)] == [
        ("a", "float", False),
        ("b", "Point", False),
        ("c", None, False),  # a string `Self` isn't unwrapped
        ("d", None, False),  # only a bare `Self` is the class
        ("e", None, False),  # decorated
        ("g", None, False),  # redefined
        ("h", None, False),
    ]


def test_a_generic_classes_methods_are_not_inferred() -> None:
    """A generic class's method returns depend on its parameters, as does a `TypeVar` return."""
    source: str = textwrap.dedent(
        """
    from typing import Generic, TypeVar

    T = TypeVar("T")

    class Box(Generic[T]):
      def get(self) -> int:
        return 0

    class Plain:
      def echo(self, x: T) -> T:
        return x

    def f(b: Box[int], p: Plain) -> None:
      a = b.get()
      c = p.echo(1)
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", None), ("c", None)]


def test_a_method_call_on_a_guessed_class_is_guessed_too() -> None:
    """A module class's method called on an unsafely-fixed local is no more certain than the local."""
    source: str = textwrap.dedent(
        """
    class Box:
      def label(self) -> str:
        return ""

    def f() -> None:
      a = Box()
      b = a.label()
    """,
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("a", "Box", True),
        ("b", "str", True),
    ]
