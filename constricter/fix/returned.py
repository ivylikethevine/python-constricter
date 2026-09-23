# SPDX-License-Identifier: MIT
"""`--fix` for calls to unannotated functions: their own `return` statements decide their type.

A function (or method) counts when it's plain (a `def` directly in the module or a class body, not
`async`, decorated, redefined or a generator), declares no return type, every `return` it has gives
a value whose type `--fix` is sure of, all the same, and it can't fall off its end (which returns
`None`). A module function's type is certain; a method's is a guess, since a subclass may override
it. Each `return`'s value is typed as the checker sees it there, with the function's own locals.
"""

import ast
import bisect
import operator
from collections.abc import Collection, Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.inference import ASSIGNED
from constricter.fix.known import Inference, Returned
from constricter.rules.syntax import FunctionDef
from constricter.rules.walked import classes, of_type

# A `return` statement as the checker saw it: its value's inference (`None`: none, or unknown), and
# what that rests on if it's a guess (`FIX_KINDS`; empty: certain).
Recorded: TypeAlias = tuple[Inference | None, frozenset[str]]
# A `self.x = value` as the checker saw it: the attribute, and its value as a `return`'s is recorded.
Assigned: TypeAlias = tuple[str, Recorded]
SELF: Final = "self"
_NOT_METHODS: Final = frozenset({"staticmethod", "classmethod"})
_NUMBERS: Final = ("bool", "int", "float", "complex")  # narrowest first: an attribute takes the widest
_FUNCTIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef)
_END: Final = 1 << 62  # past any line: a module's span has no end
# What a call calls: a name (`f()`), or an attribute (`x.m()`), the other `None`.
_Callee: TypeAlias = tuple[str | None, str | None]
_Call: TypeAlias = tuple[tuple[int, int], _Callee]  # where a call starts (line, column), and what it calls
_Start: TypeAlias = tuple[int, int]  # where a node starts: its line and column
_Uses: TypeAlias = tuple[list[_Start], list[str]]  # attributes used: where each starts, and its name
_Listed: TypeAlias = list[tuple[_Start, str]]  # attributes used, each where it starts and its name
# The functions by name: the module's (`[False]`), then the classes' methods (`[True]`).
_Named: TypeAlias = tuple[dict[str, list[FunctionDef]], dict[str, list[FunctionDef]]]
# One function to put in call order, and its callees still to put in before it.
_Visit: TypeAlias = tuple[FunctionDef, Iterator[FunctionDef]]
_SCOPES: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def returned(
    tree: ast.Module,
    recorded: Mapping[int, Sequence[Recorded]],
    assigned: Mapping[int, Sequence[Assigned]],
) -> Returned:
    """Read what the module's unannotated functions and methods return, and what its classes assign.

    `recorded` holds each checked function's `return` statements, and `assigned` its `self.x = value`
    assignments, by the function's `id()`.

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
    for name, annotation, origins in _typed(tree.body, recorded):
        calls[name] = annotation
        if origins:
            guesses[name] = origins
    attributes: dict[str, dict[str, str]] = {}
    node: ast.ClassDef
    for node in _classes(tree):
        for name, annotation, origins in _typed(node.body, recorded):
            methods.setdefault(node.name, {})[name] = annotation
            if origins:
                guesses[f"{node.name}.{name}"] = origins
        if _class_names(tree)[node.name] == 1:  # its attributes are looked up by its name
            for name, annotation, origins in _attributes(tree, node, assigned):
                attributes.setdefault(node.name, {})[name] = annotation
                guesses[f"{node.name}.{name}"] = origins
    return Returned(calls, methods, guesses, attributes)


@lru_cache(maxsize=4)  # asked once per round, of the same module
def _class_names(tree: ast.Module) -> Mapping[str, int]:
    """Count the classes the module defines by each name.

    Returns:
      Each name's count.

    """
    counts: dict[str, int] = {}
    node: ast.ClassDef
    for node in _classes(tree):
        counts[node.name] = counts.get(node.name, 0) + 1
    return counts


def _attributes(
    tree: ast.Module,
    node: ast.ClassDef,
    assigned: Mapping[int, Sequence[Assigned]],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Find the class's unannotated instance attributes whose every assignment decides their type.

    One counts when every place the class's code stores or deletes it (`self.x`, anywhere in the
    class) is a plain `self.x = value` in one of its own methods, the class's body doesn't bind the
    name (a class attribute, a method, a property), and every value's type is known and the same, or
    numbers (`int`, then `float`: the widest). A guess: a subclass or outside code may assign it too.

    Yields:
      Each one's name, type, and what that rests on: `assigned`, and its values' own guesses.

    """
    values: dict[str, list[Recorded]] = {}
    method: FunctionDef
    for method in _methods(node):
        attr: str
        value: Recorded
        for attr, value in assigned.get(id(method), ()):
            values.setdefault(attr, []).append(value)
    if not values:
        return
    starts: list[_Start]
    stored: list[str]
    starts, stored = _uses(tree)[2]
    stores: dict[str, int] = {}
    for attr in stored[_span(starts, node)]:
        stores[attr] = stores.get(attr, 0) + 1
    bound: frozenset[str] = _class_bound(node)
    found: list[Recorded]
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
    return {id(method): node for node in _classes(module) for method in _methods(node)}


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
    starts: list[_Start]
    found: list[str]
    starts, found = _uses(module)[1 if anywhere else 0]
    return bool(attributes) and any(attr in attributes for attr in found[_span(starts, node)])


