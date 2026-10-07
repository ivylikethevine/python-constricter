# SPDX-License-Identifier: MIT
"""`--fix` for calls to unannotated functions: their own `return` statements decide their type.

A function (or method) counts when it's plain (a `def` directly in the module or a class body, not
`async`, decorated or redefined), declares no return type, every `return` it has gives a value whose
type `--fix` is sure of, all the same, and it can't fall off its end (which returns `None`). A
generator counts by its `yield`s instead, all of one type `T`: a `Generator[T, None, None]` (see
`constricter.rules.recorded`). A module function's type is certain; a method's is a guess, since a
subclass may override it. Each value is typed as the checker sees it there, with the function's own
locals.
"""

import ast
import operator
from collections.abc import Collection, Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.inherited import Lineage
from constricter.fix.core.known import Inference, Returned, Returns
from constricter.fix.values import entered, fills
from constricter.fix.values.inference import ASSIGNED, RETURNED
from constricter.rules.annotations import roots
from constricter.rules.decorators import FIXTURES, spelled
from constricter.rules.flow import members
from constricter.rules.syntax import FunctionDef, Start, has_within, own_nodes, within
from constricter.rules.walked import classes, of_type

# A `return` statement as the checker saw it: its value's inference (`None`: none, or unknown), and
# what that rests on if it's a guess (`FIX_KINDS`; empty: certain). A generator has one: its type.
Recorded: TypeAlias = tuple[Inference | None, frozenset[str]]
# A `self.x = value` as the checker saw it: the attribute, and its value as a `return`'s is recorded.
Assigned: TypeAlias = tuple[str, Recorded]
# What a read of an empty container adds to it, each part as a `return`'s value is recorded (a
# `dict`'s key and value, any other's element): none for one that adds nothing, `None` for one that
# might, unseen.
Added: TypeAlias = tuple[Recorded, ...] | None
# A read of `self.x`, an attribute bound to an empty container, as the checker saw it.
Used: TypeAlias = tuple[str, Added]
# What a class's methods store in its attributes: each one's assigned values, and what's added to it.
_Stored: TypeAlias = tuple[dict[str, list[Recorded]], dict[str, list[Added]]]
_Emptied: TypeAlias = tuple[str, str]  # a `self.x = []`: the attribute, and the container's kind
_Under: TypeAlias = tuple[list[Recorded], list[Added], int]  # see `_under`
_FILLED: Final = "filled"  # the fix kind of an empty container typed by what's added to it
SELF: Final = "self"
_NONE: Final = "None"
_NOT_METHODS: Final = frozenset({"staticmethod", "classmethod"})
_NUMBERS: Final = ("bool", "int", "float", "complex")  # narrowest first: an attribute takes the widest
_FUNCTIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef)
# What a call calls: a name (`f()`), or an attribute (`x.m()`), the other `None`.
_Callee: TypeAlias = tuple[str | None, str | None]
_Call: TypeAlias = tuple[tuple[int, int], _Callee]  # where a call starts (line, column), and what it calls
_Uses: TypeAlias = tuple[list[Start], list[str]]  # attributes used: where each starts, and its name
_Listed: TypeAlias = list[tuple[Start, str]]  # attributes used, each where it starts and its name
# The functions by name: the module's (`[False]`), then the classes' methods (`[True]`).
_Named: TypeAlias = tuple[dict[str, list[FunctionDef]], dict[str, list[FunctionDef]]]
# One function to put in call order, and its callees still to put in before it.
_Visit: TypeAlias = tuple[FunctionDef, Iterator[FunctionDef]]


def returned(
    tree: ast.Module,
    recorded: Mapping[int, Sequence[Recorded]],
    assigned: Mapping[int, Sequence[Assigned]],
    used: Mapping[int, Sequence[Used]],
) -> Returned:
    """Read what the module's unannotated functions and methods return, and what its classes assign.

    `recorded` holds each checked function's `return` statements, `assigned` its `self.x = value`
    assignments and `used` its reads of `self`'s empty containers, by the function's `id()`.

    Returns:
      Their return types: the module's functions', and each class's methods'; and each class's
      unannotated instance attributes' types (see `_attributes`).

    """
    calls: dict[str, str] = {}
    methods: dict[str, dict[str, str]] = {}
    guesses: dict[str, frozenset[str]] = {}
    name: str
    annotation: str
    origins: frozenset[str]
    for name, annotation, origins in _typed(tree, tree.body, recorded):
        calls[name] = annotation
        if origins:
            guesses[name] = origins
    attributes: dict[str, dict[str, str]] = {}
    node: ast.ClassDef
    for node in classes(tree):
        for name, annotation, origins in _typed(tree, node.body, recorded):
            methods.setdefault(node.name, {})[name] = annotation
            if origins:
                guesses[f"{node.name}.{name}"] = origins
        if _class_names(tree)[node.name] == 1:  # its attributes are looked up by its name
            for name, annotation, origins in _attributes(tree, node, (assigned, used)):
                attributes.setdefault(node.name, {})[name] = annotation
                guesses[f"{node.name}.{name}"] = origins
    return Returned(calls, methods, guesses, attributes)


