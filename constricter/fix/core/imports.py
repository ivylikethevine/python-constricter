# SPDX-License-Identifier: MIT
"""Fixes that add an import: how a module can name a library type, and where an import goes."""

import ast
import bisect
from collections.abc import Iterator, Mapping, Sequence
from itertools import accumulate
from typing import Final, TypeAlias, cast
from weakref import WeakKeyDictionary

from constricter.fix.core.known import Checking, Guarded, ImportPlan, Origin, Returns
from constricter.rules.annotations import roots
from constricter.rules.syntax import FunctionDef, Start, import_bindings
from constricter.rules.walked import of_type

_TYPE_CHECKING: Final = "TYPE_CHECKING"
_FUTURE: Final = "__future__"
_ANNOTATIONS: Final = "annotations"  # `from __future__ import annotations` postpones them all
# Each module's names, for as long as its tree lives: the index reads them, then the check.
_Taken: TypeAlias = tuple[frozenset[str], frozenset[str]]
_TAKEN: Final[WeakKeyDictionary[ast.Module, _Taken]] = WeakKeyDictionary()
_Rebound: TypeAlias = dict[str, list[Start]]
_REBOUND: Final[WeakKeyDictionary[ast.Module, _Rebound]] = WeakKeyDictionary()
_Import: TypeAlias = ast.Import | ast.ImportFrom
_Inner: TypeAlias = tuple[_Import, ...]
_INNER: Final[WeakKeyDictionary[ast.Module, _Inner]] = WeakKeyDictionary()
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
    taken, values = taken_names(tree)
    bound: dict[str, str] = _bound(tree)
    return ImportPlan(
        bound,
        taken,
        _after(tree),
        _defined(tree),
        checking=Checking(
            _block(tree),
            _lazy(tree, bound),
            {
                name: origin
                for stmt in tree.body
                if isinstance(stmt, ast.If) and _is_checking(stmt.test)
                for name, origin, _ in import_bindings(stmt.body)
            },
        ),
        postponed=_postponed(tree),
        values=values,
    )


def added_origin(statement: str) -> Origin:
    """Read what an import `ImportPlan.spell` added binds: `from m import T`, or `import m`.

    Returns:
      Its origin: `("m", "T")`, or `("m", None)`.

    """
    module: str
    name: str
    module, _, name = statement.removeprefix("from ").removeprefix("import ").partition(" import ")
    return module, name or None


def added_dotted(statement: str) -> str:
    """Spell what an added import binds, dotted: `m.T` for `from m import T`, `m` for `import m`.

    Returns:
      It.

    """
    module: str
    name: str | None
    module, name = added_origin(statement)
    return f"{module}.{name}" if name else module