def _callees_in(module: ast.Module, node: ast.AST) -> Sequence[_Callee]:
    """Find what `node` (the module, a function, or a statement in it) calls, by its span of the source.

    Returns:
      Each call's callee: a name (`f()`) or an attribute (`x.m()`).

    """
    starts: list[_Start]
    callees: list[_Callee]
    starts, callees = _calls(module)
    return callees[_span(starts, node)]


def _span(starts: list[_Start], node: ast.AST) -> slice:
    """Find which of `starts` (in source order) are within `node`'s span of the source.

    Returns:
      Their slice.

    """
    begin: _Start = (getattr(node, "lineno", 0), getattr(node, "col_offset", 0))
    end: _Start = (getattr(node, "end_lineno", _END) or _END, getattr(node, "end_col_offset", 0) or 0)
    return slice(bisect.bisect_left(starts, begin), bisect.bisect_left(starts, end))


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
    self_reads: _Uses
    reads: _Uses
    stores: _Uses
    self_reads, reads, stores = (([start for start, _ in kind], [attr for _, attr in kind]) for kind in found)
    return self_reads, reads, stores


class Slot(NamedTuple):
    """Where a function's return type goes in the table: its class (`None`: the module's), and its name."""

    owner: str | None
    name: str


@lru_cache(maxsize=4)
def slots(module: ast.Module) -> dict[int, Slot]:
    """Find the functions whose `return`s can type their calls: plain, directly in the module or a class.

    As `_typed` finds them: a `def` (not `async`) whose name nothing else in the same body defines.

    Returns:
      Each one's slot, by the function's `id()`.

    """
    found: dict[int, Slot] = {}
    owner: str | None
    body: list[ast.stmt]
    for owner, body in ((None, module.body), *((node.name, node.body) for node in classes(module))):
        counts: dict[str, int] = {}
        stmt: ast.stmt
        for stmt in body:
            if isinstance(stmt, _FUNCTIONS):
                counts[stmt.name] = counts.get(stmt.name, 0) + 1
        for stmt in body:
            if isinstance(stmt, ast.FunctionDef) and counts[stmt.name] == 1:
                found[id(stmt)] = Slot(owner, stmt.name)
    return found


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