def joined(imported: Returns, own: Returned) -> Returned:
    """Add what the functions a module imports return to what its own return (its own first).

    Returns:
      Both.

    """
    if not imported.calls and not imported.methods:
        return own
    return own._replace(
        calls={**imported.calls, **own.calls},
        methods={**imported.methods, **own.methods},
        guesses={**imported.guesses, **own.guesses},
    )


def exported(own: Returned, lineage: Lineage) -> Returns:
    """Pick out what the module's own functions and its classes' methods return, for the files importing them.

    A class has the methods it takes from the module's other classes too (see `Lineage`), but one
    whose type names that base, which may be the class itself (`return self`).

    Returns:
      Their types, and their guesses' origins (a method's as `C.m`).

    """
    methods: dict[str, dict[str, str]] = {owner: dict(typed) for owner, typed in own.methods.items() if typed}
    guesses: dict[str, frozenset[str]] = {
        name: own.guesses[name]
        for name in (*own.calls, *(f"{owner}.{name}" for owner, typed in methods.items() for name in typed))
        if name in own.guesses
    }
    owner: str
    bases: tuple[str, ...]
    for owner, bases in lineage.order.items():
        base: str
        name: str
        annotation: str
        for base in bases:
            for name, annotation in own.methods.get(base, {}).items():
                if lineage.definer(owner, name) == base and base not in roots(annotation):
                    methods.setdefault(owner, {})[name] = annotation
                    if f"{base}.{name}" in own.guesses:
                        guesses[f"{owner}.{name}"] = own.guesses[f"{base}.{name}"]
    return Returns(dict(own.calls), guesses, methods=methods)


def unannotated(body: Sequence[ast.stmt]) -> frozenset[str]:
    """Name the functions in `body` whose `return`s could type their calls (see `_return_type`).

    Returns:
      Each plain function's name that has no decorator or declared return.

    """
    return frozenset(func.name for func in _plain(body) if not _decorated(func) and func.returns is None)


@lru_cache(maxsize=4)  # asked once per round, of the same module
def _class_names(tree: ast.Module) -> Mapping[str, int]:
    """Count the classes the module defines by each name.

    Returns:
      Each name's count.

    """
    counts: dict[str, int] = {}
    node: ast.ClassDef
    for node in classes(tree):
        counts[node.name] = counts.get(node.name, 0) + 1
    return counts


