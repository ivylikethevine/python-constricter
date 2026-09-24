# SPDX-License-Identifier: MIT
"""The rules: every local variable is typed where it's first bound (see README)."""

import ast
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import replace
from typing import Final, NamedTuple, cast

from constricter.fix import imports, narrowed, returned, stdlib
from constricter.fix.doubts import Facts, inner_starts, passed, tests
from constricter.fix.inference import inference
from constricter.fix.known import (
    Classes,
    ClassSide,
    Inference,
    Known,
    LibraryNames,
    Observed,
    Outside,
    Returned,
    Returns,
)
from constricter.jsonc import as_text
from constricter.offences import (
    DEFAULT_CHECKS,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    Checks,
    Offence,
    at,
)
from constricter.rules import binding, late, parsed
from constricter.rules.annotations import (
    Tables,
    awaited_returns,
    casts,
    class_attributes,
    class_methods,
    factories,
    free_of,
    free_of_all,
    generic_classes,
    imported_from,
    module_tables,
    node_name,
    self_returns,
)
from constricter.rules.calls import keyed, observed, seed_parameters, unshadowed
from constricter.rules.flow import Finding, Hierarchy
from constricter.rules.narrowing import flow_offences, module_flow, module_names
from constricter.rules.redundant import redundant
from constricter.rules.scope import Kind, Late, Scope, Settings, certain_type, guesses_in
from constricter.rules.syntax import (
    BRANCHING,
    FUNCTION_DEFS,
    FunctionDef,
    Start,
    child_statements,
    collect_functions,
    expressions,
    has_within,
    owners,
    python2_compatible,
    target_names,
)
from constricter.rules.walked import classes, of_type, walk

# The node class of `type X = ...` statements, by name: Python 3.11's `ast` has no `TypeAlias`.
_TYPE_ALIAS: Final = "TypeAlias"
_CLASSMETHOD: Final = "classmethod"
_ROUNDS: Final = 5  # how many times to re-check what calls an unannotated function, at most
# Enum members mustn't be annotated: a base imported from here is one, however it's aliased.
_ENUM_MODULES: Final = frozenset({"enum"})
# The conventional name of an instance method's first parameter: typed as its class, for `--fix`.
_SELF: Final = "self"
_TYPE_CHECKING: Final = "TYPE_CHECKING"


def check_source(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
    *,
    outside: Outside | None = None,
) -> list[Offence]:
    """Return the offences in `source`, sorted. Raises `SyntaxError`.

    `outside` adds what's known of it from other files and a type checker, for `--fix` (see `Outside`).

    Returns:
      Every offence; `# noqa` comments are the caller's to apply.

    """
    return checked_source(source, filename, checks, outside=outside).offences


def checked_source(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
    *,
    outside: Outside | None = None,
) -> "Checked":
    """Check `source`, as `check_source` does.

    Returns:
      Its offences, and what its functions return (see `Checked`).

    """
    tree: ast.Module
    own: Tables | None
    tree, own = _parse(source, filename)
    return checked_tree(tree, checks, lines=as_text(source).splitlines(), outside=outside, own=own)


def _parse(source: str | bytes, filename: str) -> tuple[ast.Module, Tables | None]:
    """Parse `source` (see `parsed.parse`), or take the tree the index kept for it (`parsed.take`).

    Returns:
      The module, and the tables the index read from it if it was kept. Raises `SyntaxError`.

    """
    kept: parsed.Kept | None = parsed.take(source) if isinstance(source, str) else None
    return kept or (parsed.parse(source, filename), None)