class Table:
    """What the module's unannotated functions return, filled in as each is checked, in call order.

    `returned` is the live table, for the check to read as it goes. Each function's stamp is how
    many entries the table had when it was checked: one checked before a callee of its was typed
    (in a cycle) is `stale`, and checked again. A class's attributes are typed once all its methods
    are checked: what reads them later knows them the first time.
    """

    def __init__(self, module: ast.Module) -> None:
        """Start an empty table for `module`."""
        self.module: ast.Module = module
        self.recorded: dict[int, list[Recorded]] = {}
        self.assigned: dict[int, list[Assigned]] = {}  # each checked function's `self.x = value`s
        self.calls: dict[str, str] = {}
        self.methods: dict[str, dict[str, str]] = {}
        self.guesses: dict[str, frozenset[str]] = {}
        self.attributes: dict[str, dict[str, str]] = {}
        self.returned: Returned = Returned(self.calls, self.methods, self.guesses, self.attributes)
        self.entries: list[tuple[Slot, str]] = []
        self.stamps: dict[int, int] = {}

    def checked(self, func: FunctionDef, returns: list[Recorded], assigned: list[Assigned]) -> None:
        """Record a checked function's `return`s and `self.x = value`s; its return type, if they decide it."""
        self.stamps[id(func)] = len(self.entries)
        self.recorded[id(func)] = returns
        self.assigned[id(func)] = assigned
        self._completed(func)
        slot: Slot | None = slots(self.module).get(id(func))
        found: tuple[str, frozenset[str]] | None
        if (
            slot is None
            or not isinstance(func, ast.FunctionDef)
            or (found := _return_type(func, returns)) is None
        ):
            return
        annotation: str
        origins: frozenset[str]
        annotation, origins = found
        if slot.owner is None:
            self.calls[slot.name] = annotation
        else:
            self.methods.setdefault(slot.owner, {})[slot.name] = annotation
        if origins:
            self.guesses[slot.name if slot.owner is None else f"{slot.owner}.{slot.name}"] = origins
        self.entries.append((slot, annotation))

    def _completed(self, func: FunctionDef) -> None:
        """Type the attributes of `func`'s class, if it's the last of the class's methods to be checked."""
        node: ast.ClassDef | None = _owners(self.module).get(id(func))
        if (
            node is None
            or _class_names(self.module)[node.name] != 1
            or any(id(method) not in self.assigned for method in _methods(node))
        ):
            return
        name: str
        annotation: str
        origins: frozenset[str]
        for name, annotation, origins in _attributes(self.module, node, self.assigned):
            self.attributes.setdefault(node.name, {})[name] = annotation
            self.guesses[f"{node.name}.{name}"] = origins

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
    its own, which the rounds of `checker._returned` asked of every function again and again.

    Returns:
      Where each call starts (its line and column), and what it calls: a name (`f()`) or an
      attribute (`x.m()`), each `None` if not.

    """
    found: list[_Call] = []
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
    body: Sequence[ast.stmt],
    recorded: Mapping[int, Sequence[Recorded]],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Find the plain unannotated functions directly in `body` whose `return`s decide their type.

    Yields:
      Each one's name, return type, and what that rests on if it's a guess.

    """
    counts: dict[str, int] = {}
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, _FUNCTIONS):
            counts[stmt.name] = counts.get(stmt.name, 0) + 1
    for stmt in body:
        found: tuple[str, frozenset[str]] | None
        if (
            isinstance(stmt, ast.FunctionDef)
            and counts[stmt.name] == 1
            and (found := _return_type(stmt, recorded.get(id(stmt), ()))) is not None
        ):
            yield stmt.name, *found


def _return_type(func: ast.FunctionDef, returns: Sequence[Recorded]) -> tuple[str, frozenset[str]] | None:
    """Type a plain function from its recorded `return`s.

    Returns:
      The one type they all give, and what it rests on if any is a guess; or `None` if it's
      decorated, annotated, a generator, can fall off its end, or has a `return` without a value or
      of an unknown or different type.

    """
    if (
        func.decorator_list
        or func.returns is not None
        or not returns
        or _generator(func)
        or not terminates(func.body)
    ):
        return None
    types: set[str | None] = {None if found is None else found.annotation for found, _ in returns}
    found: str | None = next(iter(types)) if len(types) == 1 else None
    return None if found is None else (found, frozenset[str]().union(*(origins for _, origins in returns)))


@lru_cache(maxsize=16)  # read once per round, of the same module
def _classes(tree: ast.Module) -> tuple[ast.ClassDef, ...]:
    """Find every class the module defines, however deep.

    Returns:
      Them.

    """
    return tuple(classes(tree))


@lru_cache(maxsize=4096)  # asked of the same functions once per round
def _generator(func: ast.FunctionDef) -> bool:
    """Check whether `func` is a generator: a `yield` in its own body (not a nested function's).

    Returns:
      Whether it is.

    """
    return any(isinstance(node, ast.Yield | ast.YieldFrom) for node in _own(func.body))


def _own(found: Sequence[ast.AST]) -> Iterator[ast.AST]:
    """Walk `found` without entering a nested function, lambda or class.

    Yields:
      Each node.

    """
    node: ast.AST
    for node in found:
        yield node
        if not isinstance(node, _SCOPES):
            yield from _own(list(ast.iter_child_nodes(node)))


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
