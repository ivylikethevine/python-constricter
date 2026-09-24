# SPDX-License-Identifier: MIT
"""`--fix` for an empty container filled later: `x = []`, then only `x.append(v)`, is `list[T]`.

A guess (`--unsafe-fixes`): only this function's own uses are seen, and something else could still
add to it. So every use of the name must be one of a few that can't: a fill whose value's type is
known (`append`, `insert`, `add`, `setdefault`, `x[k] = v`), a read (`x[k]`, `x.get(k)`, iterating it,
`len(x)`, `", ".join(x)`, returning it), or one that only shrinks or reorders it (`pop`, `sort`,
`clear`). Anything else (`extend`, `update`, passing it to another function, aliasing it, a nested
function that sees it) leaves it alone.
"""

import ast
from collections.abc import Mapping, Sequence
from typing import Final, NamedTuple

from constricter.fix.inference import inference
from constricter.fix.known import Inference, Known
from constricter.rules.syntax import NESTED_SCOPES, own_nodes
from constricter.rules.walked import walk

_LIST: Final = "list"
_DICT: Final = "dict"
_SET: Final = "set"
# What adds an element, by container: the method, and which argument is the element (the key, for a
# `dict`, is argument 0).
_ADDERS: Final = {
    _LIST: {"append": 0, "insert": 1},
    _SET: {"add": 0},
    _DICT: {"setdefault": 1},
}
# Methods that only read, shrink or reorder.
_READERS: Final = frozenset(
    {"pop", "get", "items", "keys", "values", "copy", "sort", "reverse", "clear", "count", "index"}
    | {"remove", "discard", "popitem"},
)
# Builtins a container can be passed to without being changed.
_PURE: Final = frozenset(
    {"len", "sorted", "list", "tuple", "set", "frozenset", "enumerate", "reversed", "any", "all"}
    | {"sum", "min", "max", "zip", "iter", "bool", "str", "repr", "dict"},
)
_JOIN: Final = "join"


class _Fill(NamedTuple):
    """One element added: its key (a `dict`'s), and its value."""

    key: ast.expr | None
    value: ast.expr


def empty(value: ast.expr) -> str | None:
    """Recognise an empty container: `[]`, `{}`, `list()`, `dict()`, `set()`.

    Returns:
      Its kind (`list`, `dict`, `set`), or `None` for anything else.

    """
    name: str
    match value:
        case ast.List(elts=[]):
            return _LIST
        case ast.Dict(keys=[]):
            return _DICT
        case ast.Call(func=ast.Name(id=name), args=[], keywords=[]) if name in {_LIST, _DICT, _SET}:
            return name
        case _:
            return None


class Uses(NamedTuple):
    """A function body's names as `filled` judges them, read once for all its empty containers.

    `names`: each name's uses (not its bindings) outside nested scopes; `parents`: each node's parent,
    by `id()`; `nested`: every name a nested function, lambda or class uses.
    """

    names: Mapping[str, list[ast.Name]]
    parents: Mapping[int, ast.AST]
    nested: frozenset[str]


def uses(body: Sequence[ast.stmt]) -> Uses:
    """Read a function body's names for `filled`.

    Returns:
      Them.

    """
    names: dict[str, list[ast.Name]] = {}
    parents: dict[int, ast.AST] = {}
    nested: set[str] = set()
    node: ast.AST
    for node in own_nodes(body, parents):
        if isinstance(node, NESTED_SCOPES):
            nested.update(inner.id for inner in walk(node) if isinstance(inner, ast.Name))
        elif isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Store):
            names.setdefault(node.id, []).append(node)
    return Uses(names, parents, frozenset(nested))


def filled(
    found: Uses,
    name: str,
    kind: str,
    known: Known,
    declared: Mapping[str, str],
) -> Inference | None:
    """Type an empty container `name` of `kind` from what its function's body (`found`) adds to it.

    Returns:
      `list[T]`, `set[T]` or `dict[K, V]`, or `None` if a use could add something unseen (a nested
      scope sees it, out of this function's sight), nothing is added, or what's added isn't typed
      alike.

    """
    if name in found.nested:
        return None
    fills: list[_Fill] = []
    node: ast.Name
    for node in found.names.get(name, []):
        fill: _Fill | bool
        if (fill := _use(node, kind, found.parents)) is False:
            return None
        if isinstance(fill, _Fill):
            fills.append(fill)
    return _typed(fills, kind, known, declared) if fills else None


