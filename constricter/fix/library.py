# SPDX-License-Identifier: MIT
"""Calls to the standard library `--fix` types from the tables (see `constricter.fix.stdlib`).

A class, or a function returning one (`library_class`); a function with a fixed builtin result, one
whose arguments decide its type (`constricter.fix.overloads`), an installed package's too (see
`constricter.fix.stubbed`), or `os.environ.get` (`library_call`).
"""

import ast
from collections.abc import Callable
from typing import Final

from constricter.fix import overloads, stdlib
from constricter.fix.known import ImportPlan, Inference, Known

_STDLIB: Final = "stdlib"  # the fix kind
_STR: Final = "str"
_SELF: Final = "Self"  # a method's own class, in a template
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


def installed_call(
    value: ast.expr,
    known: Known,
    infer: Callable[[ast.expr], Inference | None],
) -> Inference | None:
    """Infer a call to an installed package's function whose arguments decide its type (`np.empty`).

    By the signature its arguments certainly match (see `constricter.fix.stubbed`); `infer` types an
    argument.

    Returns:
      The inference, or `None` for any other call, or arguments that don't decide it.

    """
    callee: str
    func: ast.Name | ast.Attribute
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (callee := ast.unparse(func)) in (
            known.names.installed
        ):
            return overloads.chosen(callee, value, known, infer)
        case _:
            return None


def installed_method(receiver: str, name: str, known: Known) -> stdlib.Method | None:
    """Find an installed class's method whose arguments or instance decide its type, on a receiver's type.

    Its class's type parameters bound to the receiver's type arguments (`np.ndarray[tuple[int], ...]`),
    and `Self` to the receiver's type.

    Returns:
      It (its `entry`: the method's key in `LibraryNames.installed`), or `None`.

    """
    tree: ast.expr = ast.parse(receiver, mode="eval").body
    base: ast.expr = tree.value if isinstance(tree, ast.Subscript) else tree
    entry: str
    if (entry := f"{ast.unparse(base)}.{name}") not in known.names.installed:
        return None
    args: list[ast.expr] = []
    if isinstance(tree, ast.Subscript):
        args = list(tree.slice.elts) if isinstance(tree.slice, ast.Tuple) else [tree.slice]
    params: tuple[str, ...] = known.names.parameters.get(ast.unparse(base), ())
    types: dict[str, str] = dict(zip(params, (ast.unparse(arg) for arg in args), strict=False))
    return stdlib.Method(entry, None, {**types, _SELF: receiver})


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
