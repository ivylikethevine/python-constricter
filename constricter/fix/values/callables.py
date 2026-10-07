# SPDX-License-Identifier: MIT
"""`--fix` for a function, a bound method or a lambda bound to a name: `dump = json.dumps`, `grow = it.grow`.

A `Callable[..., R]`, `R` what a call of it gives whatever it's passed: a function declaring its
return (the module's, another checked file's, a builtin's or the standard library's with one), or
a method one does on a receiver whose type is known. Its parameters are left open (`...`): a
`Callable[[A], R]` would refuse the keywords and defaults a call through the name may use. Not a
class (a `type[C]`), a callee typed only by its `return`s, nor a name the function reads an
attribute of (`run.cache_clear()`), which a `Callable` doesn't have. A lambda is one of what its
body gives, where that rests on none of its parameters or its function's names: `Callable[[], R]`
if it takes none.
"""

import ast
import builtins
from collections.abc import Callable, Mapping
from typing import Final, TypeAlias

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.libraries import stdlib
from constricter.fix.values.guesses import fixed_by_callee
from constricter.fix.values.inference import inference
from constricter.rules.annotations import dotted
from constricter.rules.syntax import FunctionDef
from constricter.rules.walked import walk

KIND: Final = "callable"  # the fix kind of a function or method bound to a name
_CALLABLE: Final = "collections.abc.Callable"
_Infer: TypeAlias = Callable[[ast.expr], Inference | None]


def aliased(
    target: ast.Name,
    value: ast.expr,
    function: FunctionDef,
    known: Known,
    typed: tuple[Mapping[str, str], _Infer],
) -> tuple[Inference, ast.expr] | None:
    """Infer a name bound to a function, a bound method or a lambda, in `function`: a `Callable[..., R]`.

    `typed`: the scope's typed names, and what infers a value with them.

    Returns:
      The inference, and the call that gives `R` (whose guesses are its own); `None` for any other
      value, one whose call's type its arguments decide or nothing declares, a class, a module that
      can't name `Callable`, or a name the function reads an attribute of.

    """
    if isinstance(value, ast.Lambda):
        return _lambda(target, value, function, known)
    if not isinstance(value, ast.Name | ast.Attribute) or _is_class(value, known):
        return None
    call: ast.Call = ast.copy_location(ast.Call(value, [], []), value)
    fixed: bool = fixed_by_callee(call, known, typed[0]) or (
        stdlib.resolved(value, known.names.stdlib) in stdlib.RETURNS
    )
    found: Inference | None = typed[1](call) if fixed else None
    plan: ImportPlan | None = known.names.plan
    if found is None or plan is None or _read(target.id, function):
        return None
    spelled: str | None
    if (spelled := plan.spell(_CALLABLE)) is None:
        return None
    reason: str = f"`{ast.unparse(value)}`, whose call gives {found.reason}"
    return Inference(f"{spelled}[..., {found.annotation}]", reason, found.kinds | {KIND}), call


def _lambda(
    target: ast.Name,
    value: ast.Lambda,
    function: FunctionDef,
    known: Known,
) -> tuple[Inference, ast.expr] | None:
    """Infer a name bound to a lambda: a `Callable` of what its body gives, whatever its names hold.

    `Callable[[], R]` for one that takes nothing, `Callable[..., R]` otherwise: nothing types its
    parameters, and its function's names are read only when it's called, so its body's type rests
    on neither.

    Returns:
      The inference, and the body (whose guesses are its own); or `None` (see `aliased`).

    """
    args: ast.arguments = value.args
    params: bool = any((args.posonlyargs, args.args, args.kwonlyargs, args.vararg, args.kwarg))
    # With none of the function's names: it reads them when it's called, whatever they hold then.
    found: Inference | None = inference(value.body, known, {})
    plan: ImportPlan | None = known.names.plan
    spelled: str | None = None if plan is None or found is None else plan.spell(_CALLABLE)
    if found is None or spelled is None or _read(target.id, function):
        return None
    taken: str = "..." if params else "[]"
    reason: str = f"a lambda, whose body is {found.reason}"
    return Inference(f"{spelled}[{taken}, {found.annotation}]", reason, found.kinds | {KIND}), value.body


def _is_class(value: ast.expr, known: Known) -> bool:
    """Check whether a name is a class the module knows, or a builtin one it doesn't rebind.

    Returns:
      Whether it is: calling it constructs one, and the name is a `type[C]`.

    """
    name: str | None
    if (name := dotted(value)) is None:
        return False
    return name in known.classes or (known.is_builtin(name) and isinstance(vars(builtins).get(name), type))


def _read(name: str, function: FunctionDef) -> bool:
    """Check whether `function` reads an attribute of `name` (`name.cache_clear()`, `name.__name__`).

    Returns:
      Whether it does.

    """
    return any(
        isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == name
        for node in walk(function)
    )
