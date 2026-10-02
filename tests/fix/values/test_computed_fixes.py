# SPDX-License-Identifier: MIT
"""`--fix` for values computed from others: conditionals, arithmetic, comprehensions, and more."""

import pytest

from constricter import Offence, check_source

NAME: str = "x_"  # the variable each case binds


@pytest.mark.parametrize(
    ("value", "fix"),
    [
        ("n if flag else 0", "int"),
        ("n if flag else 's'", None),  # the sides disagree
        ("n + 1", "int"),
        ("n / 2", "float"),
        ("n * ratio", "float"),
        ("flag + flag", "int"),
        ("n ** 2", None),  # `2 ** -1` is a float
        ("n << 1", None),
        ("'x' * n", "str"),
        ("'%s' % n", "str"),
        ("'a' + 'b'", "str"),
        ("b'a' + b'b'", "bytes"),
        ("'a' + n", None),  # a `TypeError`, not a `str`
        ("'a' - 'b'", None),
        ("n * 'x'", None),  # the text isn't on the left: not followed
        ("unknown() + 1", None),
        ("[line.strip() for line in lines]", "list[str]"),
        ("{x for x in range(3)}", "set[int]"),
        ("{k: v + 1 for k, v in ages.items()}", "dict[str, int]"),
        ("[x for x in unknown()]", None),
        ("[n for n in unknown()]", None),  # the target shadows the parameter `n`
        ("{k: other for k in lines}", None),  # `other` isn't known
        ("(x for x in lines)", None),  # a generator is left alone
        ("sorted(lines)", "list[str]"),
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
        "async def f(n: int, ratio: float, flag: bool, lines: list[str], ages: dict[str, int]) -> None:\n"
        f"    {NAME} = {value}\n"
    )
    offences: list[Offence] = [o for o in check_source(source) if o.name == NAME]
    assert [(o.fix, o.unsafe) for o in offences] == [(fix, False)]


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
