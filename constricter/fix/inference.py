# SPDX-License-Identifier: MIT
"""What `--fix` infers a value's type from: literals, calls, and the locals a scope already typed."""

import ast
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Final, TypeAlias, cast

from constricter.fix import stdlib
from constricter.fix.known import ImportPlan, Inference, Known
from constricter.fix.members import assigned_attribute, member, returned_method, subscripted
from constricter.fix.opened import opened
from constricter.fix.returns import BUILTIN_RETURNS
from constricter.fix.targets import (
    DICT_VIEWS,
    ENUMERATE,
    RANGE,
    SAME_ELEMENTS,
    ZIP,
    counted,
    element_type,
    iterated,
    iterator_call,
    unpacked,
)
from constricter.offences import CONSTRUCTOR
from constricter.rules.annotations import GENERICS, is_vague, node_name

if TYPE_CHECKING:
    from types import EllipsisType

# Calls that return a class or a special form, not an instance of what they're named.
_FACTORIES: Final = frozenset(
    {
        "Enum",
        "Flag",
        "IntEnum",
        "IntFlag",
        "NamedTuple",
        "NewType",
        "ParamSpec",
        "StrEnum",
        "TypeVar",
        "TypeVarTuple",
        "TypedDict",
    },
)


_NUMBERS: Final = (int, float, complex)
# The builtin scalars arithmetic on which nothing can overload: numbers, and text.
_FLOAT: Final = "float"
_NUMBER_NAMES: Final = frozenset({"bool", "int", _FLOAT})
_INTEGER_NAMES: Final = frozenset({"bool", "int"})
_TEXT_NAMES: Final = frozenset({"str", "bytes"})
_STDLIB: Final = "stdlib"  # the fix kind of a standard-library call
RETURNED: Final = "returned"  # the fix kind of an unannotated function's `return`s
ASSIGNED: Final = "assigned"  # the fix kind of an instance attribute typed by its assignments
_STR: Final = "str"
COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_Comprehension: TypeAlias = ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp
# One part of a loop target (see `looped_parts`): its inference, and the values it came from.
LoopPart: TypeAlias = tuple[Inference | None, list[ast.expr]]
_WITH_DEFAULT: Final = 2  # `os.environ.get(key, default)`'s arguments
# Builtins that build a container of their argument's elements, and the type they build.
CONTAINER_BUILDERS: Final = {
    "sorted": "list[{}]",
    "list": "list[{}]",
    "set": "set[{}]",
    "frozenset": "frozenset[{}]",
    "tuple": "tuple[{}, ...]",
}


def _kinds(*parts: Inference | None, kind: str) -> frozenset[str]:
    """Collect `kind` and the kinds of each part an inference was built from.

    Returns:
      Them all.

    """
    return frozenset({kind}).union(*(part.kinds for part in parts if part is not None))


def inferred(value: ast.expr, known: Known, declared: Mapping[str, str]) -> str | None:
    """Return the annotation `value` makes unambiguous, given what the module declares (`known`).

    `inference`'s annotation, without its reason.

    Returns:
      The annotation as source text, or `None` if the value doesn't decide one.

    """
    found: Inference | None = inference(value, known, declared)
    return None if found is None else found.annotation


