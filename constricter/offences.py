# SPDX-License-Identifier: MIT
"""The codes, their messages and levels, and the `Offence` and `Checks` types every module shares."""

import ast
from dataclasses import dataclass, field
from enum import IntEnum, StrEnum
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
CAN_BE_FINAL: Final = "LVA012"
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
    CAN_BE_FINAL: "{name} is bound once and never rebound; it could be `Final`",
}
# Codes reported only when selected by their full code (`--select LVA012`), never by a prefix.
OPT_IN: Final = frozenset({CAN_BE_FINAL})
# Each way `--fix` can decide an annotation, by its stable id (`--show-fixes`, `fix-select`).
FIX_KINDS: dict[str, str] = {
    "literal": "a literal, an f-string, or `not x`",
    "container": "a list, set, tuple or dict display whose elements' types agree",
    "copy": "a copy of a local whose type is known",
    "subscript": "a subscript of a known container",
    "attribute": "an attribute of a class the module defines",
    "method": "a method with a fixed or declared return type, on a known local",
    "builtin": "a builtin with a fixed return type (`len`, `str`, ...)",
    "call": "a function that declares its return type (this module's, or another checked file's)",
    "constructor": "a call to a capitalised name, taken to construct one (a guess)",
    "conditional": "both sides of `a if c else b`",
    "arithmetic": "arithmetic on builtin scalars",
    "comprehension": "a list, set or dict comprehension's elements",
    "builder": "`sorted`, `list`, `set`, `frozenset` or `tuple` of known elements",
    "await": "`await` of the module's `async def`",
    "cast": "`typing.cast(T, x)`: its `T`",
    "stdlib": "a standard-library function with a builtin result or class (`time.time`, `uuid4`)",
    "optional": "`x = None`, then only ever a value of one known type `T`: `T | None`",
    "rebound": "a name later bound to a wider type: the type every value fits (`int`, then `float`)",
    "filled": "an empty container, then only what the function adds to it (a guess)",
    "returned": "an unannotated function's own `return`s (a method's: a guess)",
    "assigned": "an unannotated instance attribute's every `self.x = value` in its class (a guess)",
    "final": "LVA012's `Final`: around its annotation, or with LVA001's type (`Final[int]`)",
    "checker": "a type checker's inferred type, from its inlay hints (`--infer-with`; a guess)",
    "open": "`open(path, mode)`'s file object, by its literal mode (`io.TextIOWrapper`, ...)",
    "loop": "what a loop (or `sorted`, `list`, ...) iterates over",
    "unpack": "an unpacking, split over its names",
    "narrow": "LVA008's or LVA010's narrower annotation (a guess)",
    "comment": "LVA003: the loop's own `# type:` comment, as a declaration",
    "redundant": "LVA007: the repeated annotation, dropped",
}
CONSTRUCTOR: Final = "constructor"
NARROW: Final = "narrow"
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
    CAN_BE_FINAL: Level.SUFFOCATE,
}
# Codes reported only from a level up (the rest are reported at every level).
_REPORTED_FROM: dict[str, Level] = {
    VAGUE_TYPE: Level.STRICT,
    NESTED_TYPE: Level.STRICT,
    LONG_TUPLE: Level.STRICT,
    NARROWABLE_TYPE: Level.CONSTRICT,
    UNUSED_UNION_MEMBER: Level.CONSTRICT,
}


class Edit(StrEnum):
    """Where a `Fix` writes its annotation."""

    ANNOTATE = "annotate"  # `: T` after the offence's name
    REPLACE = "replace"  # over an annotation already there (`Fix.span`: its start and end column)
    DECLARE = "declare"  # `name: T` on a line of its own before a statement (`Fix.span`: its line and column)


class Fix(NamedTuple):
    """The annotation `--fix` would write for an offence, how its value decided it, and where."""

    annotation: str
    reason: str = ""  # `--show-fixes`
    unsafe: bool = False  # a guess, applied only with `--unsafe-fixes`
    edit: Edit = Edit.ANNOTATE
    span: tuple[int, int] = (0, 0)  # see `Edit`; columns count UTF-8 bytes, as `ast`'s do
    kinds: frozenset[str] = frozenset()  # every `FIX_KINDS` mechanism that decided it
    # With `Edit.DECLARE`: the columns to delete on the statement's line too (the type comment it replaces).
    drop: tuple[int, int] | None = None
    imports: tuple[str, ...] = ()  # statements the annotation needs added (`from io import BytesIO`)
    after: int = 0  # the line they go after (see `fix.imports.plan`)


class FixPolicy(NamedTuple):
    """Which `FIX_KINDS` `--fix` offers (`select`, empty for all, less `ignore`), and which guesses it trusts.

    A guess is certain when every guessing mechanism it rests on (`constructor`, `narrow`, through
    any guessed local it copies) is in `unsafe_select`, as ruff's `extend-safe-fixes` does.
    """

    select: frozenset[str] = frozenset()
    ignore: frozenset[str] = frozenset()
    unsafe_select: frozenset[str] = frozenset()

    def allows(self, kinds: frozenset[str]) -> bool:
        """Check whether a fix decided by `kinds` is offered.

        Returns:
          Whether every one is selected and none ignored.

        """
        return (not self.select or kinds <= self.select) and not kinds & self.ignore

    def trusts(self, origins: frozenset[str]) -> bool:
        """Check whether a guess resting on `origins` is promoted to certain.

        Returns:
          Whether it rests on something, and all of it is in `unsafe_select`.

        """
        return bool(origins) and origins <= self.unsafe_select


@dataclass(frozen=True, order=True)
class Offence:
    """One untyped first binding; `col` is 0-based."""

    line: int
    col: int
    name: str
    code: str = UNANNOTATED
    # What `--fix` would write, where the value makes it unambiguous (or, if `unsafe`, a guess).
    edit: Fix | None = field(default=None, compare=False)
    # In a notebook, the cell (from 1); `line` is then the line in that cell.
    cell: int | None = field(default=None, compare=False)
    # What the message names besides the variable: LVA008's to LVA010's type, LVA011's length.
    detail: str = field(default="", compare=False)

    @property
    def fix(self) -> str | None:
        """The annotation `--fix` would write, if any."""
        return None if self.edit is None else self.edit.annotation

    @property
    def unsafe(self) -> bool:
        """Whether the fix is a guess, applied only with `--unsafe-fixes`."""
        return self.edit is not None and self.edit.unsafe

    @property
    def reason(self) -> str:
        """How the value decided the fix (`--show-fixes`)."""
        return "" if self.edit is None else self.edit.reason

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
    fixes: FixPolicy = FixPolicy()  # which fixes `--fix` offers; it never changes what's reported
    final: bool = False  # look for LVA012 (opt-in: see `OPT_IN`)


DEFAULT_CHECKS: Final = Checks()


def at(node: ast.expr | ast.pattern | ast.stmt) -> tuple[int, int]:
    """Find where `node` starts, as an offence is placed.

    Returns:
      Its line and (0-based) column.

    """
    return node.lineno, node.col_offset
