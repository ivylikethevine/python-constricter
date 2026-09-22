# SPDX-License-Identifier: MIT
"""The rules: every local variable is typed where it's first bound (see README)."""

import ast
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.inference import (
    Inference,
    Known,
    guessed,
    inference,
    inferred,
    iterated,
    looped,
    unpacked,
)
from constricter.jsonc import as_text
from constricter.offences import (
    CAN_BE_FINAL,
    COMMENT_TYPED_TARGET,
    CONSTRUCTOR,
    DEFAULT_CHECKS,
    LONG_TUPLE,
    NARROW,
    NESTED_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    VAGUE_TYPE,
    Checks,
    Edit,
    Fix,
    FixPolicy,
    Offence,
    at,
)
from constricter.rules.annotations import (
    awaited_returns,
    classes,
    depth,
    factories,
    imported_from,
    is_vague,
    length,
    method_returns,
    node_name,
    returns,
)
from constricter.rules.flow import Finding, Hierarchy, Kind, Lifetime, augmented, findings, members
from constricter.rules.redundant import redundant
from constricter.rules.syntax import (
    FunctionDef,
    captures,
    child_statements,
    collect_functions,
    expressions,
    owners,
    python2_compatible,
    target_names,
)

# The node class of `type X = ...` statements, by name: Python 3.11's `ast` has no `TypeAlias`.
_TYPE_ALIAS: Final = "TypeAlias"
_DISCARD: Final = "_"
_FINAL: Final = "Final"
# Enum members mustn't be annotated: a base imported from here is one, however it's aliased.
_ENUM_MODULES: Final = frozenset({"enum"})
# The conventional name of an instance method's first parameter: typed as its class, for `--fix`.
_SELF: Final = "self"
_TYPE_CHECKING: Final = "TYPE_CHECKING"


@dataclass(frozen=True)
class _Settings:
    """One module's options, and its source lines (to place a `**rest` capture)."""

    type_comments: bool
    all_scopes: bool
    nesting: int
    max_length: int
    lines: Sequence[str]
    known: Known  # what the module declares that `--fix` infers types from
    hierarchy: Hierarchy  # which types are narrower than which, for value flow
    owners: dict[int, str]  # each method's class, by `id()`, to type its `self`, for `--fix`
    fixes: FixPolicy  # which fixes `--fix` offers, and which guesses it trusts


def check_source(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
    *,
    calls: Mapping[str, str] | None = None,
) -> list[Offence]:
    """Return the offences in `source`, sorted. Raises `SyntaxError`.

    `calls` adds the return types of functions other modules define, for `--fix` (see `project.calls`).

    Returns:
      Every offence; `# noqa` comments are the caller's to apply.

    """
    tree: ast.Module = _parse(source, filename)
    return check_tree(tree, checks, lines=as_text(source).splitlines(), calls=calls)


def _parse(source: str | bytes, filename: str) -> ast.Module:
    """Parse `source` with its `# type:` comments; without them if one is misplaced.

    Returns:
      The module. Raises `SyntaxError`.

    """
    try:
        return ast.parse(source, filename, type_comments=True)
    except SyntaxError:  # a misplaced `# type:` comment, or a real error raised again here
        return ast.parse(source, filename)


def _settings(
    tree: ast.Module,
    checks: Checks,
    lines: Sequence[str],
    calls: dict[str, str],
) -> _Settings:
    return _Settings(
        checks.type_comments or python2_compatible(tree),
        checks.all_scopes,
        checks.nesting,
        checks.max_length,
        lines,
        Known(calls, factories(tree), classes(tree), method_returns(tree), awaited_returns(tree)),
        Hierarchy.for_module(tree, {name: frozenset(wider) for name, wider in checks.narrower}),
        owners(tree),
        checks.fixes,
    )