def present(found: ImportPlan, guarded: Mapping[str, Guarded]) -> frozenset[str]:
    """Name those of `guarded` the module imports already as their statements would.

    Under `if TYPE_CHECKING:`, or to run: a fix of its own may have added either.

    Returns:
      Each name whose import to add is one the module has.

    """
    return frozenset(
        name
        for name, each in guarded.items()
        if each.statement is not None
        and added_dotted(each.statement) in {found.checking.bound.get(name), found.bound.get(name)}
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


def checking(tree: ast.Module) -> frozenset[str]:
    """Name what the module imports under a top-level `if` on a flag, which may not run.

    `if TYPE_CHECKING:`, and any other name tested alone (`if MYPY_CHECK_RUNNING:`): what it imports
    may be unbound when the module runs.

    Returns:
      The names they bind.

    """
    return frozenset(
        alias.asname or alias.name.split(".", 1)[0]
        for stmt in tree.body
        if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Name | ast.Attribute)
        for node in stmt.body
        if isinstance(node, ast.Import | ast.ImportFrom)
        for alias in node.names
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


def inner_imports(tree: ast.Module) -> Sequence[ast.Import | ast.ImportFrom]:
    """Find the imports inside the module's functions: what one binds, it binds there alone.

    Returns:
      Them, in source order.

    """
    found: _Inner | None
    if (found := _INNER.get(tree)) is None:
        found = _INNER[tree] = tuple(_read_inner_imports(tree))
    return found


def _read_inner_imports(tree: ast.Module) -> Iterator[ast.Import | ast.ImportFrom]:
    statements: list[_Import] = cast("list[_Import]", of_type(tree, ast.Import, ast.ImportFrom))
    functions: list[FunctionDef] = cast(
        "list[FunctionDef]",
        of_type(tree, ast.FunctionDef, ast.AsyncFunctionDef),
    )
    spans: list[tuple[Start, Start]] = sorted(
        ((node.lineno, node.col_offset), (node.end_lineno or node.lineno, node.end_col_offset or 0))
        for node in functions
    )
    starts: list[Start] = [start for start, _ in spans]
    # Where the last of the functions starting no later than each one ends.
    ends: list[Start] = list(accumulate((end for _, end in spans), max))
    stmt: _Import
    for stmt in sorted(statements, key=lambda node: (node.lineno, node.col_offset)):
        start: Start = (stmt.lineno, stmt.col_offset)
        before: int = bisect.bisect_left(starts, start)
        if before and start < ends[before - 1]:
            yield stmt


def _lazy(tree: ast.Module, bound: dict[str, str]) -> frozenset[str]:
    """Name the top-level packages only the module's functions import (see `ImportPlan.lazy`).

    Returns:
      Them.

    """
    running: set[str] = {origin.partition(".")[0] for origin in bound.values()}
    return (
        frozenset(
            module.partition(".")[0]
            for stmt in inner_imports(tree)
            for module in (
                [alias.name for alias in stmt.names]
                if isinstance(stmt, ast.Import)
                else [stmt.module or ""] * (not stmt.level)
            )
        )
        - running
    )


def taken_names(tree: ast.Module) -> tuple[frozenset[str], frozenset[str]]:
    """Find every name bound anywhere in the module: its own, a function's, a class's, a parameter's.

    Returns:
      Them all; and those bound by anything but an import or a class statement (an assignment, a
      parameter, a `def`), which name a value, not a class or module, somewhere.

    """
    found: tuple[frozenset[str], frozenset[str]] | None
    if (found := _TAKEN.get(tree)) is None:
        found = _TAKEN[tree] = _read_taken_names(tree)
    return found


def _read_taken_names(tree: ast.Module) -> tuple[frozenset[str], frozenset[str]]:
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


def rebound_names(tree: ast.Module) -> dict[str, list[Start]]:
    """Find the names the module binds more than once, anywhere in it, and where.

    One bound once (by its import, say) means the same thing throughout: no function shadows it.
    One bound again is shadowed only by a function one of its bindings is in.

    Returns:
      Each such name, and where each of its bindings starts, in source order.

    """
    found: dict[str, list[Start]] | None
    if (found := _REBOUND.get(tree)) is None:
        found = _REBOUND[tree] = _read_rebound_names(tree)
    return found


def _read_rebound_names(tree: ast.Module) -> dict[str, list[Start]]:
    found: dict[str, list[Start]] = {}
    node: ast.AST
    name: str
    asname: str | None
    for node in of_type(tree, *_BINDERS):
        match node:
            case ast.alias(name=name, asname=asname):
                found.setdefault(asname or name.split(".", 1)[0], []).append((node.lineno, node.col_offset))
            case (
                ast.Name(id=name, ctx=ast.Store() | ast.Del())
                | ast.arg(arg=name)
                | ast.FunctionDef(name=name)
                | ast.AsyncFunctionDef(name=name)
                | ast.ClassDef(name=name)
                | ast.ExceptHandler(name=str() as name)
                | ast.MatchAs(name=str() as name)
            ):
                found.setdefault(name, []).append((node.lineno, node.col_offset))
            case _:
                pass
    return {name: sorted(starts) for name, starts in found.items() if len(starts) > 1}


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


def exported_names(
    returns: Returns,
    guarded: Mapping[str, Guarded],
    added: Mapping[str, str],
) -> dict[str, Origin]:
    """Find what each name `returns`' types use refers to, where the module doesn't import it to run.

    Imported for type checking alone (`guarded`), or by an import its fixes add (`added`): a library
    type it doesn't import yet (`types.ModuleType`) is named for its importers too, or they'd type
    its calls only on a second pass, once the import is in the source.

    Returns:
      Each such name's origin.

    """
    return {
        name: guarded[name].origin if name in guarded else added_origin(added[name])
        for annotation in (
            *returns.calls.values(),
            *(a for m in returns.methods.values() for a in m.values()),
        )
        for name in roots(annotation)
        if name in guarded or name in added
    }


def bound_within(func: ast.FunctionDef) -> frozenset[str]:
    """Name what a function's own body imports or defines as a class, at any depth.

    Returns:
      Each name: one nothing outside the function can spell.

    """
    found: set[str] = set()
    node: ast.AST
    for node in ast.walk(func):
        if isinstance(node, ast.ClassDef):
            found.add(node.name)
        elif isinstance(node, ast.Import | ast.ImportFrom):
            found.update((alias.asname or alias.name).split(".")[0] for alias in node.names)
    return frozenset(found)
