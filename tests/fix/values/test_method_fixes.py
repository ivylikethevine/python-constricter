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
        ("nums: list[int]", "nums.index(1)", "int"),
        ("nums: list[int]", "nums.sort()", None),  # not in the table
        ("items: set[str]", "items.pop()", "str"),
        ("items: set[str]", "items.copy()", "set[str]"),
        ("pairs: dict[str, int]", "pairs.pop('k')", "int"),
        ("pairs: dict[str, int]", "pairs.pop('k', None)", "int | None"),  # a literal default's type joins
        ("pairs: dict[str, int]", "pairs.pop('k', -1)", "int"),
        ("pairs: dict[str, int]", "pairs.pop('k', fallback)", None),  # a default of any other kind
        ("pairs: dict[str, int]", "pairs.pop(key='k')", None),  # a keyword decides nothing
        ("pairs: dict[str, int]", "pairs.setdefault('k', 1)", "int"),
        ("pairs: dict[str, int]", "pairs.get('k')", "int | None"),
        ("pairs: dict[str, int]", "pairs.get('k', 0)", "int"),  # a default of the values' type
        ("pairs: dict[str, int]", "pairs.get('k', None)", "int | None"),
        (
            "pairs: dict[str, int]",
            "pairs.get('k', 'x')",
            "int | str",
        ),  # another type's, as a checker's overload
        ("pairs: dict[str, float]", "pairs.get('k', 0)", "float"),  # an `int` is a `float`'s
        ("pairs: dict[str, list[int]]", "pairs.get('k', [])", "list[int]"),  # an empty display of its kind
        ("pairs: dict[str, list[int]]", "pairs.get('k', list())", "list[int]"),
        ("pairs: dict[str, Sequence[int]]", "pairs.get('k', ())", "Sequence[int]"),
        ("pairs: dict[str, dict[str, int] | None]", "pairs.get('k', {})", "dict[str, int] | None"),
        ("pairs: dict[str, Optional[set[str]]]", "pairs.pop('k', set())", "Optional[set[str]]"),
        ("pairs: dict[str, Union[str, tuple[str]]]", "pairs.get('k', ())", "Union[str, tuple[str]]"),
        ("pairs: dict[str, list[int]]", "pairs.get('k', {})", None),  # another kind's: its elements unknown
        ("pairs: dict[str, list[int]]", "pairs.get('k', [1])", "list[int]"),  # the display's own type
        ("pairs: dict[str, 'Node']", "pairs.get('k', 0)", "Node | int"),
        ("pairs: dict[str, 'no way']", "pairs.get('k', 0)", None),
        ("pairs: dict[str, int]", "pairs.get('k', ...)", None),
        ("pairs: dict[str, int]", "pairs.get('k', default=0)", None),
        ("pairs: dict[str, 'no way']", "pairs.get('k')", None),  # `'no way' | None` fails where evaluated
        ("pairs: dict[str, 'no way']", "pairs.get('k', None)", None),
        ("pairs: dict[str, 'Node']", "pairs.get('k')", "Node | None"),  # a quoted type is read as its text
        ("pairs: dict[str, int]", "pairs.popitem()", "tuple[str, int]"),
        ("pairs: dict[str, int]", "pairs.copy()", "dict[str, int]"),
        ("pairs: dict[str, int]", "pairs.keys()", None),  # a view, not in the table
    ],
)
def test_fixes_infer_a_typed_containers_method_call(param: str, call: str, fix: str | None) -> None:
    """A `list`/`set`/`dict` method whose return is the receiver's own element type offers it, as certain."""
    source: str = f"from typing import Optional, Sequence, Union\ndef f({param}) -> None:\n  x = {call}\n"
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
        ("c", "Point", False),  # a string `Self` is read as its text
        ("d", None, False),  # only a bare `Self` is the class
        ("e", None, False),  # decorated
        ("g", None, False),  # redefined
        ("h", None, False),
    ]


def test_a_type_variable_return_is_not_inferred() -> None:
    """A generic function's return depends on its arguments; a generic class's plain one doesn't.

    See `test_generic_fixes` for a generic class's members that name its parameters.
    """
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
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", "int"), ("c", None)]
    guarded: str = source.replace('T = TypeVar("T")', 'if TYPE_CHECKING:\n  T = TypeVar("T")')
    assert guarded != source  # a type variable under an `if` is one too
    assert [(o.name, o.fix) for o in check_source(guarded)] == [("a", "int"), ("c", None)]


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


_AGREED_OVERLOADS: str = """
from typing import Self, overload


class Tree:
    @overload
    @classmethod
    def from_dict(cls, d: dict[str, int]) -> Self: ...
    @overload
    @classmethod
    def from_dict(cls, d: list[int]) -> Self: ...
    @classmethod
    def from_dict(cls, d) -> Self:
        return cls()

    @overload
    def size(self, x: int) -> int: ...
    @overload
    def size(self, x: str) -> int: ...
    def size(self, x) -> str:
        return ""

    @overload
    def get(self, x: int) -> int: ...
    @overload
    def get(self, x: str) -> str: ...
    def get(self, x):
        return x


def f(t: Tree, anything) -> None:
    made = Tree.from_dict(anything)
    counted = t.size(anything)
    got = t.get(anything)
"""


def test_a_functions_overloads_declaring_one_return_type_its_calls_whatever_their_arguments() -> None:
    """Every overload of `from_dict` returns `Self`: its call is the class. Not where any return differs."""
    fixes: dict[str, str | None] = {o.name: o.fix for o in check_source(textwrap.dedent(_AGREED_OVERLOADS))}
    assert fixes == {"made": "Tree", "counted": None, "got": None}
