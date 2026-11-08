"""A module's own tables `--fix` reads, read once for the cross-file index and the check."""

import ast
from collections import Counter
from collections.abc import Mapping
from typing import Final, NamedTuple

from constricter.fix.core.imports import rebound_names, taken_names
from constricter.fix.core.inherited import Lineage, lineage
from constricter.fix.core.signatures import AWAIT
from constricter.fix.values.targets import aliased_unions, named_tuples
from constricter.source import walked
from constricter.source.declarations import (
    class_methods,
    classes,
    held,
    held_class_methods,
    method_returns,
    partial_method_returns,
    partial_returns,
    returns,
    self_returns,
)
from constricter.source.decorators import Held, Pass, passes
from constricter.source.syntax import Start, import_bindings

_NEW_TYPES: Final = frozenset({"typing.NewType", "typing_extensions.NewType"})
_CALL: Final = "__call__"  # what calling an instance calls


class Tables(NamedTuple):
    """A module's own tables (see `returns`, `classes`, `method_returns`, `class_methods`).

    Its functions' declared returns (a `NewType` bound nowhere else returning itself: `Ref(name)` is
    a `Ref`; an instance of a callable class of its own, its `__call__`'s: see `_called_instances`),
    and its classes' attributes and methods' returns (their classmethods' and staticmethods' too,
    which an instance has as well; an `async` method's as what awaiting its call gives, its name
    after `signatures.AWAIT`), the attributes each takes from the module's other classes included
    (see `Lineage`); `held`, the functions other modules' decorators may give back, and `passes`,
    its own such decorators; `sides`, its classes' classmethods' and staticmethods' returns, those
    each takes from the module's other classes included (see `Lineage`), and `held_sides`, those
    other modules' decorators may give back; `side_calls`, `sides` as called on the class (see
    `_side_calls`). `partial` and
    `partial_methods`: its functions' and methods' returns that are tuples with a vague part.
    `tuples`: its named tuples, each with the tuple unpacking one gives (see `named_tuples`).
    `unions`: its type aliases of a union, each with the union (see `aliased_unions`).
    """

    returns: dict[str, str]
    classes: dict[str, dict[str, str]]
    methods: dict[str, dict[str, str]]
    held: dict[str, Held]
    passes: dict[str, Pass]
    sides: dict[str, dict[str, str]]
    held_sides: dict[str, dict[str, Held]]
    side_calls: dict[str, str]
    partial: dict[str, str]
    partial_methods: dict[str, dict[str, str]]
    order: Lineage  # its classes' ancestry, as far as the module alone sees
    tuples: dict[str, str]
    unions: dict[str, str]


def module_tables(tree: ast.Module) -> Tables:
    """Read the module's own tables, once for the cross-file index and the check (see `parsed.keep`).

    Returns:
      Them.

    """
    own: dict[str, dict[str, str]] = class_methods(tree)
    order: Lineage = lineage(tree, self_returns(tree), frozenset())
    sides: dict[str, dict[str, str]] = order.flattened(own)
    awaited: dict[str, dict[str, str]] = method_returns(tree, awaited=True)
    made: list[str] = _new_types(tree)
    rebound: frozenset[str] = frozenset(rebound_names(tree)) if made else frozenset()
    methods: dict[str, dict[str, str]] = {
        owner: {
            **own.get(owner, {}),
            **plain,
            **{AWAIT + name: each for name, each in awaited[owner].items()},
        }
        for owner, plain in method_returns(tree).items()
    }
    return Tables(
        {
            **_called_instances(tree, order.flattened(methods)),
            **returns(tree),
            **{name: name for name in made if name not in rebound},
        },
        order.flattened(classes(tree)),
        methods,
        held(tree),
        passes(tree),
        sides,
        held_class_methods(tree),
        _side_calls(tree, sides),
        partial_returns(tree),
        partial_method_returns(tree),
        order,
        named_tuples(tree),
        aliased_unions(tree),
    )


