# SPDX-License-Identifier: MIT
"""Applying `--fix`'s annotations to source lines (constricter.fixes)."""

from constricter.fix import fixes
from constricter.offences import Fix, Offence


def test_apply_adds_each_fixable_offences_annotation() -> None:
    """Fixable offences are applied right to left, so earlier columns on a line stay valid."""
    lines: list[str] = ["a = 1\n", "b, c = 1, 2\n"]
    offences: list[Offence] = [Offence(1, 0, "a", edit=Fix("int")), Offence(2, 0, "b")]
    assert fixes.apply(lines, offences) == ["a: int = 1\n", "b, c = 1, 2\n"]


def test_apply_skips_a_fix_that_would_split_a_multi_byte_character() -> None:
    """A `col` landing inside a multi-byte character (rare) is left unfixed, not corrupted."""
    lines: list[str] = ["café = 1\n"]
    # `é`.encode() is 2 bytes (\xc3\xa9), and col=3 lands between them, not before or after both.
    offences: list[Offence] = [Offence(1, 3, "x", edit=Fix("int"))]
    assert fixes.apply(lines, offences) == lines
