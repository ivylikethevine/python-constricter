# SPDX-License-Identifier: MIT
"""Fixes that add an import: how a module can name a library type, and where an import goes."""

import ast
from collections.abc import Iterator
from functools import lru_cache
from typing import Final

from constricter.fix.known import ImportPlan
from constricter.rules.syntax import import_bindings
from constricter.rules.walked import of_type

_TYPE_CHECKING: Final = "TYPE_CHECKING"
_FUTURE: Final = "__future__"
_ANNOTATIONS: Final = "annotations"  # `from __future__ import annotations` postpones them all
# The nodes that bind a name: all `_taken` needs look at.
_BINDERS: Final = (
    ast.Name,
    ast.arg,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.alias,
    ast.ExceptHandler,
    ast.MatchAs,
)


def plan(tree: ast.Module) -> ImportPlan:
    """Read what `tree` already imports, every name it binds, and where its imports end.

    Only imports that run count as binding a name to use (not those under `if TYPE_CHECKING:`: a
    module's own annotations are evaluated when it's imported); every name bound anywhere in the
    file is taken, so an added import never shadows one (nor a builtin).

    Returns:
      A fresh plan for the module's fixes.

    """
    taken: frozenset[str]
    values: frozenset[str]
    taken, values = _taken(tree)
    return ImportPlan(
        _bound(tree),
        taken,
        _after(tree),
        _defined(tree),
        block=_block(tree),
        postponed=_postponed(tree),
        values=values,
    )


def _is_checking(test: ast.expr) -> bool:
    """Check whether an `if`'s test is `TYPE_CHECKING` (or `typing.TYPE_CHECKING`).

    Returns:
      Whether it is.

    """
    return (isinstance(test, ast.Name) and test.id == _TYPE_CHECKING) or (
        isinstance(test, ast.Attribute) and test.attr == _TYPE_CHECKING
    )


def _block(tree: ast.Module) -> tuple[int, int]:
    """Find the body of the module's first top-level `if TYPE_CHECKING:` with no `else`.

    Returns:
      Its first and last line (from 1), or zeros.

    """
    return next(
        (
            (stmt.body[0].lineno, stmt.end_lineno or stmt.lineno)
            for stmt in tree.body
            if isinstance(stmt, ast.If) and _is_checking(stmt.test) and not stmt.orelse
        ),
        (0, 0),
    )


def _postponed(tree: ast.Module) -> bool:
    """Check whether the module has `from __future__ import annotations`.

    Returns:
      Whether it has.

    """
    return any(
        isinstance(stmt, ast.ImportFrom)
        and stmt.module == _FUTURE
        and any(alias.name == _ANNOTATIONS for alias in stmt.names)
        for stmt in tree.body
    )


def _bound(tree: ast.Module) -> dict[str, str]:
    """Map the names the module's own imports bind (at its top, or under a top-level `if`/`try`).

    Returns:
      Each name, mapped to what it is: `os` for `import os` (`import os.path` binds `os`),
      `os.path` for `import os.path as p`, `io.BytesIO` for `from io import BytesIO`.

    """
    return {name: origin for name, origin, _ in import_bindings(_running(tree.body))}


def _defined(tree: ast.Module) -> dict[str, int]:
    """Map each name the module binds at its top level (or under a top-level `if`/`try`) to its line.

    Returns:
      Each name, and the line it's first bound on.

    """
    found: dict[str, int] = {}
    stmt: ast.stmt
    for stmt in _running(tree.body):
        name: str
        for name in _names(stmt):
            _ = found.setdefault(name, stmt.lineno)
    return found


def _names(stmt: ast.stmt) -> list[str]:
    """Name what one top-level statement binds, when it's plainly a name (not an unpacking's parts).

    Returns:
      The names.

    """
    name: str
    targets: list[ast.expr]
    match stmt:
        case ast.Import() | ast.ImportFrom():
            return [alias.asname or alias.name.split(".", 1)[0] for alias in stmt.names]
        case ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name) | ast.ClassDef(name=name):
            return [name]
        case ast.AnnAssign(target=ast.Name(id=name)):
            return [name]
        case ast.Assign(targets=targets):
            return [target.id for target in targets if isinstance(target, ast.Name)]
        case _:
            return []


def _running(body: list[ast.stmt]) -> Iterator[ast.stmt]:
    """Walk the module's top-level statements, into `if` and `try` blocks but not `if TYPE_CHECKING:`.

    Yields:
      Each statement.

    """
    stmt: ast.stmt
    test: ast.expr
    for stmt in body:
        yield stmt
        match stmt:
            case ast.If(test=test) if not _is_checking(test):
                yield from _running(stmt.body + stmt.orelse)
            case ast.Try() | ast.TryStar():
                yield from _running(stmt.body + [s for h in stmt.handlers for s in h.body] + stmt.orelse)
            case _:
                pass


@lru_cache(maxsize=16)
def _taken(tree: ast.Module) -> tuple[frozenset[str], frozenset[str]]:
    """Find every name bound anywhere in the module: its own, a function's, a class's, a parameter's.

    Returns:
      Them all; and those bound by anything but an import or a class statement (an assignment, a
      parameter, a `def`), which name a value, not a class or module, somewhere.

    """
    names: set[str] = set()
    values: set[str] = set()
    node: ast.AST
    name: str
    asname: str | None
    for node in of_type(tree, *_BINDERS):
        match node:
            case ast.ClassDef(name=name):
                names.add(name)
            case ast.alias(name=name, asname=asname):
                names.add(asname or name.split(".", 1)[0])
            case (
                ast.Name(id=name, ctx=ast.Store())
                | ast.arg(arg=name)
                | ast.FunctionDef(name=name)
                | ast.AsyncFunctionDef(name=name)
                | ast.ExceptHandler(name=str() as name)
                | ast.MatchAs(name=str() as name)
            ):
                names.add(name)
                values.add(name)
            case _:
                pass
    return frozenset(names), frozenset(values)


def _after(tree: ast.Module) -> int:
    """Find the line an added import goes after: the end of the imports the module starts with.

    After its docstring and `from __future__` imports, before anything else (and so before an
    `if TYPE_CHECKING:` block); the top of the file (0) if it starts with neither.

    Returns:
      That line (from 1), or 0.

    """
    after: int = 0
    stmt: ast.stmt
    index: int
    for index, stmt in enumerate(tree.body):
        is_docstring: bool = (
            index == 0
            and isinstance(stmt, ast.Expr)
            and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str)
        )
        if not (is_docstring or isinstance(stmt, ast.Import | ast.ImportFrom)):
            break
        after = stmt.end_lineno or stmt.lineno
    return after
