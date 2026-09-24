# SPDX-License-Identifier: MIT
"""One walk of a whole module, shared by every pass over all of it (importing nothing of constricter's)."""

import ast
from collections.abc import Sequence
from typing import Final, TypeAlias, cast
from weakref import WeakKeyDictionary

_CTX: Final = "ctx"
# What a node's field holds, as far as the walk cares: a node, a list (of nodes, or of names), or else.
_Value: TypeAlias = ast.AST | list[ast.AST | str] | str | int | None


_Walk: TypeAlias = dict[type[ast.AST], list[ast.AST]]  # a module's nodes, by their type
# Each node class's fields, but its `ctx` (only ever `Load`, `Store` or `Del`: no pass looks at them).
_FIELDS: dict[type[ast.AST], tuple[str, ...]] = {}


# Each module's walk, for as long as its tree lives: the cross-file index's walk of a file is the
# check's too, when the index kept its tree (`parsed.keep`), however many files came between.
_WALKS: Final[WeakKeyDictionary[ast.Module, "_Walk"]] = WeakKeyDictionary()


def _by_type(tree: ast.Module) -> dict[type[ast.AST], list[ast.AST]]:
    """Walk a whole module once, sorting its nodes by type, for every pass that looks at all of it.

    `ast.walk` was most of a check's time (on the standard library, 57%), eight passes each walking
    every module whole. This walk is `ast.walk`'s, breadth first, without its per-node generators:
    a generation of nodes at a time, and each class's fields looked up once.

    Returns:
      Each type's nodes, in `ast.walk`'s order (all but the `Load`, `Store` and `Del` markers).

    """
    found: dict[type[ast.AST], list[ast.AST]] | None
    if (found := _WALKS.get(tree)) is not None:
        return found
    found = _WALKS[tree] = {}
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
            field: str
            for field in _fields_of(kind):
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


def children(node: ast.AST) -> list[ast.AST]:
    """List a node's children, as `ast.iter_child_nodes` does but for their `ctx`, and without its generator.

    Returns:
      Them, in their fields' order.

    """
    found: list[ast.AST] = []
    field: str
    for field in _fields_of(type(node)):
        value: _Value = cast("_Value", getattr(node, field, None))
        if isinstance(value, list):
            found.extend([item for item in value if isinstance(item, ast.AST)])
        elif isinstance(value, ast.AST):
            found.append(value)
    return found


def walk(node: ast.AST) -> list[ast.AST]:
    """List a node and everything under it (but `ctx` markers), for a pass that needn't their order.

    Returns:
      Them, depth first (not `ast.walk`'s breadth first order).

    """
    found: list[ast.AST] = []
    waiting: list[ast.AST | None] = [None, node]  # `None` at its bottom ends it
    item: ast.AST
    for item in iter(waiting.pop, None):
        found.append(item)
        waiting.extend(children(item))
    return found


def _fields_of(kind: type[ast.AST]) -> tuple[str, ...]:
    """Name a node class's fields but its `ctx`, worked out once per class.

    Returns:
      Them.

    """
    fields: tuple[str, ...] | None
    if (fields := _FIELDS.get(kind)) is None:
        fields = _FIELDS[kind] = tuple(field for field in kind._fields if field != _CTX)
    return fields
