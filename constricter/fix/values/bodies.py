"""What a function's body says of its calls: whether it's a generator, and whether it can fall off its end.

And which functions a body defines once, as a name reaches them (`plain`, `owned_bodies`).
"""

import ast
from collections import Counter
from collections.abc import Iterator, Sequence
from functools import lru_cache
from typing import cast

from constricter.source.syntax import FunctionDef, Start, has_within, own_nodes
from constricter.source.walked import classes, of_type


def plain(body: Sequence[ast.stmt]) -> list[FunctionDef]:
    """Find the plain functions directly in `body`: a `def` or `async def` no other there shares a name with.

    Returns:
      Them, in source order.

    """
    counts: Counter[str] = Counter(
        stmt.name for stmt in body if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
    )
    return [
        stmt
        for stmt in body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef) and counts[stmt.name] == 1
    ]


def owned_bodies(tree: ast.Module) -> Iterator[tuple[Sequence[ast.stmt], str]]:
    """Walk the bodies a function is named in: the module's, then each class's it defines once.

    Yields:
      Each body, and what its functions' names follow: `""`, or a class's (`Class.`).

    """
    yield tree.body, ""
    nodes: Sequence[ast.ClassDef] = classes(tree)
    owners: Counter[str] = Counter(node.name for node in nodes)
    node: ast.ClassDef
    for node in nodes:
        if owners[node.name] == 1:
            yield node.body, f"{node.name}."


def is_generator(module: ast.Module, func: FunctionDef) -> bool:
    """Check whether `func`, in `module`, is a generator: a `yield` in its own body (not a nested function's).

    Most functions have no `yield` anywhere in them (see `_yields`): only one with some is walked.

    Returns:
      Whether it is.

    """
    return has_within(_yields(module), func) and yields_itself(func)


# By the function alone, not its module too: a cache holding modules keeps checked trees alive, and
# the garbage collector then looks through them again and again (the standard library's check took
# 10% longer).
@lru_cache(maxsize=4096)  # asked of the same functions once per round
def yields_itself(func: FunctionDef) -> bool:
    """Check whether a `yield` is in `func`'s own body, not a nested function's.

    Returns:
      Whether one is.

    """
    return any(isinstance(node, ast.Yield | ast.YieldFrom) for node in own_nodes(func.body))


@lru_cache(maxsize=4)  # asked of the same module's functions, each round
def _yields(module: ast.Module) -> list[Start]:
    """Find where each of the module's `yield`s starts.

    Returns:
      Them, in source order.

    """
    return sorted(
        (node.lineno, node.col_offset)
        for node in cast("list[ast.expr]", of_type(module, ast.Yield, ast.YieldFrom))
    )


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
