"""`--fix` for calls to unannotated functions: their own `return` statements decide their type.

A function (or method) counts when it's plain (a `def` directly in the module or a class body, not
decorated or redefined), declares no return type, every `return` it has gives a value whose type
`--fix` is sure of, all the same, and it can't fall off its end (which returns `None`). A generator
counts by its `yield`s instead, all of one type `T`: a `Generator[T, None, None]` (see
`constricter.rules.recorded`). An `async def`'s `return`s type what awaiting its call gives, under
`AWAIT` before its name; a function `@contextmanager` makes a manager, what `with` gives of it,
under `entered.ENTERED`. A module function's type is certain; a method's is a guess, since a
subclass may override it. Each value is typed as the checker sees it there, with the function's own
locals.
"""

import ast
import operator
from collections.abc import Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.imports import bound_within
from constricter.fix.core.inherited import Lineage
from constricter.fix.core.known import Returned, Returns
from constricter.fix.core.signatures import AWAIT
from constricter.fix.values import entered
from constricter.fix.values.bodies import is_generator, plain, terminates
from constricter.fix.values.inference import RETURNED
from constricter.fix.values.stored import (
    Assigned,
    Recorded,
    Used,
    attribute_types,
    class_names,
    owners,
    self_methods,
    subclasses,
    superclasses,
)
from constricter.source.annotations import roots
from constricter.source.decorators import FIXTURES, spelled
from constricter.source.flow import members
from constricter.source.syntax import FunctionDef, Start, within
from constricter.source.walked import classes, of_type

_NONE: Final = "None"
_UNVOUCHED: Final[frozenset[str]] = frozenset()  # no decorator vouched for: a module read alone
# What a call calls: a name (`f()`), or an attribute (`x.m()`), the other `None`.
_Callee: TypeAlias = tuple[str | None, str | None]
_Call: TypeAlias = tuple[tuple[int, int], _Callee]  # where a call starts (line, column), and what it calls


def returned(
    tree: ast.Module,
    recorded: Mapping[int, Sequence[Recorded]],
    assigned: Mapping[int, Sequence[Assigned]],
    used: Mapping[int, Sequence[Used]],
    vouched: frozenset[str] = _UNVOUCHED,
) -> Returned:
    """Read what the module's unannotated functions and methods return, and what its classes assign.

    `recorded` holds each checked function's `return` statements, `assigned` its `self.x = value`
    assignments and `used` its reads of `self`'s empty containers, by the function's `id()`;
    `vouched` spells the decorators that give a function back (see `constricter.source.decorators`).

    Returns:
      Their return types: the module's functions', and each class's methods'; and each class's
      unannotated instance attributes' types (see `attribute_types`).

    """
    calls: dict[str, str] = {}
    methods: dict[str, dict[str, str]] = {}
    guesses: dict[str, frozenset[str]] = {}
    name: str
    annotation: str
    origins: frozenset[str]
    for name, annotation, origins in _typed(tree, tree.body, recorded, vouched):
        calls[name] = annotation
        if origins:
            guesses[name] = origins
    attributes: dict[str, dict[str, str]] = {}
    node: ast.ClassDef
    for node in classes(tree):
        for name, annotation, origins in _typed(tree, node.body, recorded, vouched):
            methods.setdefault(node.name, {})[name] = annotation
            if origins:
                guesses[f"{node.name}.{name}"] = origins
        if class_names(tree)[node.name] == 1:  # its attributes are looked up by its name
            _attributes(tree, node, (assigned, used), (attributes, guesses))
    return Returned(calls, methods, guesses, attributes)


def _attributes(
    tree: ast.Module,
    node: ast.ClassDef,
    seen: tuple[Mapping[int, Sequence[Assigned]], Mapping[int, Sequence[Used]]],
    tables: tuple[dict[str, dict[str, str]], dict[str, frozenset[str]]],
) -> None:
    """Enter the class's attributes' types (see `attribute_types`) in `tables`: attributes, and guesses."""
    name: str
    annotation: str
    origins: frozenset[str]
    for name, annotation, origins in attribute_types(tree, node, seen):
        tables[0].setdefault(node.name, {})[name] = annotation
        tables[1][f"{node.name}.{name}"] = origins


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