def _use(node: ast.Name, kind: str, parents: Mapping[int, ast.AST]) -> _Fill | bool:
    """Judge one read of the container.

    Returns:
      A fill (what it adds), `True` for a use that adds nothing, `False` for one that might add
      something unseen.

    """
    parent: ast.AST | None = parents.get(id(node))
    grandparent: ast.AST | None = None if parent is None else parents.get(id(parent))
    attr: str
    match parent:
        case ast.Attribute(attr=attr) if isinstance(grandparent, ast.Call) and grandparent.func is parent:
            return _method(attr, grandparent, kind)
        case ast.Subscript(ctx=ast.Store()):
            return _stored(parent, grandparent, kind)
        case _:
            return _reads(parent)


def _reads(parent: ast.AST | None) -> bool:
    """Judge a use by the node it's in: one that can't add to the container.

    Returns:
      Whether it only reads it: indexed, compared, returned, iterated, tested, formatted, or passed to
      a builtin that doesn't change it (`len`, `sorted`, ...) or to `str.join`.

    """
    func: str
    attr: str
    match parent:
        case ast.Subscript() | ast.Compare() | ast.Return() | ast.For() | ast.comprehension():
            return True
        case (
            ast.If()
            | ast.While()
            | ast.IfExp()
            | ast.BoolOp()
            | ast.UnaryOp(op=ast.Not())
            | ast.FormattedValue()
        ):
            return True
        case ast.Call(func=ast.Name(id=func)):
            return func in _PURE
        case ast.Call(func=ast.Attribute(value=ast.Constant(value=str()), attr=attr)):
            return attr == _JOIN
        case _:
            return False


def _method(attr: str, call: ast.Call, kind: str) -> _Fill | bool:
    """Judge a method called on the container.

    Returns:
      A fill for an adder (with the arguments it needs), `True` for a reader, else `False`.

    """
    position: int | None = _ADDERS[kind].get(attr)
    if position is not None and not call.keywords and len(call.args) == position + 1:
        return _Fill(call.args[0] if kind == _DICT else None, call.args[position])
    return attr in _READERS


def _stored(target: ast.Subscript, statement: ast.AST | None, kind: str) -> _Fill | bool:
    """Judge `x[k] = v`: a `dict`'s fill (key and value), a `list`'s element replaced.

    Returns:
      The fill, or `False` for any other store (`x[k] += v`, `x[1:2] = ...`, a set's).

    """
    if (
        isinstance(statement, ast.Assign)
        and statement.targets == [target]
        and kind != _SET
        and not isinstance(target.slice, ast.Slice)
    ):
        return _Fill(target.slice if kind == _DICT else None, statement.value)
    return False


def _typed(fills: Sequence[_Fill], kind: str, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Type the container from its fills, if they agree.

    Returns:
      The inference, or `None` if a key or value isn't typed, or they differ.

    """
    values: list[Inference | None] = [inference(fill.value, known, declared) for fill in fills]
    keys: list[Inference | None] = [
        inference(fill.key, known, declared) for fill in fills if fill.key is not None
    ]
    parts: list[Inference] = [part for part in (*values, *keys) if part is not None]
    value_types: set[str | None] = {None if part is None else part.annotation for part in values}
    key_types: set[str | None] = {None if part is None else part.annotation for part in keys}
    if len(parts) != len(values) + len(keys) or len(value_types) != 1 or len(key_types) > 1:
        return None
    value: str = str(next(iter(value_types)))
    annotation: str = f"dict[{next(iter(key_types))}, {value}]" if kind == _DICT else f"{kind}[{value}]"
    reason: str = f"what the function adds to it ({len(fills)} {'fill' if len(fills) == 1 else 'fills'})"
    return Inference(annotation, reason, frozenset({"filled"}).union(*(part.kinds for part in parts)))