def _side_calls(tree: ast.Module, sides: Mapping[str, Mapping[str, str]]) -> dict[str, str]:
    """Spell the calls to the module's classes' classmethods and staticmethods on the class itself.

    `Box.make()`, for a top-level class defined once whose name nothing in the module binds as a
    value (see `imports.taken_names`): there, the name is the class.

    Returns:
      Each call's name as written (`Box.make`), and its declared return.

    """
    if not any(sides.values()):  # most modules: no class-side method declares a return
        return {}
    values: frozenset[str] = taken_names(tree)[1]
    counts: Counter[str] = Counter(node.name for node in walked.classes(tree))
    return {
        f"{stmt.name}.{name}": annotation
        for stmt in tree.body
        if isinstance(stmt, ast.ClassDef) and counts[stmt.name] == 1 and stmt.name not in values
        for name, annotation in sides.get(stmt.name, {}).items()
    }


def _called_instances(tree: ast.Module, methods: Mapping[str, Mapping[str, str]]) -> dict[str, str]:
    """Type the calls of the module's instances of its callable classes: `gettz(name)`, by `gettz: _GetTZ`.

    A top-level name bound once, declared (`gettz: _GetTZ`) or bound (`add = Adder()`) as an
    instance of a top-level class defined once whose name nothing binds as a value, which has a
    `__call__` (its own, or one it takes from the module's other classes) declaring a return as
    `method_returns` reads one: not a generic class's, nor an `async` one's.

    Returns:
      Each such name, and that return.

    """
    if not any(_CALL in each for each in methods.values()):  # most modules: no callable class
        return {}
    rebound: dict[str, list[Start]] = rebound_names(tree)
    values: frozenset[str] = taken_names(tree)[1]
    counts: Counter[str] = Counter(node.name for node in walked.classes(tree))
    top: frozenset[str] = frozenset(stmt.name for stmt in tree.body if isinstance(stmt, ast.ClassDef))
    found: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    klass: str
    for stmt in tree.body:
        match stmt:
            case (
                ast.AnnAssign(target=ast.Name(id=name), annotation=ast.Name(id=klass))
                | ast.Assign(targets=[ast.Name(id=name)], value=ast.Call(func=ast.Name(id=klass)))
            ) if (
                name not in rebound
                and klass in top
                and counts[klass] == 1
                and klass not in values
                and _CALL in methods.get(klass, {})
            ):
                found[name] = methods[klass][_CALL]
            case _:
                pass
    return found


def _new_types(tree: ast.Module) -> list[str]:
    """Name the module's `NewType`s: `Ref = NewType("Ref", str)`, at its top level.

    By `typing`'s or `typing_extensions`' `NewType`, however it's imported.

    Returns:
      Them.

    """
    made: list[tuple[str, ast.Name | ast.Attribute]] = []
    stmt: ast.stmt
    name: str
    func: ast.expr
    text: str
    for stmt in tree.body:
        match stmt:
            case ast.Assign(
                targets=[ast.Name(id=name)],
                value=ast.Call(
                    func=ast.Name() | ast.Attribute() as func,
                    args=[ast.Constant(value=str() as text), _],
                ),
            ) if text == name:
                made.append((name, func))
            case _:
                pass
    if not made:  # most modules
        return []
    bound: dict[str, str] = {name: origin for name, origin, _ in import_bindings(tree.body)}
    return [name for name, func in made if _origin(func, bound) in _NEW_TYPES]


def _origin(func: ast.Name | ast.Attribute, bound: Mapping[str, str]) -> str | None:
    """Resolve a callee one or two names long through the module's imports (`bound`).

    Returns:
      Its dotted origin (`typing.NewType`), or `None`.

    """
    name: str
    attr: str
    match func:
        case ast.Name(id=name):
            return bound.get(name)
        case ast.Attribute(value=ast.Name(id=name), attr=attr) if name in bound:
            return f"{bound[name]}.{attr}"
        case _:
            return None
