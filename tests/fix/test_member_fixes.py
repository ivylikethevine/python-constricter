# SPDX-License-Identifier: MIT
"""`--fix` for members of any value whose type is known: `self.a.b`, `f().x`, `xs[0].m()`, ..."""

import textwrap

import pytest

from constricter import Checks, Offence, check_source
from constricter.offences import FixPolicy

_CLASSES: str = """
class Index:
  name: str
  items: list[str]
  counts: dict[str, int]

  def label(self) -> str: ...
  def size(self, extra: int) -> int: ...
  def guessed(self):
    return 1


class Table:
  index: Index

  def make(self) -> Index: ...
"""


def _fixes(body: str) -> list[tuple[str, str | None, bool]]:
    source: str = _CLASSES + textwrap.dedent(body)
    return [(o.name, o.fix, o.unsafe) for o in check_source(source)]


@pytest.mark.parametrize(
    ("value", "fix"),
    [
        ("t.index.name", "str"),  # an attribute of an attribute
        ("t.index.label()", "str"),  # a method on an attribute
        ("t.make().name", "str"),  # an attribute of a method's return
        ("t.make().label().upper()", "str"),  # a fixed-return method on a declared one's
        ("t.index.items[0]", "str"),  # a subscript of an attribute
        ("t.index.items[1:]", "list[str]"),
        ("t.index.items[0].split()", "list[str]"),  # a method on a subscript
        ("t.index.counts.get('a')", "int | None"),  # an element method on an attribute
        ("tables[0].index", "Index"),  # an attribute of a subscript
        ("make_table().index.name", "str"),  # through a function declaring its return
        ("t.index.missing", None),
        ("t.index.name.missing()", None),
        ("t.missing.name", None),
    ],
)
def test_a_member_of_any_typed_value_is_typed(value: str, fix: str | None) -> None:
    """The receiver is typed as any value is, and the member looked up on its type."""
    body: str = f"""
    def make_table() -> Table: ...
    def f(t: Table, tables: list[Table]) -> None:
      x = {value}
    """
    assert _fixes(body)[-1] == ("x", fix, False)


def test_a_member_of_a_guessed_receiver_is_a_guess() -> None:
    """`Table().index.name` is a `str` only if `Table()` is a `Table`, a guess."""
    body: str = """
    def f() -> None:
      a = Table().index.name
      b = Table().make().label()
    """
    assert _fixes(body) == [("a", "str", True), ("b", "str", True)]


def test_a_chained_members_kinds_include_its_receivers() -> None:
    """What typed a receiver that isn't a plain local decided its member too (`fix-ignore`)."""
    source: str = _CLASSES + "def f() -> None:\n  a = Table().index\n"
    found: list[Offence] = check_source(
        source,
        checks=Checks(fixes=FixPolicy(ignore=frozenset({"constructor"}))),
    )
    assert [(o.name, o.fix) for o in found] == [("a", None)]
    found = check_source(source)
    assert [(o.name, o.edit.kinds if o.edit else None) for o in found] == [
        ("a", frozenset({"attribute", "constructor"})),
    ]


def test_a_method_typed_by_its_returns_on_a_chained_receiver_is_a_guess() -> None:
    """`t.index.guessed()` has only its `return`s to go by: a guess, resting on them and `t.index`."""
    source: str = _CLASSES + "def f(t: Table) -> None:\n  a = t.index.guessed()\n"
    found: list[Offence] = check_source(source)
    assert [(o.name, o.fix, o.unsafe) for o in found] == [("a", "int", True)]
    assert [o.edit.kinds for o in found if o.edit] == [frozenset({"returned", "attribute"})]


@pytest.mark.parametrize(
    ("value", "fix"),
    [
        ("len(Table())", "int"),
        ("'{}'.format(Table())", "str"),
        ("t.index.size(Table())", "int"),
        ("t.index.counts.get(Table())", "int | None"),
        ("make(Table())", "str"),
    ],
)
def test_a_fixed_return_calls_arguments_dont_make_it_a_guess(value: str, fix: str) -> None:
    """A call whose type is its callee's alone is certain, whatever its arguments are."""
    body: str = f"""
    def make(t: object) -> str: ...
    def f(t: Table) -> None:
      x = {value}
    """
    assert _fixes(body)[-1] == ("x", fix, False)


def test_a_rebound_builtins_arguments_still_decide() -> None:
    """A `len` the module binds itself isn't the builtin: nothing's typed through it."""
    body: str = """
    def f(len) -> None:
      x = len(Table())
    """
    assert _fixes(body)[-1] == ("x", None, False)


def test_an_index_typed_slice_slices() -> None:
    """`items[since]`, `since` a `slice`, is a `list`, not an element."""
    body: str = """
    def f(t: Table, since: slice, at: int) -> None:
      a = t.index.items[since]
      b = t.index.items[at]
    """
    assert _fixes(body) == [("a", "list[str]", False), ("b", "str", False)]


def test_a_dict_view_on_a_chained_receiver_is_certain() -> None:
    """`t.index.counts.items()` iterates `tuple[str, int]`, for a loop and a builder alike."""
    body: str = """
    def f(t: Table) -> None:
      pairs = list(t.index.counts.items())
      for key, count in t.index.counts.items():
        pass
    """
    assert _fixes(body) == [
        ("pairs", "list[tuple[str, int]]", False),
        ("key", "str", False),
        ("count", "int", False),
    ]
