# SPDX-License-Identifier: MIT
"""A module's plain top-level functions with a parameter left unannotated, and their parameters.

What `constricter.fix.index.callers` matches each call's arguments to (`Param`).
"""

import ast
from typing import Final, TypeAlias

# A function's parameter: its name, kind (`p` positional only, `e` either, `k` keyword only), and
# whether it has a default and an annotation.
Param: TypeAlias = tuple[str, str, bool, bool]
_POSITIONAL: Final = "p"
_EITHER: Final = "e"
_KEYWORD: Final = "k"


def open_functions(tree: ast.Module) -> dict[str, tuple[Param, ...]]:
    """Find a module's plain top-level functions with a parameter left unannotated.

    Plain: not decorated (a decorator may change how it's called), without `*args` or `**kwargs`
    (whose arguments can't be matched), and defined once.

    Returns:
      Each one's parameters, by its name.

    """
    counts: dict[str, int] = {}
    stmt: ast.stmt
    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            counts[stmt.name] = counts.get(stmt.name, 0) + 1
    return {
        stmt.name: _params(stmt.args)
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
        and counts[stmt.name] == 1
        and _plain(stmt)
    }


def _plain(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check a function is undecorated, without `*args` or `**kwargs`, and has an unannotated parameter.

    Returns:
      Whether it is.

    """
    args: ast.arguments = function.args
    return (
        not function.decorator_list
        and args.vararg is None
        and args.kwarg is None
        and any(arg.annotation is None for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs))
    )


def _params(args: ast.arguments) -> tuple[Param, ...]:
    """Read a function's parameters (see `Param`).

    Returns:
      Them, in order.

    """
    positional: list[ast.arg] = [*args.posonlyargs, *args.args]
    first_default: int = len(positional) - len(args.defaults)
    return (
        *(
            (
                arg.arg,
                _POSITIONAL if at < len(args.posonlyargs) else _EITHER,
                at >= first_default,
                arg.annotation is not None,
            )
            for at, arg in enumerate(positional)
        ),
        *(
            (arg.arg, _KEYWORD, default is not None, arg.annotation is not None)
            for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True)
        ),
    )
