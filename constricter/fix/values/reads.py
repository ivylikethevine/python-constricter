"""Unannotated parameters typed by what a function reads of them: the one class with every member read.

Where the members a function reads of a parameter (`p.x`, `p.m()`: two names or more, no dunder)
are all members of exactly one class the module defines at its top level or imports from another
checked file (see `members`), or of one it defines and others inheriting from it, and not all of
any builtin type's nor any class's the standard-library tables hold, the parameter is that class's
instance. A guess (`reads`): another module's class, or an installed package's, may have them too.
Not for a parameter the function probes (`isinstance(p, ...)`, `hasattr(p, ...)`): it expects more
than one type.
"""

import ast
import builtins
from collections.abc import Iterable, Mapping, Sequence
from typing import Final, NamedTuple, cast

from constricter.fix.core.known import Classes
from constricter.fix.libraries import stdlib

KIND: Final = "reads"  # the guessing mechanism (`FIX_KINDS`)
_LEAST: Final = 2  # names read: one alone (`p.name`) fits too many classes
_PROBES: Final = frozenset({"isinstance", "hasattr", "getattr", "type"})
_DUNDER: Final = "__"
# Each builtin type's members, as the running Python has them.
_BUILTIN_MEMBERS: Final = tuple(
    frozenset(dir(kind))
    for kind in cast("Iterable[object]", vars(builtins).values())
    if isinstance(kind, type)
)


class Members(NamedTuple):
    """A class's members (see `members`), and the module's classes it inherits from."""

    names: frozenset[str]
    ancestors: frozenset[str]


def members(
    tree: ast.Module,
    imported: Classes | None = None,
    same: Iterable[frozenset[str]] = (),
) -> dict[str, Members]:
    """Name the members of each class `tree` defines once at its top level, and of those it imports.

    A class's own: what its body binds (methods, variables, nested classes), what its methods assign
    to their first parameter's attributes (`self.x = ...`), and the same of its bases the module
    defines. `imported`: the typed members of the classes it imports from other checked files, as it
    spells each (see `Classes`), each by one spelling of those `same` groups (the shortest).

    Returns:
      Each class's members, by its name as the module spells it.

    """
    found: dict[str, Members] = {} if imported is None else _imported(imported, same)
    defined: dict[str, list[ast.ClassDef]] = {}
    stmt: ast.stmt
    for stmt in tree.body:
        if isinstance(stmt, ast.ClassDef):
            defined.setdefault(stmt.name, []).append(stmt)
    own: dict[str, ast.ClassDef] = {name: nodes[0] for name, nodes in defined.items() if len(nodes) == 1}
    name: str
    for name in own:
        seen: set[str] = set()
        names: set[str] = _inherited(name, own, seen)
        found[name] = Members(frozenset(names), frozenset(seen - {name}))
    return found


def _imported(imported: Classes, same: Iterable[frozenset[str]]) -> dict[str, Members]:
    """Name the typed members of each class the module imports, by one of its spellings alone.

    Returns:
      Each one's, by that spelling.

    """
    spelled: set[str] = imported.attributes.keys() | imported.methods.keys()
    group: frozenset[str]
    for group in same:
        present: list[str] = sorted(group & spelled, key=lambda name: (len(name), name))
        spelled.difference_update(present[1:])
    return {
        name: Members(
            frozenset(imported.attributes.get(name, {})) | frozenset(imported.methods.get(name, {})),
            frozenset(),
        )
        for name in spelled
    }


def _inherited(name: str, own: Mapping[str, ast.ClassDef], seen: set[str]) -> set[str]:
    """Name the members of the class `own` has as `name`, with those of its bases `own` has too.

    Returns:
      Them; nothing for a class `seen` already (a cycle of bases).

    """
    if name in seen:
        return set()
    seen.add(name)
    node: ast.ClassDef = own[name]
    found: set[str] = _own(node)
    base: ast.expr
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in own:
            found |= _inherited(base.id, own, seen)
    return found


def _own(node: ast.ClassDef) -> set[str]:
    """Name what a class's own body binds, and what its methods assign to `self`'s attributes.

    Returns:
      Them.

    """
    found: set[str] = set()
    stmt: ast.stmt
    for stmt in node.body:
        name: str
        targets: list[ast.expr]
        match stmt:
            case ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name) | ast.ClassDef(name=name):
                found.add(name)
                if not isinstance(stmt, ast.ClassDef):
                    found |= _assigned(stmt)
            case ast.Assign(targets=targets):
                found.update(target.id for target in targets if isinstance(target, ast.Name))
            case ast.AnnAssign(target=ast.Name(id=name)):
                found.add(name)
            case _:
                pass
    return found


def _assigned(method: ast.FunctionDef | ast.AsyncFunctionDef) -> set[str]:
    """Name the attributes a method assigns to its first parameter (`self.x = ...`).

    Returns:
      Them.

    """
    named: list[ast.arg]
    if not (named := [*method.args.posonlyargs, *method.args.args]):
        return set()
    first: str = named[0].arg
    return {
        node.attr
        for node in ast.walk(method)
        if isinstance(node, ast.Attribute)
        and isinstance(node.ctx, ast.Store)
        and isinstance(node.value, ast.Name)
        and node.value.id == first
    }


def typed(
    nodes: Iterable[ast.AST],
    names: Sequence[str],
    classes: Mapping[str, Members],
) -> dict[str, str]:
    """Type each parameter of `names` by what `nodes` (a function's own) read of it (see the docstring).

    `classes`: the module's classes' members (see `members`).

    Returns:
      Each typed parameter's class, by its name.

    """
    read: dict[str, set[str]] = {name: set() for name in names}
    probed: set[str] = set()
    node: ast.AST
    for node in nodes:
        name: str
        attr: str
        probe: str
        match node:
            case ast.Attribute(value=ast.Name(id=name), attr=attr) if name in read and not attr.startswith(
                _DUNDER,
            ):
                read[name].add(attr)
            case ast.Call(func=ast.Name(id=probe), args=[ast.Name(id=name), *_]) if probe in _PROBES:
                probed.add(name)
            case _:
                pass
    found: dict[str, str] = {}
    each: set[str]
    for name, each in read.items():
        matched: list[str] = (
            []
            if len(each) < _LEAST or name in probed
            else [c for c, has in classes.items() if each <= has.names]
        )
        # The one every other inherits from: a cycle of bases has none.
        root: list[str] = [
            c for c in matched if all(other == c or c in classes[other].ancestors for other in matched)
        ]
        if len(root) == 1 and not _elsewhere(each):
            found[name] = root[0]
    return found


def _elsewhere(read: set[str]) -> bool:
    """Check whether a builtin type or a class the standard-library tables hold has every name of `read`.

    Returns:
      Whether one does.

    """
    if any(read <= has for has in _BUILTIN_MEMBERS):
        return True
    having: Mapping[str, frozenset[str]] = stdlib.member_classes()
    shared: frozenset[str] | None = None
    name: str
    for name in read:
        shared = having.get(name, frozenset()) if shared is None else shared & having.get(name, frozenset())
        if not shared:
            return False
    return True
