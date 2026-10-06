# SPDX-License-Identifier: MIT
"""`--fix` for values computed from others: conditionals, arithmetic, comprehensions, and more."""

import pytest

from constricter import Offence, check_source

NAME: str = "x_"  # the variable each case binds
LOCAL: str = "LVA001"  # an unannotated local's code


@pytest.mark.parametrize(
    ("value", "fix"),
    [
        ("n if flag else 0", "int"),
        ("n if flag else 's'", None),  # the sides disagree
        ("n + 1", "int"),
        ("n / 2", "float"),
        ("n * ratio", "float"),
        ("flag + flag", "int"),
        ("n ** 2", "int"),
        ("n ** -1", None),  # a float
        ("n ** n", None),  # by a negative `n`, a float
        ("flag ** 2", "int"),
        ("ratio ** 2", "float"),
        ("ratio ** n", "float"),
        ("ratio ** ratio", None),  # a negative number's is a complex
        ("n ** ratio", None),
        ("2 ** 32 - 1", "int"),
        ("n << 1", "int"),
        ("n >> flag", "int"),
        ("n | 1", "int"),
        ("n & flag", "int"),
        ("flag ^ flag", "bool"),
        ("ratio | 1", None),
        ("ratio << 1", None),
        ("n @ n", None),
        ("'x' * n", "str"),
        ("'%s' % n", "str"),
        ("'a' + 'b'", "str"),
        ("b'a' + b'b'", "bytes"),
        ("'a' + n", None),  # a `TypeError`, not a `str`
        ("'a' - 'b'", None),
        ("n * 'x'", "str"),
        ("flag * b'x'", "bytes"),
        ("n * lines", "list[str]"),
        ("n * ages", None),
        ("ratio * 'x'", None),
        ("n * unknown()", None),
        ("pair + pair", "tuple[int, str, int, str]"),
        ("pair + pair + pair", None),  # too long to list, and of two types
        ("pair + (n,)", "tuple[int, str, int]"),
        ("row + row", "tuple[int, ...]"),
        ("row + (n,)", "tuple[int, ...]"),
        ("(n,) + row", "tuple[int, ...]"),
        ("row + ('x',)", None),
        ("(n, n, n) + (n, n)", "tuple[int, ...]"),
        ("pair + lines", None),
        ("pair + unknown()", None),
        ("pair - pair", None),
        ("row * 2", "tuple[int, ...]"),
        ("2 * row", "tuple[int, ...]"),
        ("(n, n) * n", "tuple[int, ...]"),
        ("(n,) * 3", "tuple[int, ...]"),
        ("pair * 2", None),  # of two types
        ("row * ratio", None),
        ("() + row", None),
        ("names | names", "set[str]"),
        ("names & names", "set[str]"),
        ("names - {'x'}", "set[str]"),
        ("names ^ names", "set[str]"),
        ("frozen - frozen", "frozenset[str]"),
        ("names | frozen", None),  # which of the two types it gives is the left one's to say
        ("names + names", None),
        ("names | unknown()", None),
        ("ages | {'x': 1}", "dict[str, int]"),
        ("ages | {1: 'x'}", None),
        ("ages & ages", None),
        ("names & ages.keys()", "set[str]"),  # a `dict`'s keys' operators give a `set` of them
        ("ages.keys() - names", "set[str]"),
        ("ages.keys() | ages.keys()", "set[str]"),
        ("ages.keys() - {1}", None),
        ("ages.keys(1) - names", None),
        ("unknown().keys() - names", None),
        ("ages.values() - names", None),
        ("unknown() + 1", None),
        ("[line.strip() for line in lines]", "list[str]"),
        ("{x for x in range(3)}", "set[int]"),
        ("{k: v + 1 for k, v in ages.items()}", "dict[str, int]"),
        ("[x for x in unknown()]", None),
        ("[n for n in unknown()]", None),  # the target shadows the parameter `n`
        ("{k: other for k in lines}", None),  # `other` isn't known
        ("(x for x in lines)", None),  # a generator is left alone
        ("sorted(lines)", "list[str]"),
        ("sorted(lines, key=len, reverse=True)", "list[str]"),
        ("sorted(lines, cmp=len)", None),
        ("list(lines, key=len)", None),
        ("list(ages)", "list[str]"),
        ("set(range(3))", "set[int]"),
        ("frozenset(lines)", "frozenset[str]"),
        ("tuple(lines)", "tuple[str, ...]"),
        ("list(unknown())", None),
        ("await fetch()", "bytes"),
        ("await other()", None),
    ],
)
def test_a_computed_value_is_typed(value: str, fix: str | None) -> None:
    """Each of these is certain when it's typed at all: nothing in it is a guess."""
    source: str = (
        "async def fetch() -> bytes: ...\n\n\n"
        "async def f(\n"
        "    n: int, ratio: float, flag: bool, lines: list[str], ages: dict[str, int],\n"
        "    pair: tuple[int, str], row: tuple[int, ...], names: set[str], frozen: frozenset[str],\n"
        ") -> None:\n"
        f"    {NAME} = {value}\n"
    )
    offences: list[Offence] = [o for o in check_source(source) if o.name == NAME]
    assert [(o.fix, o.unsafe) for o in offences] == [(fix, False)]


