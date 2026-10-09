# SPDX-License-Identifier: MIT
"""Where a guess, once declared, makes an error of what its function goes on to do with the name.

A type checker takes a call of an unannotated function for anything, and checks nothing done with
its value; declared, the value is held to its type. So a guess isn't offered where the function
then takes an attribute its class hasn't (`cfg.verbose`, of a class whose attributes are set from
outside it), nor a union's where it takes an attribute or an item of the name that no test narrows
(`opt.cb`, of an `Option | None`). Nor where it uses a comparison of the name as more than a `bool`
(`(when == index).any()`: the class compares element by element, whatever its stubs say), formats a
`bytes` into a string (`f"{raw}"`, which mypy reports), or stores the name, or an item of it, in an
attribute it stores something else in too (the attribute then has the name's type).
"""

import ast
from collections.abc import Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.values.narrowed import Regions, read_narrowed, tested_lines
from constricter.rules.syntax import FunctionDef
from constricter.rules.walked import classes, walk

# A use of a name: its line, and the attribute taken of it (none: an item).
Use: TypeAlias = tuple[int, str]
_DUNDER: Final = "__"
# What gives a class attributes its body doesn't name.
_DYNAMIC: Final = frozenset({"__getattr__", "__getattribute__", "setattr", "__dict__", "vars"})
_OBJECT: Final = "object"
_BYTES: Final = "bytes"
_FORMAT: Final = "format"
_BITWISE: Final = (ast.BitAnd, ast.BitOr, ast.BitXor)


@lru_cache(maxsize=64)  # asked of each of a function's guesses
def uses(function: FunctionDef) -> Mapping[str, tuple[Use, ...]]:
    """Find where a function takes an attribute or an item of a name: `x.attr`, `x[0]`.

    Returns:
      Each such name's uses, the functions' inside it too.

    """
    found: dict[str, list[Use]] = {}
    node: ast.AST
    name: str
    attr: str
    for node in walk(function):
        match node:
            case ast.Attribute(value=ast.Name(id=name), attr=attr):
                found.setdefault(name, []).append((node.value.lineno, attr))
            case ast.Subscript(value=ast.Name(id=name)):
                found.setdefault(name, []).append((node.value.lineno, ""))
            case _:
                pass
    return {name: tuple(taken) for name, taken in found.items()}


def unnarrowed(function: FunctionDef, name: str, regions: Regions) -> bool:
    """Check whether a function takes an attribute or an item of `name` where no test narrows it.

    Returns:
      Whether it does: an error, for a name declared a union.

    """
    tested: frozenset[int] = tested_lines(function).get(name, frozenset())
    return any(
        line not in tested and not read_narrowed(regions, name, line, union=True)
        for line, _ in uses(function).get(name, ())
    )


def misused(function: FunctionDef, name: str, annotation: str) -> bool:
    """Check whether a function does with `name` what its type `annotation` makes an error of.

    See `_compared`, `_formatted` and `_restored`.

    Returns:
      Whether it does.

    """
    found: _Misuses = _misuses(function)
    return name in found.compared | found.restored or (annotation == _BYTES and name in found.formatted)


class _Misuses(NamedTuple):
    """The names a function compares, formats and stores as `misused` has it."""

    compared: frozenset[str]
    formatted: frozenset[str]
    restored: frozenset[str]


@lru_cache(maxsize=64)  # asked of each of a function's guesses
def _misuses(function: FunctionDef) -> _Misuses:
    compared: set[str] = set()
    formatted: set[str] = set()
    stored: dict[str, list[str]] = {}
    target: ast.Attribute
    value: ast.expr
    node: ast.AST
    for node in walk(function):
        compared.update(_compared(node))
        formatted.update(_formatted(node))
        match node:
            case ast.Assign(targets=[ast.Attribute() as target], value=value):
                stored.setdefault(ast.unparse(target), []).append(_held(value))
            case _:
                pass
    restored: set[str] = {name for names in stored.values() if len(set(names)) > 1 for name in names if name}
    return _Misuses(frozenset(compared), frozenset(formatted), frozenset(restored))


def _held(value: ast.expr) -> str:  # the name a stored value is, or is an item of; else nothing
    name: str
    match value:
        case ast.Name(id=name) | ast.Subscript(value=ast.Name(id=name)):
            return name
        case _:
            return ""


def _compared(node: ast.AST) -> Iterator[str]:
    """Name what `node` compares, where it uses the comparison as more than a `bool`.

    An attribute or an item of it (`(a == b).any()`), or an operand of `&`, `|`, `^` or `~`.

    Yields:
      Each name compared.

    """
    used: list[ast.expr] = []
    inner: ast.expr
    left: ast.expr
    right: ast.expr
    op: ast.operator
    match node:
        case ast.Attribute(value=ast.Compare() as inner) | ast.Subscript(value=ast.Compare() as inner):
            used.append(inner)
        case ast.UnaryOp(op=ast.Invert(), operand=ast.Compare() as inner):
            used.append(inner)
        case ast.BinOp(left=left, op=op, right=right) if isinstance(op, _BITWISE):
            used += [left, right]
        case _:
            pass
    side: ast.expr
    for inner in used:
        if isinstance(inner, ast.Compare):
            for side in (inner.left, *inner.comparators):
                if isinstance(side, ast.Name):
                    yield side.id