def unannotated(body: Sequence[ast.stmt], vouched: frozenset[str] = _UNVOUCHED) -> frozenset[str]:
    """Name the functions in `body` whose `return`s could type their calls (see `_return_type`).

    Returns:
      Each plain function's name that has no declared return, nor a decorator but those `vouched`
      spells (see `constricter.source.decorators`).

    """
    return frozenset(
        func.name
        for func in plain(body)
        if isinstance(func, ast.FunctionDef) and not _decorated(func, vouched) and func.returns is None
    )


def held_back(body: Sequence[ast.stmt]) -> dict[str, tuple[str, ...]]:
    """Name the functions in `body` whose `return`s could type their calls, but for their decorators.

    Returns:
      Each plain function's name that has no declared return, with its decorators as spelled: another
      module may vouch for them (see `constricter.fix.index.decorated`). Not one with a decorator
      that can't be spelled.

    """
    found: dict[str, tuple[str, ...]] = {}
    func: FunctionDef
    for func in plain(body):
        if isinstance(func, ast.FunctionDef) and func.returns is None and _decorated(func, _UNVOUCHED):
            spellings: list[str | None] = [spelled(each) for each in func.decorator_list]
            if None not in spellings:
                found[func.name] = tuple(text for text in spellings if text is not None)
    return found


def called(module: ast.Module, node: ast.AST, found: Returned) -> bool:
    """Check whether `node` (the module, a function, or a statement in it) calls any function `found` types.

    By name, or as a method. A function's decorators aren't its own calls: they're before it.

    Returns:
      Whether it does: otherwise checking it again would change nothing.

    """
    methods: set[str] = {_called(name) for methods in found.methods.values() for name in methods}
    calls: set[str] = {_called(name) for name in found.calls}
    return any(name in calls or attr in methods for name, attr in callees_in(module, node))


def _called(key: str) -> str:  # a table's entry's function's name (see `_key`)
    return key.removeprefix(entered.ENTERED).removeprefix(AWAIT)


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


def callees_in(module: ast.Module, node: ast.AST) -> Sequence[_Callee]:
    """Find what `node` (the module, a function, or a statement in it) calls, by its span of the source.

    Returns:
      Each call's callee: a name (`f()`) or an attribute (`x.m()`).

    """
    starts: list[Start]
    callees: list[_Callee]
    starts, callees = _calls(module)
    return callees[within(starts, node)]


class Slot(NamedTuple):
    """Where a function's return type goes in the table: its class (`None`: the module's), and its name."""

    owner: str | None
    name: str


@lru_cache(maxsize=4)
def slots(module: ast.Module) -> dict[int, Slot]:
    """Find the functions whose `return`s can type their calls: plain, directly in the module or a class.

    As `_typed` finds them (see `bodies.plain`).

    Returns:
      Each one's slot, by the function's `id()`.

    """
    return {
        id(func): Slot(owner, _key(func))
        for owner, body in ((None, module.body), *((node.name, node.body) for node in classes(module)))
        for func in plain(body)
    }


def _key(func: FunctionDef) -> str:
    """Name a function's entry in the tables: its name, after what says how its call is read.

    Returns:
      It: after `AWAIT` for an `async def`, `entered.ENTERED` for a manager (see the module docstring).

    """
    if isinstance(func, ast.AsyncFunctionDef):
        return f"{AWAIT}{func.name}"
    return f"{entered.ENTERED}{func.name}" if entered.is_manager(func) else func.name


