"""A module's scopes, built for a check: each function's and class body's, their statements visited.

What each binds and declares, in order, and which of them a check already finished.
"""

import ast
from collections.abc import Mapping, Sequence
from typing import Final, cast

from constricter.fix.core import imports
from constricter.fix.core.known import (
    Passed,
)
from constricter.fix.values import ordered, returned
from constricter.offences import (
    UNANNOTATED,
    UNANNOTATED_MEMBER,
)
from constricter.rules import binding, late, recorded
from constricter.rules.annotations import node_name
from constricter.rules.calls import seed_parameters, unshadowed
from constricter.rules.declarations import (
    imported_from,
)
from constricter.rules.narrowing import module_names
from constricter.rules.quoted import written
from constricter.rules.scope import Scope
from constricter.rules.scoped import Kind, Late, Seeded, Settings
from constricter.rules.syntax import (
    BRANCHING,
    FunctionDef,
    Start,
    arm_ends,
    child_statements,
    collect_functions,
    expressions,
    has_within,
    target_names,
)
from constricter.rules.walked import classes

# The node class of `type X = ...` statements, by name: Python 3.11's `ast` has no `TypeAlias`.
_TYPE_ALIAS: Final = "TypeAlias"
_CLASSMETHOD: Final = "classmethod"


# Enum members mustn't be annotated: a base imported from here is one, however it's aliased.
_ENUM_MODULES: Final = frozenset({"enum"})
# The conventional name of an instance method's first parameter: typed as its class, for `--fix`.
_SELF: Final = "self"


def bound_once(tree: ast.Module, settings: Settings) -> dict[str, Passed]:
    """Type the names the module binds once, anywhere in it, at its top level: what its functions read.

    `LIMIT = 10` is an `int` in every function, and `NAMES: Final = ["a"]` a `list[str]`: a name bound
    once means the same thing throughout (see `imports.rebound_names`), and a type checker takes its
    one value's type for its own. As the module's body types it, before its functions are checked.

    Returns:
      Each such name's type, and what it rests on if it's a guess.

    """
    scope: Scope = _body_scope(tree.body, settings, Kind(UNANNOTATED_MEMBER, fixable=True))
    rebound: Mapping[str, list[Start]] = imports.rebound_names(tree)
    return {
        name: (held, scope.inferred.origins.get(name, frozenset()))
        for name, held in scope.inferred.types.items()
        if name not in rebound
    }


def module_scopes(tree: ast.Module, settings: Settings, table: returned.Table | None = None) -> list["Scope"]:
    """Collect the scopes to check.

    With a `table` (see `returned.Table`), the functions are checked callees first, each one's
    return type recorded as soon as it's checked: a caller checked later knows it the first time.

    Returns:
      Every function's scope, and with `all_scopes` every module and class body's.

    """
    functions: list[FunctionDef] = []
    collect_functions(tree.body, functions)
    if table is not None:
        functions = ordered.in_call_order(tree, functions)
    scopes: list[Scope] = _function_scopes(functions, settings, table)
    if settings.checks.all_scopes:
        scopes += body_scopes(tree, settings)
    return scopes


def body_scopes(tree: ast.Module, settings: Settings) -> list["Scope"]:
    """Collect the module and class bodies (LVA004).

    Returns:
      Their scopes, but for an enum's.

    """
    imported: frozenset[str] = imported_from(tree, _ENUM_MODULES)
    # A class body isn't fixed: annotating a dataclass's variable makes it a field. A plain class's
    # variable typed by its value is (see `Scope.assign`).
    return [
        _body_scope(tree.body, settings, Kind(UNANNOTATED_MEMBER, fixable=True)),
        *(
            _body_scope(node.body, settings, Kind(UNANNOTATED_MEMBER, fixable=False, owner=node.name))
            for node in classes(tree)
            if not _is_enum(node, imported)
        ),
    ]


def _body_scope(body: list[ast.stmt], settings: Settings, kind: Kind) -> "Scope":
    """Check one module's or class's body.

    Returns:
      Its scope.

    """
    scope: Scope = Scope({"_"}, [], settings, kind)
    stmt: ast.stmt
    for stmt in body:
        _visit(scope, stmt)
    return scope


