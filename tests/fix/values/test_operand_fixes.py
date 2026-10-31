"""`--fix` on a `str`'s or `bytes`'s `+` or `*` with a value of no known type: the text's type (a guess)."""

import pytest

from constricter import Offence, check_source
from constricter.fix.values.inference import OPERAND


@pytest.mark.parametrize(
    ("value", "fix", "unsafe"),
    [
        ('"pre-" + x', "str", True),
        ('x + ".pyc"', "str", True),
        ('" " * x', "str", True),
        ('x * " "', "str", True),
        ('b"\\x00" * x', "bytes", True),
        ('x + "/" + y', "str", True),  # the inner guess, joined with a `str`
        ('"a" + "b"', "str", False),  # both sides known: certain
        ('"%s" % x', "str", False),  # formatting gives a `str` whatever it's given
        ('"a" - x', None, False),  # no such operator of a `str`'s
        ("x + 1", None, False),  # a number's: anything numeric
        ("x + y", None, False),
        ("[1] + x", None, False),  # a list's `+` takes lists alone, but `x` may be anything's `__radd__`
    ],
)
def test_a_texts_operator_with_an_unknown_operand_is_the_texts_type(
    value: str,
    fix: str | None,
    *,
    unsafe: bool,
) -> None:
    """A guess: a NumPy array's or a pandas `Series`'s own operator gives one of those instead."""
    offence: Offence
    [offence] = check_source(f"def f(x, y) -> None:\n    v = {value}\n")
    assert (offence.fix, offence.unsafe) == (fix, unsafe)
    assert fix is None or not unsafe or OPERAND in (offence.edit.kinds if offence.edit else ())