def _formatted(node: ast.AST) -> Iterator[str]:
    """Name what `node` formats into a string as `str()` would: `f"{x}"`, `"{}".format(x)`, `"%s" % x`.

    Yields:
      Each name; not one an f-string converts itself (`f"{x!r}"`).

    """
    given: list[ast.expr] = []
    value: ast.expr
    attr: str
    args: list[ast.expr]
    match node:
        case ast.FormattedValue(value=value, conversion=-1):
            given.append(value)
        case ast.Call(func=ast.Attribute(value=ast.Constant(value=str()), attr=attr), args=args) if (
            attr == _FORMAT
        ):
            given += args
        case ast.BinOp(left=ast.Constant(value=str()), op=ast.Mod(), right=ast.Tuple(elts=args)):
            given += args
        case ast.BinOp(left=ast.Constant(value=str()), op=ast.Mod(), right=value):
            given.append(value)
        case _:
            pass
    for value in given:
        if isinstance(value, ast.Name):
            yield value.id


def lacks(tree: ast.Module, function: FunctionDef, name: str, annotation: str) -> bool:
    """Check whether a function takes an attribute of `name` that the class `annotation` names hasn't.

    Returns:
      Whether it does: `annotation` is one of the module's classes whose every attribute its own
      body, and its bases', name (see `closed`), and one the function takes isn't among them.

    """
    known: frozenset[str] | None = closed(tree).get(annotation)
    return known is not None and any(
        attr and not attr.startswith(_DUNDER) and attr not in known
        for _, attr in uses(function).get(name, ())
    )


@lru_cache(maxsize=4)  # asked of the same module's functions
def closed(tree: ast.Module) -> Mapping[str, frozenset[str]]:
    """Find the module's classes whose attributes are all in sight, and name them.

    A class defined once, undecorated, with no base but others such, that neither answers for
    attributes it doesn't name (`__getattr__`) nor sets them by name (`setattr`). Its attributes:
    every name, attribute and string its body has, so what it binds, its `__slots__`, and what its
    methods store (`self.x = ...`).

    Returns:
      Each such class's attributes, its bases' too.

    """
    defined: dict[str, list[ast.ClassDef]] = {}
    node: ast.ClassDef
    for node in classes(tree):
        defined.setdefault(node.name, []).append(node)
    found: dict[str, frozenset[str]] = {}
    name: str
    for name in defined:
        _ = _close(name, defined, found, frozenset())
    return found


def _close(
    name: str,
    defined: Mapping[str, Sequence[ast.ClassDef]],
    found: dict[str, frozenset[str]],
    under: frozenset[str],
) -> frozenset[str] | None:
    """Name the attributes of the class `name`, if they're all in sight (see `closed`), into `found`.

    `under`: the classes whose bases are being read, which a class can't be its own base through.

    Returns:
      Them, or `None`.

    """
    if name in found:
        return found[name]
    nodes: Sequence[ast.ClassDef] = defined.get(name, ())
    if len(nodes) != 1 or name in under or nodes[0].decorator_list or nodes[0].keywords:
        return None
    attributes: set[str] | None = _attributes(nodes[0])
    base: ast.expr
    for base in nodes[0].bases:
        inherited: frozenset[str] | None = (
            frozenset()
            if isinstance(base, ast.Name) and base.id == _OBJECT
            else _close(base.id, defined, found, under | {name})
            if isinstance(base, ast.Name)
            else None
        )
        if attributes is None or inherited is None:
            return None
        attributes |= inherited
    if attributes is None:
        return None
    found[name] = frozenset(attributes)
    return found[name]


def _attributes(node: ast.ClassDef) -> set[str] | None:
    """Name what a class's own body gives its instances.

    Returns:
      Each attribute, or `None` if something in it may give others (see `_DYNAMIC`).

    """
    found: set[str] = set()
    inner: ast.AST
    for inner in walk(node):
        if isinstance(inner, ast.Name):
            found.add(inner.id)
        elif isinstance(inner, ast.Attribute):
            found.add(inner.attr)
        elif isinstance(inner, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            found.add(inner.name)
        elif isinstance(inner, ast.alias):
            found.add((inner.asname or inner.name).split(".")[0])
        elif isinstance(inner, ast.Constant) and isinstance(inner.value, str):
            found.add(inner.value)  # one of its `__slots__`
    return None if found & _DYNAMIC else found