def _is_enum(node: ast.ClassDef, imported: frozenset[str]) -> bool:
    """Check whether a base is an enum: enum members mustn't be annotated.

    Returns:
      Whether a base is imported from `enum` (`imported`, however it's aliased), or else its name
      ends in `Enum` or `Flag` (for one imported some other way).

    """
    return any(
        node_name(base) in imported or node_name(base).endswith(("Enum", "Flag")) for base in node.bases
    )


def _function_scopes(
    functions: list[FunctionDef],
    settings: Settings,
    table: returned.Table | None = None,
) -> list["Scope"]:
    """Check `functions` and every function defined inside them (recording each in `table`).

    Returns:
      Their scopes.

    """
    scopes: list[Scope] = []
    func: FunctionDef
    for func in functions:
        nested: list[FunctionDef] = []
        scope: Scope = function_scope(func, nested, settings)
        scopes.append(scope)
        if table is not None:
            finish(table.module, [scope])
            # Its returns are typed as it's checked; but one with late types (`None` rebound, ...) is
            # checked again knowing them (`_returned`), and until then nothing's recorded: a caller
            # would take its type too soon (`int`, for `None` rebound to `int`: `int | None`).
            settled: bool = not scope.inferred.late.keys() - scope.inferred.seeded.keys()
            table.checked(
                func,
                recorded.returns(scope, func, table.module) if settled else [],
                (recorded.assigned(scope), recorded.used(scope, func, table.module)) if settled else ([], []),
            )
        scopes += _function_scopes(nested, scope.settings, table)
    return scopes


def function_scope(
    func: FunctionDef,
    functions: list[FunctionDef],
    settings: Settings,
    seed: Mapping[str, Late] | None = None,
) -> "Scope":
    """Check one function; functions defined in it are collected into `functions`.

    `seed`: names already known to be typed late (see `Inferred.late`), known from the start.

    Returns:
      Its scope.

    """
    settings = unshadowed(settings, func)
    args: ast.arguments = func.args
    named: tuple[ast.arg, ...] = (*args.posonlyargs, *args.args, *args.kwonlyargs)
    params: set[str] = {a.arg for a in named}
    params.update(extra.arg for extra in (args.vararg, args.kwarg) if extra is not None)
    # `_` is a discard.
    scope: Scope = Scope(
        params | {"_"},
        functions,
        settings,
        Kind(UNANNOTATED, fixable=True, function=func),
    )
    # A copy of a plain, annotated parameter (`*args`/`**kwargs` aren't the type they're annotated
    # with) can be typed the same way, the moment it's assigned.
    scope.inferred.types.taking(
        {arg.arg: written(arg.annotation) for arg in named if arg.annotation is not None},
    )
    # A method's `self` is its class's instance; so is the `self` a function defined in it reads.
    owner: str | None = settings.owners.get(id(func))
    if owner is not None and (_SELF not in params or [arg.arg for arg in named[:1]] == [_SELF]):
        _ = scope.inferred.types.setdefault(_SELF, owner)
    # A classmethod's first parameter is its class (`type[C]`), whatever it's called.
    if owner is not None and named and [node_name(d) for d in func.decorator_list] == [_CLASSMETHOD]:
        _ = scope.inferred.types.setdefault(named[0].arg, f"type[{owner}]")
    seed_parameters(scope, func, named)
    # What the module's top level binds once, the function reads as it's typed there.
    name: str
    passed: Passed
    for name, passed in (settings.parameters or Seeded()).module.items():
        scope.inferred.learn(name, passed[0], passed[1] or None)
    arg: ast.arg
    for arg in named:
        # A parameter holds whatever its callers pass: its declared type, as far as value flow knows.
        if arg.annotation is not None:
            scope.lifetime(arg.arg).declare(ast.unparse(arg.annotation), (arg.lineno, arg.col_offset))
        scope.lifetime(arg.arg).bind(
            (arg.lineno, arg.col_offset),
            None if arg.annotation is None else ast.unparse(arg.annotation),
        )
    scope.opaque(extra.arg for extra in (args.vararg, args.kwarg) if extra is not None)
    typed: Late
    for name, typed in (seed or {}).items():
        scope.inferred.seeded[name] = typed
        scope.inferred.learn(name, typed[0], typed[1] or None)
    stmt: ast.stmt
    for stmt in func.body:
        _visit(scope, stmt)
    return scope


