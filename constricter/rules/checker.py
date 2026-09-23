# SPDX-License-Identifier: MIT
"""The rules: every local variable is typed where it's first bound (see README)."""

import ast
import warnings
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import replace
from functools import lru_cache
from typing import Final, NamedTuple, cast

from constricter.fix import hinted, imports, returned, stdlib
from constricter.fix.inference import inference, looped
from constricter.fix.known import (
    Classes,
    ClassSide,
    Inference,
    Known,
    LibraryNames,
    Outside,
    Returned,
)
from constricter.fix.opened import opened
from constricter.fix.targets import iterated, unpacked
from constricter.jsonc import as_text
from constricter.offences import (
    COMMENT_TYPED_TARGET,
    DEFAULT_CHECKS,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    Checks,
    Edit,
    Fix,
    Offence,
    at,
)
from constricter.rules.annotations import (
    awaited_returns,
    casts,
    class_attributes,
    class_methods,
    factories,
    imported_from,
    method_returns,
    node_name,
    returns,
)
from constricter.rules.annotations import classes as instance_attributes
from constricter.rules.flow import Finding, Hierarchy, augmented
from constricter.rules.narrowing import flow_offences
from constricter.rules.redundant import redundant
from constricter.rules.scope import Kind, Late, Scope, Settings, certain_type, guesses_in
from constricter.rules.syntax import (
    FUNCTION_DEFS,
    FunctionDef,
    captures,
    child_statements,
    collect_functions,
    comment_type,
    expressions,
    owners,
    python2_compatible,
    target_names,
    type_comment_span,
)
from constricter.rules.walked import classes, of_type

# The node class of `type X = ...` statements, by name: Python 3.11's `ast` has no `TypeAlias`.
_TYPE_ALIAS: Final = "TypeAlias"
_CLASSMETHOD: Final = "classmethod"
_ROUNDS: Final = 5  # how many times to re-check what calls an unannotated function, at most
_COMMENT: Final = "comment"  # the fix kind of LVA003's declaration
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
    tree: ast.Module = _parse(source, filename)
    return check_tree(
        tree,
        checks,
        lines=as_text(source).splitlines(),
        outside=outside,
    )


