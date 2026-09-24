# SPDX-License-Identifier: MIT
"""Where a type checker narrows a value: the lines a test governs, and what it tests there.

An `if` or `while` narrows what its condition tests in its body (and, negated, in its `else`); a
`match` its subject in each case; an `assert`, and an `if` whose body always leaves (`return`,
`raise`, `continue`, `break`), what they test for the rest of their block. A copy of a narrowed
value there has the narrowed type, not its declared one: `--fix` offers it none (see `scope`). A
check (`isinstance`, a `TypeGuard`, a `match`) narrows any type; a truth test or a comparison only
a union (`int | None`).
"""

import ast
from collections.abc import Iterator, Mapping, Sequence
from typing import Final, TypeAlias, cast

# The lines a test governs (first and last, from 1), and whether it's a check, which narrows any
# type (not a truth test or comparison, which narrows only a union); by each value it narrows.
Region: TypeAlias = tuple[int, int, bool]
Regions: TypeAlias = Mapping[str, tuple[Region, ...]]
_LEAVING: Final = (ast.Return, ast.Raise, ast.Continue, ast.Break)
_GUARDS: Final = frozenset({"isinstance", "issubclass", "callable", "hasattr"})
_READS: Final = (ast.Name, ast.Attribute, ast.Subscript)


def regions(tree: ast.Module) -> Regions:
    """Find every region a test narrows a value in, in a module.

    Returns:
      Each value's regions.

    """
    found: dict[str, list[Region]] = {}
    text: str
    region: Region
    for text, region in _block(tree.body):
        found.setdefault(text, []).append(region)
    return {text: tuple(spans) for text, spans in found.items()}


def narrowed_at(found: Regions, value: ast.expr, line: int, *, union: bool) -> bool:
    """Check whether a read (`x`, `self.x`, `d[k]`) is narrowed at `line` by a test around it.

    `union`: whether its type is one, which a truth test or a comparison narrows too.

    Returns:
      Whether it is.

    """
    if not isinstance(value, _READS):
        return False
    spans: tuple[Region, ...] = found.get(ast.unparse(value), ())
    return any(start <= line <= end and (check or union) for start, end, check in spans)


def _block(body: Sequence[ast.stmt]) -> Iterator[tuple[str, Region]]:
    """Walk a block's statements for the regions their tests narrow, inner blocks included.

    Yields:
      Each narrowed value, and a region.

    """
    end: int = (body[-1].end_lineno or body[-1].lineno) if body else 0
    stmt: ast.stmt
    for stmt in body:
        rest: tuple[int, int] = ((stmt.end_lineno or stmt.lineno) + 1, end)
        text: str
        check: bool
        for text, check in _tested(stmt):
            yield from ((text, (*span, check)) for span in _governed(stmt, rest))
        inner: list[ast.stmt]
        for inner in _bodies(stmt):
            yield from _block(inner)


def _tested(stmt: ast.stmt) -> frozenset[tuple[str, bool]]:
    """Name what a statement's test narrows.

    Returns:
      Each value, as source text, and whether it's checked (see `Region`).

    """
    test: ast.expr
    subject: ast.expr
    match stmt:
        case ast.If(test=test) | ast.While(test=test) | ast.Assert(test=test):
            return frozenset(_narrows(test))
        case ast.Match(subject=subject) if isinstance(subject, _READS):
            return frozenset({(ast.unparse(subject), True)})
        case _:
            return frozenset()


def _narrows(test: ast.expr) -> Iterator[tuple[str, bool]]:
    """Walk a condition for the values it narrows: a value tested for truth, compared, or checked.

    Yields:
      Each, as source text (`x`, `self.x`), not what it's compared with or checked against; and
      whether it's checked (a call's argument: `isinstance`, a `TypeGuard` function).

    """
    operand: ast.expr
    values: list[ast.expr]
    left: ast.expr
    args: list[ast.expr]
    name: str
    match test:
        case ast.Name() | ast.Attribute() | ast.Subscript():
            yield ast.unparse(test), False
        case ast.UnaryOp(operand=operand):
            yield from _narrows(operand)
        case ast.BoolOp(values=values):
            yield from (found for value in values for found in _narrows(value))
        case ast.Compare(left=left) if isinstance(left, _READS):
            yield ast.unparse(left), False
        case ast.Call(func=ast.Name(id=name), args=args) if name in _GUARDS:
            yield from ((ast.unparse(arg), True) for arg in args[:1] if isinstance(arg, _READS))
        case ast.Call(args=args):  # a `TypeGuard` or `TypeIs` function may narrow any it's passed
            yield from ((ast.unparse(arg), True) for arg in args if isinstance(arg, _READS))
        case _:
            pass


def _governed(stmt: ast.stmt, rest: tuple[int, int]) -> Iterator[tuple[int, int]]:
    """Find the lines a statement's test governs.

    Yields:
      Each region: its branches, and the rest of its block (`rest`) after an `assert`, or after an
      `if` whose body always leaves.

    """
    match stmt:
        case ast.Assert():
            yield rest
        case ast.If() | ast.While():
            yield from (_span(branch) for branch in (stmt.body, stmt.orelse) if branch)
            if isinstance(stmt, ast.If) and isinstance(stmt.body[-1], _LEAVING):
                yield rest
        case _:  # a `match`, the one other statement `_tested` finds a test in
            yield from (_span(case.body) for case in cast("ast.Match", stmt).cases)


def _span(body: Sequence[ast.stmt]) -> tuple[int, int]:
    return body[0].lineno, body[-1].end_lineno or body[-1].lineno


def _bodies(stmt: ast.stmt) -> Iterator[list[ast.stmt]]:
    """Find the blocks inside a statement: a function's or class's body, a branch, a handler, a case.

    Yields:
      Each.

    """
    match stmt:
        case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef() | ast.With() | ast.AsyncWith():
            yield stmt.body
        case ast.If() | ast.For() | ast.AsyncFor() | ast.While():
            yield from (block for block in (stmt.body, stmt.orelse) if block)
        case ast.Try() | ast.TryStar():
            yield from (block for block in (stmt.body, stmt.orelse, stmt.finalbody) if block)
            yield from (handler.body for handler in stmt.handlers)
        case ast.Match():
            yield from (case.body for case in stmt.cases)
        case _:
            pass
