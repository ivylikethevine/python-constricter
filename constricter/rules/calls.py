# SPDX-License-Identifier: MIT
"""What a module passes checked files' functions whose parameters aren't all annotated (`observed`).

Each call to one is recorded with what `--fix` knows each argument's type to be where it's made: in a
function, by that function's scope; elsewhere (a module or class body, a lambda), by the value alone.
Only a type made of builtins alone counts (`int`, `list[str]`, not a union): another's spelling may
mean nothing in the callee's module, and a union is what a check narrows. A guess counts, with what
it rests on: `--unsafe-fixes` writes it, and the next run would take it as certain. A function
used any way but called (a callback, a stored reference) escapes: its callers can't all be known.
A name the calling function binds itself isn't the module's function, whatever it's called.
"""

import ast
import builtins
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Final, cast

from constricter.fix.core.known import (
    Call,
    Callee,
    ImportPlan,
    Inference,
    Known,
    LibraryNames,
    Observed,
    Passed,
    Seeds,
)
from constricter.fix.index import callers, fixtures
from constricter.fix.values.guesses import guessing
from constricter.fix.values.inference import inference, scalar
from constricter.rules.annotations import dotted
from constricter.rules.decorators import is_fixture
from constricter.rules.flow import members
from constricter.rules.scope import Scope, Seeded, Settings, guesses_in
from constricter.rules.syntax import FunctionDef, Start, has_within, own_nodes
from constricter.rules.walked import of_type

_BUILTINS: Final = frozenset(dir(builtins))
_TEST: Final = "test"  # how pytest's test functions' names start
_NONE: Final = "None"  # says nothing of what the parameter's other callers pass, nor what it's for
# pytest's own fixtures whose value is a standard-library class's instance: each one's class.
_OWN_FIXTURES: Final = {"tmp_path": "pathlib.Path"}
_DEFINED: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)  # what binds a name, inside


def observed(
    tree: ast.Module,
    scopes: Sequence[Scope],
    known: Known,
    callees: Mapping[str, Callee],
) -> Observed:
    """Find what the module passes, and does with, the functions in `callees` (as it spells them).

    Returns:
      Each one's calls, and those that escape.

    """
    named: list[tuple[ast.AST, str]]
    if not (named := _naming(tree, callees) if callees else []):
        return Observed()
    owner: dict[int, Scope]  # each such node's innermost function scope, by `id()`
    bound: dict[int, frozenset[str]]  # each of those functions' own names, by its scope's `id()`
    owner, bound = _owning(scopes, [node for node, _ in named])
    called: set[int] = {id(node.func) for node in cast("list[ast.Call]", of_type(tree, ast.Call))}
    calls: dict[Callee, list[Call]] = {}
    escaped: set[Callee] = set()
    node: ast.AST
    spelled: str
    for node, spelled in named:
        where: Scope | None = owner.get(id(node))
        if where is not None and spelled.partition(".")[0] in bound[id(where)]:
            continue
        if isinstance(node, ast.Call):
            calls.setdefault(callees[spelled], []).append(_call(node, where, known))
        elif id(node) not in called and isinstance(cast("ast.Name", node).ctx, ast.Load):
            escaped.add(callees[spelled])
    return Observed({callee: tuple(found) for callee, found in calls.items()}, frozenset(escaped))


def _owning(
    scopes: Sequence[Scope],
    named: Sequence[ast.AST],
) -> tuple[dict[int, Scope], dict[int, frozenset[str]]]:
    """Find the innermost function scope of each node in `named`, and what each such function binds.

    Only the functions one of them is in are walked: most have none.

    Returns:
      Each node's scope, by the node's `id()` (none for one outside any function's own body); and
      each of those scopes' function's own names, by the scope's `id()`.

    """
    wanted: set[int] = {id(node) for node in named}
    starts: list[Start] = sorted(
        (cast("ast.expr", node).lineno, cast("ast.expr", node).col_offset) for node in named
    )
    owner: dict[int, Scope] = {}
    bound: dict[int, frozenset[str]] = {}
    scope: Scope
    for scope in scopes:
        if scope.kind.function is not None and has_within(starts, scope.kind.function):
            nodes: list[ast.AST] = list(own_nodes(scope.kind.function.body))
            owner.update((id(node), scope) for node in nodes if id(node) in wanted)
            bound[id(scope)] = _bound(scope.kind.function, nodes)
    return owner, bound


