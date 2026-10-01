# SPDX-License-Identifier: MIT
"""`--fix` for calls to unannotated generator functions: their `yield`s decide their type."""

import textwrap
from typing import Final, TypeAlias

from constricter import Offence, check_source
from constricter.fix import fixes

_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_SOURCE: Final = """
import collections.abc
import typing as t
from collections.abc import Iterable


def numbers(count: int):
    for index in range(count):
        yield index


def words():
    yield "a"
    yield from ["b", "c"]
    return


def mixed():
    yield 1
    yield "a"


def sent():
    got = yield 1


def ended():
    yield 1
    return "done"


def bare():
    yield


def later():
    value = 1
    value = 2
    yield value


def unknown(items):
    yield from items


def boxes():
    yield Tree()


async def awaited():
    yield 1


class Tree:
    def walk(self):
        yield self.size()

    def size(self) -> int:
        return 1

    def f(self) -> None:
        for size in self.walk():
            pass


def use(
    items: Iterable[str],
    it: t.Iterator[bytes],
    made: collections.abc.Generator[float, None, None],
) -> None:
    a = numbers(3)
    b = words()
    c = mixed()
    d = sent()
    e = ended()
    g = bare()
    h = later()
    i = unknown([])
    j = boxes()
    k = awaited()
    for n in numbers(3):
        pass
    for w in words():
        pass
    for item in items:
        pass
    for chunk in it:
        pass
    for number in made:
        pass
"""


def _fixes(source: str) -> _Fixes:
    """Check `source`.

    Returns:
      Each untyped name's fix, and whether it's a guess.

    """
    return {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(source))}


def test_a_generator_is_typed_by_its_yields() -> None:
    """Every `yield` a statement giving one type, and no value returned: a `Generator` of it."""
    assert _fixes(_SOURCE) == {
        "index": ("int", False),
        "got": (None, False),
        "value": ("int", False),
        "size": ("int", True),  # a method: a subclass may override it
        "a": ("Generator[int, None, None]", False),
        "b": ("Generator[str, None, None]", False),
        "c": (None, False),  # two types
        "d": (None, False),  # what's sent in is used
        "e": (None, False),  # it returns a value
        "g": (None, False),  # a bare `yield`
        "h": (None, False),  # a local bound twice: which reaches the `yield` isn't known
        "i": (None, False),  # elements of an unknown type
        "j": ("Generator[Tree, None, None]", True),  # a guessed value: a guess
        "k": (None, False),  # `async`
        "n": ("int", False),
        "w": ("str", False),
        "item": ("str", False),
        "chunk": ("bytes", False),
        "number": ("float", False),
    }


def test_the_generator_class_is_imported_for_the_fix() -> None:
    """As any library class a fix names: by an import the module has, or one added."""
    source: str = "def gen():\n    yield 1\n\n\ndef f() -> None:\n    made = gen()\n"
    offences: list[Offence] = check_source(source)
    fixed: str = "".join(fixes.apply(source.splitlines(keepends=True), offences))
    expected: str = (
        "from collections.abc import Generator\n"
        "def gen():\n    yield 1\n\n\n"
        "def f() -> None:\n    made: Generator[int, None, None] = gen()\n"
    )
    assert fixed == expected


def test_a_module_that_cant_name_the_class_gets_no_fix() -> None:
    """Its own `Generator` is in the way of the import."""
    source: str = "Generator = 1\n\n\ndef gen():\n    yield 1\n\n\ndef f() -> None:\n    made = gen()\n"
    assert _fixes(source) == {"made": (None, False)}
