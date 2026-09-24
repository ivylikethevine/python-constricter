# SPDX-License-Identifier: MIT
"""Calls to the standard library `--fix` types from the tables (see `constricter.fix.stdlib`).

A class, or a function returning one (`library_class`); a function with a fixed builtin result, one
whose arguments decide its type (`constricter.fix.overloads`), or `os.environ.get`
(`library_call`).
"""

import ast
from collections.abc import Callable
from typing import Final

from constricter.fix import overloads, stdlib
from constricter.fix.known import ImportPlan, Inference, Known

_STDLIB: Final = "stdlib"  # the fix kind
_STR: Final = "str"
_WITH_DEFAULT: Final = 2  # `os.environ.get(key, default)`'s arguments


def library_class(value: ast.expr, known: Known) -> Inference | None:
    """Infer a call to a standard-library class, or a function returning one (`stdlib.CLASSES`).

    Returns:
      The class, spelled (and imported, if it must be) as the module can; or `None`.

    """
    func: ast.expr
    match value:
        case ast.Call(func=func):
            pass
        case _:
            return None
    name: str | None = stdlib.resolved(func, known.names.stdlib)
    plan: ImportPlan | None = known.names.plan
    spelled: str | None = (
        None if name not in stdlib.CLASSES or plan is None else plan.spell(stdlib.CLASSES[name])
    )
    return None if spelled is None else Inference(spelled, f"`{name}`'s return type", frozenset({_STDLIB}))


def library_variable(value: ast.expr, known: Known) -> Inference | None:
    """Infer a standard-library module's variable (`sys.path`, `os.sep`, `from sys import argv`).

    Returns:
      Its type, a class spelled (and imported, if it must be) as the module can; or `None`.

    """
    name: str | None = (
        stdlib.resolved(value, known.names.stdlib) if isinstance(value, ast.Name | ast.Attribute) else None
    )
    found: str | None = None if name is None else stdlib.VARIABLES.get(name)
    plan: ImportPlan | None = known.names.plan
    if found is not None and stdlib.is_class(found):
        found = None if plan is None else plan.spell(found)
    return (
        None
        if found is None
        else Inference(found, f"`{name}`'s annotation in typeshed", frozenset({_STDLIB}))
    )


def library_call(
    value: ast.expr,
    known: Known,
    infer: Callable[[ast.expr], Inference | None],
) -> Inference | None:
    """Infer a call to a standard-library function the tables type (see `constricter.fix.stdlib`).

    A fixed builtin result, whatever the arguments; the signature its arguments certainly match, for
    one whose overloads or type variables they decide (see `constricter.fix.overloads`); and
    `os.environ.get`'s `str | None` (`str` with a `str` default), passed positionally. `infer`
    types an argument.

    Returns:
      The inference, or `None` for any other call, or arguments that don't decide it.

    """
    call: ast.Call
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match value:
        case ast.Call(args=args, keywords=keywords) as call:
            pass
        case _:
            return None
    name: str | None = stdlib.resolved(call.func, known.names.stdlib)
    reason: str = f"`{name}`'s return type"
    kinds: frozenset[str] = frozenset({_STDLIB})
    if name in stdlib.RETURNS:
        return Inference(stdlib.RETURNS[name], reason, kinds)
    if name is not None and name in stdlib.OVERLOADS:
        return overloads.chosen(name, call, known, infer)
    # `os.environ.get`, decided by its positional arguments' types, worked out only for it.
    if keywords or name != stdlib.ENVIRONMENT:
        return None
    parts: list[Inference | None] = [infer(arg) for arg in args]
    if len(args) == 1:
        return Inference("str | None", reason, kinds)
    default: Inference | None = parts[1] if len(args) == _WITH_DEFAULT else None
    return Inference(_STR, reason, kinds | default.kinds) if default and default.annotation == _STR else None