def check_tree(
    tree: ast.Module,
    checks: Checks = DEFAULT_CHECKS,
    *,
    lines: Sequence[str] = (),
    calls: Mapping[str, str] | None = None,
) -> list[Offence]:
    """Return the offences in a parsed module, sorted.

    `# type:` comments are seen only if it was parsed with `type_comments=True`; they count for `=`
    and `with` too in a module written to run on Python 2. With its source `lines`, a `**rest`
    capture is reported at its name rather than at its pattern's start.

    Returns:
      Every offence, in source order.

    """
    settings: _Settings = _settings(tree, checks, lines, {**(calls or {}), **returns(tree)})
    scopes: list[_Scope] = _scopes(tree, settings)
    # A finding's kind is the code that reports it (LVA008, LVA009, LVA010).
    flow: list[Offence] = _flow_offences(_value_flow(tree, scopes), settings.fixes)
    finals: list[Offence] = [o for scope in scopes for o in scope.finals()] if checks.final else []
    return sorted([*(o for scope in scopes for o in scope.reported()), *redundant(tree), *flow, *finals])


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
    settings: _Settings = _settings(tree, checks, as_text(source).splitlines(), {})
    scopes: list[_Scope] = _scopes(tree, settings)
    total: int = sum(len(scope.bound()) for scope in scopes)
    untyped: int = sum(o.code in _UNTYPED for scope in scopes for o in scope.reported())
    return Coverage(total - untyped, total)


def _scopes(tree: ast.Module, settings: _Settings) -> list["_Scope"]:
    """Collect the scopes to check.

    Returns:
      Every function's scope, and with `all_scopes` every module and class body's.

    """
    functions: list[FunctionDef] = []
    collect_functions(tree.body, functions)
    scopes: list[_Scope] = _function_scopes(functions, settings)
    if settings.all_scopes:
        scopes += _body_scopes(tree, settings)
    return scopes


def _body_scopes(tree: ast.Module, settings: _Settings) -> list["_Scope"]:
    """Collect the module and class bodies (LVA004).

    Returns:
      Their scopes, but for an enum's.

    """
    imported: frozenset[str] = imported_from(tree, _ENUM_MODULES)
    class_bodies: list[list[ast.stmt]] = [
        node.body
        for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef) and not _is_enum(node, imported)
    ]
    scopes: list[_Scope] = []
    body: list[ast.stmt]
    for body in (tree.body, *class_bodies):
        # A class body is never fixed: annotating a dataclass's variable makes it a field.
        scope: _Scope = _Scope({"_"}, [], settings, unannotated=UNANNOTATED_MEMBER, fixable=body is tree.body)
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


class _Kind(NamedTuple):
    """What kind of body a scope is: the code its unannotated names get, and whether `--fix` fixes it."""

    unannotated: str  # LVA001 in a function, LVA004 in a module or class body
    fixable: bool  # a class body never is: annotating a dataclass's variable makes it a field


# One plain assignment: where, and whether it's in a loop's body.
_Placed: TypeAlias = tuple[tuple[int, int], bool]


@dataclass
class _Assignments:
    """A scope's plain `name = value` (or `name: T = value`) bindings, for LVA012."""

    found: dict[str, list[_Placed]] = field(default_factory=dict[str, list[_Placed]])  # each name's
    looping: int = 0  # how many loops deep the statement being visited is


@dataclass
class _Inferred:
    """What `--fix` knows of a scope's names so far."""

    types: dict[str, str] = field(default_factory=dict[str, str])  # each known type, for `x = y`'s
    guesses: set[str] = field(default_factory=set[str])  # `types` from an unsafe fix: copies are too
    # Each guess's guessing mechanisms (`FIX_KINDS`), for `unsafe-fix-select` to trust or not.
    origins: dict[str, frozenset[str]] = field(default_factory=dict[str, frozenset[str]])