def _naming(tree: ast.Module, callees: Mapping[str, Callee]) -> list[tuple[ast.AST, str]]:
    """Find the module's calls, names and attributes that spell one of `callees`.

    From its one shared walk, each looked at only if its last name is one of theirs.

    Returns:
      Each such node, with what it spells (a call's callee), calls first, each kind in the walk's order.

    """
    last: frozenset[str] = frozenset(spelled.rpartition(".")[2] for spelled in callees)
    found: list[tuple[ast.AST, str]] = []
    node: ast.AST
    for node in of_type(tree, ast.Call, ast.Name, ast.Attribute):
        target: ast.AST = node.func if isinstance(node, ast.Call) else node
        name: str = (
            target.id
            if isinstance(target, ast.Name)
            else target.attr
            if isinstance(target, ast.Attribute)
            else ""
        )
        spelled: str | None = dotted(cast("ast.expr", target)) if name in last else None
        if spelled is not None and spelled in callees:
            found.append((node, spelled))
    return found


def _bound(function: ast.FunctionDef | ast.AsyncFunctionDef, nodes: Sequence[ast.AST]) -> frozenset[str]:
    """Name what a function binds itself: its parameters, and what it assigns or imports.

    Returns:
      Them.

    """
    args: ast.arguments = function.args
    params: list[ast.arg | None] = [*args.posonlyargs, *args.args, *args.kwonlyargs, args.vararg, args.kwarg]
    return frozenset(
        [
            *(arg.arg for arg in params if arg is not None),
            *(node.id for node in nodes if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)),
            *(
                (alias.asname or alias.name).partition(".")[0]
                for node in nodes
                if isinstance(node, ast.Import | ast.ImportFrom)
                for alias in node.names
            ),
            *(node.name for node in nodes if isinstance(node, _DEFINED)),
        ],
    )


def _call(call: ast.Call, where: Scope | None, known: Known) -> Call:
    """Read one call's arguments' types (see the module docstring).

    Returns:
      Them; a call unpacking `*args` or `**kwargs` is only marked so.

    """
    if any(isinstance(arg, ast.Starred) for arg in call.args) or any(k.arg is None for k in call.keywords):
        return Call(unpacked=True)
    return Call(
        tuple(_type(arg, where, known) for arg in call.args),
        tuple((keyword.arg or "", _type(keyword.value, where, known)) for keyword in call.keywords),
    )


def _type(value: ast.expr, where: Scope | None, known: Known) -> Passed | None:
    """Type one argument, with builtins alone (see the module docstring).

    Returns:
      Its type, and what it rests on if it's a guess; or `None`.

    """
    typed: Inference | None
    guess: tuple[bool, frozenset[str]]
    if where is None:
        typed = inference(value, known, {})
        guess = guessing(value, known, frozenset(), {}, {})
    else:
        typed = inference(value, where.settings.known, where.inferred.types)
        guess = guesses_in(where, [value])
    if typed is None or not plain(typed.annotation, known):
        return None
    return typed.annotation, guess[1] if guess[0] else frozenset()


