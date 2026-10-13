# SPDX-License-Identifier: MIT
"""Hold values to annotations three ways, and print where the ways differ: the witness's own, typeguard's, beartype's.

  PYTHONPATH=DIR local/.venv/bin/python -m scratch.witness_checkers

`DIR` holds both packages (`uv pip install --target DIR typeguard beartype`): neither is a
dependency. For each case (a value, an annotation, and what a type checker would say of them) it
prints the witness's `holds` (`True`, `False`, or `None` for can't tell), typeguard's `check_type`
with every item of a collection checked, and beartype's `is_bearable`; an exception is printed by
its class. Then what each costs: its import, and a call on a scalar, a short list and a long one.
"""

import collections.abc
import io
import sys
import time
import timeit
import typing
from unittest import mock

from tests.corpus.witness import constricter_witness as witness


class Shape(typing.Protocol):
    def area(self) -> float: ...


@typing.runtime_checkable
class Sized(typing.Protocol):
    def size(self) -> int: ...


class Square:
    def area(self) -> float:
        return 1.0

    def size(self) -> int:
        return 1


class Row(typing.TypedDict):
    name: str
    count: int


class Box(typing.Generic[typing.TypeVar("T")]):
    pass


class Loud:
    """A container whose every read is seen: a checker that iterates it runs the value's code."""

    read = 0

    def __iter__(self) -> typing.Iterator[int]:
        Loud.read += 1
        return iter([1, 2])

    def __len__(self) -> int:
        Loud.read += 1
        return 2


collections.abc.Collection.register(Loud)
T = typing.TypeVar("T")
B = typing.TypeVar("B", bound=int)
UserId = typing.NewType("UserId", int)


def _generator() -> typing.Iterator[int]:
    yield 1
    yield 2


CASES: list[tuple[str, object, object, object]] = [
    # what it shows, the value, the annotation, what a type checker says
    ("an element in the middle", [1, "a", 3], list[int], False),
    ("a first element", ["a", 1], list[int], False),
    ("a dict's value", {"a": 1, "b": "c"}, dict[str, int], False),
    ("a dict's key", {"a": 1, 2: 3}, dict[str, int], False),
    ("a nested element", {"a": [1, "b"]}, dict[str, list[int]], False),
    ("a tuple, part by part", (1, "a"), tuple[int, str], True),
    ("a tuple's part", (1, 2), tuple[int, str], False),
    ("a tuple of any length", (1, 2, "a"), tuple[int, ...], False),
    ("a set's element", {1, "a"}, set[int], False),
    ("an empty list", [], list[int], True),
    ("a union's element", [1, None], list[int | None], True),
    ("an int for a float", 1, float, True),
    ("a bool for an int", True, int, True),
    ("a literal", "b", typing.Literal["a"], False),
    ("a protocol met", Square(), Shape, True),
    ("a protocol not met", object(), Shape, False),
    ("a checked protocol not met", object(), Sized, False),
    ("a mock for a class", mock.MagicMock(), Square, None),
    ("a mock with a spec", mock.MagicMock(spec=Square), Square, None),
    ("a type variable, unbound", "a", T, None),
    ("a type variable's bound", "a", B, False),
    ("a new type", 1, UserId, True),
    ("a new type, not its base", "a", UserId, False),
    ("a typed dict", {"name": "a", "count": 1}, Row, True),
    ("a typed dict's value", {"name": "a", "count": "b"}, Row, False),
    ("a typed dict's missing key", {"name": "a"}, Row, False),
    ("a callable", len, collections.abc.Callable[[str], int], True),
    ("not a callable", 1, collections.abc.Callable[[str], int], False),
    ("a class for type[C]", Square, type[Square], True),
    ("another class for type[C]", int, type[Square], False),
    ("a generic class's instance", Box(), Box[int], True),
    ("a text file", io.StringIO(), typing.TextIO, True),
    ("a file for IO[str]", io.StringIO(), typing.IO[str], True),
    ("a generator for an iterator", _generator(), collections.abc.Iterator[int], True),
    ("a generator for an iterator of str", _generator(), collections.abc.Iterator[str], None),
    ("a container that sees its reads", Loud(), collections.abc.Collection[int], True),
    ("annotated", 1, typing.Annotated[int, "meta"], True),
    ("None for an optional", None, int | None, True),
]


def _said(check: typing.Callable[[object, object], object], value: object, hint: object) -> str:
    try:
        return str(check(value, hint))
    except Exception as error:  # what a checker raises of a hint it can't hold
        return type(error).__name__


def main() -> int:
    started = time.perf_counter()
    import typeguard

    guard_import = time.perf_counter() - started
    started = time.perf_counter()
    from beartype.door import is_bearable

    bear_import = time.perf_counter() - started

    def guarded(value: object, hint: object) -> bool:
        try:
            typeguard.check_type(
                value,
                hint,
                collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS,
                forward_ref_policy=typeguard.ForwardRefPolicy.ERROR,
            )
        except typeguard.TypeCheckError:
            return False
        return True

    print(f"{'case':<36}{'a checker':<11}{'witness':<9}{'typeguard':<20}beartype")
    for what, value, hint, checker in CASES:
        Loud.read = 0
        row = [_said(witness.holds, value, hint), _said(guarded, value, hint), _said(is_bearable, value, hint)]
        if isinstance(value, Loud):
            row = [f"{said}" for said in row]
        marks = ["" if said == str(checker) else " *" for said in row]
        print(f"{what:<36}{checker!s:<11}{row[0] + marks[0]:<9}{row[1] + marks[1]:<20}{row[2] + marks[2]}")
    print("\n* differs from what a type checker says (None: it can't be told from the value)")
    for name, check in (("witness", witness.holds), ("typeguard", guarded), ("beartype", is_bearable)):
        Loud.read = 0
        _ = _said(check, Loud(), collections.abc.Collection[int])
        print(f"{name}: read the value's own container {Loud.read} times")
    print(f"\nimport: typeguard {guard_import * 1000:.0f} ms, beartype {bear_import * 1000:.0f} ms")
    short, long = list(range(10)), list(range(100_000))
    for name, check in (("witness", witness.holds), ("typeguard", guarded), ("beartype", is_bearable)):
        costs = [
            min(timeit.repeat(lambda: check(1, int | None), number=2000, repeat=3)) / 2000,
            min(timeit.repeat(lambda: check(short, list[int]), number=2000, repeat=3)) / 2000,
            min(timeit.repeat(lambda: check(long, list[int]), number=3, repeat=3)) / 3,
        ]
        print(
            f"{name:<10} int | None: {costs[0] * 1e6:6.1f} us   list[int] of 10: {costs[1] * 1e6:6.1f} us"
            f"   of 100,000: {costs[2] * 1e3:7.2f} ms",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
