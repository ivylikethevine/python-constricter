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
from collections.abc import Iterable, Iterator, Mapping, Sequence
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.known import Classes
from constricter.fix.libraries import stdlib
from constricter.overrides import override
from constricter.source.syntax import FunctionDef, Start, within
from constricter.source.walked import of_type

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
# Where a module takes a name's attributes, in source order, and each attribute's name.
_Spans: TypeAlias = tuple[list[Start], list[str]]
_Taken: TypeAlias = tuple[Start, str]  # where one attribute is taken, and its name


class Members(NamedTuple):
    """A class's members (see `members`), and the module's classes it inherits from."""

    names: frozenset[str]
    ancestors: frozenset[str]


class Read(Mapping[str, Members]):
    """The members of a module's classes (see `members`), each class's worked out when it's first asked for.

    Only a function reading two names or more of a parameter asks (see `readable`): most modules
    have none. The attributes the module takes are kept to tell which, and to find what its methods
    assign to their first parameter's without walking them.
    """

    def __init__(
        self,
        imported: dict[str, Members],
        own: dict[str, ast.ClassDef],
        attributes: Sequence[ast.Attribute],
    ) -> None:
        """Keep the imported classes' members, the module's own classes, and every attribute it takes."""
        self.imported: dict[str, Members] = imported
        self.own: dict[str, ast.ClassDef] = own
        self.attributes: Sequence[ast.Attribute] = attributes
        self.names: tuple[str, ...] = tuple(dict.fromkeys([*imported, *own]))
        self.worked: dict[str, Members] = {}
        self.read: dict[str, _Spans] | None = None
        self.stored: dict[str, _Spans] | None = None

    @override
    def __getitem__(self, key: str) -> Members:
        """Find a class's members, as `members` names them.

        Returns:
          They; a `KeyError` for a class the module has none of.

        """
        if key not in self.own:
            return self.imported[key]
        found: Members | None
        if (found := self.worked.get(key)) is None:
            if self.stored is None:
                self.stored = _by_name(self.attributes, stored=True)
            seen: set[str] = set()
            names: set[str] = _inherited(key, self.own, seen, self.stored)
            found = self.worked[key] = Members(frozenset(names), frozenset(seen - {key}))
        return found

    @override
    def __iter__(self) -> Iterator[str]:
        """Name the classes.

        Returns:
          An iterator of their names.

        """
        return iter(self.names)

    @override
    def __len__(self) -> int:
        """Count the classes.

        Returns:
          How many.

        """
        return len(self.names)

    def readable(self, function: FunctionDef, names: Iterable[str]) -> frozenset[str]:
        """Name those of `names` the module reads two names or more of within `function`'s span.

        Its nested functions' reads count too: no fewer than its own nodes read (see `typed`).

        Returns:
          Them.

        """
        if self.read is None:
            self.read = _by_name(self.attributes, stored=False)
        found: set[str] = set()
        name: str
        for name in names:
            spans: _Spans | None
            if (spans := self.read.get(name)) is not None and len(
                set(spans[1][within(spans[0], function)]),
            ) >= _LEAST:
                found.add(name)
        return frozenset(found)


def members(
    tree: ast.Module,
    imported: Classes | None = None,
    same: Iterable[frozenset[str]] = (),
) -> Read:
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
    # A module with no class types no parameter: its attributes needn't be kept.
    attributes: Sequence[ast.AST] = of_type(tree, ast.Attribute) if found or own else ()
    return Read(found, own, cast("Sequence[ast.Attribute]", attributes))


def readable(classes: Mapping[str, Members], function: FunctionDef, names: Iterable[str]) -> frozenset[str]:
    """Name those of `names` that `typed` may type in `function`: each it reads two names or more of.

    `classes`: the module's (see `members`); where they don't say what it reads, each of `names`.

    Returns:
      Them; none where the module has no class.

    """
    if not classes:
        return frozenset()
    return classes.readable(function, names) if isinstance(classes, Read) else frozenset(names)


def _by_name(attributes: Iterable[ast.Attribute], *, stored: bool) -> dict[str, _Spans]:
    """Find where the module takes each name's attributes (`p.x`): any but a dunder, or those it assigns.

    Returns:
      Each name's, in source order: where each starts, and its name.

    """
    found: dict[str, list[_Taken]] = {}
    node: ast.Attribute
    for node in attributes:
        if isinstance(node.value, ast.Name) and (
            isinstance(node.ctx, ast.Store) if stored else not node.attr.startswith(_DUNDER)
        ):
            found.setdefault(node.value.id, []).append(((node.lineno, node.col_offset), node.attr))
    spans: dict[str, _Spans] = {}
    name: str
    each: list[_Taken]
    for name, each in found.items():
        each.sort()
        spans[name] = ([start for start, _ in each], [attr for _, attr in each])
    return spans


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


def _inherited(
    name: str,
    own: Mapping[str, ast.ClassDef],
    seen: set[str],
    stored: Mapping[str, _Spans],
) -> set[str]:
    """Name the members of the class `own` has as `name`, with those of its bases `own` has too.

    `stored`: where the module assigns each name's attributes (see `_by_name`).

    Returns:
      Them; nothing for a class `seen` already (a cycle of bases).

    """
    if name in seen:
        return set()
    seen.add(name)
    node: ast.ClassDef = own[name]
    found: set[str] = _own(node, stored)
    base: ast.expr
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in own:
            found |= _inherited(base.id, own, seen, stored)
    return found


def _own(node: ast.ClassDef, stored: Mapping[str, _Spans]) -> set[str]:
    """Name what a class's own body binds, and what its methods assign to `self`'s attributes.

    `stored`: where the module assigns each name's attributes (see `_by_name`).

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
                    found |= _assigned(stmt, stored)
            case ast.Assign(targets=targets):
                found.update(target.id for target in targets if isinstance(target, ast.Name))
            case ast.AnnAssign(target=ast.Name(id=name)):
                found.add(name)
            case _:
                pass
    return found


def _assigned(method: FunctionDef, stored: Mapping[str, _Spans]) -> set[str]:
    """Name the attributes a method assigns to its first parameter (`self.x = ...`), anywhere in it.

    `stored`: where the module assigns each name's attributes (see `_by_name`): those within the
    method's span, from its first decorator on.

    Returns:
      Them.

    """
    named: list[ast.arg]
    spans: _Spans | None
    if (
        not (named := [*method.args.posonlyargs, *method.args.args])
        or (spans := stored.get(named[0].arg)) is None
    ):
        return set()
    begin: Start | None = (
        (method.decorator_list[0].lineno, method.decorator_list[0].col_offset)
        if method.decorator_list
        else None
    )
    return set(spans[1][within(spans[0], method, begin)])


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
