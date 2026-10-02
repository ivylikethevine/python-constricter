# SPDX-License-Identifier: MIT
"""Small shapes `--fix` types from their parts' types.

A union the author would write (`a if c else None`, `a or b`), `type(x)`, `d.get(key, default)` and
`os.environ[key]`. `infer` types a part as `constricter.fix.inference` does.

A part that is a read (`x`, `self.x`, `d[k]`) is taken as its declared type, which a type checker
narrows where the function tests it: it's named in the inference's `reads` (see `doubts`), and one
whose type is a union of two types or more isn't taken at all.
"""

import ast
from collections.abc import Callable
from typing import Final, TypeAlias

from constricter.fix import stdlib
from constricter.fix.known import Inference, Known
from constricter.fix.members import parsed
from constricter.rules.flow import members

Infer: TypeAlias = Callable[[ast.expr], Inference | None]
_NONE: Final = "None"
_READS: Final = (ast.Name, ast.Attribute, ast.Subscript)
_CONDITIONAL: Final = "conditional"  # the fix kind of `a if c else b`
_BOOLEAN: Final = "boolean"  # the fix kind of `a or b`
_BUILTIN: Final = "builtin"
_METHOD: Final = "method"
_STDLIB: Final = "stdlib"
_TYPE: Final = "type"
_GET: Final = "get"
_ENVIRON: Final = "os.environ"
_QUOTES: Final = frozenset("'\"")


def _is_none(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _typed(node: ast.expr, infer: Infer) -> Inference | None:
    """Type one part of a shape, a read only as the module docstring has it.

    Returns:
      Its inference, a read named in its `reads`; or `None`.

    """
    found: Inference | None = infer(node)
    if found is None or not isinstance(node, _READS):
        return found
    if len((members(found.annotation) or frozenset()) - {_NONE}) > 1:
        return None
    return found._replace(reads=(*found.reads, ast.unparse(node)))


def _or_none(annotation: str) -> str | None:
    """Write `annotation`, or `None`: as it is if it allows `None` already.

    Returns:
      The union, or `None` for an annotation that can't be read, or holds a string (a forward
      reference can't take `| None` where it's evaluated).

    """
    found: frozenset[str] | None = members(annotation)
    if found is None or _QUOTES.intersection(annotation):
        return None
    return annotation if _NONE in found else f"{annotation} | {_NONE}"


def optional(value: ast.IfExp, infer: Infer) -> Inference | None:
    """Infer `a if c else None` (or `None if c else a`): `a`'s type, or `None`.

    Returns:
      The inference, or `None` if neither side or both are `None`, the other's type isn't known, or
      `c` tests it (`x if isinstance(x, C) else None`): it's narrowed there.

    """
    sides: list[ast.expr] = [side for side in (value.body, value.orelse) if not _is_none(side)]
    tested: set[str] = {ast.unparse(node) for node in ast.walk(value.test) if isinstance(node, _READS)}
    known: bool = len(sides) == 1 and ast.unparse(sides[0]) not in tested
    found: Inference | None = _typed(sides[0], infer) if known else None
    annotation: str | None = None if found is None else _or_none(found.annotation)
    if found is None or annotation is None:
        return None
    return Inference(
        annotation,
        "one side of a conditional, or `None`",
        found.kinds | {_CONDITIONAL},
        found.reads,
    )


def boolean(value: ast.BoolOp, infer: Infer) -> Inference | None:
    """Infer `a or b` and `a and b` whose operands have one type: that type.

    `or` gives an operand before its last only if it's true, which `None` never is: `a or b` with
    `a: T | None` and `b: T` is a `T`.

    Returns:
      The last operand's type, or `None` if an operand's isn't known or they differ.

    """
    parts: list[Inference | None] = [_typed(operand, infer) for operand in value.values]
    found: list[Inference] = [part for part in parts if part is not None]
    if len(found) != len(parts):
        return None
    dropped: frozenset[str] = frozenset({_NONE}) if isinstance(value.op, ast.Or) else frozenset()
    types: set[frozenset[str]] = {(members(part.annotation) or frozenset()) - dropped for part in found}
    if len(types) != 1 or not next(iter(types)):
        return None
    operator: str = "or" if dropped else "and"
    return Inference(
        found[-1].annotation,
        f"the operands of `{operator}`, of one type",
        frozenset({_BOOLEAN}).union(*(part.kinds for part in found)),
        tuple(read for part in found for read in part.reads),
    )


def class_of(value: ast.expr, known: Known, infer: Infer) -> Inference | None:
    """Infer `type(x)`, with `x`'s type `C` known: `type[C]`.

    Returns:
      The inference, or `None` for anything else, a module that binds `type` itself, or an `x`
      whose type is a union or `None`.

    """
    arg: ast.expr
    match value:
        case ast.Call(func=ast.Name(id="type"), args=[arg], keywords=[]) if known.is_builtin(
            _TYPE,
        ) and not isinstance(arg, ast.Starred):
            found: Inference | None = _typed(arg, infer)
            types: frozenset[str] = frozenset() if found is None else members(found.annotation) or frozenset()
            if found is None or len(types) != 1 or _NONE in types:
                return None
            return Inference(
                f"{_TYPE}[{found.annotation}]",
                f"`type` of {found.reason}",
                found.kinds | {_BUILTIN},
                found.reads,
            )
        case _:
            return None


def defaulted(receiver: str, call: ast.Call, infer: Infer) -> Inference | None:
    """Infer `d.get(key, default)` on a `dict[K, V]`, by a default of type `V`: `V` (`V | None`, by `None`).

    Returns:
      The inference, or `None` for any other call, or a default of another type.

    """
    item: ast.expr
    default: ast.expr
    attr: str
    match parsed(receiver), call:
        case (
            ast.Subscript(value=ast.Name(id="dict" | "Dict"), slice=ast.Tuple(elts=[_, item])),
            ast.Call(func=ast.Attribute(attr=attr), args=[_, default], keywords=[]),
        ) if attr == _GET:
            text: str = ast.unparse(item)
            reason: str = "`dict.get` with a default of its values' type"
            if _is_none(default):
                union: str | None = _or_none(text)
                return None if union is None else Inference(union, reason, frozenset({_METHOD}))
            found: Inference | None = infer(default)
            same: bool = found is not None and found.annotation == text
            return Inference(text, reason, found.kinds | {_METHOD}) if found and same else None
        case _:
            return None


def environment(value: ast.expr, known: Known) -> Inference | None:
    """Infer `os.environ[key]`, however the module names `os.environ`: a `str`.

    Returns:
      The inference, or `None` for anything else, a slice included.

    """
    mapping: ast.expr
    index: ast.expr
    match value:
        case ast.Subscript(value=ast.Name() | ast.Attribute() as mapping, slice=index) if (
            not isinstance(index, ast.Slice) and stdlib.resolved(mapping, known.names.stdlib) == _ENVIRON
        ):
            return Inference("str", f"`{_ENVIRON}`'s values", frozenset({_STDLIB}))
        case _:
            return None
