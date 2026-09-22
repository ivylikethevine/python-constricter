# SPDX-License-Identifier: MIT
"""The rules: every local variable is typed where it's first bound (see README)."""

import ast
import re
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.annotations import (
    Known,
    classes,
    depth,
    factories,
    guessed,
    imported_from,
    inferred,
    is_vague,
    method_returns,
    node_name,
    returns,
)
from constricter.flow import Finding, Hierarchy, Lifetime, augmented, findings, members
from constricter.jsonc import as_text

UNANNOTATED: Final = "LVA001"
UNTYPED_TARGET: Final = "LVA002"
COMMENT_TYPED_TARGET: Final = "LVA003"
UNANNOTATED_MEMBER: Final = "LVA004"
VAGUE_TYPE: Final = "LVA005"
NESTED_TYPE: Final = "LVA006"
REDUNDANT_TYPE: Final = "LVA007"
MESSAGES: dict[str, str] = {
    UNANNOTATED: "local variable {name} is not annotated where it's first bound",
    UNTYPED_TARGET: "for/match variable {name} is untyped; declare it before the statement",
    COMMENT_TYPED_TARGET: "for variable {name} is typed only by a type comment; declare it before the loop",
    UNANNOTATED_MEMBER: "module or class variable {name} is not annotated where it's first bound",
    VAGUE_TYPE: "the annotation of {name} is vague: Any, object, or a generic without its parameters",
    NESTED_TYPE: "the annotation of {name} nests too deeply; name a part of it with a `type` alias",
    REDUNDANT_TYPE: "{name} is annotated again with the type it already has, in the same block",
}
NESTING: Final = 3  # LVA006's default depth

_FunctionDef: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef
_FUNCTION_DEFS: tuple[type[ast.FunctionDef], type[ast.AsyncFunctionDef]] = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
)
# The node class of `type X = ...` statements, by name: Python 3.11's `ast` has no `TypeAlias`.
_TYPE_ALIAS: Final = "TypeAlias"
_FUTURE: Final = "__future__"
# `from __future__` features only code that also runs on Python 2 imports: its type comments count.
_PYTHON2_FUTURES: frozenset[str] = frozenset(
    {
        "nested_scopes",
        "generators",
        "division",
        "absolute_import",
        "with_statement",
        "print_function",
        "unicode_literals",
    },
)
# Enum members mustn't be annotated: a base imported from here is one, however it's aliased.
_ENUM_MODULES: Final = frozenset({"enum"})
# The conventional name of an instance method's first parameter: typed as its class, for `--fix`.
_SELF: Final = "self"
_TYPE_CHECKING: Final = "TYPE_CHECKING"


class Level(IntEnum):
    """How strict: each level makes one more code an error rather than a warning."""

    RELAXED = 0
    STRICT = 1
    CONSTRICT = 2
    SUFFOCATE = 3


# Each level by name and by number, as the options take it.
LEVELS: dict[str, Level] = {key: level for level in Level for key in (level.name.lower(), str(level.value))}
_ERROR_FROM: dict[str, Level] = {
    UNANNOTATED: Level.STRICT,
    UNTYPED_TARGET: Level.CONSTRICT,
    COMMENT_TYPED_TARGET: Level.SUFFOCATE,
    UNANNOTATED_MEMBER: Level.STRICT,
    VAGUE_TYPE: Level.SUFFOCATE,
    NESTED_TYPE: Level.SUFFOCATE,
    REDUNDANT_TYPE: Level.SUFFOCATE,
}
# Codes reported only from a level up (the rest are reported at every level).
_REPORTED_FROM: dict[str, Level] = {VAGUE_TYPE: Level.STRICT, NESTED_TYPE: Level.STRICT}


@dataclass(frozen=True)
class _Settings:
    """One module's options, and its source lines (to place a `**rest` capture)."""

    type_comments: bool
    all_scopes: bool
    nesting: int
    lines: Sequence[str]
    known: Known  # what the module declares that `--fix` infers types from
    hierarchy: Hierarchy  # which types are narrower than which, for value flow
    owners: dict[int, str]  # each method's class, by `id()`, to type its `self`, for `--fix`


