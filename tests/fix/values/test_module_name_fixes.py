# SPDX-License-Identifier: MIT
"""`--fix` types what a function reads of the names its module binds once, at its top level."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, Offence, check_source

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
SOURCE: Final = """
import re
from typing import ClassVar, Final, TypeAlias

LIMIT = 10
NAMES = ["a", "b"]
TYPED: float = 3
PATTERN = re.compile("x")
SIZE: Final = 4
WIDE: Final[float] = 1.5
KEPT: ClassVar[int] = 1
ODD: Final = unknown()
Alias: TypeAlias = int
MODE = "r"
made = Box()
twice = 1
shadow = 1
looped = 1
count = 0
nothing = None
for index in range(3):
    pass
first, second = 1, "x"


def call(mode: str) -> None: ...


call(MODE)


def bump() -> None:
    global count
    count += 1


def other(shadow) -> None:
    for looped in "ab":
        pass


class Holder:
    def read(self) -> None:
        a = LIMIT + 1

    def inner(self) -> None:
        def nested() -> None:
            b = NAMES[0]


def f() -> None:
    c = LIMIT
    d = TYPED
    e = PATTERN.match("x")
    g = SIZE
    h = WIDE
    i = KEPT
    j = ODD
    k = Alias
    m = MODE
    n = made
    o = twice
    p = shadow
    q = count
    r = nothing
    s = index
    t = second
    for u in NAMES:
        pass


twice = 2
"""


def _fixed(source: str, checks: Checks | None = None) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if len(o.name) == 1}


def test_a_function_reads_a_modules_name_as_its_one_value_types_it() -> None:
    """A name the module binds once means one thing in every function: its value's type, or its annotation."""
    assert _fixed(SOURCE) == {
        "a": ("int", False),
        "b": ("str", False),  # in a function defined in a method
        "c": ("int", False),
        "d": ("float", False),  # as annotated
        "e": ("re.Match[str] | None", False),
        "g": ("int", False),  # a bare `Final`: its value's type
        "h": ("float", False),
        "i": ("int", False),
        "j": (None, False),  # `Final`, of no known type
        "k": (None, False),  # an alias isn't a value of its type
        "m": ("str", True),  # a constant passed to a call keeps its literal's type: a guess, as there
        "n": ("Box", True),  # a guess there, a guess here
        "o": (None, False),  # bound twice
        "p": (None, False),  # a parameter of the same name, somewhere
        "q": (None, False),  # a function binds it again (`global`)
        "r": (None, False),
        "s": ("int", False),  # a loop's target
        "t": ("str", False),  # an unpacking's
        "u": ("str", False),
    }


def test_the_modules_own_body_is_fixed_as_before() -> None:
    """With `all_scopes`, the module's names are still reported and fixed where they're bound."""
    source: str = "LIMIT = 10\n\n\ndef f() -> None:\n    a = LIMIT\n"
    found: list[Offence] = check_source(source, checks=Checks(all_scopes=True))
    assert [(o.name, o.code, o.fix) for o in found] == [("LIMIT", "LVA004", "int"), ("a", "LVA001", "int")]


def test_a_name_bound_to_what_a_function_returns_is_read_in_the_same_run() -> None:
    """The module's name is typed once its function's `return`s are: what reads it, in the same run."""
    source: str = """
    def size():
        return 3


    SIZE = size()
    TWICE = double()


    def double():
        return SIZE * 2


    def f() -> None:
        a = SIZE
        b = TWICE
    """
    assert _fixed(source) == {"a": ("int", False), "b": ("int", False)}


def test_a_module_body_reads_a_qualified_name_as_the_type_it_wraps() -> None:
    """A `Final[T]`'s is `T`, and a bare `Final`'s its value's: `Final` is no type to copy or hold."""
    source: str = """
    import typing
    from typing import Final

    A = "a"
    B: Final = "b"
    C: Final[str] = "c"
    D: typing.Final = 4
    E: Final = unknown()
    copied = B
    wrapped = C
    names = {"A": A, "B": B}
    mixed = (B, D)
    odd = E
    """
    found: list[Offence] = check_source(textwrap.dedent(source), checks=Checks(all_scopes=True))
    assert {o.name: o.fix for o in found if o.name.islower()} == {
        "copied": "str",
        "wrapped": "str",
        "names": "dict[str, str]",
        "mixed": "tuple[str, int]",
        "odd": None,
    }
