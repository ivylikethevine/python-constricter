# SPDX-License-Identifier: MIT
"""`--fix` reads a quoted annotation as its text, and quotes a module body's fix naming what's unbound."""

import ast
import textwrap
from typing import Final

import pytest

from constricter import Checks, Offence, check_source
from constricter.rules.quoted import written

SOURCE: Final = """
from typing import TYPE_CHECKING, Annotated, Literal

if TYPE_CHECKING:
    from shapes import Shape

    import late.bound

xs: "list[Node]" = []
first = xs[0]
for each in xs:
    pass
shape: "Shape" = make()
copy = shape


class Node:
    name: str
    kids: list["Node"]
    mode: Literal["r", "w"]
    tag: Annotated["Node", "meta"]
    odd: "no way"


later = xs[0]


def get() -> "Node":
    return Node()


def f(ys: "list[Node]", node: "Node", shape: "Shape") -> None:
    a = ys[0]
    for b in ys:
        pass
    c = node.kids
    d = node.kids[0].name
    e = shape
    g = get()
    h = node.mode
    i = node.tag
    j = node.odd
"""


def test_a_quoted_annotation_types_what_an_unquoted_one_does() -> None:
    """A whole annotation in quotes, or a part of one, is read as what it quotes; not a `Literal`'s values."""
    found: list[Offence] = check_source(textwrap.dedent(SOURCE), checks=Checks(all_scopes=True))
    assert {o.name: o.fix for o in found if o.fix is not None} == {
        "first": '"Node"',  # in a module body, before `Node` is bound: quoted again
        "each": '"Node"',  # a declaration's line is the loop's
        "copy": '"Shape"',  # imported for type checking alone
        "later": "Node",
        "a": "Node",
        "b": "Node",
        "c": "list[Node]",
        "d": "str",
        "e": "Shape",
        "g": "Node",
        "h": "Literal['r', 'w']",
        "i": "Annotated[Node, 'meta']",
        "j": "'no way'",
    }


def test_postponed_annotations_need_no_quotes() -> None:
    """With `from __future__ import annotations`, a module body's annotation isn't evaluated."""
    source: str = (
        'from __future__ import annotations\nxs: "list[Node]" = []\nfirst = xs[0]\nclass Node: ...\n'
    )
    found: list[Offence] = check_source(source, checks=Checks(all_scopes=True))
    assert [(o.name, o.fix) for o in found] == [("first", "Node")]


@pytest.mark.parametrize(
    ("annotation", "text"),
    [
        ("list[int]", "list[int]"),
        ('"list[Node]"', "list[Node]"),
        ('list["Node"]', "list[Node]"),
        ("\"dict[str, 'Node']\"", "dict[str, Node]"),
        ('"Node" | None', "Node | None"),
        ('Optional["A | B"]', "Optional[A | B]"),
        ('tuple["A", "B"]', "tuple[A, B]"),
        ('Callable[["A"], "B"]', "Callable[[A], B]"),
        ('Literal["a", "b"]', "Literal['a', 'b']"),
        ('Annotated["A", "meta"]', "Annotated[A, 'meta']"),
        ('list["no way"]', "list['no way']"),
        ('x + "y"', "x + 'y'"),
    ],
)
def test_written_unquotes_types_alone(annotation: str, text: str) -> None:
    """A quoted type is what it quotes; a `Literal`'s string, `Annotated`'s metadata and a non-type aren't."""
    assert written(ast.parse(annotation, mode="eval").body) == text


def test_a_fix_naming_a_value_of_its_scope_is_dropped() -> None:
    """A parameter or local the annotation would name is the variable there, not the type."""
    source: str = """
    class Row: ...


    def load() -> type[Row]:
        return Row


    def one() -> "Thing":
        return Thing()


    def f(str, n: int) -> None:
        a = "text"
        b = n
        Row = load()
        c = load()


    Thing = one()
    """
    found: list[Offence] = check_source(textwrap.dedent(source), checks=Checks(all_scopes=True))
    assert [(o.name, o.fix) for o in found] == [
        ("a", None),  # `str` is the parameter
        ("b", "int"),
        ("Row", None),  # `type[Row]` would name the local itself
        ("c", None),  # and so would this, bound before it or after
        ("Thing", None),
    ]