def test_an_operator_is_typed_by_its_left_operands_library_method() -> None:
    """A standard-library class's operator gives what its method declares for the right operand.

    The first signature whose operand takes it: the same class, one under it, or a number promoted
    to it. Not where a signature before that can't be read, the right operand's class is under the
    left's (its reflected method may answer), or it's no builtin's or library class's instance.
    """
    source: str = (
        "import datetime\n"
        "from collections import Counter, UserString\n"
        "from datetime import date, timedelta\n"
        "from decimal import Decimal\n"
        "from fractions import Fraction\n"
        "class Mine(datetime.datetime): ...\n"
        "def f(when: datetime.datetime, day: date, span: timedelta, d: Decimal, fr: Fraction,\n"
        "      n: int, x: float, flag: bool, c: Counter[str], mine: Mine, us: UserString, other):\n"
        "    a = when - when\n"
        "    b = when - span\n"
        "    c_ = when + span\n"
        "    e = day - day\n"
        "    g = day - when\n"
        "    h = span / span\n"
        "    i = span / n\n"
        "    j = span * flag\n"
        "    k = d + n\n"
        "    m = d * d\n"
        "    o = fr + fr\n"
        "    p = fr + x\n"
        "    q = fr + flag\n"
        "    r = when + n\n"
        "    s = when - other\n"
        "    t = when - mine\n"
        "    u = c + c\n"
        "    v = when @ span\n"
        "    w = d + x\n"
        "    y = (when - when).total_seconds()\n"
        "    z = when - (when if flag else None)\n"
        "    us2 = us + us\n"
    )
    fixed: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(source) if o.code == LOCAL
    }
    assert fixed == {
        "a": ("timedelta", False),
        "b": ("datetime.datetime", False),
        "c_": ("datetime.datetime", False),
        "e": ("timedelta", False),
        "g": (None, False),  # a `datetime` is a `date`: its reflected method may answer first
        "h": ("float", False),
        "i": ("timedelta", False),  # an `int`, where a `float` is taken
        "j": ("timedelta", False),
        "k": ("Decimal", False),
        "m": ("Decimal", False),
        "o": ("Fraction", False),
        "p": ("float", False),
        "q": ("Fraction", False),  # a `bool`, where an `int` is taken
        "r": (None, False),
        "s": (None, False),
        "t": (None, False),  # a class of the module's: its own `__rsub__` may answer
        "u": (None, False),  # a generic class's operand
        "v": (None, False),
        "w": (None, False),
        "y": ("float", False),
        "z": (None, False),
        "us2": (None, False),  # an operand typed `object`
    }


def test_a_path_joined_by_a_slash_is_a_path() -> None:
    """A `pathlib` class's `/` with a `str` or another path gives its class back; nothing else does."""
    source: str = (
        "from pathlib import Path, PurePath\n"
        "def f(root: Path, pure: PurePath, name: str, n: int):\n"
        "    a = root / 'x'\n"
        "    b = root / name / 'y'\n"
        "    c = root / root\n"
        "    d = pure / name\n"
        "    e = root / n\n"
        "    g = name / root\n"  # the path isn't on the left: not followed
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [
        ("a", "Path"),
        ("b", "Path"),
        ("c", "Path"),
        ("d", "PurePath"),
        ("e", None),
        ("g", None),
    ]


def test_a_comprehension_over_a_guess_is_a_guess() -> None:
    """A comprehension over a value only guessed is no more certain than it."""
    source: str = (
        "class Box:\n    parts: list[int]\n\n\n"
        "def f() -> None:\n    box = Box()\n    x_ = [b for b in box.parts]\n"
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("box", "Box", True),
        ("x_", "list[int]", True),
    ]
