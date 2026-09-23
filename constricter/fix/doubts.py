# SPDX-License-Identifier: MIT
"""Where a type checker sees a value otherwise than `--fix` infers it, and what `--fix` does then.

- A copy, attribute or subscript of a union may be narrowed where it's read (`if x is not None:`,
  `isinstance`), which a type checker sees and `--fix` doesn't; so may a comprehension's elements, by
  its condition (`[c for c in cs if isinstance(c, Column)]`). Their fixes are guesses.
- An ALL_CAPS module-level name is a constant to pyright, which keeps its literal's type
  (`Literal["r"]`) where `str` would widen it: a guess too, where the module passes it to a call
  or a default (see `passed`), for a parameter that may take only some values.
- `self`, and a method declared to return `Self` called on `self` or `cls`, are `Self`, not the class
  (a subclass's `self` isn't its base): written as the module already spells `Self`, or not at all.
- A generic class the module defines, written bare (`list[Mapper]`, as `self` makes one), is missing
  its type arguments: not offered.
"""

import ast
from collections.abc import Mapping
from functools import lru_cache
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.known import ImportPlan, Inference
from constricter.rules.annotations import node_name
from constricter.rules.flow import members
from constricter.rules.syntax import FunctionDef
from constricter.rules.walked import of_type

# What a copy, an attribute and a subscript of a narrowable union rest on, as guesses.
_Read: TypeAlias = type[ast.expr]
_READS: Final[dict[_Read, str]] = {
    ast.Name: "copy",
    ast.Attribute: "attribute",
    ast.Subscript: "subscript",
}
# Where a function tests a value, a type checker may narrow it (`isinstance`, `is None`, a `TypeGuard`).
_TESTS: Final = (ast.If, ast.While, ast.Assert, ast.IfExp, ast.comprehension, ast.Match)
_SELF: Final = "Self"
_COMPREHENSION: Final = "comprehension"
_LITERAL: Final = "literal"
_COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_UNIONS: Final = frozenset({"Optional", "Union"})
_SELF_ORIGINS: Final = frozenset({"typing.Self", "typing_extensions.Self"})
_TYPING: Final = frozenset({"typing", "typing_extensions"})


class Facts(NamedTuple):
    """What of a module decides what a type checker sees otherwise than `--fix` infers.

    Each class's methods declared to return a bare `Self` (`self_returns`), its generic classes
    (`generic_classes`), and the names it passes to a call or a default (`passed`).
    """

    selfish: Mapping[str, frozenset[str]] = MappingProxyType({})
    generics: frozenset[str] = frozenset()
    passed: frozenset[str] = frozenset()


class Owner(NamedTuple):
    """The class a method belongs to, the name its instance (or class) goes by, and its `Self` methods."""

    name: str
    first: str  # `self`, or a classmethod's first parameter
    selfish: frozenset[str]  # its methods declared to return a bare `Self` (see `self_returns`)


def doubts(value: ast.expr, found: Inference, *, constant: bool, narrowed: bool) -> frozenset[str]:
    """Find what makes `found`, a certain inference of `value`, a guess (see the module docstring).

    `constant`: whether the value is bound to an ALL_CAPS module-level name; `narrowed`: whether the
    function tests the value itself somewhere (`isinstance(x, C)`, `x is None`, `is_c(x)`), where a
    type checker narrows it, whatever its type.

    Returns:
      The guessing mechanisms (`FIX_KINDS`) it then rests on; none if it stays certain.

    """
    kind: str | None = _READS.get(type(value))
    if kind is not None and (narrowed or len(members(found.annotation) or ()) > 1):
        return frozenset({kind})
    if isinstance(value, _COMPREHENSIONS) and any(g.ifs for g in value.generators) and _has_union(found):
        return frozenset({_COMPREHENSION})
    if constant and _literal(value):
        return frozenset({_LITERAL})
    return frozenset()


@lru_cache(maxsize=64)  # asked by each assignment in the function's scope
def tested(function: FunctionDef) -> frozenset[str]:
    """List what a function tests (see `_TESTS`), where a type checker may narrow it: `x`, `self.x`, `d[k]`.

    Returns:
      Each name, attribute and subscript in a test, as source text.

    """
    return frozenset(
        ast.unparse(read)
        for node in ast.walk(function)
        if isinstance(node, _TESTS)
        for test in _tested_parts(node)
        for read in ast.walk(test)
        if isinstance(read, ast.Name | ast.Attribute | ast.Subscript)
    )


def _tested_parts(node: ast.AST) -> list[ast.expr]:
    """Find what one of `_TESTS` tests: an `if`'s condition, a comprehension's, a `match`'s subject.

    Returns:
      Them.

    """
    test: ast.expr
    ifs: list[ast.expr]
    match node:
        case ast.If(test=test) | ast.While(test=test) | ast.Assert(test=test) | ast.IfExp(test=test):
            return [test]
        case ast.comprehension(ifs=ifs):
            return list(ifs)
        case _:  # a `match` (see `_TESTS`)
            return [cast("ast.Match", node).subject]