class _Scope:
    """One function body: names bound so far and offences found."""

    def __init__(
        self,
        declared: set[str],
        nested: list[FunctionDef],
        settings: _Settings,
        *,
        unannotated: str = UNANNOTATED,
        fixable: bool = True,
    ) -> None:
        self.declared: set[str] = declared
        self.nested: list[FunctionDef] = nested
        self.settings: _Settings = settings
        self.kind: _Kind = _Kind(unannotated, fixable=fixable)
        self.offences: list[Offence] = []
        self.first: list[str] = []  # each first binding the rules cover, typed or not
        self.inferred: _Inferred = _Inferred()  # what `--fix` knows of the names bound so far
        self.flow: dict[str, Lifetime] = {}  # every binding of each name, for value flow
        self.assignments: _Assignments = _Assignments()  # for LVA012

    def lifetime(self, name: str) -> Lifetime:
        """Find `name`'s value-flow record, starting one if it has none.

        Returns:
          It.

        """
        return self.flow.setdefault(name, Lifetime())

    def bind(self, name: str, where: tuple[int, int], code: str | None, fix: Fix | None = None) -> None:
        """Bind `name` to a value value flow can't see; unless it's already bound, report `code`.

        `code` is reported at `(line, col)` (`None` means typed), offering `fix` if there's one.
        """
        self.lifetime(name).bind(where, None)
        self._first(name, where, code, fix)

    def assign(self, target: ast.Name, code: str | None, value: ast.expr) -> None:
        """Bind `target` to `value` (`name = value`), offering `--fix`'s annotation for it."""
        name: str = target.id
        fix: Inference | None = inference(value, self.settings.known, self.inferred.types)
        unsafe: bool = guessed(
            value,
            self.settings.known,
            frozenset(self.inferred.guesses),
            self.inferred.types,
        )
        origins: frozenset[str] = _origins(self, [value]) if unsafe else frozenset()
        self.lifetime(name).bind(at(target), _certain(self, value))
        self.assigned(name, at(target))
        self._first(name, at(target), code, None if fix is None else self.offer(fix, origins, unsafe=unsafe))
        if fix is not None and name not in self.inferred.types:
            self.inferred.types[name] = fix.annotation
            if unsafe:
                self.inferred.guesses.add(name)
                self.inferred.origins[name] = origins

    def offer(
        self,
        fix: Inference,
        origins: frozenset[str],
        *,
        unsafe: bool,
        edit: Edit = Edit.ANNOTATE,
        span: tuple[int, int] = (0, 0),
    ) -> Fix | None:
        """Offer `fix` as the project's fix policy has it: selected, and a guess unless trusted.

        Returns:
          The fix, or `None` if a mechanism that decided it isn't selected, or is ignored.

        """
        policy: FixPolicy = self.settings.fixes
        if not policy.allows(fix.kinds):
            return None
        certain: bool = not unsafe or policy.trusts(origins)
        return Fix(fix.annotation, fix.reason, not certain, edit, span, fix.kinds)

    def _first(
        self,
        name: str,
        where: tuple[int, int],
        code: str | None,
        fix: Fix | None,
    ) -> None:
        """Unless `name` is already bound, record its first binding, reporting `code` (`None`: typed).

        The offence offers `fix`, unless this is a class body (a dataclass's annotation is a field).
        """
        if name not in self.declared:
            self.declared.add(name)
            self.first.append(name)
            if code is not None:
                self.offences.append(Offence(*where, name, code, fix if self.kind.fixable else None))

    def declare(self, name: str) -> None:
        """Bind `name` by an annotation (`name: T`, `name: T = ...`): a typed first binding."""
        # position is unused: `code` is `None`, so nothing is reported
        self._first(name, (0, 0), None, None)

    def opaque(self, names: Iterable[str]) -> None:
        """Record bindings whose values value flow can't see: an import, a `def`, `except ... as`."""
        name: str
        for name in names:
            self.lifetime(name).bind((0, 0), None)

    def value_flow(self, escaped: frozenset[str], skipped: frozenset[str]) -> list[Finding]:
        """Compare each name's values with its declared type.

        `escaped` names are written elsewhere; `skipped` ones aren't compared at all.

        Returns:
          The findings, for names the rules cover.

        """
        name: str
        # A module or class body's names are state anything can rebind out of its sight (an instance's
        # `self.x = ...`, another module's `mod.X = ...`, `monkeypatch`, `globals().update(...)`).
        body: bool = self.kind.unannotated == UNANNOTATED_MEMBER
        for name in self.flow.keys() if body else escaped & self.flow.keys():
            self.flow[name].escaped = True
        return [
            found
            for name, lifetime in self.flow.items()
            if self._covered(name) and name not in skipped
            for found in findings(name, lifetime, self.settings.hierarchy)
        ]

    def assigned(self, name: str, where: tuple[int, int]) -> None:
        """Record a plain assignment to `name` at `where`, for LVA012."""
        self.assignments.found.setdefault(name, []).append((where, self.assignments.looping > 0))

    def finals(self) -> list[Offence]:
        """Find the names that could be `Final` (LVA012); run after `value_flow`, which marks escapes.

        Returns:
          An offence for each name bound exactly once, by a plain assignment outside any loop, and not
          declared apart from it or already `Final`, nor written from another scope.

        """
        found: list[Offence] = []
        name: str
        lifetime: Lifetime
        for name, lifetime in self.flow.items():
            if (
                name == _DISCARD
                or lifetime.escaped
                or self.kind.unannotated == UNANNOTATED_MEMBER
                or len(lifetime.bindings) != 1
            ):
                continue
            where: tuple[int, int] = lifetime.bindings[0].at
            if self.assignments.found.get(name) == [(where, False)] and (
                lifetime.declared is None
                or (lifetime.declared_at == where and not _is_final(lifetime.declared))
            ):
                found.append(Offence(*where, name, CAN_BE_FINAL))
        return found

    def _covered(self, name: str) -> bool:
        """Check whether the rules cover `name` here.

        Returns:
          Whether they do; a module or class body's dunder names are exempt.

        """
        return self.kind.unannotated != UNANNOTATED_MEMBER or not (
            name.startswith("__") and name.endswith("__")
        )

    def reported(self) -> list[Offence]:
        """Filter the offences found.

        Returns:
          All but those for exempt names.

        """
        return [o for o in self.offences if self._covered(o.name)]

    def bound(self) -> list[str]:
        """List the first bindings the rules cover.

        Returns:
          Their names, typed or not.

        """
        return [name for name in self.first if self._covered(name)]

    def annotation(self, name: str, annotation: ast.expr) -> None:
        """Report a vague annotation (LVA005), too deep a one (LVA006), or too long a tuple (LVA011)."""
        if is_vague(annotation):
            self.offences.append(Offence(*at(annotation), name, VAGUE_TYPE))
        if depth(annotation) >= self.settings.nesting:
            self.offences.append(Offence(*at(annotation), name, NESTED_TYPE))
        longest: int
        if (longest := length(annotation)) > self.settings.max_length:
            self.offences.append(Offence(*at(annotation), name, LONG_TUPLE, detail=str(longest)))

    def walrus(self, node: ast.AST) -> None:
        """Bind `:=` targets in an expression, comprehensions included, lambdas excluded."""
        in_lambda: set[int] = {
            id(inner)
            for outer in ast.walk(node)
            if isinstance(outer, ast.Lambda)
            for inner in ast.walk(outer)
        }
        current: ast.AST
        for current in ast.walk(node):
            if isinstance(current, ast.NamedExpr) and id(current) not in in_lambda:
                self.bind(current.target.id, at(current.target), self.kind.unannotated)

    def unannotated(self, type_comment: str | None) -> str | None:
        """Decide the code for an `=` or `with` binding.

        Returns:
          The code, or `None` if a counted type comment types it.

        """
        return None if type_comment is not None and self.settings.type_comments else self.kind.unannotated