def _settings(
    tree: ast.Module,
    checks: Checks,
    lines: Sequence[str],
    own: Tables,
    outside: Outside | None = None,
) -> Settings:
    # The functions' declared returns: other checked files' (see `Outside`), then the module's own.
    calls: dict[str, str] = {**({} if outside is None else outside.calls), **own.returns}
    imported: Classes | None = None if outside is None else outside.classes
    # The file's own types that mention a type variable it imports (`--fix` sees only its own).
    free: frozenset[str] = frozenset() if outside is None else outside.type_vars
    return Settings(
        checks._replace(type_comments=checks.type_comments or python2_compatible(tree)),
        lines,
        Known(
            free_of(calls, free),
            factories(tree),
            {**(imported.attributes if imported else {}), **free_of_all(own.classes, free)},
            {**(imported.methods if imported else {}), **free_of_all(own.methods, free)},
            free_of(awaited_returns(tree), free),
            ClassSide(free_of_all(class_attributes(tree), free), free_of_all(class_methods(tree), free)),
            LibraryNames(
                casts(tree),
                stdlib.origins(tree),
                replace(imports.plan(tree), guarded={} if outside is None else outside.guarded),
            ),
            checks.max_length,
        ),
        Hierarchy.for_module(tree, {name: frozenset(wider) for name, wider in checks.narrower}),
        owners(tree),
        tuple(
            sorted(
                (node.lineno, node.col_offset)
                for node in cast("list[ast.NamedExpr]", of_type(tree, ast.NamedExpr))
            ),
        ),
        () if outside is None else outside.hints,
        Facts(
            self_returns(tree),
            generic_classes(tree)
            | stdlib.generics(stdlib.origins(tree))
            | (frozenset() if outside is None else outside.generics),
            passed(tree),
            tests(tree),
            narrowed.regions(tree),
            inner_starts(tree),
        ),
        keyed(tree, {} if outside is None else outside.parameters),
    )


def check_tree(
    tree: ast.Module,
    checks: Checks = DEFAULT_CHECKS,
    *,
    lines: Sequence[str] = (),
    outside: Outside | None = None,
    own: Tables | None = None,
) -> list[Offence]:
    """Return the offences in a parsed module, sorted.

    `# type:` comments are seen only if it was parsed with `type_comments=True`; they count for `=`
    and `with` too in a module written to run on Python 2. With its source `lines`, a `**rest`
    capture is reported at its name rather than at its pattern's start. `outside` adds what's known
    of it from other files and a type checker, for `--fix` (see `Outside`). `own`: the module's own
    tables, if already read from this tree (see `parsed.keep`).

    Returns:
      Every offence, in source order.

    """
    return checked_tree(tree, checks, lines=lines, outside=outside, own=own).offences


class Checked(NamedTuple):
    """A module's offences, what its unannotated functions return, and what it passes others' functions.

    What they return is for the files importing them; what it passes, for `fix.callers`.
    """

    offences: list[Offence]
    returned: Returns
    calls: Observed = Observed()


def checked_tree(
    tree: ast.Module,
    checks: Checks = DEFAULT_CHECKS,
    *,
    lines: Sequence[str] = (),
    outside: Outside | None = None,
    own: Tables | None = None,
) -> Checked:
    """Check a parsed module, as `check_tree` does.

    Returns:
      Its offences, in source order, and what its functions return (see `returned.exported`).

    """
    own = own or module_tables(tree)
    outside = None if outside is None else outside.usable(imports.plan(tree).taken)
    imported: Returns = Returns() if outside is None else outside.returned
    table: returned.Table = returned.Table(tree, imported)
    settings: Settings = _settings(tree, checks, lines, own, outside)
    # The table, filled in as the functions are checked in call order, is what they all read.
    settings = replace(settings, known=replace(settings.known, returned=table.returned))
    scopes: list[Scope] = _scopes(tree, settings, table)
    found: Returned
    settings, scopes, found = _returned(tree, settings, scopes, table, imported)
    # A finding's kind is the code that reports it (LVA008, LVA009, LVA010).
    _finished(tree, scopes)
    flow: list[Offence] = flow_offences(module_flow(tree, scopes), settings.checks.fixes)
    finals: list[Offence] = [o for scope in scopes for o in late.finals(scope)] if checks.final else []
    reported: list[Offence] = [o for scope in scopes for o in scope.reported()]
    exported: Returns = returned.exported(found)
    return Checked(
        sorted([*reported, *redundant(tree, settings.checks.fixes), *flow, *finals]),
        exported._replace(
            names=returned.exported_names(
                exported,
                {} if outside is None else outside.guarded,
                (settings.known.names.plan or imports.plan(tree)).added,
            ),
        ),
        observed(tree, scopes, settings.known, {} if outside is None else outside.callees),
    )


class Coverage(NamedTuple):
    """How many of a module's typeable first bindings are typed, of how many."""

    typed: int
    total: int

    @property
    def percent(self) -> float:
        """The typed share, as a percentage (100 when there's nothing to type)."""
        return 100 * self.typed / self.total if self.total else 100.0


# The codes that mean a binding has no type at all (LVA003's type comment is a type).
_UNTYPED: Final = frozenset({UNANNOTATED, UNTYPED_TARGET, UNANNOTATED_MEMBER})