def _parse(source: str | bytes, filename: str) -> ast.Module:
    """Parse `source` with its `# type:` comments; without them if one is misplaced.

    Python's warnings about the source (an invalid escape sequence in a string) are left unsaid: they're
    about the code checked, not findings, and it's the checked project's to see them when it runs.

    Returns:
      The module. Raises `SyntaxError`.

    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        warnings.simplefilter("ignore", DeprecationWarning)  # what Python 3.11 warns about them with
        try:
            return ast.parse(source, filename, type_comments=True)
        except SyntaxError:  # a misplaced `# type:` comment, or a real error raised again here
            return ast.parse(source, filename)


def _settings(
    tree: ast.Module,
    checks: Checks,
    lines: Sequence[str],
    calls: dict[str, str],
    outside: Outside | None = None,
) -> Settings:
    imported: Classes | None = None if outside is None else outside.classes
    return Settings(
        checks._replace(type_comments=checks.type_comments or python2_compatible(tree)),
        lines,
        Known(
            calls,
            factories(tree),
            {**(imported.attributes if imported else {}), **instance_attributes(tree)},
            {**(imported.methods if imported else {}), **method_returns(tree)},
            awaited_returns(tree),
            ClassSide(class_attributes(tree), class_methods(tree)),
            LibraryNames(casts(tree), stdlib.origins(tree), imports.plan(tree)),
            checks.max_length,
        ),
        Hierarchy.for_module(tree, {name: frozenset(wider) for name, wider in checks.narrower}),
        owners(tree),
        bool(of_type(tree, ast.NamedExpr)),
        () if outside is None else outside.hints,
    )


def check_tree(
    tree: ast.Module,
    checks: Checks = DEFAULT_CHECKS,
    *,
    lines: Sequence[str] = (),
    outside: Outside | None = None,
) -> list[Offence]:
    """Return the offences in a parsed module, sorted.

    `# type:` comments are seen only if it was parsed with `type_comments=True`; they count for `=`
    and `with` too in a module written to run on Python 2. With its source `lines`, a `**rest`
    capture is reported at its name rather than at its pattern's start. `outside` adds what's known
    of it from other files and a type checker, for `--fix` (see `Outside`).

    Returns:
      Every offence, in source order.

    """
    calls: Mapping[str, str] = {} if outside is None else outside.calls
    settings: Settings = _settings(tree, checks, lines, {**calls, **returns(tree)}, outside)
    scopes: list[Scope] = _scopes(tree, settings)
    settings, scopes = _returned(tree, settings, scopes)
    # A finding's kind is the code that reports it (LVA008, LVA009, LVA010).
    _finished(tree, scopes)
    flow: list[Offence] = flow_offences(_value_flow(tree, scopes), settings.checks.fixes)
    finals: list[Offence] = [o for scope in scopes for o in scope.finals()] if checks.final else []
    reported: list[Offence] = [o for scope in scopes for o in scope.reported()]
    return sorted([*reported, *redundant(tree, settings.checks.fixes), *flow, *finals])


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
    tree: ast.Module = _parse(source, "<unknown>")
    settings: Settings = _settings(tree, checks, as_text(source).splitlines(), {})
    scopes: list[Scope] = _scopes(tree, settings)
    total: int = sum(len(scope.bound()) for scope in scopes)
    untyped: int = sum(o.code in _UNTYPED for scope in scopes for o in scope.reported())
    return Coverage(total - untyped, total)


def _scopes(tree: ast.Module, settings: Settings) -> list["Scope"]:
    """Collect the scopes to check.

    Returns:
      Every function's scope, and with `all_scopes` every module and class body's.

    """
    functions: list[FunctionDef] = []
    collect_functions(tree.body, functions)
    scopes: list[Scope] = _function_scopes(functions, settings)
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


def _function_scopes(functions: list[FunctionDef], settings: Settings) -> list["Scope"]:
    """Check `functions` and every function defined inside them.

    Returns:
      Their scopes.

    """
    scopes: list[Scope] = []
    func: FunctionDef
    for func in functions:
        nested: list[FunctionDef] = []
        scopes.append(_function_scope(func, nested, settings))
        scopes += _function_scopes(nested, settings)
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
    late: Late
    for name, late in (seed or {}).items():
        _ = scope.inferred.types.setdefault(name, late[0])
        if late[1]:
            scope.inferred.guesses.add(name)
            scope.inferred.origins[name] = late[1]
        scope.inferred.seeded[name] = late
    stmt: ast.stmt
    for stmt in func.body:
        _visit(scope, stmt)
    return scope


def _visit(scope: Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds, as Python would, then visit its nested statements."""
    part: ast.AST
    if scope.settings.walruses:  # most modules have no `:=`: none of their parts need a look
        for part in expressions(stmt):
            scope.walrus(part)
    _declare(scope, stmt)
    _bind(scope, stmt)
    if isinstance(stmt, ast.Return):
        scope.inferred.returns.append(stmt.value)
    # A loop's body runs again and again (not its `else`), for LVA012.
    body: set[int] = (
        {id(s) for s in stmt.body} if isinstance(stmt, ast.For | ast.AsyncFor | ast.While) else set()
    )
    child: ast.stmt
    for child in child_statements(stmt):
        scope.assignments.looping += id(child) in body
        _visit(scope, child)
        scope.assignments.looping -= id(child) in body


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


def _returned(tree: ast.Module, settings: Settings, scopes: list[Scope]) -> tuple[Settings, list[Scope]]:
    """Type calls to unannotated functions from their `return`s, and what follows from late types.

    Each round finishes the scopes (so a container filled later, or `None` rebound, is typed), reads
    what the unannotated functions return, and checks again only a function that calls one whose
    type is new, or that has a late-typed name it didn't know from the start. Repeated until nothing
    changes, so `--fix` finds in one run what it would over several.

    Returns:
      The settings with what the functions return, and the scopes checked with them.

    """
    found: Returned = Returned()
    functions: list[tuple[Scope, FunctionDef]] = [
        (scope, scope.kind.function) for scope in scopes if scope.kind.function is not None
    ]
    fresh: list[tuple[Scope, FunctionDef]] = functions  # checked this round: to finish and record
    recorded: dict[int, list[returned.Recorded]] = {}
    _round: int
    for _round in range(_ROUNDS):
        _finished(tree, [scope for scope, _ in fresh])
        recorded.update(
            (id(func), [_recorded(scope, value) for value in scope.inferred.returns]) for scope, func in fresh
        )
        latest: Returned = returned.returned(tree, recorded)
        typed: bool
        if typed := latest != found and returned.called(tree, tree, latest):  # even if only a body calls one
            found = latest
            settings = replace(settings, known=replace(settings.known, returned=found))
        again: set[int] = {
            id(scope)
            for scope, func in functions
            if (typed and returned.called(tree, func, found))
            or scope.inferred.late.keys() - scope.inferred.seeded.keys()
        }
        if not again:
            break
        fresh = [
            (_function_scope(func, [], settings, scope.inferred.late), func)
            for scope, func in functions
            if id(scope) in again
        ]
        renewed: dict[int, Scope] = {id(func): scope for scope, func in fresh}
        functions = [(renewed.get(id(func), scope), func) for scope, func in functions]
    bodies: list[Scope] = [scope for scope in scopes if scope.kind.function is None]
    if bodies and any(returned.called(tree, stmt, found) for stmt in _body_statements(tree.body)):
        bodies = _body_scopes(tree, settings)
    return settings, [scope for scope, _ in functions] + bodies


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
        scope.mark_escaped(_module_names(tree)[0])
        scope.optionals()
        scope.fills()