def _function_scopes(functions: list[FunctionDef], settings: _Settings) -> list["_Scope"]:
    """Check `functions` and every function defined inside them.

    Returns:
      Their scopes.

    """
    scopes: list[_Scope] = []
    func: FunctionDef
    for func in functions:
        nested: list[FunctionDef] = []
        scopes.append(_function_scope(func, nested, settings))
        scopes += _function_scopes(nested, settings)
    return scopes


def _function_scope(func: FunctionDef, functions: list[FunctionDef], settings: _Settings) -> "_Scope":
    """Check one function; functions defined in it are collected into `functions`.

    Returns:
      Its scope.

    """
    args: ast.arguments = func.args
    named: tuple[ast.arg, ...] = (*args.posonlyargs, *args.args, *args.kwonlyargs)
    params: set[str] = {a.arg for a in named}
    params.update(extra.arg for extra in (args.vararg, args.kwarg) if extra is not None)
    # `_` is a discard.
    scope: _Scope = _Scope(params | {"_"}, functions, settings)
    # A copy of a plain, annotated parameter (`*args`/`**kwargs` aren't the type they're annotated
    # with) can be typed the same way, the moment it's assigned.
    scope.inferred.types.update(
        (arg.arg, ast.unparse(arg.annotation)) for arg in named if arg.annotation is not None
    )
    owner: str | None = settings.owners.get(id(func))
    if owner is not None and named and named[0].arg == _SELF:
        _ = scope.inferred.types.setdefault(_SELF, owner)
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
    stmt: ast.stmt
    for stmt in func.body:
        _visit(scope, stmt)
    return scope


