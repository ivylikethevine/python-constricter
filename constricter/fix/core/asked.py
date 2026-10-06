# SPDX-License-Identifier: MIT
"""What a value was inferred to be, kept until its scope types another name.

A statement's value is asked for its type, then for whether that's a guess, then as a part of the
next value (a `with` statement's manager, three times): `asked` answers again what `keep` was told,
for the same value (by `id`), the same scope's types (`Typed`) unchanged since, and the same number
of imports the module's plan has added (an import `--fix` adds can resolve a name the next time).
"""

import ast
from collections.abc import Mapping
from typing import Final, TypeAlias

from constricter.fix.core.known import Inference, Known, Typed

# What was asked: the value and the scope's types (by `id`), how often those had changed, and how
# many imports the module's plan had added.
_Asked: TypeAlias = tuple[int, int, int, int]
# Its answer, with what was asked kept alive beside it: an `id` is only theirs while they live.
_Answered: TypeAlias = tuple[ast.expr, Known, Typed, Inference | None]
_ANSWERS: Final[dict[_Asked, _Answered]] = {}
_KEPT: Final = 2048  # then all are dropped: a few functions' worth


def _key(value: ast.expr, known: Known, declared: Typed) -> _Asked:
    return (
        id(value),
        id(declared),
        declared.version,
        0 if known.names.plan is None else len(known.names.plan.added),
    )


def asked(value: ast.expr, known: Known, declared: Mapping[str, str]) -> tuple[Inference | None] | None:
    """Find what `value` was inferred to be, if it was asked before with nothing changed since.

    Returns:
      The inference (or `None`, for no type), in a tuple; `None` if it's yet to be worked out.

    """
    held: _Answered | None = (
        _ANSWERS.get(_key(value, known, declared)) if isinstance(declared, Typed) else None
    )
    if held is None or held[0] is not value or held[1] is not known or held[2] is not declared:
        return None
    return (held[3],)


def keep(value: ast.expr, known: Known, declared: Mapping[str, str], found: Inference | None) -> None:
    """Keep what `value` was inferred to be, for a scope's own types (any other mapping may change unseen)."""
    if isinstance(declared, Typed):
        if len(_ANSWERS) >= _KEPT:
            _ANSWERS.clear()
        _ANSWERS[_key(value, known, declared)] = (value, known, declared, found)
