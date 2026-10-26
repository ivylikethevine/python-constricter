"""Binary operators on standard-library types, by their left operand's method (`__sub__`).

`operated` picks the first signature whose operand takes the right one's type, as a type checker
does, and types the result by its declared return (see `overloads.chosen` for calls).
"""

import ast
from collections.abc import Callable, Mapping
from typing import Final, TypeAlias, cast

from constricter.fix.core.known import Inference, Known
from constricter.fix.core.signatures import (
    Signature,
    Variant,
)
from constricter.fix.libraries import stdlib
from constricter.fix.libraries.overloads import KIND, members, write
from constricter.fix.libraries.receivers import (
    MAYBE,
    NO,
    SELF_TYPE,
    YES,
    parsed,
)

# The builtin numbers a type checker takes where each of these is declared.
_PROMOTED: Final = {
    "int": ("bool",),
    "float": ("int", "bool"),
    "complex": ("float", "int", "bool"),
}


_Taken: TypeAlias = tuple[str, dict[str, str]]  # whether an operand is taken, and what it binds


def operated(
    method: stdlib.Method,
    operands: tuple[str, str],
    known: Known,
    arguments: tuple[str, ...] | None = None,
    *,
    same: bool = False,
) -> Inference | None:
    """Type a binary operator by its left operand's `method` (`__sub__`), for its right operand's type.

    `operands`: both as `stdlib.operand` names them, a generic class's instance by its class. The
    first signature whose operand takes the right one answers, as a type checker picks it: the same
    type, a class under it, or a number promoted to it (an `int` where a `float` is taken).
    `arguments`: the right operand's type arguments, where it's a generic class's instance, which
    bind the operand's own type variables (`Counter.__add__` takes a `Counter[_S]`); `same`: whether
    it's the left one's own type, as an operand of `Self` must be.

    Returns:
      The inference, or `None`: no signature certainly takes it, one before that may, the Python
      versions differ, or the right operand's class is under the left's (its reflected method may
      answer first).

    """
    left: str
    right: str
    left, right = operands
    if left != right and stdlib.inherits(right, left):
        return None
    found: set[str | None] = {
        _answered(
            variant,
            method,
            known,
            lambda member: _taken(member, operands, arguments, method.types, same=same),
        )
        for variant in stdlib.method_signatures()[method.entry]
    }
    annotation: str | None
    if (annotation := found.pop() if len(found) == 1 else None) is None:
        return None
    return Inference(annotation, f"`{method.entry}`'s return type, for its operand", frozenset({KIND}))


def _answered(
    variant: Variant,
    method: stdlib.Method,
    known: Known,
    taking: Callable[[str], _Taken],
) -> str | None:
    """Type an operator by one variant of its method's signatures (see `operated`); `taking`, `_taken`'s.

    Returns:
      What the first signature taking the right operand returns, or `None`: a signature before it
      can't be read, or may take it.

    """
    signature: Signature
    for signature in variant:
        takes: str | None
        if (takes := signature.get("takes")) is None:
            return None
        taken: list[_Taken] = [taking(member) for member in members(parsed(takes))]
        if any(verdict == MAYBE for verdict, _ in taken):
            return None
        bound: dict[str, str] | None
        if (bound := next((binds for verdict, binds in taken if verdict == YES), None)) is not None:
            template: str | None = signature["returns"]
            written: str | None = (
                None if template is None else write((template, {**method.types, **bound}), known)
            )
            return None if written is None else _deduplicated(written)
    return None


def _taken(
    member: str,
    operands: tuple[str, str],
    arguments: tuple[str, ...] | None,
    types: Mapping[str, str],
    *,
    same: bool,
) -> _Taken:
    """Decide whether an operand typed `member` takes the right operand, and what that binds.

    A generic class's instance (`arguments`) is taken by `Self` where it's the left one's own type,
    and by its own class's template (`Counter[_S]`) where each type argument the left one's binds
    (`types`) is its own, binding the others; another class's template (a base's) may take it.

    Returns:
      `YES`, `NO` or `MAYBE`, and the type variables it binds.

    """
    left: str
    right: str
    left, right = operands
    if arguments is None:
        return YES if _takes(member, left, right) else NO, {}
    if member == SELF_TYPE:
        return YES if same else NO, {}
    tree: ast.expr = parsed(member)
    # A base's (`dict[_KT, _VT]`, of an `OrderedDict`): the tables may not know it is.
    if ast.unparse(tree.value if isinstance(tree, ast.Subscript) else tree) != right:
        return MAYBE, {}
    params: list[ast.expr] = (
        []
        if not isinstance(tree, ast.Subscript)
        else tree.slice.elts
        if isinstance(tree.slice, ast.Tuple)
        else [tree.slice]
    )
    if len(params) != len(arguments) or not all(isinstance(param, ast.Name) for param in params):
        return MAYBE, {}
    bound: dict[str, str] = {}
    name: str
    argument: str
    for name, argument in zip((cast("ast.Name", param).id for param in params), arguments, strict=True):
        wanted: str | None = types.get(name, bound.get(name))
        if wanted is not None and wanted != argument:
            return NO, {}
        bound[name] = argument
    return YES, bound


def _takes(member: str, left: str, right: str) -> bool:
    """Check whether an operand typed `member` (`Self`: the left operand's own class) takes `right`.

    Returns:
      Whether it does.

    """
    wanted: str = left if member == SELF_TYPE else member
    return right == wanted or right in _PROMOTED.get(wanted, ()) or stdlib.inherits(right, wanted)


def _deduplicated(annotation: str) -> str:
    """Write each union in an annotation with each member once (`Counter[str | str]`: `Counter[str]`).

    Returns:
      The annotation.

    """
    tree: ast.expr = parsed(annotation)
    node: ast.AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            slices: list[ast.expr] = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
            joined: list[ast.expr] = [parsed(" | ".join(dict.fromkeys(members(part)))) for part in slices]
            node.slice = ast.Tuple(joined, ast.Load()) if isinstance(node.slice, ast.Tuple) else joined[0]
    return ast.unparse(tree)