def annotation_coverage(source: str | bytes, checks: Checks = DEFAULT_CHECKS) -> Coverage:
    """Count the first bindings in `source` the rules cover, and how many are typed.

    Returns:
      The counts; `# noqa` comments don't make a binding typed. Raises `SyntaxError`.

    """
    tree: ast.Module = _parse(source, "<unknown>")[0]
    settings: Settings = _settings(tree, checks, as_text(source).splitlines(), module_tables(tree))
    scopes: list[Scope] = _scopes(tree, settings)
    total: int = sum(len(scope.bound()) for scope in scopes)
    untyped: int = sum(o.code in _UNTYPED for scope in scopes for o in scope.reported())
    return Coverage(total - untyped, total)


def _scopes(tree: ast.Module, settings: Settings, table: returned.Table | None = None) -> list["Scope"]:
    """Collect the scopes to check.

    With a `table` (see `returned.Table`), the functions are checked callees first, each one's
    return type recorded as soon as it's checked: a caller checked later knows it the first time.

    Returns:
      Every function's scope, and with `all_scopes` every module and class body's.

    """
    functions: list[FunctionDef] = []
    collect_functions(tree.body, functions)
    if table is not None:
        functions = returned.in_call_order(tree, functions)
    scopes: list[Scope] = _function_scopes(functions, settings, table)
    if settings.checks.all_scopes:
        scopes += _body_scopes(tree, settings)
    return scopes


def _body_scopes(tree: ast.Module, settings: Settings) -> list["Scope"]:
    """Collect the module and class bodies (LVA004).

    Returns:
      Their scopes, but for an enum's.

    """
    imported: frozenset[str] = imported_from(tree, _ENUM_MODULES)
    class_bodies: list[list[ast.stmt]] = [node.body for node in classes(tree) if not _is_enum(node, imported)]
    scopes: list[Scope] = []
    body: list[ast.stmt]
    for body in (tree.body, *class_bodies):
        # A class body is never fixed: annotating a dataclass's variable makes it a field.
        scope: Scope = Scope({"_"}, [], settings, Kind(UNANNOTATED_MEMBER, fixable=body is tree.body))
        stmt: ast.stmt
        for stmt in body:
            _visit(scope, stmt)
        scopes.append(scope)
    return scopes


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
        scope: Scope = _function_scope(func, nested, settings)
        scopes.append(scope)
        if table is not None:
            _finished(table.module, [scope])
            # Its returns are typed as it's checked; but one with late types (`None` rebound, ...) is
            # checked again knowing them (`_returned`), and until then nothing's recorded: a caller
            # would take its type too soon (`int`, for `None` rebound to `int`: `int | None`).
            settled: bool = not scope.inferred.late.keys() - scope.inferred.seeded.keys()
            table.checked(
                func,
                [_recorded(scope, value) for value in scope.inferred.returns] if settled else [],
                _assigned(scope) if settled else [],
            )
        scopes += _function_scopes(nested, scope.settings, table)
    return scopes


