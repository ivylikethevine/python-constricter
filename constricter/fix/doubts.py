# SPDX-License-Identifier: MIT
"""Where a type checker sees a value otherwise than `--fix` infers it, and what `--fix` does then.

- A copy, attribute or subscript of a union may be narrowed where it's read (`if x is not None:`,
  `isinstance`), which a type checker sees and `--fix` doesn't; so may a comprehension's elements, by
  its condition (`[c for c in cs if isinstance(c, Column)]`), and a read whose type a call takes as
  its own (`deque([x])`). Their fixes are guesses.
- An ALL_CAPS module-level name is a constant to pyright, which keeps its literal's type
  (`Literal["r"]`) where `str` would widen it: a guess too, where the module passes it to a call
  or a default (see `passed`), for a parameter that may take only some values.
- `self`, and a method declared to return `Self` called on `self` or `cls`, are `Self`, not the class
  (a subclass's `self` isn't its base): written as the module already spells `Self`, or not at all.
- A generic class the module defines, written bare (`list[Mapper]`, as `self` makes one), is missing
  its type arguments: not offered.
"""

import ast
import bisect
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.known import ImportPlan, Inference
from constricter.fix.narrowed import Regions
from constricter.rules.annotations import node_name
from constricter.rules.flow import members
from constricter.rules.syntax import FunctionDef, Start, within
from constricter.rules.walked import of_type, walk

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
_NONE: Final = "None"
_OPTIONAL: Final = "Optional"
_COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_UNIONS: Final = frozenset({"Optional", "Union"})
_SELF_ORIGINS: Final = frozenset({"typing.Self", "typing_extensions.Self"})
_TYPING: Final = frozenset({"typing", "typing_extensions"})


@dataclass(frozen=True, eq=False)  # hashed by identity: a module's, cached with each function
class Tests:
    """What a module's tests (see `_TESTS`) read, where a type checker may narrow it (see `tests`)."""

    starts: tuple[Start, ...] = ()  # where each read's test starts, in source order
    texts: tuple[str, ...] = ()  # each read, as source text


class Facts(NamedTuple):
    """What of a module decides what a type checker sees otherwise than `--fix` infers.

    Each class's methods declared to return a bare `Self` (`self_returns`), its generic classes
    (`generic_classes`), and the names it passes to a call or a default (`passed`).
    """

    selfish: Mapping[str, frozenset[str]] = MappingProxyType({})
    generics: frozenset[str] = frozenset()
    passed: frozenset[str] = frozenset()
    tests: Tests = Tests()  # what its tests read (see `tests`)
    narrowed: Regions = MappingProxyType({})  # where each value is narrowed (see `narrowed.regions`)
    inner: tuple[int, ...] = ()  # the lines functions and lambdas start on, sorted (see `inner_starts`)


class Owner(NamedTuple):
    """The class a method belongs to, the name its instance (or class) goes by, and its `Self` methods."""

    name: str
    first: str  # `self`, or a classmethod's first parameter
    selfish: frozenset[str]  # its methods declared to return a bare `Self` (see `self_returns`)


def doubts(value: ast.expr, found: Inference, *, constant: bool, narrowed: frozenset[str]) -> frozenset[str]:
    """Find what makes `found`, a certain inference of `value`, a guess (see the module docstring).

    `constant`: whether the value is bound to an ALL_CAPS module-level name; `narrowed`: what the
    function tests somewhere (`isinstance(x, C)`, `x is None`, `is_c(x)`), where a type checker
    narrows it, whatever its type: the value itself, or a read whose type it takes (`found.reads`).

    Returns:
      The guessing mechanisms (`FIX_KINDS`) it then rests on; none if it stays certain.

    """
    kind: str | None = _READS.get(type(value))
    if kind is not None and (ast.unparse(value) in narrowed or len(members(found.annotation) or ()) > 1):
        return frozenset({kind})
    if narrowed.intersection(found.reads):
        return frozenset({_READS[ast.Name]})
    if isinstance(value, _COMPREHENSIONS) and any(g.ifs for g in value.generators) and _has_union(found):
        return frozenset({_COMPREHENSION})
    if constant and _literal(value):
        return frozenset({_LITERAL})
    return frozenset()