@dataclass(frozen=True, order=True)
class Offence:
    """One untyped first binding; `col` is 0-based."""

    line: int
    col: int
    name: str
    code: str = UNANNOTATED
    # The annotation `--fix` would add, where the value makes it unambiguous.
    fix: str | None = field(default=None, compare=False)
    # In a notebook, the cell (from 1); `line` is then the line in that cell.
    cell: int | None = field(default=None, compare=False)
    # Whether `fix` is a guess, applied only with `--unsafe-fixes`.
    unsafe: bool = field(default=False, compare=False)

    @property
    def message(self) -> str:
        """The report text."""
        return MESSAGES[self.code].format(name=repr(self.name))

    def is_error(self, level: Level) -> bool:
        """Check this offence's severity at `level`.

        Returns:
          Whether it's an error rather than a warning.

        """
        return level >= _ERROR_FROM[self.code]

    def is_reported(self, level: Level) -> bool:
        """Check whether `level` reports this offence.

        Returns:
          Whether it does at all.

        """
        return level >= _REPORTED_FROM.get(self.code, Level.RELAXED)


class Checks(NamedTuple):
    """What to check, beyond the defaults.

    With `type_comments`, `x = 1  # type: int` counts as annotated; with `all_scopes`, module and
    class bodies are checked too (LVA004); an annotation nested `nesting` deep is LVA006.
    """

    type_comments: bool = False
    all_scopes: bool = False
    nesting: int = NESTING


DEFAULT_CHECKS: Final = Checks()


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
        checks.type_comments or _python2_compatible(tree),
        checks.all_scopes,
        checks.nesting,
        lines,
        Known(calls, factories(tree), classes(tree), method_returns(tree)),
        Hierarchy.for_module(tree),
        _owners(tree),
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
    return sorted([*(o for scope in _scopes(tree, settings) for o in scope.reported()), *_redundant(tree)])


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


def annotation_coverage(source: str, checks: Checks = DEFAULT_CHECKS) -> Coverage:
    """Count the first bindings in `source` the rules cover, and how many are typed.

    Returns:
      The counts; `# noqa` comments don't make a binding typed. Raises `SyntaxError`.

    """
    tree: ast.Module = _parse(source, "<unknown>")
    settings: _Settings = _settings(tree, checks, source.splitlines(), {})
    scopes: list[_Scope] = _scopes(tree, settings)
    total: int = sum(len(scope.bound()) for scope in scopes)
    untyped: int = sum(o.code in _UNTYPED for scope in scopes for o in scope.reported())
    return Coverage(total - untyped, total)


def _scopes(tree: ast.Module, settings: _Settings) -> list["_Scope"]:
    """Collect the scopes to check.

    Returns:
      Every function's scope, and with `all_scopes` every module and class body's.

    """
    functions: list[_FunctionDef] = []
    _collect_functions(tree.body, functions)
    scopes: list[_Scope] = _function_scopes(functions, settings)
    if settings.all_scopes:
        scopes += _body_scopes(tree, settings)
    return scopes


def _redundant(tree: ast.Module) -> list[Offence]:
    """Find a name annotated again with the type it already has, in the same straight-line block.

    Every block (a function, module or class body; an `if`'s body and its `orelse`; ...) is checked
    on its own: two branches that never run in the same pass typing a name the same way isn't
    redundant, so they're not compared against each other.

    Returns:
      One offence (LVA007) per redundant re-annotation.

    """
    offences: list[Offence] = []
    node: ast.AST
    block: list[ast.stmt]
    for node in ast.walk(tree):
        for block in _blocks(node):
            offences += _redundant_in(block)
    return offences


def _blocks(node: ast.AST) -> Iterator[list[ast.stmt]]:
    """Find the straight-line blocks of statements directly in `node`.

    Yields:
      Each one (an `if`'s body and its `orelse` separately, and likewise for the other compound
      statements with more than one: they run in different passes, if at all).

    """
    body: list[ast.stmt]
    orelse: list[ast.stmt]
    handlers: list[ast.ExceptHandler]
    finalbody: list[ast.stmt]
    handler: ast.ExceptHandler
    cases: list[ast.match_case]
    case: ast.match_case
    match node:
        case (
            ast.Module(body=body)
            | ast.FunctionDef(body=body)
            | ast.AsyncFunctionDef(body=body)
            | ast.ClassDef(body=body)
            | ast.With(body=body)
            | ast.AsyncWith(body=body)
        ):
            yield body
        case (
            ast.If(body=body, orelse=orelse)
            | ast.For(body=body, orelse=orelse)
            | ast.AsyncFor(body=body, orelse=orelse)
            | ast.While(body=body, orelse=orelse)
        ):
            yield body
            yield orelse  # empty when there's no `else`, which is harmless: nothing to find in it
        case (
            ast.Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)
            | ast.TryStar(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)
        ):
            yield body
            for handler in handlers:
                yield handler.body
            yield orelse
            yield finalbody
        case ast.Match(cases=cases):
            for case in cases:
                yield case.body
        case _:
            pass