def _visit(scope: _Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds, as Python would, then visit its nested statements."""
    part: ast.AST
    for part in expressions(stmt):
        scope.walrus(part)
    _declare(scope, stmt)
    _bind(scope, stmt)
    # A loop's body runs again and again (not its `else`), for LVA012.
    body: set[int] = (
        {id(s) for s in stmt.body} if isinstance(stmt, ast.For | ast.AsyncFor | ast.While) else set()
    )
    child: ast.stmt
    for child in child_statements(stmt):
        scope.assignments.looping += id(child) in body
        _visit(scope, child)
        scope.assignments.looping -= id(child) in body


def _declare(scope: _Scope, stmt: ast.stmt) -> None:
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
                scope.lifetime(name).bind(at(target), _certain(scope, stmt.value))
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


def _flow_offences(found: list[Finding], policy: FixPolicy) -> list[Offence]:
    """Report value-flow findings as offences, a finding's kind as its code.

    Each declaration LVA008 or LVA010 would narrow gets one fix, a guess (`--unsafe-fixes`: a
    declared type can be wider on purpose): the LVA008 finding's narrowed type if there's one,
    since it's already within the members the values use, else the union without its unused
    members, on the first LVA010 finding. Two rewrites of one annotation can't both apply. `policy`
    decides whether it's offered (`narrow`), and whether it's trusted.

    Returns:
      The offences.

    """
    offences: list[Offence] = []
    fixed: set[tuple[int, int]] = set()
    finding: Finding
    narrowed: set[tuple[int, int]] = {(f.line, f.col) for f in found if f.kind is Kind.NARROWABLE}
    for finding in sorted(found, key=lambda f: f.kind is not Kind.NARROWABLE):
        where: tuple[int, int] = (finding.line, finding.col)
        edit: Fix | None = None
        if (
            finding.span
            and finding.rewrite
            and where not in fixed
            and (finding.kind is Kind.NARROWABLE or where not in narrowed)
        ):
            fixed.add(where)
            reason: str = (
                "the values it's bound to"
                if finding.kind is Kind.NARROWABLE
                else "the members its values use"
            )
            kinds: frozenset[str] = frozenset({NARROW})
            if policy.allows(kinds):
                edit = Fix(
                    finding.rewrite,
                    reason,
                    unsafe=not policy.trusts(kinds),
                    edit=Edit.REPLACE,
                    span=finding.span,
                    kinds=kinds,
                )
        offences.append(Offence(*where, finding.name, finding.kind.value, edit, detail=finding.detail))
    return offences


def _is_final(annotation: str) -> bool:
    """Check whether an annotation is `Final` (`Final[T]`, `typing.Final`, ...).

    Returns:
      Whether it is.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(annotation, mode="eval").body
    return node_name(root.value if isinstance(root, ast.Subscript) else root) == _FINAL


def _origins(scope: _Scope, values: Iterable[ast.expr]) -> frozenset[str]:
    """Find what made a guess of `values` one: a call taken to construct its class, or a guessed local.

    Returns:
      The guessing mechanisms (`FIX_KINDS`): `constructor` for a call only guessed at, and each
      guessed local's own.

    """
    known: Known = scope.settings.known
    found: set[str] = set()
    value: ast.expr
    for value in values:
        if guessed(value, known, frozenset(), scope.inferred.types):
            found.add(CONSTRUCTOR)
        node: ast.AST
        for node in ast.walk(value):
            if isinstance(node, ast.Name) and node.id in scope.inferred.origins:
                found.update(scope.inferred.origins[node.id])
    return frozenset(found)


def _certain(scope: _Scope, value: ast.expr) -> str | None:
    """Infer `value`'s type for value flow: only a certain `--fix` inference, never a guess.

    `None` itself (which `--fix` never offers: `x: None = None` says nothing) is `"None"` here. A
    copy of a name typed as a union is unknown: an `isinstance` or `is None` check before it may
    have narrowed the name, which value flow (blind to control flow) can't see.

    Returns:
      The type as text, or `None` if it's unknown or only a guess.

    """
    if isinstance(value, ast.Constant) and value.value is None:
        return "None"
    if isinstance(value, ast.Name) and len(members(scope.inferred.types.get(value.id, "")) or ()) > 1:
        return None
    if guessed(value, scope.settings.known, frozenset(scope.inferred.guesses), scope.inferred.types):
        return None
    return inferred(value, scope.settings.known, scope.inferred.types)


def _bind(scope: _Scope, stmt: ast.stmt) -> None:
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
            _bind_targets(
                scope,
                [i.optional_vars for i in items if i.optional_vars],
                scope.unannotated(comment),
            )
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
        case ast.For(target=target) | ast.AsyncFor(target=target):
            _bind_targets(scope, [target], COMMENT_TYPED_TARGET)
        case ast.Match(cases=cases):
            _bind_captures(scope, cases)
        case ast.AugAssign(target=ast.Name(id=name) as single, op=op, value=value):
            scope.lifetime(name).bind(at(single), augmented(op, _certain(scope, value)))
        case _:
            pass


def _bind_declared(
    scope: _Scope,
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
    known: Known = scope.settings.known
    unsafe: bool = any(
        guessed(base, known, frozenset(scope.inferred.guesses), scope.inferred.types) for base in bases
    )
    origins: frozenset[str] = _origins(scope, bases) if unsafe else frozenset()
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
        fix: Fix | None = None
        if typed is not None and annotation is not None:
            fix = scope.offer(
                Inference(annotation, typed.reason, typed.kinds | split),
                origins,
                unsafe=unsafe,
                edit=Edit.DECLARE,
                span=(stmt.lineno, stmt.col_offset),
            )
            # What the rest of the scope infers from `name` knows its type, as for `name = value`.
            if name.id not in scope.inferred.types:
                scope.inferred.types[name.id] = annotation
                if unsafe:
                    scope.inferred.guesses.add(name.id)
                    scope.inferred.origins[name.id] = origins
        scope.bind(name.id, at(name), code, fix)


def _bind_targets(scope: _Scope, targets: list[ast.expr], code: str | None) -> None:
    """Bind every name in `targets`, reporting `code` for each first binding."""
    target: ast.expr
    name: ast.Name
    for target in targets:
        for name in target_names(target):
            scope.bind(name.id, at(name), code)


def _bind_captures(scope: _Scope, cases: list[ast.match_case]) -> None:
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
    settings: _Settings = _settings(tree, checks, as_text(source).splitlines(), returns(tree))
    return _value_flow(tree, _scopes(tree, settings))


def _value_flow(tree: ast.Module, scopes: list[_Scope]) -> list[Finding]:
    """Compare each name's values with its declared type, in each of `scopes`.

    Returns:
      Every finding, in source order.

    """
    escaped: frozenset[str] = frozenset(
        name for node in ast.walk(tree) if isinstance(node, ast.Global | ast.Nonlocal) for name in node.names
    )
    # Annotated only for type checkers (`if TYPE_CHECKING: x: str`): its runtime values may differ on
    # purpose, set from elsewhere.
    checking_only: frozenset[str] = frozenset(
        stmt.target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.If) and node_name(node.test) == _TYPE_CHECKING
        for stmt in node.body
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
    )
    return sorted(found for scope in scopes for found in scope.value_flow(escaped, checking_only))
