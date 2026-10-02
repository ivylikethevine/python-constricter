# SPDX-License-Identifier: MIT
"""`--fix` for builtins and operators their operands' types decide: `min`, `sum`, `next`, `dict`, `-n`."""

import pytest

from constricter import Offence, check_source

NAME: str = "x_"  # the variable each case binds
_SIGNATURE: str = (
    "def f(n: int, ratio: float, flag: bool, z: complex, names: list[str], ages: dict[str, int],\n"
    "      lines: Iterator[bytes], maybe: int | None, table: Mapping[str, float], other) -> None:\n"
)


@pytest.mark.parametrize(
    ("value", "fix"),
    [
        ("abs(n)", "int"),
        ("abs(flag)", "int"),
        ("abs(ratio)", "float"),
        ("abs(z)", "float"),
        ("abs(other)", None),
        ("abs(names)", None),
        ("abs(n, n)", None),
        ("abs(x=n)", None),
        ("round(ratio)", "int"),
        ("round(n)", "int"),
        ("round(ratio, None)", "int"),
        ("round(ratio, 2)", "float"),
        ("round(n, 2)", "int"),
        ("round(ratio, other)", "float"),  # whatever the digits are
        ("round(other)", None),
        ("round()", None),
        ("round(ratio, 2, 3)", None),
        ("round(ratio, ndigits=2)", None),
        ("divmod(n, 2)", "tuple[int, int]"),
        ("divmod(n, ratio)", "tuple[float, float]"),
        ("divmod(n, other)", None),
        ("divmod(n)", None),
        ("sum(ages.values())", "int"),
        ("sum([ratio, ratio])", "float"),
        ("sum(len(name) for name in names)", "int"),
        ("sum(ages.values(), 0.5)", "float"),
        ("sum(ages.values(), start=1)", "int"),
        ("sum(names)", None),  # not numbers
        ("sum(other)", None),
        ("sum(ages.values(), other)", None),
        ("sum(ages.values(), 1, start=2)", None),
        ("sum(ages.values(), begin=2)", None),
        ("sum()", None),
        ("min(n, 3)", "int"),
        ("max(names[0], 'a', key=len)", "str"),
        ("max(names)", "str"),
        ("max(names, key=len)", "str"),
        ("min(len(name) for name in names)", "int"),
        ("max(ages.values(), default=None)", "int | None"),
        ("max(ages.values(), default=0)", "int"),
        ("max(ages.values(), default='')", None),  # another type
        ("max(ages.values(), default=other)", None),
        ("max(names, default=None)", "str | None"),
        ("min(n, ratio)", None),  # two types
        ("min(n, other)", None),
        ("max(maybe, maybe)", None),  # a union: what's read may be narrowed
        ("max(n, 3, default=0)", None),  # no default with several values
        ("max(other)", None),
        ("max()", None),
        ("max(names, reverse=True)", None),
        ("max(*names)", None),
        ("max(names, **other)", None),
        ("next(lines)", "bytes"),
        ("next(iter(names))", "str"),
        ("next(reversed(names))", "str"),
        ("next(name for name in names)", "str"),
        ("next((name for name in names if name), None)", "str | None"),
        ("next(lines, b'')", "bytes"),
        ("next(lines, '')", None),
        ("next(iter(other, None))", None),  # with a sentinel, what `other` returns
        ("next(other)", None),
        ("next()", None),
        ("next(lines, None, None)", None),
        ("next(lines, default=None)", None),
        ("next((m for m in [maybe] if m), None)", None),  # the condition narrows the union
        ("dict(ages)", "dict[str, int]"),
        ("dict(table)", "dict[str, float]"),  # a `dict`, whatever mapping it copies
        ("dict(zip(names, ages.values()))", "dict[str, int]"),
        ("dict(enumerate(names))", "dict[int, str]"),
        ("dict((name, len(name)) for name in names)", "dict[str, int]"),
        ("dict(a=1, b=2)", "dict[str, int]"),
        ("dict(a=1, b='x')", None),
        ("dict(a=other)", None),
        ("dict(ages, a=1)", None),
        ("dict(names)", None),  # not pairs
        ("dict([names])", None),
        ("dict((n, n, n) for n in names)", None),
        ("dict(other)", None),
        ("dict()", None),
        ("dict(ages, ages)", None),
        ("dict.fromkeys(names, 0)", "dict[str, int]"),
        ("dict.fromkeys(names)", None),  # each value `None`, or anything
        ("dict.fromkeys(other, 0)", None),
        ("dict.fromkeys(names, other)", None),
        ("dict.fromkeys(names, value=0)", None),
        ("bytes.fromhex('00')", "bytes"),
        ("bytearray.fromhex('00')", "bytearray"),
        ("bytes.maketrans(b'a', b'b')", "bytes"),
        ("float.fromhex('0x1p0')", "float"),
        ("int.from_bytes(b'a', 'big')", "int"),
        ("str.maketrans('a', 'b')", None),  # its arguments decide it
        ("other().fromhex('00')", None),
        ("-n", "int"),
        ("+ratio", "float"),
        ("-flag", "int"),
        ("-z", "complex"),
        ("~n", "int"),
        ("~flag", "int"),
        ("~ratio", None),
        ("-names", None),
        ("-other", None),
        ("names + names", "list[str]"),
        ("names * 2", "list[str]"),
        ("names + [n]", None),  # another list's type
        ("names % n", None),
        ("names - names", None),
        ("list(str(i) for i in range(n))", "list[str]"),
        ("tuple(name.upper() for name in names)", "tuple[str, ...]"),
        ("sorted(name for name in names if name)", "list[str]"),
        ("set(other for name in names)", None),
        ("list(m for m in [maybe] if m)", None),
    ],
)
def test_a_builtin_is_typed_by_its_arguments(value: str, fix: str | None) -> None:
    """Each is certain when it's typed at all: nothing in it is a guess."""
    source: str = f"{_SIGNATURE}    {NAME} = {value}\n"
    offences: list[Offence] = [o for o in check_source(source) if o.name == NAME]
    assert [(o.fix, o.unsafe) for o in offences] == [(fix, False)]


