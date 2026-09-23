# SPDX-License-Identifier: MIT
"""One walk of a whole module, shared by every pass over all of it (importing nothing of constricter's)."""

import ast
from collections.abc import Sequence
from functools import lru_cache
from typing import cast


@lru_cache(maxsize=4)  # the module being checked: every pass over all of it reads this one walk
def nodes(tree: ast.Module) -> tuple[ast.AST, ...]:
    """Walk a whole module once, for every pass that looks at all of it.

    `ast.walk` is most of a check's time (on the standard library, 57%): eight passes each walking
    every module whole took a quarter of it.

    Returns:
      Every node in it, in `ast.walk`'s order.

    """
    return tuple(ast.walk(tree))


@lru_cache(maxsize=4)
def _by_type(tree: ast.Module) -> dict[type[ast.AST], list[ast.AST]]:
    """Sort a module's nodes by their type, once.

    Returns:
      Each type's nodes, in `ast.walk`'s order.

    """
    found: dict[type[ast.AST], list[ast.AST]] = {}
    node: ast.AST
    for node in nodes(tree):
        found.setdefault(type(node), []).append(node)
    return found


def of_type(tree: ast.Module, *kinds: type[ast.AST]) -> Sequence[ast.AST]:
    """Find a module's nodes of `kinds`: a pass that wants only those needn't look at every node.

    Returns:
      Them, each kind's in `ast.walk`'s order, the kinds one after another.

    """
    table: dict[type[ast.AST], list[ast.AST]] = _by_type(tree)
    return [node for kind in kinds for node in table.get(kind, [])]


def classes(tree: ast.Module) -> Sequence[ast.ClassDef]:
    """Find every class a module defines, however deep.

    Returns:
      Them, in `ast.walk`'s order.

    """
    return cast("list[ast.ClassDef]", _by_type(tree).get(ast.ClassDef, []))