def _attributes(
    tree: ast.Module,
    node: ast.ClassDef,
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Find the class's unannotated instance attributes whose every assignment decides their type.

    One counts when every place the class's code stores or deletes it (`self.x`, anywhere in the
    class) is a plain `self.x = value` in one of its own methods, the class's body doesn't bind the
    name (a class attribute, a method, a property), and every value's type is known and the same, or
    numbers (`int`, then `float`: the widest). One bound to an empty container counts by what the
    class's methods, and those of the module's classes under it, add to it (see `_filled`). A guess:
    another file's subclass or outside code may assign it too.

    `seen`: each checked function's `self.x = value`s, and its reads of `self`'s empty containers.

    Yields:
      Each one's name, type, and what that rests on: `assigned`, and its values' own guesses.

    """
    values: dict[str, list[Recorded]]
    uses: dict[str, list[Added]]
    values, uses = _stored(node, seen)
    if not values:
        return
    starts: list[Start]
    stored: list[str]
    starts, stored = _uses(tree)[2]
    stores: dict[str, int] = {}
    attr: str
    for attr in stored[within(starts, node)]:
        stores[attr] = stores.get(attr, 0) + 1
    bound: frozenset[str] = _class_bound(node)
    found: list[Recorded]
    for attr in sorted(_emptied(tree, node).keys() & values.keys() - bound):
        filled: tuple[str, frozenset[str]] | None
        if (
            stores[attr] == len(values[attr])
            and len(uses.get(attr, ())) == _read(tree, node, attr)
            and (filled := _filled_under(tree, node, attr, (values[attr], uses.get(attr, ())), seen))
            is not None
        ):
            yield attr, *filled
    for attr, found in values.items():
        types: set[str] = {value.annotation for value, _ in found if value is not None}
        widest: str | None
        if (
            stores[attr] == len(found)
            and attr not in bound
            and all(value is not None for value, _ in found)
            and (widest := _widest(types)) is not None
        ):
            yield attr, widest, frozenset({ASSIGNED}).union(*(origins for _, origins in found))


def _filled_under(
    tree: ast.Module,
    node: ast.ClassDef,
    attr: str,
    own: tuple[Sequence[Recorded], Sequence[Added]],
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> tuple[str, frozenset[str]] | None:
    # `_filled`, by what the class's `own` methods store and add, and the module's classes' under it.
    more: _Under | None = _under(tree, _family(tree, node), attr, seen)
    kind: str
    bare: int
    kind, bare = _emptied(tree, node)[attr]
    return None if more is None else _filled((kind, bare + more[2]), [*own[0], *more[0]], [*own[1], *more[1]])


@lru_cache(maxsize=1024)  # asked of the same classes once per round, and of each method as it's checked
def _family(module: ast.Module, node: ast.ClassDef) -> tuple[ast.ClassDef, ...]:
    """Find the module's classes under `node`, however far: each defined once, by a base named as it is.

    Returns:
      Them, in source order; none for a class whose name another of the module's has.

    """
    counts: Mapping[str, int] = _class_names(module)
    names: set[str] = {node.name} if counts[node.name] == 1 else set()
    found: list[ast.ClassDef] = []
    each: ast.ClassDef
    for each in sorted(classes(module), key=lambda one: (one.lineno, one.col_offset)):
        if (
            each is not node
            and counts[each.name] == 1
            and any(isinstance(base, ast.Name) and base.id in names for base in each.bases)
        ):
            names.add(each.name)
            found.append(each)
    return tuple(found)


def _under(
    tree: ast.Module,
    family: Sequence[ast.ClassDef],
    attr: str,
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> _Under | None:
    """Gather what the classes under one (`family`) store in its attribute `attr`, an empty container.

    Each one's methods' `self.attr = value`s and reads of it, as the class's own are gathered.

    Returns:
      Their values, their uses, and how many of their assignments bind it empty too; or `None` if
      one binds the name in its body, stores it any other way, or reads it where the checker
      didn't judge the read (a nested function).

    """
    found: _Under = ([], [], 0)
    starts: list[Start]
    stored: list[str]
    starts, stored = _uses(tree)[2]
    node: ast.ClassDef
    for node in family:
        values: list[Recorded] = [
            value for method in _methods(node) for name, value in seen[0].get(id(method), ()) if name == attr
        ]
        uses: list[Added] = [
            use for method in _methods(node) for name, use in seen[1].get(id(method), ()) if name == attr
        ]
        if (
            attr in _class_bound(node)
            or stored[within(starts, node)].count(attr) != len(values)
            or _read(tree, node, attr) != len(uses)
        ):
            return None
        found[0].extend(values)
        found[1].extend(uses)
    return found[0], found[1], sum(_emptied(tree, node).get(attr, ("", 0))[1] for node in family)


def _stored(
    node: ast.ClassDef,
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
) -> _Stored:
    """Gather what the class's own methods store in each attribute of `self` (see `_attributes`).

    Returns:
      Each attribute's assigned values, and each empty container's reads.

    """
    values: dict[str, list[Recorded]] = {}
    uses: dict[str, list[Added]] = {}
    method: FunctionDef
    for method in _methods(node):
        attr: str
        value: Recorded
        for attr, value in seen[0].get(id(method), ()):
            values.setdefault(attr, []).append(value)
        use: Added
        for attr, use in seen[1].get(id(method), ()):
            uses.setdefault(attr, []).append(use)
    return values, uses


def _filled(
    emptied: tuple[str, int],
    found: Sequence[Recorded],
    uses: Sequence[Added],
) -> tuple[str, frozenset[str]] | None:
    """Type an attribute bound to an empty container by what its class's methods add to it.

    `emptied`: its kind, and how many of its assignments (`found`) bind it empty; `uses`: every read
    of it in the class, as `fills.stored` judges them. As `fills.filled` types a local: no read may
    add something unseen, and what's added, or assigned to it instead, must be typed alike.

    Returns:
      Its type, and what that rests on (`assigned`, `filled`, and its values' own guesses); or `None`.

    """
    kind: str
    bare: int
    kind, bare = emptied
    values: list[Recorded] = [value for value in found if value[0] is not None]
    added: list[tuple[Recorded, ...]] = [use for use in uses if use]
    parts: list[Recorded] = [*values, *(part for use in added for part in use)]
    if len(values) + bare != len(found) or None in uses or any(part[0] is None for part in parts):
        return None
    types: set[str] = {value.annotation for value, _ in values if value is not None} | {
        f"{kind}[{', '.join(part.annotation for part, _ in use if part is not None)}]" for use in added
    }
    if len(types) != 1:
        return None
    return types.pop(), frozenset({ASSIGNED, _FILLED}).union(*(origins for _, origins in parts))


@lru_cache(maxsize=4)  # asked of the same module's classes, each round
def _empties(module: ast.Module) -> tuple[list[Start], list[_Emptied]]:
    """Find the module's `self.x = []`s: each assignment of an empty container to an attribute of `self`.

    Returns:
      Where each starts, in source order; and its attribute and kind (see `fills.empty`).

    """
    found: list[tuple[Start, _Emptied]] = []
    node: ast.AST
    for node in of_type(module, ast.Assign):
        kind: str | None
        if isinstance(node, ast.Assign) and (kind := fills.empty(node.value)) is not None:
            found.extend(
                ((target.lineno, target.col_offset), (target.attr, kind))
                for target in node.targets
                if isinstance(target, ast.Attribute)
                and isinstance(target.value, ast.Name)
                and target.value.id == SELF
            )
    found.sort()
    return [start for start, _ in found], [each for _, each in found]


@lru_cache(maxsize=1024)  # asked of the same classes once per round, and of each method as it's checked
def _emptied(module: ast.Module, node: ast.ClassDef) -> Mapping[str, tuple[str, int]]:
    """Find the attributes the class's code binds to an empty container, always of one kind.

    Returns:
      Each one's kind, and how many assignments bind it so.

    """
    starts: list[Start]
    found: list[_Emptied]
    starts, found = _empties(module)
    kinds: dict[str, list[str]] = {}
    attr: str
    kind: str
    for attr, kind in found[within(starts, node)]:
        kinds.setdefault(attr, []).append(kind)
    return {attr: (each[0], len(each)) for attr, each in kinds.items() if len(set(each)) == 1}


def empties(module: ast.Module, func: FunctionDef) -> Mapping[str, str]:
    """Find the attributes of `self` a method's class, or one above it, binds to an empty container.

    Returns:
      Each one's kind; none for a function that isn't a class's own method.

    """
    node: ast.ClassDef | None
    if (node := _owners(module).get(id(func))) is None:
        return {}
    # Its own class's, and those of the module's classes it's under: their fills are its own too.
    above: list[ast.ClassDef] = [each for each in classes(module) if node in _family(module, each)]
    return {attr: kind for each in (*above, node) for attr, (kind, _) in _emptied(module, each).items()}


def _read(module: ast.Module, node: ast.ClassDef, attr: str) -> int:
    """Count the class's reads of `self.attr`, anywhere in it: a nested function's too.

    Returns:
      How many.

    """
    starts: list[Start]
    found: list[str]
    starts, found = _uses(module)[0]
    return found[within(starts, node)].count(attr)


def _widest(types: set[str]) -> str | None:
    """Find the one type every value's fits: the only one, or the widest of builtin numbers.

    Returns:
      It, or `None`.

    """
    if len(types) == 1:
        return next(iter(types))
    return max(types, key=_NUMBERS.index) if types <= set(_NUMBERS) else None


@lru_cache(maxsize=4)  # asked of each function as it's checked
def _owners(module: ast.Module) -> dict[int, ast.ClassDef]:
    """Map each class's own methods (see `_methods`) to it, by the method's `id()`.

    Returns:
      Each one's class.

    """
    return {id(method): node for node in classes(module) for method in _methods(node)}


@lru_cache(maxsize=1024)  # asked of the same classes once per round
def _methods(node: ast.ClassDef) -> tuple[FunctionDef, ...]:
    """Find the class's own methods whose first parameter is `self`: not a static or class method.

    Returns:
      Them.

    """
    return tuple(
        stmt
        for stmt in node.body
        if isinstance(stmt, _FUNCTIONS)
        and [arg.arg for arg in (*stmt.args.posonlyargs, *stmt.args.args)][:1] == [SELF]
        and not any(isinstance(d, ast.Name) and d.id in _NOT_METHODS for d in stmt.decorator_list)
    )


@lru_cache(maxsize=1024)  # asked of the same classes once per round
def _class_bound(node: ast.ClassDef) -> frozenset[str]:
    """Find the names the class's own body binds: its class attributes, methods and nested classes.

    Returns:
      Them.

    """
    return frozenset(
        name.id
        for stmt in node.body
        for target in _body_targets(stmt)
        for name in ast.walk(target)
        if isinstance(name, ast.Name)
    ) | frozenset(stmt.name for stmt in node.body if isinstance(stmt, (*_FUNCTIONS, ast.ClassDef)))


def _body_targets(stmt: ast.stmt) -> list[ast.expr]:
    """List what a class-body statement assigns to.

    Returns:
      Its targets: none but for an assignment.

    """
    targets: list[ast.expr]
    target: ast.expr
    match stmt:
        case ast.Assign(targets=targets):
            return targets
        case ast.AnnAssign(target=target) | ast.AugAssign(target=target):
            return [target]
        case _:
            return []


def called(module: ast.Module, node: ast.AST, found: Returned) -> bool:
    """Check whether `node` (the module, a function, or a statement in it) calls any function `found` types.

    By name, or as a method. A function's decorators aren't its own calls: they're before it.

    Returns:
      Whether it does: otherwise checking it again would change nothing.

    """
    methods: set[str] = {name for methods in found.methods.values() for name in methods}
    return any(name in found.calls or attr in methods for name, attr in _callees_in(module, node))


def reads(module: ast.Module, node: ast.AST, attributes: Collection[str], *, anywhere: bool = False) -> bool:
    """Check whether `node` (a function, or a statement) reads any of `attributes` of `self` (`self.a`).

    `anywhere`: of any value (`x.a`, whatever `x` is), by its name alone, as `called` counts methods.

    Returns:
      Whether it does: otherwise checking it again, knowing their types, would change nothing.

    """
    starts: list[Start]
    found: list[str]
    starts, found = _uses(module)[1 if anywhere else 0]
    return bool(attributes) and any(attr in attributes for attr in found[within(starts, node)])


def reads_own(tree: ast.Module, func: FunctionDef, classes_of: Mapping[int, str], found: Returned) -> bool:
    """Check whether a method reads an attribute of its own class's (`self.a`) that `found` types.

    `classes_of`: each method's class, by the method's `id()`.

    Returns:
      Whether it does: checking it again could type more.

    """
    owner: str | None
    if (owner := classes_of.get(id(func))) is None:
        return False
    node: ast.ClassDef | None = _owners(tree).get(id(func))
    above: list[str] = (
        [] if node is None else [each.name for each in classes(tree) if node in _family(tree, each)]
    )
    return reads(tree, func, {attr for name in (owner, *above) for attr in found.attributes.get(name, {})})


def retyped(before: Returned, after: Returned) -> set[str]:
    """Name the attributes, of any class, that `after` types and `before` didn't, or typed otherwise.

    Returns:
      Their names.

    """
    return {
        attr
        for owner, attributes in after.attributes.items()
        for attr, annotation in attributes.items()
        if before.attributes.get(owner, {}).get(attr) != annotation
    }


def _callees_in(module: ast.Module, node: ast.AST) -> Sequence[_Callee]:
    """Find what `node` (the module, a function, or a statement in it) calls, by its span of the source.

    Returns:
      Each call's callee: a name (`f()`) or an attribute (`x.m()`).

    """
    starts: list[Start]
    callees: list[_Callee]
    starts, callees = _calls(module)
    return callees[within(starts, node)]


@lru_cache(maxsize=4)  # asked of the same module's functions and classes, each round
def _uses(module: ast.Module) -> tuple[_Uses, _Uses, _Uses]:
    """Find the module's attribute uses: reads of `self`'s (`self.a`), reads of any, stores to `self`'s.

    A store includes a deletion (`del self.a`).

    Returns:
      Those three: each's starts, in source order, and its attribute's name.

    """
    found: tuple[_Listed, ...] = ([], [], [])
    node: ast.AST
    receiver: ast.expr
    attr: str
    for node in of_type(module, ast.Attribute):
        match node:
            case ast.Attribute(value=receiver, ctx=ast.Load(), attr=attr):
                if isinstance(receiver, ast.Name) and receiver.id == SELF:
                    found[0].append(((node.lineno, node.col_offset), attr))
                found[1].append(((node.lineno, node.col_offset), attr))
            case ast.Attribute(value=ast.Name(id="self"), attr=attr):  # a store or deletion
                found[2].append(((node.lineno, node.col_offset), attr))
            case _:
                pass
    kind: _Listed
    for kind in found:
        kind.sort()
    of_self: _Uses
    of_any: _Uses
    stored: _Uses
    of_self, of_any, stored = (([start for start, _ in kind], [attr for _, attr in kind]) for kind in found)
    return of_self, of_any, stored


class Slot(NamedTuple):
    """Where a function's return type goes in the table: its class (`None`: the module's), and its name."""

    owner: str | None
    name: str


@lru_cache(maxsize=4)
def slots(module: ast.Module) -> dict[int, Slot]:
    """Find the functions whose `return`s can type their calls: plain, directly in the module or a class.

    As `_typed` finds them (see `_plain`).

    Returns:
      Each one's slot, by the function's `id()`.

    """
    return {
        id(func): Slot(owner, func.name)
        for owner, body in ((None, module.body), *((node.name, node.body) for node in classes(module)))
        for func in _plain(body)
    }


def _decorated(func: FunctionDef) -> bool:
    """Check whether a function has a decorator that may change what calling it gives.

    Not a pytest fixture's alone: the fixture's value is what the function returns (or yields).

    Returns:
      Whether it has.

    """
    return bool(func.decorator_list) and not all(spelled(each) in FIXTURES for each in func.decorator_list)


def _plain(body: Sequence[ast.stmt]) -> list[ast.FunctionDef]:
    """Find the plain functions directly in `body`: a `def` (not `async`) no other there shares a name with.

    Returns:
      Them, in source order.

    """
    counts: dict[str, int] = {}
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, _FUNCTIONS):
            counts[stmt.name] = counts.get(stmt.name, 0) + 1
    return [stmt for stmt in body if isinstance(stmt, ast.FunctionDef) and counts[stmt.name] == 1]


def in_call_order(module: ast.Module, functions: Sequence[FunctionDef]) -> list[FunctionDef]:
    """Order `functions` so that each comes after the functions it calls (a cycle's, in any order).

    Its callees: the module's functions it calls by name, and every method named as it calls one
    (`x.m()`: any class's `m`), as `called` counts them.

    Returns:
      Them, callees first; otherwise in their own order.

    """
    named: _Named = ({}, {})
    func: FunctionDef
    for func in functions:
        slot: Slot | None
        if (slot := slots(module).get(id(func))) is not None:
            named[slot.owner is not None].setdefault(slot.name, []).append(func)
    ordered: list[FunctionDef] = []
    seen: set[int] = set()
    for func in functions:
        if id(func) not in seen:
            seen.add(id(func))
            _after_callees(module, func, named, (ordered, seen))
    return ordered


def _after_callees(
    module: ast.Module,
    func: FunctionDef,
    named: "_Named",
    into: tuple[list[FunctionDef], set[int]],
) -> None:
    """Put `func` in the order after its callees, depth first, with a stack: a call chain can be long."""
    ordered: list[FunctionDef]
    seen: set[int]
    ordered, seen = into
    # Each entry: a function, and its callees still to put in before it; `None` at the bottom ends it.
    waiting: list[_Visit | None] = [None, (func, _callees(module, func, named))]
    entry: _Visit
    for entry in iter(waiting.pop, None):
        callee: FunctionDef | None
        if (callee := next((one for one in entry[1] if id(one) not in seen), None)) is None:
            ordered.append(entry[0])
        else:
            seen.add(id(callee))
            waiting.extend([entry, (callee, _callees(module, callee, named))])


def _callees(module: ast.Module, func: FunctionDef, named: "_Named") -> Iterator[FunctionDef]:
    """Find the functions of `named` that `func` calls: the module's by name, methods by attribute.

    Yields:
      Each, in the order of its calls.

    """
    name: str | None
    attr: str | None
    for name, attr in _callees_in(module, func):
        yield from named[False].get(name, []) if name is not None else named[True].get(attr or "", [])


class _Tables(NamedTuple):
    """The live tables a `Table` fills in, as `Returned` holds them."""

    calls: dict[str, str]
    methods: dict[str, dict[str, str]]
    guesses: dict[str, frozenset[str]]
    attributes: dict[str, dict[str, str]]


class Table:
    """What the module's unannotated functions return, filled in as each is checked, in call order.

    `returned` is the live table, for the check to read as it goes. Each function's stamp is how
    many entries the table had when it was checked: one checked before a callee of its was typed
    (in a cycle) is `stale`, and checked again. A class's attributes are typed once all its methods
    are checked: what reads them later knows them the first time.
    """

    def __init__(self, module: ast.Module, imported: Returns | None = None) -> None:
        """Start a table for `module`, with what the functions it imports from other files return."""
        imported = imported or Returns()
        self.module: ast.Module = module
        self.recorded: dict[int, list[Recorded]] = {}
        self.assigned: dict[int, list[Assigned]] = {}  # each checked function's `self.x = value`s
        self.used: dict[int, list[Used]] = {}  # each checked function's reads of `self`'s empty containers
        methods: dict[str, dict[str, str]] = {owner: dict(typed) for owner, typed in imported.methods.items()}
        self.tables: _Tables = _Tables(dict(imported.calls), methods, dict(imported.guesses), {})
        self.returned: Returned = Returned(*self.tables)
        self.entries: list[tuple[Slot, str]] = []
        self.stamps: dict[int, int] = {}

    def checked(
        self,
        func: FunctionDef,
        returns: list[Recorded],
        stored: tuple[list[Assigned], list[Used]],
    ) -> None:
        """Record a checked function's `return`s, and what it stores in `self`'s attributes.

        `stored`: its `self.x = value`s, and its reads of `self`'s empty containers. Its return type
        is recorded too, if its `return`s decide it.
        """
        self.stamps[id(func)] = len(self.entries)
        self.recorded[id(func)] = returns
        self.assigned[id(func)], self.used[id(func)] = stored
        self._completed(func)
        slot: Slot | None = slots(self.module).get(id(func))
        found: tuple[str, frozenset[str]] | None
        if (
            slot is None
            or not isinstance(func, ast.FunctionDef)
            or (found := _return_type(self.module, func, returns)) is None
        ):
            return
        annotation: str
        origins: frozenset[str]
        annotation, origins = found
        if slot.owner is None:
            self.tables.calls[slot.name] = annotation
        else:
            self.tables.methods.setdefault(slot.owner, {})[slot.name] = annotation
        if origins:
            self.tables.guesses[slot.name if slot.owner is None else f"{slot.owner}.{slot.name}"] = origins
        self.entries.append((slot, annotation))

    def _completed(self, func: FunctionDef) -> None:
        """Type the attributes of `func`'s class (and those above it) whose methods are all checked now."""
        own: ast.ClassDef | None = _owners(self.module).get(id(func))
        above: list[ast.ClassDef] = (
            []
            if own is None
            else [each for each in classes(self.module) if own in _family(self.module, each)]
        )
        node: ast.ClassDef
        for node in above if own is None else (own, *above):
            # With the classes under it: their methods fill its empty containers too.
            if _class_names(self.module)[node.name] != 1 or any(
                id(method) not in self.assigned
                for each in (node, *_family(self.module, node))
                for method in _methods(each)
            ):
                continue
            name: str
            annotation: str
            origins: frozenset[str]
            for name, annotation, origins in _attributes(self.module, node, (self.assigned, self.used)):
                self.tables.attributes.setdefault(node.name, {})[name] = annotation
                self.tables.guesses[f"{node.name}.{name}"] = origins

    def stale(self, func: FunctionDef) -> bool:
        """Check whether `func` calls a function whose type the table gained after `func` was checked.

        Returns:
          Whether it does: checking it again, knowing that, could type more.

        """
        since: slice = slice(self.stamps.get(id(func), 0), None)
        newer: list[tuple[Slot, str]] = self.entries[since]
        calls: dict[str, str] = {}
        methods: dict[str, dict[str, str]] = {}
        slot: Slot
        annotation: str
        for slot, annotation in newer:
            if slot.owner is None:
                calls[slot.name] = annotation
            else:
                methods.setdefault(slot.owner, {})[slot.name] = annotation
        return bool(newer) and called(self.module, func, Returned(calls, methods))


@lru_cache(maxsize=4)  # asked of the same module's functions, each round
def _calls(module: ast.Module) -> tuple[list[tuple[int, int]], list[_Callee]]:
    """Find every call in the module, in source order, from its one shared walk (`nodes`).

    A function's (or statement's) calls are then those within its span of the source: no walk of
    its own, which the rounds of `checker._returned` asked of every function again and again. A
    `with` statement that binds a target calls its manager's `__enter__`.

    Returns:
      Where each call starts (its line and column), and what it calls: a name (`f()`) or an
      attribute (`x.m()`), each `None` if not.

    """
    found: list[_Call] = [(start, (None, entered.ENTER)) for start in entered.targets(module)]
    node: ast.AST
    name: str
    attr: str
    for node in of_type(module, ast.Call):
        match node:
            case ast.Call(func=ast.Name(id=name)):
                found.append(((node.lineno, node.col_offset), (name, None)))
            case ast.Call(func=ast.Attribute(attr=attr)):
                found.append(((node.lineno, node.col_offset), (None, attr)))
            case _:
                pass
    found.sort(key=operator.itemgetter(0))
    return [start for start, _ in found], [callee for _, callee in found]


def _typed(
    module: ast.Module,
    body: Sequence[ast.stmt],
    recorded: Mapping[int, Sequence[Recorded]],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Find the plain unannotated functions directly in `body` whose `return`s decide their type.

    Yields:
      Each one's name, return type, and what that rests on if it's a guess.

    """
    func: ast.FunctionDef
    for func in _plain(body):
        found: tuple[str, frozenset[str]] | None
        if (found := _return_type(module, func, recorded.get(id(func), ()))) is not None:
            yield func.name, *found


def _return_type(
    module: ast.Module,
    func: ast.FunctionDef,
    returns: Sequence[Recorded],
) -> tuple[str, frozenset[str]] | None:
    """Type a plain function from its recorded `return`s.

    Returns:
      The one type they all give, and what it rests on if any is a guess; or `None` if it's
      decorated or annotated (by a `# type:` comment too), can fall off its end (but for a
      generator, recorded as its type), or has a `return` without a value or of an unknown or
      different type.

    """
    if (
        _decorated(func)
        or func.returns is not None
        or func.type_comment
        or not returns
        or not (is_generator(module, func) or terminates(func.body))
    ):
        return None
    types: set[str | None] = {None if found is None else found.annotation for found, _ in returns}
    found: str | None
    if (found := next(iter(types)) if len(types) == 1 else None) is None:
        return None
    # An `X | None` is a guess: a type checker takes the unannotated function's call for anything,
    # and what its callers do with it unchecked for `None` is an error only once it's declared.
    doubted: frozenset[str] = frozenset({RETURNED}) if _NONE in (members(found) or ()) else frozenset()
    return found, doubted.union(*(origins for _, origins in returns))


def is_generator(module: ast.Module, func: ast.FunctionDef) -> bool:
    """Check whether `func`, in `module`, is a generator: a `yield` in its own body (not a nested function's).

    Most functions have no `yield` anywhere in them (see `_yields`): only one with some is walked.

    Returns:
      Whether it is.

    """
    return has_within(_yields(module), func) and yields_itself(func)


# By the function alone, not its module too: a cache holding modules keeps checked trees alive, and
# the garbage collector then looks through them again and again (the standard library's check took
# 10% longer).
@lru_cache(maxsize=4096)  # asked of the same functions once per round
def yields_itself(func: ast.FunctionDef) -> bool:
    """Check whether a `yield` is in `func`'s own body, not a nested function's.

    Returns:
      Whether one is.

    """
    return any(isinstance(node, ast.Yield | ast.YieldFrom) for node in own_nodes(func.body))


@lru_cache(maxsize=4)  # asked of the same module's functions, each round
def _yields(module: ast.Module) -> list[Start]:
    """Find where each of the module's `yield`s starts.

    Returns:
      Them, in source order.

    """
    return sorted(
        (node.lineno, node.col_offset)
        for node in cast("list[ast.expr]", of_type(module, ast.Yield, ast.YieldFrom))
    )


def terminates(body: Sequence[ast.stmt]) -> bool:
    """Check that running `body` can't reach its end: it always returns or raises first.

    Its last statement returns or raises, or is an `if` or `try` whose every way through does (a
    `try`'s body with its `else`, and each handler), or a `with` whose body does.

    Returns:
      Whether it can't.

    """
    if not body:
        return False
    last: ast.stmt = body[-1]
    match last:
        case ast.Return() | ast.Raise():
            return True
        case ast.If():
            return terminates(last.body) and terminates(last.orelse)
        case ast.With() | ast.AsyncWith():
            return terminates(last.body)
        case ast.Try() | ast.TryStar():
            return terminates(last.orelse or last.body) and all(terminates(h.body) for h in last.handlers)
        case _:
            return False
