# SPDX-License-Identifier: MIT
"""`--fix` for an empty container filled later: `x = []`, then only `x.append(v)`, is `list[T]`.

A guess (`--unsafe-fixes`): only this function's own uses are seen, and something else could still
add to it. So every use of the name must be one of a few that can't: a fill whose value's type is
known (`append`, `insert`, `add`, `setdefault`, `x[k] = v`; `extend` and `update`, by their one
argument's elements), a read (`x[k]`, `x.get(k)`, iterating it, `len(x)`, `", ".join(x)`,
`x + more`, `[*x]`, returning it, alone or in a tuple), one that only shrinks or reorders it
(`pop`, `sort`, `clear`), or a local bound to it (`alias = x`) whose own uses all only read it.
Anything else (passing it to another function, a nested function that sees it) leaves it alone.

An instance attribute bound to one (`self.items = []`) is judged the same way, each read of it in its
class's methods a use (`stored`): `constricter.fix.values.returned` types it from them all.
"""

import ast
from collections.abc import Iterator, Mapping, Sequence
from typing import Final, NamedTuple

from constricter.fix.core.known import Inference, Known
from constricter.fix.values.inference import inference, looped
from constricter.fix.values.targets import dict_parts
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
# What adds every element of its one argument, by container (a `dict`'s: another's entries).
_SPREADERS: Final = {_LIST: "extend", _SET: "update", _DICT: "update"}
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


class Fill(NamedTuple):
    """One addition: its key (a `dict`'s), and its value.

    `spread`: the value isn't what's added, but holds it: its elements (`extend`), or a `dict`'s
    entries (`update`).
    """

    key: ast.expr | None
    value: ast.expr
    spread: bool = False


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
    fills: list[Fill] = []
    node: ast.Name
    for node in found.names.get(name, []):
        fill: Fill | bool
        if (fill := _use(node, kind, found.parents)) is False and not _only_read(node, kind, found):
            return None
        if isinstance(fill, Fill):
            fills.append(fill)
    return _typed(fills, kind, known, declared) if fills else None


def added_names(found: Uses, name: str, kind: str) -> frozenset[str]:
    """Name what the body (`found`) adds to container `name` that is a bare name: `d`, in `xs.append(d)`.

    Where the function tests one (`isinstance(d, C)`), what's added is narrowed there: its
    declared type isn't the elements'.

    Returns:
      The names.

    """
    fills: list[Fill] = [
        fill
        for fill in (_use(node, kind, found.parents) for node in found.names.get(name, []))
        if isinstance(fill, Fill) and not fill.spread
    ]
    return frozenset(
        part.id for fill in fills for part in (fill.key, fill.value) if isinstance(part, ast.Name)
    )


def stored(body: Sequence[ast.stmt], kinds: Mapping[str, str]) -> Iterator[tuple[str, Fill | bool]]:
    """Judge each read of `self`'s attributes bound to an empty container, in one method's body.

    `kinds`: each such attribute's kind. A nested function's or lambda's reads aren't judged.

    Yields:
      The attribute, and its use as `filled` judges a name's: a fill, `True` for one that adds
      nothing, `False` for one that might add something unseen.

    """
    parents: dict[int, ast.AST] = {}
    found: Uses | None = None  # read only for an attribute a local is bound to
    node: ast.AST
    attr: str
    for node in own_nodes(body, parents):
        match node:
            case ast.Attribute(value=ast.Name(id="self"), attr=attr, ctx=ast.Load()) if attr in kinds:
                use: Fill | bool = _use(node, kinds[attr], parents)
                if use is False and isinstance(parents.get(id(node)), ast.Assign):
                    found = found or uses(body)
                    use = _only_read(node, kinds[attr], found._replace(parents={**found.parents, **parents}))
                yield attr, use
            case _:
                pass


