"""The plugins' options, the same in flake8 and pylint: each one's name, kind, default and help."""

from typing import Final, NamedTuple

from constricter.offences import LEVELS, MAX_LENGTH, NESTING, VAGUE

LEVEL: Final = "level"  # one of `LEVELS`' names
FLAG: Final = "flag"  # on or off
WHOLE: Final = "whole"  # a whole number
TEXT: Final = "text"


class Option(NamedTuple):
    """One option: `--constricter-{name}` in flake8, `constricter-{name}` in pylint."""

    name: str
    kind: str
    default: str | int | bool
    help: str


OPTIONS: Final = (
    Option(LEVEL, LEVEL, "strict", "which codes are reported"),
    Option("type-comments", FLAG, default=False, help="count `x = 1  # type: int` as annotated"),
    Option("all-scopes", FLAG, default=False, help="also check module and class bodies (LVA004)"),
    Option("nesting", WHOLE, NESTING, "report an annotation nested this deep (LVA006)"),
    Option(
        "max-length",
        WHOLE,
        MAX_LENGTH,
        "report a fixed-length tuple annotation listing more types (LVA011)",
    ),
    Option("vague", WHOLE, VAGUE, "how vague an annotation may be before it's LVA005; -1 reports none"),
    Option(
        "narrower",
        TEXT,
        "",
        "your own type hierarchy for LVA008-LVA010, as `B=A, C=A, int=` (B is narrower than A)",
    ),
)
CHOICES: Final = list(LEVELS)  # what `level` takes
