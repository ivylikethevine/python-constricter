# SPDX-License-Identifier: MIT
"""`--fix` for a module's type alias: `Json = dict[str, "Json"]`, declared `Json: TypeAlias`.

Only a value that can be nothing but a type made of others: a subscript of what `typing` or
`collections.abc` define (`Union[A, B]`, `Callable[..., R]`), of a builtin generic
(`dict[str, int]`) or of a generic class the module names (its own, another checked file's, the
standard library's); or a union of those, of builtin classes, of classes the module knows and of
`None`; or a copy of a name the module declares an alias (`Rows = Table`). Not a bare class's alias
(`Alias = Class`), which declared one loses the class's type parameters; nor a name the module
binds again, which is a variable to a type checker.

`TypeAlias` is named as the module's imports can, else imported from `typing`, which has it from
Python 3.10: certain where every Python the module runs on has it there (`min-python`), or the
module imports the name already; else a guess.
"""

import ast
import builtins
from typing import Final, TypeAlias, cast

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.libraries import stdlib
from constricter.fix.values import hinted
from constricter.fix.values.doubts import Facts
from constricter.rules.annotations import dotted, node_name

KIND: Final = "alias"  # the fix kind
_SINCE: Final = (3, 10)  # the first Python whose `typing` has `TypeAlias`
# Where every name that takes a subscript makes a type of it.
_FORMS: Final = frozenset({"typing", "typing_extensions", "collections.abc"})
_GENERICS: Final = frozenset({"dict", "frozenset", "list", "set", "tuple", "type"})
_CLASSES: Final = frozenset(
    name for name in dir(builtins) if isinstance(cast("object", getattr(builtins, name)), type)
)
# Imports that bind `TypeAlias`, or a module that has it, on every Python.
_ALWAYS: Final = frozenset({"typing.TypeAlias", "typing_extensions.TypeAlias", "typing_extensions"})
_REASON: Final = "a type alias, written as a type made of others"
# What makes a type of a call's result, by where it's from.
_FACTORIES: Final = frozenset(
    {
        *(
            f"{module}.{name}"
            for module in ("typing", "typing_extensions")
            for name in (
                "NamedTuple",
                "NewType",
                "ParamSpec",
                "TypeAliasType",
                "TypeVar",
                "TypeVarTuple",
                "TypedDict",
            )
        ),
        *(f"enum.{name}" for name in ("Enum", "Flag", "IntEnum", "IntFlag", "StrEnum")),
        "collections.namedtuple",
    },
)
# An inference, whether it's a guess, and what the guess rests on: what `Scope.valued` gives.
_Valued: TypeAlias = tuple[Inference, bool, frozenset[str]]


def factory(value: ast.expr, known: Known) -> bool:
    """Check whether `value` makes a type, not a value: a `TypeVar`, a `NewType`, a functional `NamedTuple`.

    What it's bound to can't be annotated: a type checker would take the name for a variable. However
    the factory is imported (`TypeVar`, `typing.TypeVar`, `t.TypeVar`), as long as it's `typing`'s,
    `typing_extensions`', `enum`'s or `collections.namedtuple`.

    Returns:
      Whether it does.

    """
    plan: ImportPlan | None = known.names.plan
    return (
        isinstance(value, ast.Call)
        and plan is not None
        and stdlib.resolved(value.func, plan.bound) in _FACTORIES
    )


def declares(annotation: ast.expr) -> bool:
    """Check whether an annotation declares its name a type alias: `TypeAlias`, however it's spelled.

    Returns:
      Whether it does.

    """
    return node_name(annotation) == hinted.ALIAS


def declared(
    target: ast.Name,
    value: ast.expr,
    known: Known,
    facts: Facts,
    scope: tuple[frozenset[str], tuple[int, int] | None],
) -> _Valued | None:
    """Declare the type alias a module body's `target = value` binds (see the module docstring).

    `scope`: the names the module body has declared aliases so far, and the oldest Python the
    module runs on (`min-python`).

    Returns:
      `TypeAlias` as the module names it, whether that's a guess, and what the guess rests on; or
      `None` for anything else, or a module that can't name it there.

    """
    plan: ImportPlan | None = known.names.plan
    if plan is None or facts.rebound is None or target.id in facts.rebound:
        return None
    aliases: frozenset[str]
    min_python: tuple[int, int] | None
    aliases, min_python = scope
    copied: bool = isinstance(value, ast.Name) and value.id in aliases
    named: str | None = (
        hinted.type_alias(known, target.lineno)
        if copied or composite(value, known, plan, facts.generics)
        else None
    )
    if named is None:
        return None
    certain: bool = (min_python is not None and min_python >= _SINCE) or (
        plan.bound.get(named.partition(".")[0]) in _ALWAYS
    )
    return (
        Inference(named, _REASON, frozenset({KIND})),
        not certain,
        frozenset() if certain else frozenset({KIND}),
    )


def composite(value: ast.expr, known: Known, plan: ImportPlan, generics: frozenset[str]) -> bool:
    """Check whether `value` can only be a type made of others: a subscript of a generic, or a union.

    `generics`: the generic classes the module names (see `Facts.generics`).

    Returns:
      Whether it is.

    """
    head: ast.expr
    left: ast.expr
    right: ast.expr
    match value:
        case ast.Subscript(value=ast.Name() | ast.Attribute() as head):
            return _generic(head, known, plan, generics)
        case ast.BinOp(op=ast.BitOr(), left=left, right=right):
            return all(_member(side, known, plan, generics) for side in (left, right))
        case _:
            return False


def _generic(
    head: ast.Name | ast.Attribute,
    known: Known,
    plan: ImportPlan,
    generics: frozenset[str],
) -> bool:
    """Check whether a subscript's `head` is what only a type's is: a special form, or a generic class.

    Returns:
      Whether it is, by what the module's imports say it is; never a name it binds as a value.

    """
    spelled: str | None = dotted(head)
    if spelled is None or spelled.partition(".")[0] in plan.values:
        return False
    if spelled in _GENERICS:
        return known.is_builtin(spelled)
    origin: str = stdlib.resolved(head, plan.bound) or ""
    return spelled in generics or origin.rpartition(".")[0] in _FORMS


def _member(node: ast.expr, known: Known, plan: ImportPlan, generics: frozenset[str]) -> bool:
    """Check whether a union's member is a type: `None`, a class, or a type made of others.

    Returns:
      Whether it is: a builtin class, or one the module defines or imports from a checked file.

    """
    name: str
    match node:
        case ast.Constant(value=None):
            return True
        case ast.Name(id=name):
            return (name in _CLASSES and known.is_builtin(name)) or (
                name in known.classes and name not in plan.values
            )
        case _:
            return composite(node, known, plan, generics)