def _redundant_in(block: list[ast.stmt]) -> list[Offence]:
    """Find a name in `block` annotated the same way twice.

    Returns:
      One offence per repeat, at the later statement.

    """
    offences: list[Offence] = []
    seen: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    annotation: ast.expr
    for stmt in block:
        match stmt:
            case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation):
                text: str = ast.unparse(annotation)
                if seen.get(name) == text:
                    offences.append(Offence(*_at(stmt), name, REDUNDANT_TYPE))
                seen[name] = text
            case _:
                pass
    return offences


def _python2_compatible(tree: ast.Module) -> bool:
    """Check for a `from __future__` import only Python 2 needs.

    Returns:
      Whether it marks the module as written for Python 2.

    """
    return any(
        isinstance(stmt, ast.ImportFrom)
        and stmt.module == _FUTURE
        and any(alias.name in _PYTHON2_FUTURES for alias in stmt.names)
        for stmt in tree.body
    )


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


def _collect_functions(body: list[ast.stmt], into: list[_FunctionDef]) -> None:
    """Collect functions in a module or class body, through compound statements and classes."""
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, _FUNCTION_DEFS):
            into.append(stmt)
        elif isinstance(stmt, ast.ClassDef):
            _collect_functions(stmt.body, into)
        else:
            _collect_functions(_child_statements(stmt), into)


def _owners(tree: ast.Module) -> dict[int, str]:
    """Map each direct method of a class to that class's name, by the method's `id`.

    For `--fix` to type a method's `self`. A method is a function directly in a class's body,
    however deep through `if`/`try`/..., but not through a nested class's or function's own body.

    Returns:
      Each such function, by `id()`, mapped to its class's name.

    """
    found: dict[int, str] = {}
    node: ast.AST
    methods: list[_FunctionDef]
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            _direct_methods(node.body, methods)
            found.update((id(method), node.name) for method in methods)
    return found


def _direct_methods(body: list[ast.stmt], into: list[_FunctionDef]) -> None:
    """Collect the functions directly in a class's body, through compound statements.

    A nested class's own methods aren't included.
    """
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, _FUNCTION_DEFS):
            into.append(stmt)
        elif not isinstance(stmt, ast.ClassDef):
            _direct_methods(_child_statements(stmt), into)


def _child_statements(stmt: ast.stmt) -> list[ast.stmt]:
    """Collect the statements nested directly in `stmt`.

    Returns:
      Them, in source order.

    """
    children: list[ast.stmt] = []
    handler: ast.ExceptHandler
    case: ast.match_case
    match stmt:
        case ast.If() | ast.For() | ast.AsyncFor() | ast.While():
            children += stmt.body + stmt.orelse
        case ast.With() | ast.AsyncWith():
            children += stmt.body
        case ast.Try() | ast.TryStar():
            children += stmt.body
            for handler in stmt.handlers:
                children += handler.body
            children += stmt.orelse + stmt.finalbody
        case ast.Match():
            for case in stmt.cases:
                children += case.body
        case _:
            pass
    return children


def _expressions(stmt: ast.stmt) -> Iterator[ast.AST]:
    """Walk the parts of `stmt` that aren't statements.

    Yields:
      Each, as where a `:=` can bind.

    """
    child: ast.AST
    for child in ast.iter_child_nodes(stmt):
        if isinstance(child, ast.match_case | ast.ExceptHandler):
            yield from (part for part in ast.iter_child_nodes(child) if not isinstance(part, ast.stmt))
        elif not isinstance(child, ast.stmt):
            yield child


def _names(target: ast.expr) -> Iterator[ast.Name]:
    """Walk an assignment target.

    Yields:
      Each plain name it binds.

    """
    elements: list[ast.expr]
    element: ast.expr
    value: ast.expr
    match target:
        case ast.Name():
            yield target
        case ast.Tuple(elts=elements) | ast.List(elts=elements):
            for element in elements:
                yield from _names(element)
        case ast.Starred(value=value):
            yield from _names(value)
        case _:
            return


def _captures(pattern: ast.pattern, lines: Sequence[str]) -> Iterator[tuple[str, tuple[int, int]]]:
    """Walk a `case` pattern.

    Yields:
      Each name it captures, with where it's bound.

    """
    node: ast.AST
    name: str
    for node in ast.walk(pattern):
        match node:
            case ast.MatchAs(name=str() as name) | ast.MatchStar(name=str() as name):
                yield name, _at(node)
            case ast.MatchMapping(rest=str() as name):
                yield name, _rest_at(node, name, lines)
            case _:
                pass