def plain(annotation: str, known: Known) -> bool:
    """Check an annotation is made of builtins alone, none of them rebound, and isn't a union.

    Returns:
      Whether it is.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    return (
        annotation != _NONE
        and len(members(annotation) or ()) == 1
        and all(
            isinstance(node, ast.Name) and node.id in _BUILTINS and known.is_builtin(node.id)
            for node in ast.walk(tree)
            if isinstance(node, ast.Name | ast.Attribute)
        )
    )


def keyed(tree: ast.Module, typed: Seeds) -> dict[int, Mapping[str, Passed]]:
    """Key what every call passes the module's top-level functions' parameters by each function's `id()`.

    A nested function or method of the same name isn't the one its callers call.

    Returns:
      Each function's parameters' types.

    """
    return {
        id(stmt): typed[stmt.name]
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef) and stmt.name in typed
    }


def seed_parameters(scope: Scope, func: FunctionDef, named: Sequence[ast.arg]) -> None:
    """Type the unannotated parameters every call passes one type (see `fix.index.callers`), as guesses.

    Not one the function binds again itself, whose type a guess from its callers wouldn't be after.
    """
    seeded: Seeded = scope.settings.parameters or Seeded()
    typed: Mapping[str, Passed] = seeded.callers.get(id(func), {})
    injected: Mapping[str, Passed] = _injected(seeded, func, scope.settings.known)
    if not (typed or injected):
        return
    rebound: set[str] = {
        node.id
        for node in own_nodes(func.body)
        if isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load)
    }
    arg: ast.arg
    for arg in named:
        given: Passed | None = typed.get(arg.arg)
        if arg.annotation is not None or arg.arg in rebound:
            continue
        if arg.arg in injected:
            scope.inferred.learn(arg.arg, *injected[arg.arg])
        elif given is not None and plain(given[0], scope.settings.known):
            scope.inferred.learn(arg.arg, given[0], frozenset({callers.KIND}) | given[1])


def _injected(seeded: Seeded, func: FunctionDef, known: Known) -> Mapping[str, Passed]:
    """Type the parameters pytest gives a test or a fixture: its fixtures' values, and `parametrize`'s.

    A fixture the module's tests can take (see `fix.index.fixtures`), by its name, or else one of
    pytest's own (`tmp_path`, a `Path`: see `_OWN_FIXTURES`); and, before them, a name
    `@pytest.mark.parametrize` gives literals of one type. Guesses (`fixture`).

    Returns:
      Each such parameter's type and what it rests on; nothing for any other function.

    """
    if not (func.name.startswith(_TEST) or is_fixture(func)):
        return {}
    return {**_own(func, known), **seeded.fixtures, **_parametrized(func)}


def _own(func: FunctionDef, known: Known) -> dict[str, Passed]:
    """Type the parameters of `func` that name pytest's own fixtures (see `_OWN_FIXTURES`).

    Returns:
      Each one's type, as the module can write it, a guess resting on `fixture`.

    """
    plan: ImportPlan | None = known.names.plan
    args: ast.arguments = func.args
    named: set[str] = {arg.arg for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
    found: dict[str, Passed] = {}
    name: str
    for name in sorted(_OWN_FIXTURES.keys() & named):
        spelled: str | None
        if (spelled := None if plan is None else plan.spell(_OWN_FIXTURES[name])) is not None:
            found[name] = (spelled, frozenset({fixtures.KIND}))
    return found


def _parametrized(func: FunctionDef) -> dict[str, Passed]:
    """Type the names `@pytest.mark.parametrize` gives a function literals of one type each.

    `"n"` with `[1, 2]`, or `"n, s"` (or `("n", "s")`) with `[(1, "a"), (2, "b")]`.

    Returns:
      Each one's type, a guess resting on `fixture`.

    """
    found: dict[str, Passed] = {}
    decorator: ast.expr
    for decorator in func.decorator_list:
        names: list[str]
        rows: list[list[ast.expr]]
        names, rows = _cases(decorator)
        at: int
        name: str
        for at, name in enumerate(names):
            types: set[str | None] = {scalar(row[at]) if len(row) == len(names) else None for row in rows}
            only: str | None = types.pop() if len(types) == 1 else None
            if only is not None and only != _NONE:
                found[name] = (only, frozenset({fixtures.KIND}))
    return found


def _cases(decorator: ast.expr) -> tuple[list[str], list[list[ast.expr]]]:
    """Read a `parametrize` decorator: the names it gives values, and each case's values.

    Returns:
      Them; no names for any other decorator, or one whose names or cases aren't written out.

    """
    names: ast.expr
    cases: list[ast.expr]
    parts: list[ast.expr]
    text: str
    match decorator:
        case ast.Call(func=ast.Attribute(attr="parametrize"), args=[names, ast.List(elts=cases), *_]):
            pass
        case _:
            return [], []
    found: list[str]
    match names:
        case ast.Constant(value=str() as text):
            found = [part.strip() for part in text.split(",")]
        case ast.Tuple(elts=parts) | ast.List(elts=parts) if all(
            isinstance(part, ast.Constant) and isinstance(part.value, str) for part in parts
        ):
            found = [str(cast("ast.Constant", part).value) for part in parts]
        case _:
            return [], []
    if len(found) == 1:
        return found, [[case] for case in cases]
    return found, [list(case.elts) if isinstance(case, ast.Tuple | ast.List) else [] for case in cases]


def unshadowed(settings: Settings, function: FunctionDef) -> Settings:
    """Drop the standard-library names a function binds itself from what it's checked knowing.

    A parameter, local, import or nested definition named `getpid` isn't `os.getpid`, whatever the
    module imports; the functions inside it are checked knowing the same.

    Returns:
      The settings, less those names; the same settings if it binds none of them.

    """
    names: LibraryNames = settings.known.names
    rebound: Mapping[str, Sequence[Start]] | None = settings.facts.rebound
    # Most functions can shadow none: no name the module imports is bound in them. They aren't walked.
    if rebound is not None and not any(
        has_within(rebound[name], function) for name in names.stdlib.keys() & rebound.keys()
    ):
        return settings
    bound: frozenset[str]
    if not (bound := _bound(function, list(own_nodes(function.body))) & names.stdlib.keys()):
        return settings
    stdlib: dict[str, str] = {name: origin for name, origin in names.stdlib.items() if name not in bound}
    return replace(settings, known=replace(settings.known, names=names._replace(stdlib=stdlib)))
