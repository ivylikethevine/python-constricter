"""The parameters a module's functions annotate, and those they leave bare (see `consistent`).

Not their locals: `--fix` annotates those, and what it wrote would count the next time round.
"""

import ast
from typing import Final, cast

from constricter.rules.walked import of_type

# A method's own: what each is follows from its class, not from the name.
_UNNAMED: Final = frozenset({"self", "cls"})
_FUNCTIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef)


def _functions(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return cast("list[ast.FunctionDef | ast.AsyncFunctionDef]", of_type(tree, *_FUNCTIONS))


def _named(args: ast.arguments) -> list[ast.arg]:
    return [arg for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs) if arg.arg not in _UNNAMED]


def annotations(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    """Find each name the module's functions annotate a parameter by, with every annotation of it.

    Not `*args` or `**kwargs`, annotated by element; a string's as the type it holds, one that
    doesn't parse left out.

    Returns:
      Each name's annotations as written, one for each time it's annotated.

    """
    found: dict[str, list[str]] = {}
    arg: ast.arg
    for arg in (arg for function in _functions(tree) for arg in _named(function.args)):
        _add(found, arg.arg, arg.annotation)
    return {name: tuple(texts) for name, texts in found.items()}


def _add(found: dict[str, list[str]], name: str, annotation: ast.expr | None) -> None:
    """Record `name`'s annotation as written, a string's as the type it holds."""
    text: str
    match annotation:
        case None:
            return
        case ast.Constant(value=str() as text):
            try:
                text = ast.unparse(ast.parse(text.strip(), mode="eval").body)
            except SyntaxError:
                return
        case _:
            text = ast.unparse(annotation)
    found.setdefault(name, []).append(text)


def bare(tree: ast.Module) -> frozenset[str]:
    """Name the parameters a module's functions leave unannotated, with no default.

    Returns:
      Them, `self` and `cls` left out.

    """
    return frozenset(
        arg.arg
        for function in _functions(tree)
        for arg in required(function.args)
        if arg.annotation is None and arg.arg not in _UNNAMED
    )


def required(args: ast.arguments) -> list[ast.arg]:
    """Find a function's parameters with no default, not `*args` or `**kwargs`.

    Returns:
      Them, in order.

    """
    positional: list[ast.arg] = [*args.posonlyargs, *args.args]
    return [
        *positional[: len(positional) - len(args.defaults)],
        *(arg for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True) if default is None),
    ]