def _at(node: ast.expr | ast.pattern | ast.stmt) -> tuple[int, int]:
    return node.lineno, node.col_offset


_REST: Final = re.compile(rb"\*\*\s*(\w+)\b")


def _rest_at(node: ast.MatchMapping, name: str, lines: Sequence[str]) -> tuple[int, int]:
    """Find `**name` in a mapping pattern's source.

    Returns:
      Its position (as `ast` gives it, a byte column), or else the pattern's start.

    """
    target: bytes = name.encode()
    number: int
    encoded: bytes
    start: int
    found: re.Match[bytes]
    for number in range(node.lineno, min(node.end_lineno or node.lineno, len(lines)) + 1):
        encoded = lines[number - 1].encode()
        start = node.col_offset if number == node.lineno else 0
        for found in _REST.finditer(encoded, start):
            if found.group(1) == target:
                return number, found.start(1)
    return _at(node)


@dataclass
class _Inferred:
    """What `--fix` knows of a scope's names so far."""

    types: dict[str, str] = field(default_factory=dict[str, str])  # each known type, for `x = y`'s
    guesses: set[str] = field(default_factory=set[str])  # `types` from an unsafe fix: copies are too


class _Scope:
    """One function body: names bound so far and offences found."""

    def __init__(
        self,
        declared: set[str],
        nested: list[_FunctionDef],
        settings: _Settings,
        *,
        unannotated: str = UNANNOTATED,
        fixable: bool = True,
    ) -> None:
        self.declared: set[str] = declared
        self.nested: list[_FunctionDef] = nested
        self.settings: _Settings = settings
        self.unannotated_code: str = unannotated
        self.fixable: bool = fixable
        self.offences: list[Offence] = []
        self.first: list[str] = []  # each first binding the rules cover, typed or not
        self.inferred: _Inferred = _Inferred()  # what `--fix` knows of the names bound so far
        self.flow: dict[str, Lifetime] = {}  # every binding of each name, for value flow

    def lifetime(self, name: str) -> Lifetime:
        """Find `name`'s value-flow record, starting one if it has none.

        Returns:
          It.

        """
        return self.flow.setdefault(name, Lifetime())

    def bind(self, name: str, at: tuple[int, int], code: str | None) -> None:
        """Bind `name` to a value value flow can't see; unless it's already bound, report `code`.

        `code` is reported at `(line, col)`; `None` means typed.
        """
        self.lifetime(name).bind(at, None)
        self._first(name, at, code, None, unsafe=False)

    def assign(self, target: ast.Name, code: str | None, value: ast.expr) -> None:
        """Bind `target` to `value` (`name = value`), offering `--fix`'s annotation for it."""
        name: str = target.id
        fix: str | None = inferred(value, self.settings.known, self.inferred.types)
        unsafe: bool = guessed(
            value,
            self.settings.known,
            frozenset(self.inferred.guesses),
            self.inferred.types,
        )
        self.lifetime(name).bind(_at(target), _certain(self, value))
        self._first(name, _at(target), code, fix, unsafe=unsafe)
        if fix is not None and name not in self.inferred.types:
            self.inferred.types[name] = fix
            if unsafe:
                self.inferred.guesses.add(name)

    def _first(
        self,
        name: str,
        at: tuple[int, int],
        code: str | None,
        fix: str | None,
        *,
        unsafe: bool,
    ) -> None:
        """Unless `name` is already bound, record its first binding, reporting `code` (`None`: typed)."""
        if name not in self.declared:
            self.declared.add(name)
            self.first.append(name)
            if code is not None:
                self.offences.append(Offence(*at, name, code, fix if self.fixable else None, unsafe=unsafe))

    def declare(self, name: str) -> None:
        """Bind `name` by an annotation (`name: T`, `name: T = ...`): a typed first binding."""
        # position is unused: `code` is `None`, so nothing is reported
        self._first(name, (0, 0), None, None, unsafe=False)

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
        # A class body (the one scope never fixed) sees none of its instances' rebindings.
        for name in self.flow.keys() if not self.fixable else escaped & self.flow.keys():
            self.flow[name].escaped = True
        return [
            found
            for name, lifetime in self.flow.items()
            if self._covered(name) and name not in skipped
            for found in findings(name, lifetime, self.settings.hierarchy)
        ]

    def _covered(self, name: str) -> bool:
        """Check whether the rules cover `name` here.

        Returns:
          Whether they do; a module or class body's dunder names are exempt.

        """
        return self.unannotated_code != UNANNOTATED_MEMBER or not (
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
        """Report an annotation that's vague (LVA005) or nests too deeply (LVA006)."""
        if is_vague(annotation):
            self.offences.append(Offence(*_at(annotation), name, VAGUE_TYPE))
        if depth(annotation) >= self.settings.nesting:
            self.offences.append(Offence(*_at(annotation), name, NESTED_TYPE))

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
                self.bind(current.target.id, _at(current.target), self.unannotated_code)

    def unannotated(self, type_comment: str | None) -> str | None:
        """Decide the code for an `=` or `with` binding.

        Returns:
          The code, or `None` if a counted type comment types it.

        """
        return None if type_comment is not None and self.settings.type_comments else self.unannotated_code


def _function_scopes(functions: list[_FunctionDef], settings: _Settings) -> list["_Scope"]:
    """Check `functions` and every function defined inside them.

    Returns:
      Their scopes.

    """
    scopes: list[_Scope] = []
    func: _FunctionDef
    for func in functions:
        nested: list[_FunctionDef] = []
        scopes.append(_function_scope(func, nested, settings))
        scopes += _function_scopes(nested, settings)
    return scopes


def _function_scope(func: _FunctionDef, functions: list[_FunctionDef], settings: _Settings) -> "_Scope":
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
    for part in _expressions(stmt):
        scope.walrus(part)
    _declare(scope, stmt)
    _bind(scope, stmt)
    child: ast.stmt
    for child in _child_statements(stmt):
        _visit(scope, child)


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
            _collect_functions(stmt.body, scope.nested)  # methods of a class defined in a function
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
            scope.lifetime(name).declare(ast.unparse(annotation), _at(target))
            if stmt.value is not None:
                scope.lifetime(name).bind(_at(target), _certain(scope, stmt.value))
        case _ if type(stmt).__name__ == _TYPE_ALIAS:
            alias: ast.expr = cast("ast.expr", next(ast.iter_child_nodes(stmt)))  # its first field, the name
            scope.declared.update(name.id for name in _names(alias))
        case ast.Try(handlers=handlers) | ast.TryStar(handlers=handlers):
            names = [handler.name for handler in handlers if handler.name]
            scope.declared.update(names)
            scope.opaque(names)
        case _:
            pass


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
        case ast.Assign(targets=targets, type_comment=comment):
            _bind_targets(scope, targets, scope.unannotated(comment))
        case ast.With(items=items, type_comment=comment) | ast.AsyncWith(items=items, type_comment=comment):
            _bind_targets(
                scope,
                [i.optional_vars for i in items if i.optional_vars],
                scope.unannotated(comment),
            )
        case ast.For(target=target, type_comment=comment) | ast.AsyncFor(target=target, type_comment=comment):
            _bind_targets(scope, [target], UNTYPED_TARGET if comment is None else COMMENT_TYPED_TARGET)
        case ast.Match(cases=cases):
            _bind_captures(scope, cases)
        case ast.AugAssign(target=ast.Name(id=name) as single, op=op, value=value):
            scope.lifetime(name).bind(_at(single), augmented(op, _certain(scope, value)))
        case _:
            pass


def _bind_targets(scope: _Scope, targets: list[ast.expr], code: str | None) -> None:
    """Bind every name in `targets`, reporting `code` for each first binding."""
    target: ast.expr
    name: ast.Name
    for target in targets:
        for name in _names(target):
            scope.bind(name.id, _at(name), code)


def _bind_captures(scope: _Scope, cases: list[ast.match_case]) -> None:
    """Bind every name the `case` patterns capture: LVA002 unless declared first."""
    case: ast.match_case
    name: str
    at: tuple[int, int]
    for case in cases:
        for name, at in _captures(case.pattern, scope.settings.lines):
            scope.bind(name, at, UNTYPED_TARGET)


def value_flow(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
) -> list[Finding]:
    """Return the value-flow findings in `source`, sorted (see `constricter.flow`). Raises `SyntaxError`.

    Not yet reported as offences: the groundwork for LVA008, LVA009 and LVA010.

    Returns:
      Every finding, in source order.

    """
    tree: ast.Module = _parse(source, filename)
    settings: _Settings = _settings(tree, checks, (), returns(tree))
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
    return sorted(
        found for scope in _scopes(tree, settings) for found in scope.value_flow(escaped, checking_only)
    )