def inference(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer the annotation `value` makes unambiguous, and say how.

    A literal's type (containers too, when their elements agree), a call to a module function that
    declares its return type, a class it constructs, or (`declared`) another local this scope
    already gave a type: a plain copy, a subscript of a known container, an attribute of a class
    defined in this module, or a method call on it (a `str`/`bytes` or `list`/`set`/`dict` method,
    or a method of a class defined in this module; see `method_return`).

    Returns:
      The annotation as source text and its reason, or `None` if the value doesn't decide one.

    """
    return _from_local(value, known, declared) or _from_value(value, known, declared)


def _from_local(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer from what this scope already typed: a copy of a local, or a member of any typed value.

    A member (an attribute, a method call, a subscript) has its receiver typed as any value is (a
    local, `self.index`, `f()`, `x[0]`), and is looked up on it (see `members.member`); a method
    typed only by its `return`s is a guess. What typed a receiver that isn't a plain local decided
    the member too (its fix kinds).

    Returns:
      The inference, or `None`.

    """
    name: str
    receiver: ast.expr
    attr: str
    match value:
        case ast.Name(id=name) if name in declared:
            return Inference(declared[name], f"a copy of `{name}`", frozenset({"copy"}))
        case (
            ast.Attribute(value=receiver, attr=attr) | ast.Call(func=ast.Attribute(value=receiver, attr=attr))
        ):
            pass
        case ast.Subscript(value=receiver):
            attr = ""
        case _:
            return None
    typed: Inference | None = inference(receiver, known, declared)
    found: Inference | None = (
        None if typed is None else _member_of(value, typed.annotation, attr, known, declared)
    )
    if typed is None or found is None:
        return None
    return found if isinstance(receiver, ast.Name) else found._replace(kinds=found.kinds | typed.kinds)


def _member_of(
    value: ast.expr,
    receiver: str,
    attr: str,
    known: Known,
    declared: Mapping[str, str],
) -> Inference | None:
    """Type `value`, a subscript, a method call or an attribute (`attr`) of a value typed `receiver`.

    Returns:
      The inference, or `None`.

    """
    text: str | None
    match value:
        case ast.Subscript():
            text = subscripted(receiver, value, inferred(value.slice, known, declared))
            return (
                None
                if text is None
                else Inference(
                    text,
                    f"a subscript of `{ast.unparse(value.value)}`, a `{receiver}`",
                    frozenset({"subscript"}),
                )
            )
        case ast.Call():
            found: Inference | None = member(receiver, attr, value, known)
            text = None if found is not None else returned_method(receiver, attr, known)
            return (
                found
                if text is None
                else Inference(text, f"`{receiver}.{attr}`'s `return`s", frozenset({RETURNED}))
            )
        case _:
            found = member(receiver, attr, None, known)
            text = None if found is not None else assigned_attribute(receiver, attr, known)
            return (
                found
                if text is None
                else Inference(text, f"`{receiver}.{attr}`'s assignments", frozenset({ASSIGNED}))
            )


def _scalar_reason(value: ast.expr) -> str:
    """Say how `_scalar` typed `value`.

    Returns:
      The reason.

    """
    match value:
        case ast.JoinedStr():
            return "an f-string"
        case ast.UnaryOp(op=ast.Not()):
            return "`not`, always a `bool`"
        case _:
            return "a literal"


def _from_value(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer from the value itself: a literal, a container of them, or a call.

    Returns:
      The inference, or `None`.

    """
    found: str | None
    if found := _scalar(value):
        return Inference(found, _scalar_reason(value), frozenset({"literal"}))
    return (
        _container(value, known, declared)
        or _computed(value, known, declared)
        or _cast(value, known.names.casts)
        or opened(value, known)
        or library_class(value, known)
        or _library(value, known, declared)
        or _returns(value, known)
        or _called(value, known)
    )


def _returns(value: ast.expr, known: Known) -> Inference | None:
    """Infer a call to one of the module's unannotated functions whose `return`s decide its type.

    Returns:
      The inference, or `None`.

    """
    name: str
    match value:
        case ast.Call(func=ast.Name(id=name)) if name in known.returned.calls and name not in known.calls:
            return Inference(known.returned.calls[name], f"`{name}`'s `return`s", frozenset({RETURNED}))
        case _:
            return None


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


def _library(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a call to a standard-library function the tables type (see `constricter.fix.stdlib`).

    A fixed builtin result, whatever the arguments; an `AnyStr` function's, when every argument is a
    `str` (or every one a `bytes`), and an environment lookup's `str | None` (`str` with a `str`
    default), passed positionally.

    Returns:
      The inference, or `None` for any other call, or arguments that don't decide it.

    """
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match value:
        case ast.Call(func=func, args=args, keywords=keywords):
            pass
        case _:
            return None
    name: str | None = stdlib.resolved(func, known.names.stdlib)
    reason: str = f"`{name}`'s return type"
    kinds: frozenset[str] = frozenset({_STDLIB})
    if name in stdlib.RETURNS:
        return Inference(stdlib.RETURNS[name], reason, kinds)
    # The others are decided by their positional arguments' types, worked out only for them.
    if keywords or name not in stdlib.BY_ARGUMENTS:
        return None
    parts: list[Inference | None] = [inference(arg, known, declared) for arg in args]
    types: set[str | None] = {None if part is None else part.annotation for part in parts}
    if name in stdlib.ANY_STR:
        return (
            Inference(str(next(iter(types))), reason, _kinds(*parts, kind=_STDLIB))
            if len(types) == 1 and types <= _TEXT_NAMES
            else None
        )
    if len(args) == 1:
        return Inference("str | None", reason, kinds)
    default: Inference | None = parts[1] if len(args) == _WITH_DEFAULT else None
    return (
        Inference(_STR, reason, _kinds(default, kind=_STDLIB))
        if default and default.annotation == _STR
        else None
    )


def _cast(value: ast.expr, spellings: frozenset[str]) -> Inference | None:
    """Infer `typing.cast(T, x)`: `T` as written, or a string's contents.

    Returns:
      The inference, or `None` if `value` isn't such a call, or `T` is vague or not an expression.

    """
    func: ast.expr
    target: ast.expr
    match value:
        case ast.Call(func=func, args=[target, _], keywords=[]) if ast.unparse(func) in spellings:
            pass
        case _:
            return None
    text: str = (
        target.value.strip()
        if isinstance(target, ast.Constant) and isinstance(target.value, str)
        else ast.unparse(target)
    )
    try:
        parsed: ast.expr = ast.parse(text, mode="eval").body
    except SyntaxError:
        return None
    return (
        None
        if is_vague(parsed)
        else Inference(ast.unparse(parsed), "`cast`'s target type", frozenset({"cast"}))
    )


def _computed(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a value computed from others whose types are known.

    `a if c else b` when both agree; arithmetic on builtin scalars (`_arithmetic`); a list, set or
    dict comprehension whose elements' type is known, its targets typed as a loop's; `sorted`,
    `list`, `set`, `frozenset` or `tuple` of something whose elements are known; and `await` of a
    call to one of the module's `async def`s.

    Returns:
      The inference, or `None`.

    """
    body: ast.expr
    orelse: ast.expr
    name: str
    first: ast.expr
    match value:
        case ast.IfExp(body=body, orelse=orelse):
            sides: tuple[Inference | None, Inference | None] = (
                inference(body, known, declared),
                inference(orelse, known, declared),
            )
            return (
                Inference(
                    sides[0].annotation,
                    "both sides of a conditional",
                    _kinds(*sides, kind="conditional"),
                )
                if sides[0] and sides[1] and sides[0].annotation == sides[1].annotation
                else None
            )
        case ast.BinOp():
            return _arithmetic(value, known, declared)
        case ast.ListComp() | ast.SetComp() | ast.DictComp():
            return _comprehension(value, known, declared)
        case ast.Call(func=ast.Name(id=name), args=[first], keywords=[]) if (
            name in CONTAINER_BUILDERS and known.is_builtin(name)
        ):
            found: Inference | None = looped(first, known, declared)
            built: str = CONTAINER_BUILDERS[name]
            return (
                None
                if found is None
                else Inference(
                    built.format(found.annotation),
                    f"`{name}` of {found.reason}",
                    _kinds(found, kind="builder"),
                )
            )
        case ast.Await(value=ast.Call(func=ast.Name(id=name))) if name in known.awaits:
            return Inference(
                known.awaits[name],
                f"`{name}`'s declared return type, awaited",
                frozenset({"await"}),
            )
        case _:
            return None


def _arithmetic(value: ast.BinOp, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer arithmetic on builtin scalars, whose operators nothing can overload.

    Numbers: `/` gives a `float`; `+`, `-`, `*`, `//` and `%` a `float` if either side is one, else
    an `int` (`**` can give a `float` from `int`s, so it's left out). `str` and `bytes`: `+` of two,
    `*` by an `int`, and `%` formatting give the same type back.

    Returns:
      The inference, or `None` for any other operator or operand.

    """
    sides: tuple[Inference | None, Inference | None] = (
        inference(value.left, known, declared),
        inference(value.right, known, declared),
    )
    left: str | None = None if sides[0] is None else sides[0].annotation
    right: str | None = None if sides[1] is None else sides[1].annotation
    op: ast.operator = value.op
    reason: str = "arithmetic on builtin types"
    kinds: frozenset[str] = _kinds(*sides, kind="arithmetic")
    if left in _NUMBER_NAMES and right in _NUMBER_NAMES:
        if isinstance(op, ast.Div):
            return Inference("float", reason, kinds)
        if isinstance(op, ast.Add | ast.Sub | ast.Mult | ast.FloorDiv | ast.Mod):
            return Inference(_FLOAT if _FLOAT in {left, right} else "int", reason, kinds)
        return None
    text: str | None = left if left in _TEXT_NAMES else None
    return Inference(text, reason, kinds) if text is not None and _keeps_text(op, text, right) else None


def _keeps_text(op: ast.operator, text: str, right: str | None) -> bool:
    """Check whether `text op right` (`text` a `str` or `bytes`) gives `text` back.

    Returns:
      Whether it does: `+` of two, `*` by an integer, or `%` formatting.

    """
    if isinstance(op, ast.Add):
        return right == text
    if isinstance(op, ast.Mult):
        return right in _INTEGER_NAMES
    return isinstance(op, ast.Mod)


def _comprehension(
    value: ast.ListComp | ast.SetComp | ast.DictComp,
    known: Known,
    declared: Mapping[str, str],
) -> Inference | None:
    """Infer a comprehension's type from its elements', its targets typed as a loop's are.

    Returns:
      The inference, or `None` if an element's type isn't known.

    """
    inside: Mapping[str, str] = comprehended(value, known, declared)
    reason: str = "a comprehension's elements"
    # What the targets iterate over decided them too.
    loops: list[Inference | None] = [looped(g.iter, known, inside) for g in value.generators]
    match value:
        case ast.DictComp():
            key: Inference | None = inference(value.key, known, inside)
            item: Inference | None = inference(value.value, known, inside)
            return (
                Inference(
                    f"dict[{key.annotation}, {item.annotation}]",
                    reason,
                    _kinds(key, item, *loops, kind="comprehension"),
                )
                if key and item
                else None
            )
        case _:
            element: Inference | None = inference(value.elt, known, inside)
            kind: str = "list" if isinstance(value, ast.ListComp) else "set"
            return (
                Inference(
                    f"{kind}[{element.annotation}]",
                    reason,
                    _kinds(element, *loops, kind="comprehension"),
                )
                if element
                else None
            )


def comprehended(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Mapping[str, str]:
    """Type the targets of every comprehension in `value`, as a loop's are, over what's `declared`.

    A target whose type isn't known is dropped (it shadows any outer name of the same name).

    Returns:
      `declared`, with the targets' types: `declared` itself, uncopied, where there's none (most values).

    """
    return targets_typed(
        [node for node in ast.walk(value) if isinstance(node, COMPREHENSIONS)],
        known,
        declared,
    )


def targets_typed(
    comprehensions: Sequence[ast.AST],
    known: Known,
    declared: Mapping[str, str],
) -> Mapping[str, str]:
    """Type the targets of `comprehensions`, as a loop's are, over what's `declared` (see `comprehended`).

    Returns:
      `declared`, with the targets' types: `declared` itself, uncopied, where there are none.

    """
    if not comprehensions:
        return declared
    inside: dict[str, str] = dict(declared)
    node: ast.AST
    generator: ast.comprehension
    for node in comprehensions:
        for generator in cast("_Comprehension", node).generators:
            found: Inference | None = looped(generator.iter, known, inside)
            name: ast.Name
            part: str | None
            for name, part in unpacked(generator.target, None if found is None else found.annotation):
                if part is None:
                    _ = inside.pop(name.id, None)
                else:
                    inside[name.id] = part
    return inside


def _scalar(value: ast.expr) -> str | None:
    constant: str | bytes | bool | int | float | complex | EllipsisType | None
    match value:
        case ast.Constant(value=bool() | int() | float() | complex() | str() | bytes() as constant):
            return type(constant).__name__
        case ast.UnaryOp(op=ast.USub() | ast.UAdd(), operand=ast.Constant(value=constant)) if isinstance(
            constant,
            _NUMBERS,
        ) and not isinstance(constant, bool):
            return type(constant).__name__
        case ast.UnaryOp(op=ast.Not()):  # `not x` always yields a real `bool`, unlike a comparison
            return "bool"
        case ast.JoinedStr():
            return "str"
        case _:
            return None


def _container(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a list, set, tuple or dict display whose elements' types agree.

    Returns:
      The inference, or `None`.

    """
    elements: list[ast.expr]
    keys: list[ast.expr | None]
    values: list[ast.expr]
    found: str | None = None
    parts: list[Inference | None] = []
    match value:
        case ast.List(elts=elements) | ast.Set(elts=elements) if elements:
            parts = [inference(element, known, declared) for element in elements]
            element: str | None = _uniform(parts)
            found = f"{'list' if isinstance(value, ast.List) else 'set'}[{element}]" if element else None
        case ast.Tuple(elts=elements) if elements:
            parts = [inference(element, known, declared) for element in elements]
            found = _tuple(parts, known.max_length)
        case ast.Dict(keys=keys, values=values) if keys and None not in keys:
            present: list[ast.expr] = [k for k in keys if k is not None]
            key_parts: list[Inference | None] = [inference(k, known, declared) for k in present]
            item_parts: list[Inference | None] = [inference(v, known, declared) for v in values]
            parts = [*key_parts, *item_parts]
            key: str | None = _uniform(key_parts)
            item: str | None = _uniform(item_parts)
            found = f"dict[{key}, {item}]" if key and item else None
        case _:
            pass
    return (
        None
        if found is None
        else Inference(
            found,
            f"a {found.partition('[')[0]} whose elements' types agree",
            _kinds(*parts, kind="container"),
        )
    )


def _tuple(parts: Sequence[Inference | None], max_length: int) -> str | None:
    """Type a tuple display from its elements' types.

    One type per element (`tuple[int, str]`), up to `max_length` of them; a longer one (LVA011's)
    is `tuple[T, ...]` when every element is a `T`, and nothing when they differ: its fields need
    names, not a list of types.

    Returns:
      The annotation, or `None` if an element's type isn't known or a long tuple's differ.

    """
    known_parts: list[Inference] = [part for part in parts if part is not None]
    if len(known_parts) != len(parts):
        return None
    if len(parts) <= max_length:
        return f"tuple[{', '.join(part.annotation for part in known_parts)}]"
    element: str | None = _uniform(parts)
    return None if element is None else f"tuple[{element}, ...]"


def _uniform(parts: Sequence[Inference | None]) -> str | None:
    """Find the one type every element has.

    Returns:
      That type, or `None` if they differ or any is unknown.

    """
    types: set[str | None] = {None if part is None else part.annotation for part in parts}
    return next(iter(types)) if len(types) == 1 else None


def _called(value: ast.expr, known: Known) -> Inference | None:
    func: ast.expr
    name: str
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if ast.unparse(func) in known.calls:
            return Inference(
                known.calls[ast.unparse(func)],
                f"`{ast.unparse(func)}`'s declared return type",
                frozenset({"call"}),
            )
        case ast.Call(func=ast.Name(id=name)) if name in BUILTIN_RETURNS and known.is_builtin(name):
            return Inference(BUILTIN_RETURNS[name], f"`{name}`'s fixed return type", frozenset({"builtin"}))
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if constructs(
            node_name(func),
            known.factories,
        ):
            return Inference(
                ast.unparse(func),
                f"a call to `{ast.unparse(func)}`, taken to construct one",
                frozenset({CONSTRUCTOR}),
            )
        case _:
            return None


def constructs(name: str, known_factories: frozenset[str]) -> bool:
    """Check whether a call to `name` constructs a class, by its capitalised name.

    Returns:
      Whether it does, and is worth annotating: `name` isn't a known factory, by import
      (`known_factories`) or by its bare name (`_FACTORIES`, for one imported some other way).

    """
    return (
        name[:1].isupper() and name not in known_factories and name not in _FACTORIES and name not in GENERICS
    )


def looped(iterable: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer what a `for` loop over `iterable` binds each time round, and say how.

    `range()` gives `int`s; `enumerate(x)` `tuple[int, T]` and `zip(x, y)` `tuple[T, U]`, given
    `x`'s and `y`'s; `reversed(x)` and `sorted(x)` what `x` does; a `dict`'s `.keys()`, `.values()`
    and `.items()` its keys, values and pairs; and anything else whose type is inferred, its
    elements: a `list`, `set`, `frozenset` or `tuple[T, ...]`'s `T`, a `dict`'s keys, a `str`'s
    `str`s and a `bytes`'s `int`s.

    Returns:
      The element's annotation as source text and its reason, or `None` if it isn't known.

    """
    call: tuple[str, list[ast.expr]] | None = iterator_call(iterable)
    if call is not None and known.is_builtin(call[0]):
        return _iterator(*call, known, declared)
    view: str
    receiver: ast.expr
    match iterable:
        case ast.Call(func=ast.Attribute(value=receiver, attr=view), args=[]) if view in DICT_VIEWS:
            return dict_view(receiver, view, known, declared)
        case _:
            found: Inference | None = inference(iterable, known, declared)
            return (
                None
                if found is None
                else element_type(
                    found.annotation,
                    f"the elements of {found.reason}",
                    _kinds(found, kind="loop"),
                )
            )


def _iterator(name: str, args: list[ast.expr], known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer what one of `ITERATORS`, called with `args`, yields.

    Returns:
      Its elements' annotation and reason, or `None` if an argument's elements aren't known.

    """
    if name == RANGE:
        return Inference("int", "`range`, which yields `int`s", frozenset({"loop"}))
    if name in SAME_ELEMENTS:
        return looped(args[0], known, declared)
    parts: list[Inference | None] = [looped(arg, known, declared) for arg in counted(name, args)]
    found: list[Inference] = [part for part in parts if part is not None]
    if len(found) != len(parts):
        return None
    annotations: list[str] = ["int"] * (name == ENUMERATE) + [part.annotation for part in found]
    return Inference(f"tuple[{', '.join(annotations)}]", f"`{name}`'s tuples", _kinds(*found, kind="loop"))


def looped_parts(
    iterable: ast.expr,
    known: Known,
    declared: Mapping[str, str],
) -> list[LoopPart] | None:
    """Infer each part of the tuples `enumerate` or `zip` yields on its own, even if the others aren't known.

    `enumerate`'s index is always an `int`, whatever it counts.

    Returns:
      Each part's inference (`None` if it isn't known), with the values it came from (to judge
      whether it's a guess, see `iterated`); or `None` if `iterable` isn't such a call.

    """
    call: tuple[str, list[ast.expr]] | None = iterator_call(iterable)
    if call is None or call[0] not in {ENUMERATE, ZIP} or not known.is_builtin(call[0]):
        return None
    index: list[LoopPart] = (
        [(Inference("int", "`enumerate`'s index", frozenset({"loop"})), [])] if call[0] == ENUMERATE else []
    )
    return index + [(looped(arg, known, declared), iterated(arg)) for arg in counted(*call)]


def dict_view(receiver: ast.expr, view: str, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer the elements of a `dict`'s `.keys()`, `.values()` or `.items()`.

    Returns:
      Them, or `None` if the receiver isn't a `dict` whose type is known.

    """
    found: Inference | None = inference(receiver, known, declared)
    root: ast.expr | None = None if found is None else ast.parse(found.annotation, mode="eval").body
    key: ast.expr
    value: ast.expr
    match root:
        case ast.Subscript(value=ast.Name(id="dict" | "Dict"), slice=ast.Tuple(elts=[key, value])):
            by_view: dict[str, str] = {
                "keys": ast.unparse(key),
                "values": ast.unparse(value),
                "items": f"tuple[{ast.unparse(key)}, {ast.unparse(value)}]",
            }
            return Inference(by_view[view], f"a `dict`'s `.{view}()`", _kinds(found, kind="loop"))
        case _:
            return None
