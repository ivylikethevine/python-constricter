# SPDX-License-Identifier: MIT
"""What makes a type, not a value, is bound without an annotation: it isn't reported, nor counted."""

import textwrap
from typing import Final

from constricter import Checks, annotation_coverage, check_source

_SOURCE: Final = """
import collections
import enum
import typing as t
from collections import namedtuple
from typing import NewType, ParamSpec, TypeVar
from typing_extensions import TypedDict

from other import TypeVar as Unrelated

T = TypeVar("T")
P = ParamSpec("P")
U = t.TypeVar("U")
UserId = NewType("UserId", int)
Pair = namedtuple("Pair", "a b")
Other = collections.namedtuple("Other", "a")
Color = enum.Enum("Color", "RED GREEN")
Movie = TypedDict("Movie", {"name": str})
Row = t.NamedTuple("Row", [("a", int)])
V = Unrelated("V")
made = make("y")


def f() -> None:
    W = TypeVar("W")
"""


def test_what_a_type_factory_makes_is_neither_reported_nor_counted() -> None:
    """A `TypeVar`, a `NewType` or a functional class, however `typing`, `enum` or `collections` is imported.

    An annotation would make a type checker take the name for a variable. Another module's
    `TypeVar` is any call.
    """
    source: str = textwrap.dedent(_SOURCE)
    assert [o.name for o in check_source(source, checks=Checks(all_scopes=True))] == ["V", "made"]
    assert annotation_coverage(source, Checks(all_scopes=True)) == (0, 2)
