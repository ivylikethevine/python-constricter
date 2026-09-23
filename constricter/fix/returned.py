# SPDX-License-Identifier: MIT
"""`--fix` for calls to unannotated functions: their own `return` statements decide their type.

A function (or method) counts when it's plain (a `def` directly in the module or a class body, not
`async`, decorated, redefined or a generator), declares no return type, every `return` it has gives
a value whose type `--fix` is sure of, all the same, and it can't fall off its end (which returns
`None`). A module function's type is certain; a method's is a guess, since a subclass may override
it. Each `return`'s value is typed as the checker sees it there, with the function's own locals.
"""

import ast
import bisect
import operator
from collections.abc import Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, TypeAlias

from constricter.fix.known import Inference, Returned
from constricter.rules.walked import classes, of_type

# A `return` statement as the checker saw it: its value's inference (`None`: none, or unknown), and
# what that rests on if it's a guess (`FIX_KINDS`; empty: certain).
Recorded: TypeAlias = tuple[Inference | None, frozenset[str]]
_FUNCTIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef)
_END: Final = 1 << 62  # past any line: a module's span has no end
# What a call calls: a name (`f()`), or an attribute (`x.m()`), the other `None`.
_Callee: TypeAlias = tuple[str | None, str | None]
_Call: TypeAlias = tuple[tuple[int, int], _Callee]  # where a call starts (line, column), and what it calls
_SCOPES: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def returned(tree: ast.Module, recorded: Mapping[int, Sequence[Recorded]]) -> Returned:
    """Read what the module's unannotated functions and methods return.

    `recorded` holds each checked function's `return` statements, by the function's `id()`.

    Returns:
      Their return types: the module's functions', and each class's methods'.

    """
    calls: dict[str, str] = {}
    methods: dict[str, dict[str, str]] = {}
    guesses: dict[str, frozenset[str]] = {}
    name: str
    annotation: str
    origins: frozenset[str]
    for name, annotation, origins in _typed(tree.body, recorded):
        calls[name] = annotation
        if origins:
            guesses[name] = origins
    node: ast.ClassDef
    for node in _classes(tree):
        for name, annotation, origins in _typed(node.body, recorded):
            methods.setdefault(node.name, {})[name] = annotation
            if origins:
                guesses[f"{node.name}.{name}"] = origins
    return Returned(calls, methods, guesses)


def called(module: ast.Module, node: ast.AST, found: Returned) -> bool:
    """Check whether `node` (the module, a function, or a statement in it) calls any function `found` types.

    By name, or as a method. A function's decorators aren't its own calls: they're before it.

    Returns:
      Whether it does: otherwise checking it again would change nothing.

    """
    methods: set[str] = {name for methods in found.methods.values() for name in methods}
    starts: list[tuple[int, int]]
    callees: list[_Callee]
    starts, callees = _calls(module)
    span: slice = slice(
        bisect.bisect_left(starts, (getattr(node, "lineno", 0), getattr(node, "col_offset", 0))),
        bisect.bisect_left(
            starts,
            (getattr(node, "end_lineno", _END) or _END, getattr(node, "end_col_offset", 0) or 0),
        ),
    )
    return any(name in found.calls or attr in methods for name, attr in callees[span])


@lru_cache(maxsize=4)  # asked of the same module's functions, each round
def _calls(module: ast.Module) -> tuple[list[tuple[int, int]], list[_Callee]]:
    """Find every call in the module, in source order, from its one shared walk (`nodes`).

    A function's (or statement's) calls are then those within its span of the source: no walk of
    its own, which the rounds of `checker._returned` asked of every function again and again.

    Returns:
      Where each call starts (its line and column), and what it calls: a name (`f()`) or an
      attribute (`x.m()`), each `None` if not.

    """
    found: list[_Call] = []
    node: ast.AST
    name: str
    attr: str
    for node in of_type(module, ast.Call):
        match node:
            case ast.Call(func=ast.Name(id=name)):
                found.append(((node.lineno, node.col_offset), (name, None)))
            case ast.Call(func=ast.Attribute(attr=attr)):
                found.append(((node.lineno, node.col_offset), (None, attr)))
            case _:
                pass
    found.sort(key=operator.itemgetter(0))
    return [start for start, _ in found], [callee for _, callee in found]


def _typed(
    body: Sequence[ast.stmt],
    recorded: Mapping[int, Sequence[Recorded]],
) -> Iterator[tuple[str, str, frozenset[str]]]:
    """Find the plain unannotated functions directly in `body` whose `return`s decide their type.

    Yields:
      Each one's name, return type, and what that rests on if it's a guess.

    """
    counts: dict[str, int] = {}
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, _FUNCTIONS):
            counts[stmt.name] = counts.get(stmt.name, 0) + 1
    for stmt in body:
        found: tuple[str, frozenset[str]] | None
        if (
            isinstance(stmt, ast.FunctionDef)
            and counts[stmt.name] == 1
            and (found := _return_type(stmt, recorded.get(id(stmt), ()))) is not None
        ):
            yield stmt.name, *found


def _return_type(func: ast.FunctionDef, returns: Sequence[Recorded]) -> tuple[str, frozenset[str]] | None:
    """Type a plain function from its recorded `return`s.

    Returns:
      The one type they all give, and what it rests on if any is a guess; or `None` if it's
      decorated, annotated, a generator, can fall off its end, or has a `return` without a value or
      of an unknown or different type.

    """
    if (
        func.decorator_list
        or func.returns is not None
        or not returns
        or _generator(func)
        or not terminates(func.body)
    ):
        return None
    types: set[str | None] = {None if found is None else found.annotation for found, _ in returns}
    found: str | None = next(iter(types)) if len(types) == 1 else None
    return None if found is None else (found, frozenset[str]().union(*(origins for _, origins in returns)))


@lru_cache(maxsize=16)  # read once per round, of the same module
def _classes(tree: ast.Module) -> tuple[ast.ClassDef, ...]:
    """Find every class the module defines, however deep.

    Returns:
      Them.

    """
    return tuple(classes(tree))


@lru_cache(maxsize=4096)  # asked of the same functions once per round
def _generator(func: ast.FunctionDef) -> bool:
    """Check whether `func` is a generator: a `yield` in its own body (not a nested function's).

    Returns:
      Whether it is.

    """
    return any(isinstance(node, ast.Yield | ast.YieldFrom) for node in _own(func.body))


def _own(found: Sequence[ast.AST]) -> Iterator[ast.AST]:
    """Walk `found` without entering a nested function, lambda or class.

    Yields:
      Each node.

    """
    node: ast.AST
    for node in found:
        yield node
        if not isinstance(node, _SCOPES):
            yield from _own(list(ast.iter_child_nodes(node)))


def terminates(body: Sequence[ast.stmt]) -> bool:
    """Check that running `body` can't reach its end: it always returns or raises first.

    Its last statement returns or raises, or is an `if` or `try` whose every way through does (a
    `try`'s body with its `else`, and each handler), or a `with` whose body does.

    Returns:
      Whether it can't.

    """
    if not body:
        return False
    last: ast.stmt = body[-1]
    match last:
        case ast.Return() | ast.Raise():
            return True
        case ast.If():
            return terminates(last.body) and terminates(last.orelse)
        case ast.With() | ast.AsyncWith():
            return terminates(last.body)
        case ast.Try() | ast.TryStar():
            return terminates(last.orelse or last.body) and all(terminates(h.body) for h in last.handlers)
        case _:
            return False
