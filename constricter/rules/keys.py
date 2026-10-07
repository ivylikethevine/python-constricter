# SPDX-License-Identifier: MIT
"""A `TypedDict`'s keys, held as a class's attributes are: each one's type, and which may be missing."""

import ast
from typing import Final

from constricter.rules.quoted import written

_REQUIRED: Final = "Required"
_NOT_REQUIRED: Final = "NotRequired"
_QUALIFIERS: Final = frozenset({_REQUIRED, _NOT_REQUIRED, "ReadOnly"})  # around a key's type
_TOTAL: Final = "total"


def key(name: str) -> str:
    """Spell a `TypedDict`'s key as `annotations.classes` holds it: apart from any attribute's name.

    Returns:
      It.

    """
    return f"[{name}]"


def optional(name: str) -> str:
    """Spell what says a `TypedDict`'s key may be missing: held beside `key`'s, with the same type.

    Returns:
      It.

    """
    return f"{key(name)}?"


def keys(node: ast.ClassDef) -> dict[str, str]:
    """Read a `TypedDict` class's own keys.

    Returns:
      Each one's type by its `key`, less `Required` and its like; and by its `optional` too, for one
      under `NotRequired`, or in a class with `total=False` and not under `Required`.

    """
    total: bool = not any(
        keyword.arg == _TOTAL and isinstance(keyword.value, ast.Constant) and keyword.value.value is False
        for keyword in node.keywords
    )
    found: dict[str, str] = {}
    annotated: list[tuple[str, ast.expr]] = [
        (stmt.target.id, stmt.annotation)
        for stmt in node.body
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
    ]
    name: str
    annotation: ast.expr
    for name, annotation in annotated:
        qualifiers: set[str] = set()
        found[key(name)] = written(_unqualified(annotation, qualifiers))
        if _NOT_REQUIRED in qualifiers or not (total or _REQUIRED in qualifiers):
            found[optional(name)] = found[key(name)]
    return found


def _unqualified(annotation: ast.expr, qualifiers: set[str]) -> ast.expr:
    """Take the qualifiers off a key's annotation, adding each to `qualifiers`.

    Returns:
      Its type.

    """
    name: str
    inner: ast.expr
    match annotation:
        case ast.Subscript(value=ast.Name(id=name) | ast.Attribute(attr=name), slice=inner) if (
            name in _QUALIFIERS
        ):
            qualifiers.add(name)
            return _unqualified(inner, qualifiers)
        case _:
            return annotation
