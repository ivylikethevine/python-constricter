# SPDX-License-Identifier: MIT
"""The codes, their messages and levels, and the `Offence` and `Checks` types every module shares."""

import ast
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Final, NamedTuple

from constricter.rules.flow import Narrower

UNANNOTATED: Final = "LVA001"
UNTYPED_TARGET: Final = "LVA002"
COMMENT_TYPED_TARGET: Final = "LVA003"
UNANNOTATED_MEMBER: Final = "LVA004"
VAGUE_TYPE: Final = "LVA005"
NESTED_TYPE: Final = "LVA006"
REDUNDANT_TYPE: Final = "LVA007"
NARROWABLE_TYPE: Final = "LVA008"
MISMATCHED_TYPE: Final = "LVA009"
UNUSED_UNION_MEMBER: Final = "LVA010"
LONG_TUPLE: Final = "LVA011"
MESSAGES: dict[str, str] = {
    UNANNOTATED: "local variable {name} is not annotated where it's first bound",
    UNTYPED_TARGET: "for/match variable {name} is untyped; declare it before the statement",
    COMMENT_TYPED_TARGET: "for variable {name} is typed only by a type comment; declare it before the loop",
    UNANNOTATED_MEMBER: "module or class variable {name} is not annotated where it's first bound",
    VAGUE_TYPE: "the annotation of {name} is vague: Any, object, or a generic without its parameters",
    NESTED_TYPE: "the annotation of {name} nests too deeply; name a part of it with a `type` alias",
    REDUNDANT_TYPE: "{name} is annotated again with the type it already has, in the same block",
    NARROWABLE_TYPE: "{name} only ever holds `{detail}`; its annotation could narrow to that",
    MISMATCHED_TYPE: "{name} is bound to `{detail}` here, which doesn't fit its annotation",
    UNUSED_UNION_MEMBER: "{name}'s annotation allows `{detail}`, which no value it's bound to ever is",
    LONG_TUPLE: "the annotation of {name} lists a tuple of {detail} elements; name them (a NamedTuple)",
}
NESTING: Final = 3  # LVA006's default depth
MAX_LENGTH: Final = 4  # LVA011's default: the longest fixed-length tuple an annotation may list


class Level(IntEnum):
    """How strict: each level makes one more code an error rather than a warning."""

    RELAXED = 0
    STRICT = 1
    CONSTRICT = 2
    SUFFOCATE = 3


# Each level by name and by number, as the options take it.
LEVELS: dict[str, Level] = {key: level for level in Level for key in (level.name.lower(), str(level.value))}
_ERROR_FROM: dict[str, Level] = {
    UNANNOTATED: Level.STRICT,
    UNTYPED_TARGET: Level.CONSTRICT,
    COMMENT_TYPED_TARGET: Level.SUFFOCATE,
    UNANNOTATED_MEMBER: Level.STRICT,
    VAGUE_TYPE: Level.SUFFOCATE,
    NESTED_TYPE: Level.SUFFOCATE,
    REDUNDANT_TYPE: Level.SUFFOCATE,
    NARROWABLE_TYPE: Level.SUFFOCATE,
    MISMATCHED_TYPE: Level.CONSTRICT,
    UNUSED_UNION_MEMBER: Level.SUFFOCATE,
    LONG_TUPLE: Level.SUFFOCATE,
}
# Codes reported only from a level up (the rest are reported at every level).
_REPORTED_FROM: dict[str, Level] = {
    VAGUE_TYPE: Level.STRICT,
    NESTED_TYPE: Level.STRICT,
    LONG_TUPLE: Level.STRICT,
    NARROWABLE_TYPE: Level.CONSTRICT,
    UNUSED_UNION_MEMBER: Level.CONSTRICT,
}


@dataclass(frozen=True, order=True)
class Offence:
    """One untyped first binding; `col` is 0-based."""

    line: int
    col: int
    name: str
    code: str = UNANNOTATED
    # The annotation `--fix` would add, where the value makes it unambiguous.
    fix: str | None = field(default=None, compare=False)
    # In a notebook, the cell (from 1); `line` is then the line in that cell.
    cell: int | None = field(default=None, compare=False)
    # Whether `fix` is a guess, applied only with `--unsafe-fixes`.
    unsafe: bool = field(default=False, compare=False)
    # How the value decided `fix` (`--show-fixes`).
    reason: str = field(default="", compare=False)
    # What the message names besides the variable: LVA008's to LVA010's type, LVA011's length.
    detail: str = field(default="", compare=False)

    @property
    def message(self) -> str:
        """The report text."""
        return MESSAGES[self.code].format(name=repr(self.name), detail=self.detail)

    def is_error(self, level: Level) -> bool:
        """Check this offence's severity at `level`.

        Returns:
          Whether it's an error rather than a warning.

        """
        return level >= _ERROR_FROM[self.code]

    def is_reported(self, level: Level) -> bool:
        """Check whether `level` reports this offence.

        Returns:
          Whether it does at all.

        """
        return level >= _REPORTED_FROM.get(self.code, Level.RELAXED)


class Checks(NamedTuple):
    """What to check, beyond the defaults.

    With `type_comments`, `x = 1  # type: int` counts as annotated; with `all_scopes`, module and
    class bodies are checked too (LVA004); an annotation nested `nesting` deep is LVA006, and one
    listing a fixed-length tuple longer than `max_length` is LVA011.
    """

    type_comments: bool = False
    all_scopes: bool = False
    nesting: int = NESTING
    max_length: int = MAX_LENGTH
    # A project's own type hierarchy, for LVA008-LVA010: each type and the types it's narrower than.
    narrower: tuple[Narrower, ...] = ()


DEFAULT_CHECKS: Final = Checks()


def at(node: ast.expr | ast.pattern | ast.stmt) -> tuple[int, int]:
    """Find where `node` starts, as an offence is placed.

    Returns:
      Its line and (0-based) column.

    """
    return node.lineno, node.col_offset
