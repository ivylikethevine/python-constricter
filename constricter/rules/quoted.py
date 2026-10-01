# SPDX-License-Identifier: MIT
"""Quoted annotations: a string annotation as the expression it quotes, and a quoted part as its text."""

import ast
from functools import lru_cache
from typing import Final

_LITERAL: Final = "Literal"  # its strings are values, not quoted types
_ANNOTATED: Final = "Annotated"  # its first argument alone is a type
_QUOTES: Final = frozenset("'\"")


def _head(node: ast.expr) -> str:
    """Read the last name a subscript's head is written with (`Literal`, for `typing.Literal`).

    Returns:
      It.

    """
    return ast.unparse(node).rpartition(".")[2]


@lru_cache(maxsize=256)
def parsed(annotation: ast.expr) -> ast.expr:
    """Unwrap a string annotation.

    `is_vague` and `depth` both call this on the same annotation; cached so it's parsed once.

    Returns:
      Its parsed expression, or the annotation itself if it isn't a string.

    """
    if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
        try:
            return ast.parse(annotation.value, mode="eval").body
        except SyntaxError:
            return annotation
    return annotation


def written(annotation: ast.expr) -> str:
    """Write an annotation as text `--fix` infers from: a quoted one, or a quoted part, as what it quotes.

    `"list[Node]"` and `list["Node"]` are both `list[Node]`. Not a `Literal`'s strings, nor an
    `Annotated`'s metadata, which are values; nor a string that isn't an expression.

    Returns:
      The text.

    """
    text: str = ast.unparse(annotation)
    return ast.unparse(_unquoted(annotation)) if _QUOTES.intersection(text) else text


def _unquoted(node: ast.expr) -> ast.expr:
    """Rebuild an annotation with each quoted type in it read as an expression (see `written`).

    Returns:
      The annotation: a new tree wherever it differs (the module's own is shared).

    """
    head: ast.expr
    inner: ast.expr
    first: ast.expr
    rest: list[ast.expr]
    parts: list[ast.expr]
    left: ast.expr
    right: ast.expr
    found: ast.expr = node
    match node:
        case ast.Constant(value=str()):
            found = parsed(node)
            found = found if found is node else _unquoted(found)
        case ast.Subscript(value=head) if _head(head) == _LITERAL:
            pass
        case ast.Subscript(value=head, slice=ast.Tuple(elts=[first, *rest])) if _head(head) == _ANNOTATED:
            found = ast.Subscript(head, ast.Tuple([_unquoted(first), *rest]))
        case ast.Subscript(value=head, slice=inner):
            found = ast.Subscript(head, _unquoted(inner))
        case ast.Tuple(elts=parts):
            found = ast.Tuple([_unquoted(part) for part in parts])
        case ast.List(elts=parts):
            found = ast.List([_unquoted(part) for part in parts])
        case ast.BinOp(left=left, op=ast.BitOr(), right=right):
            found = ast.BinOp(_unquoted(left), ast.BitOr(), _unquoted(right))
        case _:
            pass
    return found
