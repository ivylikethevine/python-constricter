"""The rule: every local variable is annotated where it's first bound.

No mainstream linter enforces it: ruff's and flake8-annotations' ANN rules stop at signatures, and
type checkers only complain about a local whose type they can't infer. The rule, per function body
(nested functions and lambdas have their own scope; module and class bodies are left to the type
checker's inference):

- the first binding of a name by `=`, by tuple unpacking, by `:=` or by `with ... as` must be an
  annotated assignment (`name: T = ...`), or come after a bare declaration (`name: T`) in the same
  function;
- a later rebinding needs nothing more;
- `for` targets, comprehension variables, `except ... as`, `match` captures, imports, `def`/`class`
  names, `type` aliases, parameters and `global`/`nonlocal` names are exempt: Python has no
  annotated form for them, or they're typed elsewhere.

Statements are walked in source order, so a name first bound in an `if` branch counts as bound for
the `else` branch below it."""

import ast
from collections.abc import Iterator
from dataclasses import dataclass

CODE = "LVA001"
MESSAGE = "local variable {name!r} is not annotated where it's first bound"

_FunctionDef = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True, order=True)
class Offence:
    """One unannotated first binding. `col` is 0-based, as `ast` and the linters count it."""

    line: int
    col: int
    name: str

    @property
    def message(self) -> str:
        return MESSAGE.format(name=self.name)


def check_source(source: str | bytes, filename: str = "<unknown>") -> list[Offence]:
    """Every unannotated local in `source`, in source order. Raises SyntaxError like `ast.parse`."""
    return check_tree(ast.parse(source, filename))


def check_tree(tree: ast.Module) -> list[Offence]:
    """Every unannotated local in an already parsed module, in source order."""
    functions: list[_FunctionDef] = []
    _collect_functions(tree.body, functions)
    offences: list[Offence] = []
    while functions:
        offences += _check_function(functions.pop(), functions)
    return sorted(offences)


def _collect_functions(body: list[ast.stmt], into: list[_FunctionDef]) -> None:
    """Functions and methods defined anywhere in a module or class body, including inside `if`,
    `try` and `with` blocks and nested classes; function bodies are collected as they're checked."""
    for stmt in body:
        if isinstance(stmt, _FunctionDef):
            into.append(stmt)
        elif isinstance(stmt, ast.ClassDef):
            _collect_functions(stmt.body, into)
        else:
            _collect_functions(_child_statements(stmt), into)


def _child_statements(stmt: ast.stmt) -> list[ast.stmt]:
    """The statements nested directly in a compound statement, in source order."""
    children: list[ast.stmt] = []
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


def _names(target: ast.expr) -> Iterator[ast.Name]:
    """Every plain name an assignment target binds (`a`, `a, b`, `[a, *rest]`); attribute and
    subscript targets bind nothing new."""
    match target:
        case ast.Name():
            yield target
        case ast.Tuple(elts=elts) | ast.List(elts=elts):
            for element in elts:
                yield from _names(element)
        case ast.Starred(value=value):
            yield from _names(value)
        case _:
            return


class _Scope:
    """One function body: the names bound so far, and the offences found."""

    def __init__(self, declared: set[str], nested: list[_FunctionDef]) -> None:
        self.declared: set[str] = declared
        self.nested: list[_FunctionDef] = nested
        self.offences: list[Offence] = []

    def bind(self, name: ast.Name) -> None:
        if name.id not in self.declared:
            self.declared.add(name.id)
            self.offences.append(Offence(name.lineno, name.col_offset, name.id))

    def walrus(self, node: ast.AST | None) -> None:
        """`:=` targets anywhere inside an expression, outermost first. A walrus in a
        comprehension binds in the enclosing function, so comprehensions are searched; a lambda is
        its own scope, and can't annotate anything, so lambdas aren't."""
        if node is None:
            return
        pending: list[ast.AST] = [node]
        while pending:
            current: ast.AST = pending.pop(0)
            if isinstance(current, ast.Lambda):
                continue
            if isinstance(current, ast.NamedExpr):
                self.bind(current.target)
            pending += ast.iter_child_nodes(current)


def _check_function(func: _FunctionDef, functions: list[_FunctionDef]) -> list[Offence]:
    """The offences in one function body; functions defined inside it are appended to `functions`
    to be checked as their own scopes."""
    args: ast.arguments = func.args
    params: set[str] = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
    for extra in (args.vararg, args.kwarg):
        if extra is not None:
            params.add(extra.arg)
    scope: _Scope = _Scope(params, functions)
    for stmt in func.body:
        _visit(scope, stmt)
    return scope.offences


def _visit(scope: _Scope, stmt: ast.stmt) -> None:
    """Bind the names one statement binds, as Python would, then walk its nested statements."""
    match stmt:
        case ast.FunctionDef() | ast.AsyncFunctionDef():
            scope.declared.add(stmt.name)
            scope.nested.append(stmt)  # its body is its own scope
            return
        case ast.ClassDef():
            scope.declared.add(stmt.name)
            _collect_functions(stmt.body, scope.nested)  # methods of a class defined in a function
            return
        case ast.Import(names=aliases) | ast.ImportFrom(names=aliases):
            for alias in aliases:
                scope.declared.add((alias.asname or alias.name).split(".")[0])
            return
        case ast.Global(names=names) | ast.Nonlocal(names=names):
            scope.declared.update(names)
            return
        case ast.AnnAssign(target=target, value=value):
            scope.walrus(value)
            if isinstance(target, ast.Name):
                scope.declared.add(target.id)
            return
        case ast.Assign(targets=targets, value=value):
            scope.walrus(value)
            for target in targets:
                for name in _names(target):
                    scope.bind(name)
            return
        case ast.AugAssign(value=value):
            scope.walrus(value)
            return
        case ast.For(target=target, iter=iter_) | ast.AsyncFor(target=target, iter=iter_):
            scope.walrus(iter_)
            scope.declared.update(name.id for name in _names(target))  # no annotated form: exempt
        case ast.With(items=items) | ast.AsyncWith(items=items):
            for item in items:
                scope.walrus(item.context_expr)
                if item.optional_vars is not None:
                    for name in _names(item.optional_vars):
                        scope.bind(name)
        case ast.Try(handlers=handlers) | ast.TryStar(handlers=handlers):
            for handler in handlers:
                if handler.name:
                    scope.declared.add(handler.name)
        case ast.Match(subject=subject, cases=cases):
            scope.walrus(subject)
            for case in cases:
                for node in ast.walk(case.pattern):
                    if isinstance(node, ast.MatchAs | ast.MatchStar) and node.name:
                        scope.declared.add(node.name)
                    elif isinstance(node, ast.MatchMapping) and node.rest:
                        scope.declared.add(node.rest)
                scope.walrus(case.guard)
        case ast.If(test=test) | ast.While(test=test) | ast.Assert(test=test):
            scope.walrus(test)
        case ast.Expr(value=value) | ast.Return(value=value):
            scope.walrus(value)
        case ast.TypeAlias(name=name):
            scope.declared.add(name.id)
            return
        case _:
            pass
    for child in _child_statements(stmt):
        _visit(scope, child)
