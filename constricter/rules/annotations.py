# SPDX-License-Identifier: MIT
"""What an annotation says (LVA005, LVA006, LVA011).

An annotation's vague parts, nesting depth and longest fixed-length tuple, the names it's written
with, and whether it's free of some. What a module declares is `constricter.rules.declarations`.
"""

import ast
import re
from collections.abc import Mapping
from functools import lru_cache
from typing import Final

from constricter.rules.quoted import parsed

_VAGUE: Final = frozenset({"Any", "object"})
_UNIONS: Final = frozenset({"Optional", "Union"})  # a union's members, as a subscript's arguments
# `collections.abc`'s generic classes (`typing` has each too).
ABSTRACT: Final = frozenset(
    {
        "AsyncGenerator",
        "AsyncIterable",
        "AsyncIterator",
        "Awaitable",
        "Callable",
        "Collection",
        "Container",
        "Coroutine",
        "Generator",
        "ItemsView",
        "Iterable",
        "Iterator",
        "KeysView",
        "Mapping",
        "MutableMapping",
        "MutableSequence",
        "MutableSet",
        "Reversible",
        "Sequence",
        "ValuesView",
    },
)
# Generics that say little without their parameters.
GENERICS: Final = ABSTRACT | frozenset(
    {
        "AbstractSet",
        "ChainMap",
        "Counter",
        "DefaultDict",
        "Deque",
        "Dict",
        "FrozenSet",
        "List",
        "Match",
        "OrderedDict",
        "Pattern",
        "Set",
        "Tuple",
        "Type",
        "defaultdict",
        "deque",
        "dict",
        "frozenset",
        "list",
        "set",
        "tuple",
        "type",
    },
)
_TUPLES: Final = frozenset({"tuple", "Tuple"})  # the annotations that list one type per element


def is_composite(value: ast.expr) -> bool:
    """Check whether a value is written as a type made of others: a subscript, or a union.

    What a type alias's assignment binds (`Json = dict[str, "Json"] | str`), but for a bare class's
    (`Alias = Class`).

    Returns:
      Whether it is.

    """
    return isinstance(value, ast.Subscript) or (
        isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr)
    )


def node_name(node: ast.AST) -> str:
    """Read a `Name`'s or `Attribute`'s simple name.

    Returns:
      It, or `""` if `node` is neither.

    """
    name: str
    match node:
        case ast.Name(id=name) | ast.Attribute(attr=name):
            return name
        case _:
            return ""


def dotted(node: ast.expr) -> str | None:
    """Spell a name, or a chain of attributes on one (`pkg.util.f`), as written.

    Returns:
      It, or `None` if `node` is anything else (`f().g`, `x[0].g`).

    """
    name: str
    value: ast.expr
    base: str | None
    match node:
        case ast.Name(id=name):
            return name
        case ast.Attribute(value=value, attr=name) if (base := dotted(value)) is not None:
            return f"{base}.{name}"
        case _:
            return None


def is_vague(annotation: ast.expr) -> bool:
    """Check an annotation for vague types.

    Returns:
      Whether it has `Any`, `object` or a generic without its parameters in it.

    """
    root: ast.expr = parsed(annotation)
    subscripted: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Subscript)}
    node: ast.AST
    for node in ast.walk(root):
        name: str = node_name(node)
        if name in _VAGUE or (name in GENERICS and id(node) not in subscripted):
            return True
    return False


def vague_parts(annotation: ast.expr) -> tuple[int, bool]:
    """Count an annotation's vague parts (see `is_vague`), and say whether one stands alone.

    Alone: the annotation itself or a member of its union (`Any`, `Any | None`, `Optional[object]`),
    where it says nothing at all. Anywhere else it's inside a type that says the rest
    (`tuple[str, Any]`), as a generic without its parameters is (`list`).

    Returns:
      How many there are, and whether one does.

    """
    root: ast.expr = parsed(annotation)
    subscripted: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Subscript)}
    count: int = sum(
        node_name(node) in _VAGUE or (node_name(node) in GENERICS and id(node) not in subscripted)
        for node in ast.walk(root)
    )
    return count, any(node_name(member) in _VAGUE for member in _union_members(root))


