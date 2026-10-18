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
        ("n ** -1", "float"),
        ("n ** n", "float"),  # an `int` or, by a negative `n`, a `float`: a `float` takes both
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
        ("maybe + pair", None),  # a union with a tuple isn't one
        ("some + some", None),
        ("some * 2", None),
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
        "    maybe: tuple[int, str] | None, some: list[int] | None,\n"
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
        "t": ("timedelta", False),  # a class of the module's binding neither method: `datetime`'s
        "u": ("Counter[str]", False),  # a generic class's, by its type arguments
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


def test_a_builtin_number_left_of_a_library_class_takes_its_reflected_method() -> None:
    """`2 * span` is a `timedelta`: an `int`'s `__mul__` takes numbers alone, so `__rmul__` answers.

    Not where the right one's reflected method takes no such number (`3 - span`), and not a class
    under the number's own (an `IntFlag`), whose reflected method Python asks first.
    """
    source: str = (
        "import enum\n"
        "from datetime import timedelta\n"
        "from decimal import Decimal\n"
        "from fractions import Fraction\n"
        "class Bits(enum.IntFlag):\n"
        "    A = 1\n"
        "def f(span: timedelta, d: Decimal, fr: Fraction, n: int, x: float, bits: Bits) -> None:\n"
        "    a = 2 * span\n"
        "    b = n * d\n"
        "    c = 1 + fr\n"
        "    e = x * fr\n"
        "    g = 3 - span\n"
        "    h = n + span\n"
        "    i = 2 | bits\n"
    )
    fixed: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(source) if o.code == LOCAL
    }
    assert fixed == {
        "a": ("timedelta", False),
        "b": ("Decimal", False),
        "c": ("Fraction", False),
        "e": ("float", False),
        "g": (None, False),
        "h": (None, False),
        "i": (None, False),
    }


def test_a_generic_library_class_method_is_typed_by_its_arguments() -> None:
    """`OrderedDict.fromkeys(names, 0)` binds its type parameters as a constructor's call does."""
    source: str = (
        "import collections\n"
        "def f(names: list[str]) -> None:\n"
        "    a = collections.OrderedDict.fromkeys(names, 0)\n"
        "    b = collections.ChainMap.fromkeys(names, 1.5)\n"
        "    c = collections.OrderedDict.fromkeys(names)\n"
    )
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source) if o.code == LOCAL}
    assert fixed == {
        "a": "collections.OrderedDict[str, int]",
        "b": "collections.ChainMap[str, float]",
        "c": None,  # each value `Any | None`
    }


def test_a_generic_library_class_operator_binds_its_operands_type_arguments() -> None:
    """`Counter[str] + Counter[str]` is a `Counter[str]`; a `deque[int]`'s `Self`, by another of its type.

    A type argument the left operand's own binds must be the right one's (`Counter[str] - Counter[int]`
    isn't typed). Not where a signature's operand is the class's base (`OrderedDict | OrderedDict`
    takes a `dict[_KT, _VT]`), which may take it or not.
    """
    source: str = (
        "from collections import Counter, OrderedDict, deque\n"
        "def f(c: Counter[str], ci: Counter[int], d: deque[int], ds: deque[str], o: OrderedDict[str, int],\n"
        "      n: int, odd: 'Counter[str, int]') -> None:\n"
        "    a = c + c\n"
        "    b = c + ci\n"
        "    e = c - ci\n"
        "    g = d + d\n"
        "    h = d + ds\n"
        "    i = d * n\n"
        "    j = o | o\n"
        "    k = c | c\n"
        "    m = c + odd\n"
    )
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source) if o.code == LOCAL}
    assert fixed == {
        "a": "Counter[str]",
        "b": "Counter[str | int]",
        "e": None,
        "g": "deque[int]",
        "h": None,
        "i": "deque[int]",
        "j": None,
        "k": "Counter[str]",
        "m": None,  # not as many type arguments as its template
    }


def test_a_class_under_a_library_one_takes_its_operators() -> None:
    """`Money(Decimal) + Money` is what `Decimal.__add__` gives, its `Self` the module's own class.

    Not where the class, or one between, binds the operator or its reflected twin itself.
    """
    source: str = (
        "from datetime import datetime, timedelta\n"
        "from decimal import Decimal\n"
        "class Money(Decimal):\n"
        "    pass\n"
        "class Own(Decimal):\n"
        "    def __add__(self, other: object) -> 'Own':\n"
        "        return self\n"
        "class Back(Decimal):\n"
        "    def __radd__(self, other: object) -> 'Back':\n"
        "        return self\n"
        "class Stamp(datetime):\n"
        "    pass\n"
        "def f(m: Money, o: Own, back: Back, s: Stamp, span: timedelta, d: Decimal, n: int) -> None:\n"
        "    a = m + m\n"
        "    b = m + n\n"
        "    c = o + o\n"
        "    e = s - span\n"
        "    g = s - s\n"
        "    h = d + m\n"
        "    i = n * m\n"
        "    j = d + back\n"
        "    k = n + back\n"
    )
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source) if o.code == LOCAL}
    assert fixed == {
        "a": "Decimal",
        "b": "Decimal",
        "c": None,
        "e": "Stamp",
        "g": "timedelta",
        "h": "Decimal",
        "i": "Decimal",
        "j": None,
        "k": None,
    }


def test_an_iterable_of_iterables_binds_by_the_elements_elements() -> None:
    """`chain.from_iterable(rows)`, `rows` a `list[list[int]]`, is a `chain[int]`.

    Not where the elements aren't a container it reads (a `str`'s, an unknown value's), or the
    outer container's elements aren't its first type argument's.
    """
    source: str = (
        "import itertools\n"
        "from itertools import chain\n"
        "def f(names: list[str], rows: list[list[int]], sets: tuple[set[str], ...], q,\n"
        "      table: dict[str, list[int]]) -> None:\n"
        "    a = itertools.chain.from_iterable(rows)\n"
        "    b = chain.from_iterable([names, names])\n"
        "    c = chain.from_iterable(sets)\n"
        "    g = chain.from_iterable(names)\n"
        "    h = chain.from_iterable(q)\n"
        "    i = chain.from_iterable(table)\n"
        "    j = chain.from_iterable(table.values())\n"
    )
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source) if o.code == LOCAL}
    assert fixed == {
        "a": "chain[int]",
        "b": "chain[str]",
        "c": "chain[str]",
        "g": None,
        "h": None,
        "i": None,  # a `dict`'s keys are `str`s
        "j": None,
    }
