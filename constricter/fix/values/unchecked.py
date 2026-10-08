# SPDX-License-Identifier: MIT
"""Where a guess, once declared, makes an error of what its function goes on to do with the name.

A type checker takes a call of an unannotated function for anything, and checks nothing done with
its value; declared, the value is held to its type. So a guess isn't offered where the function
then takes an attribute its class hasn't (`cfg.verbose`, of a class whose attributes are set from
outside it), nor a union's where it takes an attribute or an item of the name that no test narrows
(`opt.cb`, of an `Option | None`).
"""

import ast
from collections.abc import Mapping, Sequence
from functools import lru_cache
from typing import Final, TypeAlias

from constricter.fix.values.narrowed import Regions, read_narrowed, tested_lines
from constricter.rules.syntax import FunctionDef
from constricter.rules.walked import classes, walk

# A use of a name: its line, and the attribute taken of it (none: an item).
Use: TypeAlias = tuple[int, str]
_DUNDER: Final = "__"
# What gives a class attributes its body doesn't name.
_DYNAMIC: Final = frozenset({"__getattr__", "__getattribute__", "setattr", "__dict__", "vars"})
_OBJECT: Final = "object"


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
