"""A signature written whole, or not at all: LVA014's and LVA015's fixes held to each other.

A function's return (LVA014) and its parameters (LVA015) are fixed together or neither is: a type
checker held to complete signatures (mypy's `disallow_incomplete_defs`, pandas's and sqlalchemy's)
reports a def with some of its annotations where it reported none with none, so a return written on
a function whose parameters stay bare, or one parameter's type among bare ones, is an error where
there was none. A function is whole once every parameter but its receiver (`self`, `cls`) is
annotated or fixed, `*args` and `**kwargs` included, and so is its return.
"""

import ast
from collections.abc import Iterable, Sequence
from dataclasses import replace

from constricter.offences import UNANNOTATED_PARAMETER, UNANNOTATED_RETURN, Offence
from constricter.rules.parameters import receivers_of
from constricter.source.syntax import FUNCTION_DEFS, FunctionDef


def whole(tree: ast.Module, offences: Sequence[Offence]) -> list[Offence]:
    """Keep a function's signature fixes only where they complete it (see the module docstring).

    `offences`: LVA014's and LVA015's, with their fixes; a function's are found by where its `def`
    and its parameters start.

    Returns:
      The offences, those of an incomplete signature with no fix.

    """
    returns: dict[tuple[int, int], Offence] = {
        (o.line, o.col): o for o in offences if o.code == UNANNOTATED_RETURN
    }
    params: dict[tuple[int, int], Offence] = {
        (o.line, o.col): o for o in offences if o.code == UNANNOTATED_PARAMETER
    }
    unfixed: set[tuple[int, int]] = set()
    receivers: frozenset[int] = receivers_of(tree)
    func: FunctionDef
    for func in _functions(tree):
        start: tuple[int, int] = (func.lineno, func.col_offset)
        needed: list[tuple[int, int]] = [
            (arg.lineno, arg.col_offset) for arg in _unannotated(func, receivers)
        ]
        fixed: bool = all(where in params and params[where].edit is not None for where in needed)
        returned: bool = func.returns is not None or (start in returns and returns[start].edit is not None)
        if not (fixed and returned):
            unfixed.update([start, *needed])
    return [
        replace(o, edit=None) if (o.line, o.col) in unfixed and o.edit is not None else o for o in offences
    ]


def _functions(tree: ast.Module) -> Iterable[FunctionDef]:
    """Walk every function of the module.

    Returns:
      Them.

    """
    return (node for node in ast.walk(tree) if isinstance(node, FUNCTION_DEFS))


def _unannotated(func: FunctionDef, receivers: frozenset[int]) -> list[ast.arg]:
    """List the parameters `func` must annotate to be whole: all but a method's receiver (`receivers`).

    Returns:
      Them, `*args` and `**kwargs` included.

    """
    args: ast.arguments = func.args
    every: list[ast.arg] = [*args.posonlyargs, *args.args, *args.kwonlyargs]
    every += [arg for arg in (args.vararg, args.kwarg) if arg is not None]
    return [
        arg
        for arg in every
        if arg.annotation is None and arg.type_comment is None and id(arg) not in receivers
    ]