def _recorded(scope: Scope, value: ast.expr | None) -> returned.Recorded:
    """Record a `return` statement's value as its finished function's scope sees it.

    Returns:
      Its inference (`None` for a bare `return`, or an unknown value), and whether that's a guess.

    """
    if value is None:
        return None, frozenset()
    return inference(value, scope.settings.known, scope.inferred.types), guesses_in(scope, [value])[1]


def _bind(scope: Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds that need typing, reporting the untyped ones."""
    targets: list[ast.expr]
    target: ast.expr
    items: list[ast.withitem]
    comment: str | None
    name: str
    single: ast.Name
    value: ast.expr
    cases: list[ast.match_case]
    op: ast.operator
    match stmt:
        case ast.Assign(targets=[ast.Name() as single], value=value, type_comment=comment):
            scope.assign(single, scope.unannotated(comment), value)
        case ast.Assign(targets=[ast.Tuple() | ast.List() as target], value=value, type_comment=comment):
            typed: Inference | None = inference(value, scope.settings.known, scope.inferred.types)
            _bind_declared(scope, stmt, target, typed, [value])
        case ast.Assign(targets=targets, type_comment=comment):
            _bind_targets(scope, targets, scope.unannotated(comment))
        case ast.With(items=items, type_comment=comment) | ast.AsyncWith(items=items, type_comment=comment):
            _bind_with(scope, stmt, items, scope.unannotated(comment))
        case (
            ast.For(target=target, iter=value, type_comment=None)
            | ast.AsyncFor(
                target=target,
                iter=value,
                type_comment=None,
            )
        ):
            typed = looped(value, scope.settings.known, scope.inferred.types)
            _bind_declared(scope, stmt, target, typed, iterated(value))
        case (
            ast.For(target=target, type_comment=str() as comment)
            | ast.AsyncFor(
                target=target,
                type_comment=str() as comment,
            )
        ):
            _bind_commented(scope, stmt, target, comment)
        case ast.Match(cases=cases):
            _bind_captures(scope, cases)
        case ast.AugAssign(target=ast.Name(id=name) as single, op=op, value=value):
            scope.lifetime(name).bind(at(single), augmented(op, certain_type(scope, value)))
        case _:
            pass


def _bind_declared(
    scope: Scope,
    stmt: ast.stmt,
    target: ast.expr,
    typed: Inference | None,
    bases: list[ast.expr],
) -> None:
    """Bind each name in `target` (a loop's, or an unpacking's), offering to declare each before `stmt`.

    `typed` is what the whole target gets (a loop's element, an unpacked value's type), split over
    its names (see `unpacked`); a name whose part isn't known gets no fix. The fixes are guesses if
    any of `bases`, the values `typed` came from, is. A loop's untyped target is LVA002, an
    unpacking's LVA001 (or LVA004), unless a type comment types it.
    """
    unsafe: bool
    origins: frozenset[str]
    unsafe, origins = guesses_in(scope, bases)
    # An unpacking's names are split from the value's type; a loop's are what it iterates (`loop`).
    split: frozenset[str] = frozenset() if isinstance(stmt, ast.For | ast.AsyncFor) else frozenset({"unpack"})
    code: str | None = (
        UNTYPED_TARGET
        if isinstance(stmt, ast.For | ast.AsyncFor)
        else scope.unannotated(cast("ast.Assign", stmt).type_comment)
    )
    name: ast.Name
    annotation: str | None
    for name, annotation in unpacked(target, None if typed is None else typed.annotation):
        part: Inference | None = (
            None
            if typed is None or annotation is None
            else Inference(annotation, typed.reason, typed.kinds | split)
        )
        _bind_declaration(scope, stmt, name, code, (part, unsafe, origins))


def _bind_declaration(
    scope: Scope,
    stmt: ast.stmt,
    name: ast.Name,
    code: str | None,
    typed: tuple[Inference | None, bool, frozenset[str]],
) -> None:
    """Bind one name a statement binds, offering to declare it before `stmt` as `typed` has it.

    `typed`: its inference (`None`: unknown, when the type checker's hint is asked), whether that's a
    guess, and what the guess rests on.
    """
    found: Inference | None
    unsafe: bool
    origins: frozenset[str]
    found, unsafe, origins = typed
    if found is None and (found := scope.hint(name)) is not None:
        unsafe, origins = True, frozenset({hinted.KIND})
    fix: Fix | None = None
    if found is not None:
        fix = scope.offer(
            found,
            origins,
            unsafe=unsafe,
            edit=Edit.DECLARE,
            span=(stmt.lineno, stmt.col_offset),
        )
        # What the rest of the scope infers from `name` knows its type, as for `name = value`.
        if name.id not in scope.inferred.types:
            scope.inferred.types[name.id] = found.annotation
            if unsafe:
                scope.inferred.guesses.add(name.id)
                scope.inferred.origins[name.id] = origins
    scope.bind(name.id, at(name), code, fix)


def _bind_commented(scope: Scope, stmt: ast.For | ast.AsyncFor, target: ast.expr, comment: str) -> None:
    """Bind a loop's target typed only by its `# type:` comment (LVA003), offering to declare it instead.

    The comment's type (`int`, or `int, str` for a tuple target) is split over the target's names as
    an unpacking's is; each is declared before the loop, and the comment dropped, since a type checker
    would see the name declared twice. Only for a loop whose header is on one line, where the comment
    is found after its iterable.
    """
    drop: tuple[int, int] | None = type_comment_span(scope.settings.lines, stmt)
    annotation: str | None = comment_type(comment) if drop is not None else None
    name: ast.Name
    part: str | None
    for name, part in unpacked(target, annotation):
        fix: Fix | None = None
        if part is not None and drop is not None:
            fix = scope.offer(
                Inference(part, "its `# type:` comment", frozenset({_COMMENT})),
                frozenset(),
                unsafe=False,
                edit=Edit.DECLARE,
                span=(stmt.lineno, stmt.col_offset),
            )
            fix = None if fix is None else fix._replace(drop=drop)
        scope.bind(name.id, at(name), COMMENT_TYPED_TARGET, fix)


def _bind_with(scope: Scope, stmt: ast.stmt, items: list[ast.withitem], code: str | None) -> None:
    """Bind each `with` item's target, offering to declare `with open(path, mode) as f`'s `f` first.

    The file object `open` gives is its context manager's own (`__enter__` returns `self`), typed by
    its literal mode; any other item's names are bound untyped, as are an `async with`'s (a file
    object isn't an asynchronous context manager).
    """
    item: ast.withitem
    name: ast.Name
    target: ast.expr
    for item in items:
        typed: Inference | None = (
            opened(item.context_expr, scope.settings.known) if isinstance(stmt, ast.With) else None
        )
        match item.optional_vars:
            case ast.Name() as name:
                _bind_declaration(scope, stmt, name, code, (typed, False, frozenset()))
            case None:
                pass
            case target:
                _bind_targets(scope, [target], code)


def _bind_targets(scope: Scope, targets: list[ast.expr], code: str | None) -> None:
    """Bind every name in `targets`, reporting `code` for each first binding."""
    target: ast.expr
    name: ast.Name
    for target in targets:
        for name in target_names(target):
            scope.bind(name.id, at(name), code)


def _bind_captures(scope: Scope, cases: list[ast.match_case]) -> None:
    """Bind every name the `case` patterns capture: LVA002 unless declared first."""
    case: ast.match_case
    name: str
    where: tuple[int, int]
    for case in cases:
        for name, where in captures(case.pattern, scope.settings.lines):
            scope.bind(name, where, UNTYPED_TARGET)


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
    tree: ast.Module = _parse(source, filename)
    # Its lines place a `**rest` capture at its name, as `check_source` does.
    settings: Settings = _settings(tree, checks, as_text(source).splitlines(), returns(tree))
    return _value_flow(tree, _scopes(tree, settings))


def _value_flow(tree: ast.Module, scopes: list[Scope]) -> list[Finding]:
    """Compare each name's values with its declared type, in each of `scopes`.

    Returns:
      Every finding, in source order.

    """
    escaped: frozenset[str]
    checking_only: frozenset[str]
    escaped, checking_only = _module_names(tree)
    return sorted(found for scope in scopes for found in scope.value_flow(escaped, checking_only))


@lru_cache(maxsize=16)  # `_value_flow` runs once per round of `_returned`, on the same tree
def _module_names(tree: ast.Module) -> tuple[frozenset[str], frozenset[str]]:
    """Find the names value flow leaves alone in a module.

    Returns:
      Those a `global` or `nonlocal` writes from elsewhere, and those annotated only for type
      checkers (`if TYPE_CHECKING: x: str`), whose runtime values may differ on purpose.

    """
    escaped: set[str] = set()
    checking_only: set[str] = set()
    node: ast.AST
    for node in of_type(tree, ast.Global, ast.Nonlocal, ast.If):
        if isinstance(node, ast.Global | ast.Nonlocal):
            escaped.update(node.names)
        elif isinstance(node, ast.If) and node_name(node.test) == _TYPE_CHECKING:  # the only other kind
            checking_only.update(
                stmt.target.id
                for stmt in node.body
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
            )
    return frozenset(escaped), frozenset(checking_only)
