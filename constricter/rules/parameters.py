"""LVA015: a function's parameter with no annotation, fixed by what typed it from outside (opt-in).

A parameter left unannotated (not `self`, `cls`, `*args` or `**kwargs`) is reported where it's asked
for (`--extend-select LVA015`: ruff's ANN001 reports the same, this is for its fix). The fix writes
`: T` after its name, as `--fix` writes a local's, where a guessing mechanism typed the parameter for
the function's own check: what every call passes it (`callers`), the one class with every member
the function reads of it (`reads`), its pytest fixture's value (`fixture`), or the one type the
checked files annotate its name with (`named`; see `rules.calls.seed_parameters`). Always a guess,
resting on the mechanism; none for a parameter the function binds again, or whose type the module
can't write (`Scope.offer`).
"""

import ast
from collections.abc import Iterable
from typing import Final

from constricter.fix.core.known import Inference
from constricter.offences import PARAMETER_KINDS, UNANNOTATED_PARAMETER, Fix, Offence
from constricter.rules.scope import Scope
from constricter.source.syntax import FUNCTION_DEFS, FunctionDef

_STATIC: Final = "staticmethod"
_REASONS: Final = {
    "callers": "what every call passes it",
    "reads": "what the function reads of it",
    "fixture": "its fixture's value",
    "named": "what its name is annotated elsewhere",
}


def unannotated(tree: ast.Module, functions: Iterable[tuple[Scope, FunctionDef]]) -> list[Offence]:
    """Report each function's unannotated parameters, each fixed where its check typed it from outside.

    `functions`: each of the module's checked functions with its scope.

    Returns:
      The offences, by the parameter; a method's receiver (`self`, `cls`) isn't one.

    """
    receivers: frozenset[int] = receivers_of(tree)
    offences: list[Offence] = []
    scope: Scope
    func: FunctionDef
    for scope, func in functions:
        arg: ast.arg
        for arg in (*func.args.posonlyargs, *func.args.args, *func.args.kwonlyargs):
            if arg.annotation is not None or arg.type_comment is not None or id(arg) in receivers:
                continue
            offences.append(
                Offence(arg.lineno, arg.col_offset, arg.arg, UNANNOTATED_PARAMETER, _fix(scope, arg.arg)),
            )
    return offences


def receivers_of(tree: ast.Module) -> frozenset[int]:
    """Find the methods' receivers: the first parameter of each function directly in a class body.

    But a `@staticmethod`'s, which has none.

    Returns:
      Their `id()`s.

    """
    found: set[int] = set()
    node: ast.AST
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        member: ast.stmt
        for member in node.body:
            if not isinstance(member, FUNCTION_DEFS) or any(
                isinstance(each, ast.Name) and each.id == _STATIC for each in member.decorator_list
            ):
                continue
            first: list[ast.arg]
            if first := [*member.args.posonlyargs, *member.args.args]:
                found.add(id(first[0]))
    return frozenset(found)


def _fix(scope: Scope, name: str) -> Fix | None:
    """Offer the type a guessing mechanism gave `name` for the function's check, if one did.

    Returns:
      The fix, or `None`: nothing typed it from outside, or the module can't write the type.

    """
    origins: frozenset[str] = scope.inferred.origins.get(name, frozenset())
    kinds: frozenset[str] = origins & PARAMETER_KINDS
    annotation: str | None = scope.inferred.types.get(name)
    if not kinds or annotation is None:
        return None
    reason: str = ", ".join(_REASONS[kind] for kind in sorted(kinds))
    return scope.offer(Inference(annotation, reason, origins), origins, unsafe=True)