def _only_read(node: ast.expr, kind: str, found: Uses) -> bool:
    """Check whether a read binding the container to a local (`alias = x`) adds nothing to it.

    Returns:
      Whether every use of that local, in no nested scope, only reads it.

    """
    name: str
    value: ast.expr
    match found.parents.get(id(node)):
        case ast.Assign(targets=[ast.Name(id=name)], value=value) if (
            value is node and name not in found.nested
        ):
            return all(_use(use, kind, found.parents) is True for use in found.names.get(name, []))
        case _:
            return False


def _use(node: ast.expr, kind: str, parents: Mapping[int, ast.AST]) -> Fill | bool:
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
            return _reads(parent, grandparent)


def _reads(parent: ast.AST | None, grandparent: ast.AST | None) -> bool:
    """Judge a use by the node it's in (and the one that's in): one that can't add to the container.

    Returns:
      Whether it only reads it: indexed, compared, returned (in a tuple too), iterated, tested,
      formatted, an operand (`x + more`), unpacked (`[*x]`), or passed to a builtin that doesn't
      change it (`len`, `sorted`, ...) or to a `join`.

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
            | ast.BinOp()
            | ast.Starred()
            | ast.YieldFrom()
        ):
            return True
        case ast.Call(func=ast.Name(id=func)):
            return func in _PURE
        case ast.Call(func=ast.Attribute(attr=attr)):
            return attr == _JOIN
        case ast.Tuple():
            return isinstance(grandparent, ast.Return)
        case _:
            return False


def _method(attr: str, call: ast.Call, kind: str) -> Fill | bool:
    """Judge a method called on the container.

    Returns:
      A fill for an adder or a spreader (with the arguments it needs), `True` for a reader, else
      `False`.

    """
    position: int | None = _ADDERS[kind].get(attr)
    if position is not None and not call.keywords and len(call.args) == position + 1:
        return Fill(call.args[0] if kind == _DICT else None, call.args[position])
    if attr == _SPREADERS[kind] and not call.keywords and len(call.args) == 1:
        return Fill(None, call.args[0], spread=True)
    return attr in _READERS


def _stored(target: ast.Subscript, statement: ast.AST | None, kind: str) -> Fill | bool:
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
        return Fill(target.slice if kind == _DICT else None, statement.value)
    return False


def _typed(fills: Sequence[Fill], kind: str, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Type the container from its fills, if they agree.

    Returns:
      The inference, or `None` if a key or value isn't typed, or they differ.

    """
    each: list[list[Inference | None]] = [added(fill, kind, known, declared) for fill in fills]
    rows: list[list[Inference]] = [[part for part in row if part is not None] for row in each]
    if [len(row) for row in rows] != [len(row) for row in each]:
        return None
    parts: list[Inference] = [part for row in rows for part in row]
    # A `dict`'s keys, then its values; any other container's elements.
    types: list[set[str]] = [{row[at].annotation for row in rows} for at in range(len(rows[0]))]
    if any(len(found) != 1 for found in types):
        return None
    annotation: str = f"{kind}[{', '.join(next(iter(found)) for found in types)}]"
    reason: str = f"what the function adds to it ({len(fills)} {'fill' if len(fills) == 1 else 'fills'})"
    return Inference(annotation, reason, frozenset({"filled"}).union(*(part.kinds for part in parts)))


def added(fill: Fill, kind: str, known: Known, declared: Mapping[str, str]) -> list[Inference | None]:
    """Type what one fill adds: a `dict`'s key and value, any other container's element.

    Returns:
      Each one's inference (`None`: unknown).

    """
    if not fill.spread:
        return [inference(part, known, declared) for part in (fill.key, fill.value) if part is not None]
    if kind != _DICT:
        return [looped(fill.value, known, declared)]
    found: Inference | None = inference(fill.value, known, declared)
    types: tuple[str, str] | None = None if found is None else dict_parts(found.annotation)
    if found is None or types is None:
        return [None, None]
    return [found._replace(annotation=types[0]), found._replace(annotation=types[1])]