def says_self(function: FunctionDef) -> bool:
    """Check whether a function's signature mentions `Self` (`-> Self`, `other: Self`, `list[Self]`).

    In any other method, mypy takes `self` for its class, not `Self`.

    Returns:
      Whether it does.

    """
    args: ast.arguments = function.args
    annotations: list[ast.expr | None] = [
        function.returns,
        *(
            arg.annotation
            for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs, args.vararg, args.kwarg)
            if arg
        ),
    ]
    return any(
        node_name(node) == _SELF
        for annotation in annotations
        if annotation is not None
        for node in ast.walk(annotation)
        if isinstance(node, ast.Name | ast.Attribute)
    )


def passed(tree: ast.Module) -> frozenset[str]:
    """Find the names a module passes to a call (`f(X)`, `f(code=X)`) or gives a parameter as its default.

    Where a constant's `Literal` type matters: a parameter may take only some values
    (`code: Literal["invalid-type", ...]`), which `str` doesn't say.

    Returns:
      Them.

    """
    names: set[str] = set()
    node: ast.AST
    for node in of_type(tree, ast.Call, ast.arguments):
        values: list[ast.expr | None] = (
            [*node.args, *(keyword.value for keyword in node.keywords)]
            if isinstance(node, ast.Call)
            else [*cast("ast.arguments", node).defaults, *cast("ast.arguments", node).kw_defaults]
        )
        names.update(value.id for value in values if isinstance(value, ast.Name))
    return frozenset(names)


def is_constant(name: str) -> bool:
    """Check whether pyright takes a name for a constant: letters all capitals (`MAX`, `_DEFAULT_MODE`).

    Returns:
      Whether it does.

    """
    return name.upper() == name and any(char.isalpha() for char in name)


def corrected(
    value: ast.expr,
    found: Inference,
    owner: Owner | None,
    generics: frozenset[str],
    plan: ImportPlan | None,
) -> Inference | None:
    """Write `found` as a type checker sees it: `Self` where the value is one; nothing for a bare generic.

    Returns:
      The inference to offer, or `None` if there's none to.

    """
    if owner is not None and _selfish(value, found, owner):
        spelled: str | None = None if plan is None else spelled_self(plan)
        return (
            None if spelled is None else found._replace(annotation=spelled, reason=f"{found.reason}: `Self`")
        )
    return None if _bare(found.annotation, generics) else found


def _selfish(value: ast.expr, found: Inference, owner: Owner) -> bool:
    """Check whether `value` is `self`, or a `Self` method called on `self` or `cls`, typed as the class.

    Returns:
      Whether it is.

    """
    name: str
    method: str
    match value:
        case ast.Name(id=name) if name == owner.first:
            return found.annotation == owner.name
        case ast.Call(func=ast.Attribute(value=ast.Name(id=name), attr=method)) if name == owner.first:
            return method in owner.selfish and found.annotation == owner.name
        case _:
            return False


def spelled_self(plan: ImportPlan) -> str | None:
    """Name `Self` as the module already imports it (`Self`, `typing.Self`, `te.Self`).

    Not an import added for it: `typing.Self` is Python 3.11's, and the module may run on older ones.

    Returns:
      The name, or `None` if it doesn't import it.

    """
    bound: str
    origin: str
    for bound, origin in plan.bound.items():
        if origin in _SELF_ORIGINS:
            return bound
    for bound, origin in plan.bound.items():
        if origin in _TYPING:
            return f"{bound}.Self"
    return None


def _bare(annotation: str, generics: frozenset[str]) -> bool:
    """Check whether an annotation names one of `generics` without subscripting it.

    Returns:
      Whether it does.

    """
    if not generics:
        return False
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    subscripted: set[int] = {id(node.value) for node in ast.walk(tree) if isinstance(node, ast.Subscript)}
    return any(
        isinstance(node, ast.Name) and node.id in generics and id(node) not in subscripted
        for node in ast.walk(tree)
    )


def _has_union(found: Inference) -> bool:
    """Check whether an annotation has a union anywhere in it (`list[int | None]`, `Optional[str]`).

    Returns:
      Whether it has.

    """
    # `found.annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    return any(
        (isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr))
        or (isinstance(node, ast.Name) and node.id in _UNIONS)
        or (isinstance(node, ast.Attribute) and node.attr in _UNIONS)
        for node in ast.walk(ast.parse(found.annotation, mode="eval"))
    )


def _literal(value: ast.expr) -> bool:
    """Check whether `value` is a literal whose own type a `Literal` can be (a string, a number, a `bool`).

    Returns:
      Whether it is.

    """
    match value:
        case ast.Constant(value=str() | bytes() | int()):  # `bool` is an `int`
            return True
        case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=int())):
            return True
        case _:
            return False