def _decorated(func: FunctionDef, vouched: frozenset[str]) -> bool:
    """Check whether a function has a decorator that may change what calling it gives.

    Not a pytest fixture's: the fixture's value is what the function returns (or yields). Nor one
    `vouched` spells, which gives the function back.

    Returns:
      Whether it has.

    """
    return any(spelled(each) not in FIXTURES and spelled(each) not in vouched for each in func.decorator_list)


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

    def __init__(
        self,
        module: ast.Module,
        imported: Returns | None = None,
        vouched: frozenset[str] = _UNVOUCHED,
    ) -> None:
        """Start a table for `module`, with what the functions it imports from other files return.

        `vouched` spells the decorators that give a function back (see `constricter.source.decorators`).
        """
        imported = imported or Returns()
        self.module: ast.Module = module
        self.vouched: frozenset[str] = vouched
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
        if slot is None or (found := _return_type(self.module, func, returns, self.vouched)) is None:
            return
        annotation: str
        origins: frozenset[str]
        annotation, origins = found
        _enter(slot, annotation, self.tables.calls, self.tables.methods)
        if origins:
            self.tables.guesses[slot.name if slot.owner is None else f"{slot.owner}.{slot.name}"] = origins
        self.entries.append((slot, annotation))

    def _completed(self, func: FunctionDef) -> None:
        """Type the attributes of `func`'s class (and those above it) whose methods are all checked now."""
        own: ast.ClassDef | None = owners(self.module).get(id(func))
        above: list[ast.ClassDef] = [] if own is None else superclasses(self.module, own)
        node: ast.ClassDef
        for node in above if own is None else (own, *above):
            # With the classes under it: their methods fill its empty containers too.
            if class_names(self.module)[node.name] != 1 or any(
                id(method) not in self.assigned
                for each in (node, *subclasses(self.module, node))
                for method in self_methods(each)
            ):
                continue
            _attributes(
                self.module,
                node,
                (self.assigned, self.used),
                (self.tables.attributes, self.tables.guesses),
            )

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
            _enter(slot, annotation, calls, methods)
        return bool(newer) and called(self.module, func, Returned(calls, methods))


def _enter(slot: Slot, annotation: str, calls: dict[str, str], methods: dict[str, dict[str, str]]) -> None:
    """Enter a function's return type in its slot: in `calls` for the module's, in `methods` for a class's."""
    if slot.owner is None:
        calls[slot.name] = annotation
    else:
        methods.setdefault(slot.owner, {})[slot.name] = annotation


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
    vouched: frozenset[str],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Find the plain unannotated functions directly in `body` whose `return`s decide their type.

    Yields:
      Each one's name, return type, and what that rests on if it's a guess.

    """
    func: FunctionDef
    for func in plain(body):
        found: tuple[str, frozenset[str]] | None
        if (found := _return_type(module, func, recorded.get(id(func), ()), vouched)) is not None:
            yield _key(func), *found


def _return_type(
    module: ast.Module,
    func: FunctionDef,
    returns: Sequence[Recorded],
    vouched: frozenset[str],
) -> tuple[str, frozenset[str]] | None:
    """Type a plain function from its recorded `return`s.

    Returns:
      The one type they all give, and what it rests on if any is a guess; or `None` if it's
      decorated or annotated (by a `# type:` comment too), can fall off its end (but for a
      generator, recorded as its type; not an `async` one), or has a `return` without a value or
      of an unknown or different type.

    """
    manager: bool = entered.is_manager(func)
    declared: bool = func.returns is not None or bool(func.type_comment)
    # A generator's type is its `yield`s' (not an `async` one's); any other must end by a `return`.
    decided: bool = (
        isinstance(func, ast.FunctionDef)
        if is_generator(module, func)
        else terminates(func.body) and not manager
    )
    if (_decorated(func, vouched) and not manager) or declared or not returns or not decided:
        return None
    types: set[str | None] = {None if found is None else found.annotation for found, _ in returns}
    found: str | None
    if (found := next(iter(types)) if len(types) == 1 else None) is None:
        return None
    if roots(found) & bound_within(func):  # a class it imports or defines itself: no caller can name it
        return None
    # An `X | None` is a guess: a type checker takes the unannotated function's call for anything,
    # and what its callers do with it unchecked for `None` is an error only once it's declared.
    doubted: frozenset[str] = frozenset({RETURNED}) if _NONE in (members(found) or ()) else frozenset()
    return found, doubted.union(*(origins for _, origins in returns))