def _function_scope(
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
    scope.inferred.types.update(
        (arg.arg, ast.unparse(arg.annotation)) for arg in named if arg.annotation is not None
    )
    owner: str | None = settings.owners.get(id(func))
    if owner is not None and named and named[0].arg == _SELF:
        _ = scope.inferred.types.setdefault(_SELF, owner)
    # A classmethod's first parameter is its class (`type[C]`), whatever it's called.
    if owner is not None and named and [node_name(d) for d in func.decorator_list] == [_CLASSMETHOD]:
        _ = scope.inferred.types.setdefault(named[0].arg, f"type[{owner}]")
    seed_parameters(scope, func, named)
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
    name: str
    typed: Late
    for name, typed in (seed or {}).items():
        scope.inferred.seeded[name] = typed
        scope.inferred.learn(name, typed[0], typed[1] or None)
    stmt: ast.stmt
    for stmt in func.body:
        _visit(scope, stmt)
    return scope


def _visit(scope: Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds, as Python would, then visit its nested statements."""
    part: ast.AST
    walruses: tuple[Start, ...]
    if walruses := scope.settings.walruses:  # most modules have no `:=`: none of their parts need a look
        for part in expressions(stmt):
            if has_within(walruses, part):  # a `:=` in it
                scope.walrus(part)
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
    child: ast.stmt
    for child in child_statements(stmt):
        scope.assignments.looping += id(child) in body
        _visit(scope, child)
        scope.assignments.looping -= id(child) in body
    if before is not None:
        scope.inferred.rejoined(before)


def _declare(scope: Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds that need no annotation, or carry their own."""
    aliases: list[ast.alias]
    names: list[str]
    name: str
    annotation: ast.expr
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
        case ast.AnnAssign(target=ast.Name(id=name) as target, annotation=annotation):
            scope.declare(name)
            scope.annotation(name, annotation)
            _ = scope.inferred.types.setdefault(name, ast.unparse(annotation))
            scope.lifetime(name).declare(ast.unparse(annotation), at(target), _span(annotation, target))
            if stmt.value is not None:
                scope.lifetime(name).bind(at(target), certain_type(scope, stmt.value))
                scope.assigned(name, at(target))
        case _ if type(stmt).__name__ == _TYPE_ALIAS:
            alias: ast.expr = cast("ast.expr", next(ast.iter_child_nodes(stmt)))  # its first field, the name
            scope.declared.update(name.id for name in target_names(alias))
        case ast.Try(handlers=handlers) | ast.TryStar(handlers=handlers):
            names = [handler.name for handler in handlers if handler.name]
            scope.declared.update(names)
            scope.opaque(names)
        case _:
            pass


def _span(annotation: ast.expr, target: ast.expr) -> tuple[int, int] | None:
    """Find an annotation's columns, if it's all on its target's line (so `--fix` can rewrite it).

    Returns:
      Its start and end columns (UTF-8 bytes, as `ast` counts), or `None`.

    """
    one_line: bool = annotation.lineno == annotation.end_lineno == target.lineno
    return (annotation.col_offset, annotation.end_col_offset or 0) if one_line else None


def _returned(
    tree: ast.Module,
    settings: Settings,
    scopes: list[Scope],
    table: returned.Table,
    imported: Returns,
) -> tuple[Settings, list[Scope], Returned]:
    """Check again what the first pass, in call order, couldn't type the first time.

    That pass typed each function knowing its callees' returns (see `_scopes`); what's left is a
    function checked before a callee of its was typed (a cycle, `table.stale`), or with a late-typed
    name it didn't know from the start. Each round checks those again, reads what the unannotated
    functions return, and checks again any function calling one whose type is new; repeated until
    nothing changes, so `--fix` finds in one run what it would over several.

    Returns:
      The settings with what the functions return (those it imports, `imported`, too), the scopes
      checked with them, and what its own return.

    """
    found: Returned = returned.returned(tree, table.recorded, table.assigned)
    settings = replace(settings, known=replace(settings.known, returned=returned.joined(imported, found)))
    functions: list[tuple[Scope, FunctionDef]] = [
        (scope, scope.kind.function) for scope in scopes if scope.kind.function is not None
    ]
    # The first pass knew no attribute's type: they're read once every method is checked.
    again: set[int] = {
        id(scope)
        for scope, func in functions
        if table.stale(func)
        or scope.inferred.late.keys() - scope.inferred.seeded.keys()
        or returned.reads_own(tree, func, settings.owners, found)
    }
    changed: bool = False
    retyped: set[str] = set()  # the attributes the rounds typed anew
    _round: int
    for _round in range(_ROUNDS):
        if not again:
            break
        functions = _checked_again(tree, functions, again, settings, table)
        latest: Returned = returned.returned(tree, table.recorded, table.assigned)
        typed: bool = latest != found and returned.called(tree, tree, latest)  # even if only a body calls one
        # Attributes typed anew: what reads one, of any value, may be typed now.
        newly: set[str] = returned.retyped(found, latest)
        # Kept even when nothing here calls it: other files import what the module's functions return.
        if latest != found:
            found = latest
            settings = replace(
                settings,
                known=replace(settings.known, returned=returned.joined(imported, found)),
            )
            changed = changed or typed
            retyped |= newly
        again = {
            id(scope)
            for scope, func in functions
            if (typed and returned.called(tree, func, found))
            or returned.reads(tree, func, newly, anywhere=True)
            or scope.inferred.late.keys() - scope.inferred.seeded.keys()
        }
    return (
        settings,
        [scope for scope, _ in functions]
        + _bodies(
            tree,
            settings,
            [scope for scope in scopes if scope.kind.function is None],
            (retyped if changed or retyped else None, found),
        ),
        found,
    )


def _checked_again(
    tree: ast.Module,
    functions: list[tuple[Scope, FunctionDef]],
    again: set[int],
    settings: Settings,
    table: returned.Table,
) -> list[tuple[Scope, FunctionDef]]:
    """Check the functions whose scopes are in `again` once more, recording their `return`s and assignments.

    Returns:
      Every function, with its latest scope.

    """
    fresh: list[tuple[Scope, FunctionDef]] = [
        (_function_scope(func, [], settings, scope.inferred.late), func)
        for scope, func in functions
        if id(scope) in again
    ]
    renewed: dict[int, Scope] = {id(func): scope for scope, func in fresh}
    _finished(tree, [scope for scope, _ in fresh])
    table.recorded.update(
        (id(func), [_recorded(scope, value) for value in scope.inferred.returns]) for scope, func in fresh
    )
    table.assigned.update((id(func), _assigned(scope)) for scope, func in fresh)
    return [(renewed.get(id(func), scope), func) for scope, func in functions]


def _bodies(
    tree: ast.Module,
    settings: Settings,
    bodies: list[Scope],
    news: tuple[set[str] | None, Returned],
) -> list[Scope]:
    """Check the module and class bodies again, if the rounds typed anything they use.

    They were checked after every function, knowing the first pass's types: only what the rounds
    typed since is news to them (`news`: the attributes they typed, `None` if nothing at all; and
    what the module's own functions return).

    Returns:
      Their scopes, checked again or as they were.

    """
    retyped: set[str] | None
    own: Returned
    retyped, own = news
    if (
        retyped is not None
        and bodies
        and any(
            returned.called(tree, stmt, own) or returned.reads(tree, stmt, retyped, anywhere=True)
            for stmt in _body_statements(tree.body)
        )
    ):
        return _body_scopes(tree, settings)
    return bodies


def _body_statements(body: Sequence[ast.stmt]) -> Iterator[ast.stmt]:
    """Walk a module's and its classes' own statements, not their functions'.

    Yields:
      Each statement (a function's definition too, but not what's inside it).

    """
    stmt: ast.stmt
    for stmt in body:
        yield stmt
        if isinstance(stmt, ast.ClassDef):
            yield from _body_statements(stmt.body)
        elif not isinstance(stmt, FUNCTION_DEFS):
            yield from _body_statements(child_statements(stmt))


def _finished(tree: ast.Module, scopes: Sequence[Scope]) -> None:
    """Finish `scopes` for their late fixes (`None` rebound, filled containers).

    Those need the names written out of sight marked first. Safe to run again: marking is
    idempotent, and neither fix redoes one it made.
    """
    scope: Scope
    for scope in scopes:
        scope.mark_escaped(module_names(tree)[0])
        late.optionals(scope)
        late.rebinds(scope)
        late.fills(scope)


def _recorded(scope: Scope, value: ast.expr | None) -> returned.Recorded:
    """Record a `return` statement's value as its finished function's scope sees it.

    Returns:
      Its inference (`None` for a bare `return`, or an unknown value), and whether that's a guess.

    """
    if value is None:
        return None, frozenset()
    found: Inference | None = inference(value, scope.settings.known, scope.inferred.types)
    # What it rests on counts only for a typed value (see `returned`).
    return found, frozenset() if found is None else guesses_in(scope, [value])[1]


def _assigned(scope: Scope) -> list[returned.Assigned]:
    """Record a finished function's `self.x = value` assignments, each value as `_recorded` does a `return`'s.

    But a value reading a local bound more than once is unknown: the scope's type for it is its last
    binding's, not what reaches the assignment (`x = None`, `if c: x = 1`, then `self.x = x`).

    Returns:
      Each attribute, and its value's inference and guesses.

    """
    return [
        (attr, (None, frozenset()) if _rebound_in(scope, value) else _recorded(scope, value))
        for attr, value in scope.inferred.assigned
    ]


def _rebound_in(scope: Scope, value: ast.expr) -> bool:
    """Check whether `value` reads a local of `scope` bound more than once.

    Returns:
      Whether it does.

    """
    return any(
        isinstance(node, ast.Name) and node.id in scope.flow and len(scope.flow[node.id].bindings) > 1
        for node in walk(value)
    )


def value_flow(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
) -> list[Finding]:
    """Return the value-flow findings in `source`, sorted (see `constricter.flow`). Raises `SyntaxError`.

    `check_tree` reports each as the code its kind names (LVA008, LVA009, LVA010).

    Returns:
      Every finding, in source order.

    """
    tree: ast.Module = _parse(source, filename)[0]
    # Its lines place a `**rest` capture at its name, as `check_source` does.
    settings: Settings = _settings(tree, checks, as_text(source).splitlines(), module_tables(tree))
    return module_flow(tree, _scopes(tree, settings))
