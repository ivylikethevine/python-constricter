# SPDX-License-Identifier: MIT
"""The rule: every local variable is annotated where it's first bound (see README)."""

import ast
from collections.abc import Iterator
from dataclasses import dataclass

CODE = "LVA001"
MESSAGE = "local variable {name} is not annotated where it's first bound"

_FunctionDef = ast.FunctionDef | ast.AsyncFunctionDef


@dataclass(frozen=True, order=True)
class Offence:
    """One unannotated first binding; `col` is 0-based."""

    line: int
    col: int
    name: str

    @property
    def message(self) -> str:
        """The report text."""
        return MESSAGE.format(name=repr(self.name))


def check_source(
    source: str | bytes, filename: str = "<unknown>", *, type_comments: bool = False
) -> list[Offence]:
    """Return the unannotated locals in `source`, sorted. Raises `SyntaxError`.

    With `type_comments`, `x = 1  # type: int` counts as annotated.
    """
    return check_tree(ast.parse(source, filename, type_comments=type_comments))


def check_tree(tree: ast.Module) -> list[Offence]:
    """Return the unannotated locals in a parsed module, sorted.

    `# type:` comments count only if it was parsed with `type_comments=True`.
    """
    functions: list[_FunctionDef] = []
    _collect_functions(tree.body, functions)
    offences: list[Offence] = []
    while functions:
        offences += _check_function(functions.pop(), functions)
    return sorted(offences)


def _collect_functions(body: list[ast.stmt], into: list[_FunctionDef]) -> None:
    """Collect functions in a module or class body, through compound statements and classes."""
    for stmt in body:
        if isinstance(stmt, _FunctionDef):
            into.append(stmt)
        elif isinstance(stmt, ast.ClassDef):
            _collect_functions(stmt.body, into)
        else:
            _collect_functions(_child_statements(stmt), into)


def _child_statements(stmt: ast.stmt) -> list[ast.stmt]:
    """Return the statements nested directly in `stmt`, in source order."""
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
    """Yield the plain names an assignment target binds."""
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
    """One function body: names bound so far and offences found."""

    def __init__(self, declared: set[str], nested: list[_FunctionDef]) -> None:
        self.declared: set[str] = declared
        self.nested: list[_FunctionDef] = nested
        self.offences: list[Offence] = []

    def bind(self, name: ast.Name, *, typed: bool = False) -> None:
        """Bind `name`; its first binding is an offence unless `typed`."""
        if name.id not in self.declared:
            self.declared.add(name.id)
            if not typed:
                self.offences.append(Offence(name.lineno, name.col_offset, name.id))

    def walrus(self, node: ast.AST | None) -> None:
        """Bind `:=` targets in an expression, comprehensions included, lambdas excluded."""
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
    """Return one function's offences; nested functions are queued onto `functions`."""
    args: ast.arguments = func.args
    params: set[str] = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
    for extra in (args.vararg, args.kwarg):
        if extra is not None:
            params.add(extra.arg)
    scope: _Scope = _Scope(params | {"_"}, functions)  # `_` is a discard
    for stmt in func.body:
        _visit(scope, stmt)
    return scope.offences


# One case per statement type.
# pylint: disable-next=too-complex,too-many-branches,too-many-locals
def _visit(scope: _Scope, stmt: ast.stmt) -> None:  # ruff: ignore[complex-structure, too-many-branches]
    """Bind the names `stmt` binds, then visit its nested statements."""
    match stmt:
        case ast.FunctionDef() | ast.AsyncFunctionDef():
            scope.declared.add(stmt.name)
            scope.nested.append(stmt)  # its body is its own scope
        case ast.ClassDef():
            scope.declared.add(stmt.name)
            _collect_functions(stmt.body, scope.nested)  # methods of a class defined in a function
        case ast.Import(names=aliases) | ast.ImportFrom(names=aliases):
            for alias in aliases:
                scope.declared.add((alias.asname or alias.name).split(".")[0])
        case ast.Global(names=names) | ast.Nonlocal(names=names):
            scope.declared.update(names)
        case ast.AnnAssign(target=target, value=value):
            scope.walrus(value)
            if isinstance(target, ast.Name):
                scope.declared.add(target.id)
        case ast.Assign(targets=targets, value=value, type_comment=comment):
            scope.walrus(value)
            for target in targets:
                for name in _names(target):
                    scope.bind(name, typed=comment is not None)
        case ast.AugAssign(value=value):
            scope.walrus(value)
        case ast.For(target=target, iter=iter_) | ast.AsyncFor(target=target, iter=iter_):
            scope.walrus(iter_)
            scope.declared.update(name.id for name in _names(target))  # no annotated form: exempt
        case ast.With(items=items, type_comment=comment) | ast.AsyncWith(items=items, type_comment=comment):
            for item in items:
                scope.walrus(item.context_expr)
                if item.optional_vars is not None:
                    for name in _names(item.optional_vars):
                        scope.bind(name, typed=comment is not None)
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
        case _:
            pass
    for child in _child_statements(stmt):
        _visit(scope, child)