def test_a_builtin_the_module_rebinds_is_left_alone() -> None:
    """A module's own `max` isn't the builtin's, anywhere in it."""
    source: str = "def max(a, b): ...\n\n\ndef f(n: int) -> None:\n    x_ = max(n, 3)\n    y_ = min(n, 3)\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("x_", None), ("y_", "int")]


def test_a_builtin_of_a_guess_or_a_tested_value_is_a_guess() -> None:
    """What `min` takes as its own type is a guess where its argument is one, or the function tests it."""
    source: str = (
        "def f(low: Size, high: Size, n: int) -> None:\n"
        "    box = Box()\n"
        "    x_ = max(box.size, box.size)\n"
        "    y_ = min(low, high)\n"
        "    z_ = abs(n)\n"
        "    w_ = dict.fromkeys([n], box)\n"
        "    v_ = int.from_bytes(box.raw, 'big')\n"
        "    if isinstance(low, Small):\n"
        "        pass\n"
        "\n\n"
        "class Box:\n    size: int\n"
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("box", "Box", True),
        ("x_", "int", True),
        ("y_", "Size", True),
        ("z_", "int", False),
        ("w_", "dict[int, Box]", True),
        ("v_", "int", False),  # whatever it's given
    ]


def test_a_loop_over_a_generator_expression_or_iter_takes_its_elements() -> None:
    """`for size in (len(name) for name in names)`, and `iter(names)`, by what they yield."""
    source: str = (
        "def f(names: list[str]) -> None:\n"
        "    for size in (len(name) for name in names):\n"
        "        pass\n"
        "    for name in iter(names):\n"
        "        pass\n"
        "    for line in iter(names.pop, ''):\n"
        "        pass\n"
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [
        ("size", "int"),
        ("name", "str"),
        ("line", None),
    ]
