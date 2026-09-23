# SPDX-License-Identifier: MIT
"""One walk of a whole module, shared by every pass over all of it (importing nothing of constricter's)."""

import ast
from collections.abc import Sequence
from functools import lru_cache
from typing import Final, TypeAlias, cast

_CTX: Final = "ctx"
# What a node's field holds, as far as the walk cares: a node, a list (of nodes, or of names), or else.
_Value: TypeAlias = ast.AST | list[ast.AST | str] | str | int | None


# Each node class's fields, but its `ctx` (only ever `Load`, `Store` or `Del`: no pass looks at them).
_FIELDS: dict[type[ast.AST], tuple[str, ...]] = {}


@lru_cache(maxsize=4)  # the module being checked: every pass over all of it reads this one walk
def _by_type(tree: ast.Module) -> dict[type[ast.AST], list[ast.AST]]:
    """Walk a whole module once, sorting its nodes by type, for every pass that looks at all of it.

    `ast.walk` was most of a check's time (on the standard library, 57%), eight passes each walking
    every module whole. This walk is `ast.walk`'s, breadth first, without its per-node generators:
    a generation of nodes at a time, and each class's fields looked up once.

    Returns:
      Each type's nodes, in `ast.walk`'s order (all but the `Load`, `Store` and `Del` markers).

    """
    found: dict[type[ast.AST], list[ast.AST]] = {}
    # A generation at a time (a breadth-first queue's order): each built from the one before.
    # `None` at the bottom ends it: a generation with no children adds none to follow it.
    generations: list[list[ast.AST] | None] = [None, [tree]]
    generation: list[ast.AST]
    for generation in iter(generations.pop, None):
        following: list[ast.AST] = []
        node: ast.AST
        for node in generation:
            kind: type[ast.AST] = type(node)
            found.setdefault(kind, []).append(node)
            fields: tuple[str, ...] | None
            if (fields := _FIELDS.get(kind)) is None:
                fields = _FIELDS[kind] = tuple(field for field in kind._fields if field != _CTX)
            field: str
            for field in fields:
                value: _Value = cast("_Value", getattr(node, field, None))
                if isinstance(value, list):
                    # A list, not a generator: none's resumed for each item (and it's inlined, 3.12+).
                    following.extend([item for item in value if isinstance(item, ast.AST)])
                elif isinstance(value, ast.AST):
                    following.append(value)
        if following:
            generations.append(following)
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
