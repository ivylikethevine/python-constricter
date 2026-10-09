# SPDX-License-Identifier: MIT
"""The strings an annotation leaves inside it (an `Annotated`'s metadata), and the names in them."""

import ast
from functools import lru_cache
from typing import Final

from constricter.rules.annotations import node_name

_LITERAL: Final = "Literal"


@lru_cache(maxsize=4096)
def quoted(annotation: str) -> frozenset[str]:
    """Find the names in the strings left inside an annotation: `meta` in `Annotated[int, 'meta']`.

    A quoted type is read as its text before it gets here (see `annotations.written`). Not a
    `Literal`'s strings, nor a whole annotation's own quotes (see `roots`).

    Returns:
      The names.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    found: set[str] = set()
    waiting: list[ast.AST | None] = [None, tree]  # `None` at its bottom ends it
    node: ast.AST
    for node in iter(waiting.pop, None):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node is not tree:
            found.update(_names_in(node.value))
        elif not (isinstance(node, ast.Subscript) and node_name(node.value) == _LITERAL):
            waiting.extend(ast.iter_child_nodes(node))
    return frozenset(found)


def _names_in(text: str) -> set[str]:
    """Read the names a quoted part of an annotation is written with.

    Returns:
      Them; none if it isn't an expression.

    """
    try:
        return {node.id for node in ast.walk(ast.parse(text, mode="eval")) if isinstance(node, ast.Name)}
    except SyntaxError:
        return set()