def _visit(scope: Scope, stmt: ast.stmt, head: ast.stmt | None = None) -> None:
    """Bind the names `stmt` binds, as Python would, then visit its nested statements.

    `head`: for an `elif`, the `if` it belongs to, which a declaration of its `:=`'s goes before.
    """
    part: ast.AST
    walruses: tuple[Start, ...]
    if walruses := scope.settings.walruses:  # most modules have no `:=`: none of their parts need a look
        for part in expressions(stmt):
            if has_within(walruses, part):  # a `:=` in it
                binding.walruses(scope, part, head or stmt)
    _declare(scope, stmt)
    binding.bind(scope, stmt)
    if isinstance(stmt, ast.Return):
        scope.inferred.returns.append(stmt.value)
    elif isinstance(stmt, ast.Assign):
        scope.inferred.assigned.extend(
            (target.attr, stmt.value)
            for target in stmt.targets
            if isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == _SELF
        )
    # A loop's body runs again and again (not its `else`), for LVA012.
    body: set[int] = (
        {id(s) for s in stmt.body} if isinstance(stmt, ast.For | ast.AsyncFor | ast.While) else set()
    )
    before: dict[str, str] | None = dict(scope.inferred.types) if isinstance(stmt, BRANCHING) else None
    # What has no known type before it, or where one of its arms ends: it may still, past it.
    untyped: set[str] = set() if before is None else scope.declared - scope.inferred.types.keys()
    ends: frozenset[int] = frozenset() if before is None else arm_ends(stmt)
    child: ast.stmt
    for child in child_statements(stmt):
        scope.assignments.looping += id(child) in body
        _visit(scope, child, (head or stmt) if _is_elif(stmt, child) else None)
        scope.assignments.looping -= id(child) in body
        if before is not None and id(child) in ends:
            untyped |= scope.declared - scope.inferred.types.keys() - before.keys()
    if before is not None:
        scope.inferred.rejoined(before, frozenset(untyped))


def _is_elif(stmt: ast.stmt, child: ast.stmt) -> bool:
    """Check whether `child` is `stmt`'s `elif`: an `if`'s only `else` statement, an `if` at its own column.

    Returns:
      Whether it is.

    """
    return (
        isinstance(stmt, ast.If)
        and isinstance(child, ast.If)
        and stmt.orelse == [child]
        and child.col_offset == stmt.col_offset
    )


def _declare(scope: Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds that need no annotation, or carry their own."""
    aliases: list[ast.alias]
    names: list[str]
    handlers: list[ast.ExceptHandler]
    target: ast.Name
    match stmt:
        case ast.FunctionDef() | ast.AsyncFunctionDef():
            scope.declared.add(stmt.name)
            scope.opaque([stmt.name])
            scope.nested.append(stmt)  # its body is its own scope
        case ast.ClassDef():
            scope.declared.add(stmt.name)
            scope.opaque([stmt.name])
            collect_functions(stmt.body, scope.nested)  # methods of a class defined in a function
        case ast.Import(names=aliases) | ast.ImportFrom(names=aliases):
            names = [(alias.asname or alias.name).split(".")[0] for alias in aliases]
            scope.declared.update(names)
            scope.opaque(names)
        case ast.Global(names=names) | ast.Nonlocal(names=names):
            scope.declared.update(names)
        case ast.AnnAssign(target=ast.Name() as target):
            binding.annotated(scope, stmt, target)
        case _ if type(stmt).__name__ == _TYPE_ALIAS:
            alias: ast.expr = cast("ast.expr", next(ast.iter_child_nodes(stmt)))  # its first field, the name
            scope.declared.update(name.id for name in target_names(alias))
        case ast.Try(handlers=handlers) | ast.TryStar(handlers=handlers):
            names = [handler.name for handler in handlers if handler.name]
            scope.declared.update(names)
            scope.opaque(names)
        case _:
            pass


def finish(tree: ast.Module, scopes: Sequence[Scope]) -> None:
    """Finish `scopes` for their late fixes (`None` rebound, filled containers, shadowed types).

    Those need the names written out of sight marked first. Safe to run again: marking is
    idempotent, and no fix redoes one it made.
    """
    scope: Scope
    for scope in scopes:
        scope.mark_escaped(module_names(tree)[0])
        late.optionals(scope)
        late.rebinds(scope)
        late.extended(scope)
        late.fills(scope)
        late.lambdas(scope)
        late.widens(scope, tree)
        binding.redeclared(scope)
        late.shadowed(scope)
        late.excused(scope)
        late.unchecked(scope, tree)
