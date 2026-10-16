# SPDX-License-Identifier: MIT
"""The corpus runs' witness: a value held to the annotation a fix gave its name (`witness.holds`)."""

import collections
import collections.abc
import importlib
import types
import typing
from collections.abc import Callable
from typing import Final, TypeAlias, TypeVar
from unittest import mock

import pytest

from constricter import trace

_Holds: TypeAlias = Callable[[object, object], bool | None]
_Case: TypeAlias = tuple[object, object, bool | None]  # a value, an annotation, and whether it holds
_T = TypeVar("_T")
_HELD: Final[tuple[_Case, ...]] = (
    ([1, 2], list[int], True),
    ([1, "a", 3], list[int], False),
    ([], list[int], True),
    ([1, None], list[int | None], True),
    ([1.0, 2], list[float], True),
    ([1, "a"], collections.abc.Sequence[int], False),
    ([1, "a"], list, True),
    ({1, "a"}, set[int], False),
    (frozenset({1}), frozenset[int], True),
    (collections.deque([1, "a"]), collections.deque[int], False),
    ({"a": 1, "b": "c"}, dict[str, int], False),
    ({"a": 1, 2: 3}, dict[str, int], False),
    ({"a": [1, "b"]}, dict[str, list[int]], False),
    ({"a": "b"}, collections.abc.Mapping[str, int], False),
    ({"a": 1}, dict[str, typing.Any], True),
    ((1, "a"), tuple[int, str], True),
    ((1, 2), tuple[int, str], False),
    ((1,), tuple[int, str], False),
    ((1, 2, "a"), tuple[int, ...], False),
    ((1, 2), tuple[int, ...], True),
    ((), tuple[()], True),
    ((1,), tuple[()], False),
    ((1, "a"), tuple, True),
    # What can't be told of an element can't be told of its container, unless another differs.
    ([mock.MagicMock()], list[int], None),
    (["a"], types.GenericAlias(list, (_T,)), None),  # `list[_T]`, written where no function binds `_T`
    ([mock.MagicMock(), "a"], list[int], False),
    # A container whose arguments aren't its elements' types is held to its class alone.
    (collections.Counter("ab"), collections.Counter[str], True),
    (collections.Counter("ab"), dict[str, int], True),
)


class _Rows(list[object]):  # ruff: ignore[subclass-builtin]  # a subclass of the builtin is the case
    """A list of a class of its own: reading it may run that class's code."""


@pytest.fixture(name="holds", scope="module")
def _holds() -> _Holds:
    """Import the witness, which makes itself `constricter.trace`'s recorder, and undo that.

    Returns:
      Its `holds`.

    """
    with mock.patch.dict(trace.__dict__):
        return typing.cast(
            "_Holds",
            importlib.import_module("tests.corpus.witness.constricter_witness").holds,
        )


@pytest.mark.parametrize(("value", "hint", "held"), _HELD)
def test_a_builtin_container_is_held_to_its_arguments(
    holds: _Holds,
    value: object,
    hint: object,
    *,
    held: bool | None,
) -> None:
    """Its elements, its keys and values, a tuple's parts; a class alone where that isn't what they are."""
    assert holds(value, hint) is held


class _Framed:  # pylint: disable=too-few-public-methods
    """A base the classes these tests make share, which names their type."""


def _made() -> type[_Framed]:
    class Frame(_Framed):  # pylint: disable=too-few-public-methods
        """A class this function defines anew at each call."""

    return Frame


def test_a_class_a_function_makes_again_is_the_annotations(holds: _Holds) -> None:
    """By its module and qualified name; another class of the same name is still another."""
    first: type[_Framed] = _made()
    assert holds(_made()(), first) is True
    assert holds(type("Frame", (), {"__module__": "pkg.core"})(), first) is False


def test_a_test_modules_class_says_nothing_of_the_annotation(holds: _Holds) -> None:
    """A test's stand-in, passed where the package's class is declared, is neither fit nor differing."""
    module: str
    held: bool | None
    for module, held in (("pkg.tests.test_core", None), ("test_core", None), ("pkg.core", False)):
        stand_in: type[_Framed] = type("FakeProcess", (_Framed,), {"__module__": module})
        assert holds(stand_in(), int) is held


def test_only_a_builtin_containers_elements_are_read(holds: _Holds) -> None:
    """A subclass's own code may run as it's read: it's held to its class, and a long list by its first."""
    assert holds(_Rows([1, "a"]), list[int]) is True
    assert holds([*range(100), "a"], list[int]) is True
    assert holds({*range(200), "a"}, set[int]) is False
