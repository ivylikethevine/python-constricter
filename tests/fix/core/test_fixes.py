# SPDX-License-Identifier: MIT
"""Applying `--fix`'s annotations to source lines (constricter.fixes)."""

from constricter.fix.core import fixes
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


def test_apply_annotates_a_name_after_its_source_spelling() -> None:
    """A name the source spells unnormalised (full-width, `www` to `ast`) is annotated after all of it."""
    wide: str = "\uff57\uff57\uff57"
    fraktur: str = "\U0001d518\U0001d52b"
    lines: list[str] = [f"{wide} = 1\n", f"{fraktur} = 2\n"]
    offences: list[Offence] = [Offence(1, 0, "www", edit=Fix("int")), Offence(2, 0, "Un", edit=Fix("int"))]
    assert fixes.apply(lines, offences) == [f"{wide}: int = 1\n", f"{fraktur}: int = 2\n"]


def test_apply_skips_a_fix_whose_name_is_not_at_its_column() -> None:
    """A line that has another name, or none, where the offence's should be is left unfixed."""
    lines: list[str] = ["other = 1\n", "(a) = 2\n"]
    offences: list[Offence] = [Offence(1, 0, "name", edit=Fix("int")), Offence(2, 0, "a", edit=Fix("int"))]
    assert fixes.apply(lines, offences) == lines