def narrowed_first(value: ast.expr, found: Inference) -> bool:
    """Check whether code reading `value` almost always narrows it first, so `found` is best not offered.

    A copy, attribute or subscript of an `X | None`, and a filtered comprehension over one, is nearly
    always checked for `None` before it's used (an `assert`, an early `return`, a walrus), and a
    checker then takes it for the `X` it's narrowed to: declaring the union breaks that. A bare
    `None` (a copy of a name only ever `None`) says nothing.

    Returns:
      Whether it is.

    """
    if found.annotation == _NONE:
        return True
    optional: bool = _NONE in (members(found.annotation) or ())
    filtered: bool = isinstance(value, _COMPREHENSIONS) and any(g.ifs for g in value.generators)
    return (isinstance(value, tuple(_READS)) and optional) or (filtered and _has_none(found.annotation))


def _has_none(annotation: str) -> bool:
    """Check whether an annotation allows `None` anywhere in it (`list[int | None]`, `list[Optional[str]]`).

    Returns:
      Whether it does.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    return any(
        (isinstance(node, ast.Constant) and node.value is None)
        or (isinstance(node, ast.Name | ast.Attribute) and node_name(node) == _OPTIONAL)
        for node in ast.walk(ast.parse(annotation, mode="eval"))
    )


def inner_starts(tree: ast.Module) -> tuple[int, ...]:
    """List the lines the module's functions and lambdas start on, for `contains_inner` to look up.

    Returns:
      Them, sorted.

    """
    inner: list[FunctionDef | ast.Lambda] = cast(
        "list[FunctionDef | ast.Lambda]",
        of_type(tree, ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda),
    )
    return tuple(sorted(node.lineno for node in inner))


def contains_inner(function: FunctionDef, starts: tuple[int, ...]) -> bool:
    """Check whether a function has a function or lambda inside it, by the lines they start on.

    Returns:
      Whether one starts after its own line and by its last: most functions have none, and needn't
      be walked for one.

    """
    return bisect.bisect_right(starts, function.lineno) < bisect.bisect_right(
        starts,
        function.end_lineno or function.lineno,
    )


def tests(tree: ast.Module) -> Tests:
    """Find what the module's tests read, once for all its functions (see `tested`).

    Returns:
      Each name, attribute and subscript in a test (an `if`'s condition, a comprehension's, a
      `match`'s subject), as source text, by where its test starts.

    """
    found: list[tuple[Start, str]] = sorted(
        ((test.lineno, test.col_offset), ast.unparse(read))
        for node in of_type(tree, *_TESTS)
        for test in _tested_parts(node)
        for read in walk(test)
        if isinstance(read, ast.Name | ast.Attribute | ast.Subscript)
    )
    return Tests(tuple(start for start, _ in found), tuple(text for _, text in found))


@lru_cache(maxsize=64)  # asked by each assignment in the function's scope
def tested(function: FunctionDef, found: Tests) -> frozenset[str]:
    """List what a function tests, where a type checker may narrow it: `x`, `self.x`, `d[k]`.

    Its own tests and those of the functions inside it, its decorators' too; from the module's
    (`found`, see `tests`), by the function's span of the source.

    Returns:
      Each name, attribute and subscript in a test, as source text.

    """
    begin: Start | None = (
        (function.decorator_list[0].lineno, function.decorator_list[0].col_offset)
        if function.decorator_list
        else None
    )
    return frozenset(found.texts[within(found.starts, function, begin)])


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
    """Check whether an annotation names one of `generics` (as the module spells them) unsubscripted.

    Returns:
      Whether it does: `Box`, `util.OrderedSet`, but not `Box[int]`.

    """
    if not generics:
        return False
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    inner: set[int] = {
        id(node.value) for node in walk(tree) if isinstance(node, ast.Subscript | ast.Attribute)
    }
    return any(
        isinstance(node, ast.Name | ast.Attribute) and id(node) not in inner and ast.unparse(node) in generics
        for node in walk(tree)
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