def _union_members(node: ast.expr) -> list[ast.expr]:
    """Flatten an annotation's outermost union: `A | B`, `Optional[A]`, `Union[A, B]`.

    Returns:
      Its members; the annotation itself, if it's no union.

    """
    left: ast.expr
    right: ast.expr
    head: ast.expr
    inner: ast.expr
    match node:
        case ast.BinOp(op=ast.BitOr(), left=left, right=right):
            return [*_union_members(left), *_union_members(right)]
        case ast.Subscript(value=head, slice=inner) if node_name(head) in _UNIONS:
            parts: list[ast.expr] = inner.elts if isinstance(inner, ast.Tuple) else [inner]
            return [member for part in parts for member in _union_members(part)]
        case _:
            return [node]


def vague_fits(annotation: ast.expr, level: int) -> bool:
    """Check whether an annotation is no vaguer than `level` allows (`vague`, LVA005's).

    Below 0, no vague part at all. At 0, one, inside a type that says the rest (`tuple[str, Any]`).
    From 1, `level + 1` of them (`tuple[Any, Any]` at 1), and one alone (`Any`).

    Returns:
      Whether it is.

    """
    count: int
    alone: bool
    count, alone = vague_parts(annotation)
    return not count or (count <= level + 1 and (level > 0 or not alone))


def length(annotation: ast.expr) -> int:
    """Measure the longest fixed-length tuple an annotation lists, one type per element.

    `tuple[int, str]` is 2; `tuple[int, ...]` (any length) and anything but a tuple are 0.

    Returns:
      The most elements any `tuple[...]` or `Tuple[...]` in it lists.

    """
    node: ast.AST
    head: ast.expr
    elements: list[ast.expr]
    lengths: list[int] = [0]
    for node in ast.walk(parsed(annotation)):
        match node:
            case ast.Subscript(value=head, slice=ast.Tuple(elts=elements)) if node_name(head) in _TUPLES:
                lengths.append(0 if _variadic(elements) else len(elements))
            case ast.Subscript(value=head) if node_name(head) in _TUPLES:
                lengths.append(1)
            case _:
                pass
    return max(lengths)


def _variadic(elements: list[ast.expr]) -> bool:
    """Check whether a tuple annotation's elements end in `...` (`tuple[int, ...]`: any length).

    Returns:
      Whether they do.

    """
    # `tuple[()]` (the empty tuple) has no elements at all.
    return bool(elements) and isinstance(elements[-1], ast.Constant) and elements[-1].value is Ellipsis


def depth(annotation: ast.expr) -> int:
    """Measure how deeply an annotation's subscripts nest.

    Returns:
      The depth: `dict[str, list[int]]` is 2.

    """
    node: ast.expr = parsed(annotation)
    inner: ast.expr
    parts: list[ast.expr]
    left: ast.expr
    right: ast.expr
    match node:
        case ast.Subscript(slice=inner):
            return 1 + depth(inner)
        case ast.Tuple(elts=parts) | ast.List(elts=parts):
            return max((depth(part) for part in parts), default=0)
        case ast.BinOp(left=left, right=right):
            return max(depth(left), depth(right))
        case _:
            return 0


def free_of(types: Mapping[str, str], type_vars: frozenset[str]) -> dict[str, str]:
    """Drop the types that mention one of `type_vars` (a call's type then depends on its arguments).

    Returns:
      The others.

    """
    return {name: annotation for name, annotation in types.items() if not type_vars & set(words(annotation))}


def free_of_all(
    tables: Mapping[str, Mapping[str, str]],
    type_vars: frozenset[str],
) -> dict[str, dict[str, str]]:
    """Drop each class's member types that mention one of `type_vars` (see `free_of`).

    Returns:
      The others, per class.

    """
    return {owner: free_of(types, type_vars) for owner, types in tables.items()}


def words(annotation: str) -> list[str]:
    """Split an annotation into the words it's written with (`dict[str, Row]`: `dict`, `str`, `Row`).

    Returns:
      Them, in order.

    """
    return [word for word in re.split(r"\W+", annotation) if word]


@lru_cache(maxsize=4096)  # asked of each fix's annotation several times: a few thousand distinct
def roots(annotation: str) -> frozenset[str]:
    """Find the names an annotation (maybe a string one) is written with.

    Returns:
      The names: `m.Row` gives `m`; none for a string that isn't an expression.

    """
    tree: ast.expr = parsed(ast.parse(annotation, mode="eval").body)
    return frozenset(node.id for node in ast.walk(tree) if isinstance(node, ast.Name))
