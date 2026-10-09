# SPDX-License-Identifier: MIT
"""What `--fix` infers a value's type from: literals, calls, and the locals a scope already typed."""

import ast
import re
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Final, TypeAlias, cast

from constricter.fix.core import asked
from constricter.fix.core.known import PARAM, ImportPlan, Inference, Known, stood
from constricter.fix.libraries import overloads, stdlib, walks
from constricter.fix.libraries.library import (
    installed_call,
    installed_chain,
    installed_method,
    library_call,
    library_class,
    library_operator,
    library_variable,
)
from constricter.fix.libraries.opened import opened, opened_path
from constricter.fix.values import called, decided, displays, operated, shapes
from constricter.fix.values.members import (
    assigned_attribute,
    awaited,
    class_variable,
    keyed,
    member,
    present,
    returned_method,
    subscripted,
)
from constricter.fix.values.returns import BUILTIN_RETURNS
from constricter.fix.values.targets import (
    DICT_VIEWS,
    ENUMERATE,
    ITER,
    MAP,
    RANGE,
    SAME_ELEMENTS,
    ZIP,
    counted,
    dict_parts,
    element_type,
    iterated,
    iterator_call,
    unpacked,
)
from constricter.offences import CONSTRUCTOR, MEMBER
from constricter.rules.annotations import GENERICS, dotted, node_name
from constricter.rules.flow import members

if TYPE_CHECKING:
    from types import EllipsisType

# Comparisons whose result is always a real `bool`, whatever the operands: `in` converts `__contains__`'s
# result, and identity can't be overridden (`==` and `<` can return anything, as numpy's do).
_BOOLEAN_TESTS: Final = (ast.In, ast.NotIn, ast.Is, ast.IsNot)
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
        "TypeAliasType",
        "TypeVar",
        "TypeVarTuple",
        "TypedDict",
    },
)


_NUMBERS: Final = (int, float, complex)
# The builtin classes whose comparisons (`==`, `<`, ...) give a real `bool` (`None`'s, by identity).
_COMPARABLE: Final = frozenset(
    {
        "bool",
        "int",
        "float",
        "complex",
        "str",
        "bytes",
        "bytearray",
        "list",
        "tuple",
        "dict",
        "set",
        "frozenset",
        "range",
        "None",
    },
)
RETURNED: Final = "returned"  # the fix kind of an unannotated function's `return`s
ASSIGNED: Final = "assigned"  # the fix kind of an instance attribute typed by its assignments
_SUBSCRIPT: Final = "subscript"  # the fix kind of a subscript
_GET_ITEM: Final = "__getitem__"  # what types one of a class's instance
_GENERIC: Final = "["  # in a type's text: its arguments
COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_UNION: Final = re.compile(r"\||\b(?:None|Optional|Union)\b")  # an annotation with a union in it
_Comprehension: TypeAlias = ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp
_Pair: TypeAlias = tuple[Inference | None, Inference | None]  # a `dict` display's entry: key, value
# One part of a loop target (see `looped_parts`): its inference, and the values it came from.
LoopPart: TypeAlias = tuple[Inference | None, list[ast.expr]]
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
    held: tuple[Inference | None] | None
    if (held := asked.asked(value, known, declared)) is not None:
        return held[0]
    found: Inference | None = _from_local(value, known, declared) or _from_value(value, known, declared)
    asked.keep(value, known, declared, found)
    return found


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
        case ast.Attribute(value=ast.Name(id=name), attr="param") if f"{name}{PARAM}" in declared:
            return Inference(declared[f"{name}{PARAM}"], "its fixture's `params`", frozenset({"copy"}))
        case (
            ast.Attribute(value=receiver, attr=attr) | ast.Call(func=ast.Attribute(value=receiver, attr=attr))
        ):
            pass
        case ast.Subscript(value=receiver):
            attr = ""
        case _:
            return None
    typed: Inference | None
    if (typed := inference(receiver, known, declared)) is None:
        return installed_chain(stood(value, declared), known, lambda arg: inference(arg, known, declared))
    held: str = present(typed.annotation, attr)
    found: Inference | None = _member_of(
        value,
        held if attr else rebased(held, _GET_ITEM, known),
        attr,
        known,
        declared,
    )
    if found is None:
        return None
    return found if isinstance(receiver, ast.Name) else found._replace(kinds=found.kinds | typed.kinds)


def rebased(receiver: str, name: str, known: Known) -> str:
    """Read a class of the module's as the generic library class it takes `name` from, given its arguments.

    `Rows`, under `collections.deque[Row]`, as that: what its instance's subscript, loop or view gives.

    Returns:
      The base as the class writes it; `receiver` itself for any other.

    """
    base: str | None = known.class_side.lineage.definer(receiver, name)
    return base if base is not None and _GENERIC in base and _GENERIC not in receiver else receiver


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
                keyed(receiver, value.slice, known) or _item(value, receiver, known, declared)
                if text is None
                else Inference(
                    text,
                    f"a subscript of `{ast.unparse(value.value)}`, a `{receiver}`",
                    frozenset({_SUBSCRIPT}),
                )
            )
        case ast.Call():
            found: Inference | None = member(receiver, attr, value, known)
            method: stdlib.Method | None
            # A class of the module's takes a library base's method, matched as the base's own is.
            base: str = known.class_side.lineage.definer(receiver, attr) or receiver
            if found is None and (
                (method := stdlib.overloaded_method(receiver, attr, known)) is not None
                or (method := stdlib.overloaded_method(base, attr, known)) is not None
                or (method := installed_method(receiver, attr, known)) is not None
                or (method := installed_method(base, attr, known)) is not None
            ):
                found = overloads.chosen(
                    method.entry,
                    value,
                    known,
                    lambda arg: inference(arg, known, declared),
                    stdlib.for_receiver(method, receiver),
                )
                # The base itself is its `Self`: the receiver's own class, which the base isn't.
                found = None if found is not None and receiver != base == found.annotation else found
            if found is None:
                found = shapes.defaulted(
                    receiver,
                    value,
                    lambda arg: inference(arg, known, declared),
                    known,
                ) or opened_path(receiver, value, known)
            defined: tuple[str, str] | None = (
                returned_method(receiver, attr, known) if found is None else None
            )
            return (
                found
                if defined is None
                else Inference(defined[1], f"`{defined[0]}.{attr}`'s `return`s", frozenset({RETURNED}))
            )
        case _:
            return member(receiver, attr, None, known) or _unannotated(receiver, attr, known)


def _item(
    value: ast.Subscript,
    receiver: str,
    known: Known,
    declared: Mapping[str, str],
) -> Inference | None:
    """Type a subscript of a standard-library class's instance: what its `__getitem__` gives the index.

    As a call passing it is typed: `proxy["k"]` on a `MappingProxyType[str, int]` is an `int`.

    Returns:
      The inference, or `None`.

    """
    call: ast.Call = ast.copy_location(
        ast.Call(ast.Attribute(value.value, _GET_ITEM, ast.Load()), [value.slice], []),
        value,
    )
    found: Inference | None = stdlib.library_member(receiver, _GET_ITEM, call, known)
    method: stdlib.Method | None
    if found is None and (method := stdlib.overloaded_method(receiver, _GET_ITEM, known)) is not None:
        found = overloads.chosen(
            method.entry,
            call,
            known,
            lambda arg: inference(arg, known, declared),
            method,
        )
    return None if found is None else found._replace(kinds=found.kinds | {_SUBSCRIPT})


def _unannotated(receiver: str, attr: str, known: Known) -> Inference | None:
    """Type an attribute nothing declares: by its class's assignments, or its value in the class's body.

    Returns:
      The inference (a guess), or `None`.

    """
    text: str | None
    if (text := assigned_attribute(receiver, attr, known)) is not None:
        return Inference(text, f"`{receiver}.{attr}`'s assignments", frozenset({ASSIGNED}))
    if (text := class_variable(receiver, attr, known)) is not None:
        return Inference(text, f"`{attr}`'s value in its class's body", frozenset({MEMBER}))
    return None


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
        case ast.Compare():
            return "`in` or `is`, always a `bool`"
        case _:
            return "a literal"


def _from_value(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer from the value itself: a literal, a container of them, or a call.

    Returns:
      The inference, or `None`.

    """
    found: str | None
    if found := scalar(value):
        return Inference(found, _scalar_reason(value), frozenset({"literal"}))
    # Each kind of value is asked only of what types one: most values are names, and calls.
    match value:
        case ast.Call():
            return _computed(value, known, declared) or _from_call(value, known, declared)
        case ast.Name() | ast.Attribute():
            return (
                shapes.module_text(value, known)
                or shapes.class_text(value, known)
                or shapes.class_of(value, known, lambda arg: inference(arg, known, declared))
                or library_variable(value, known)
            )
        case ast.Subscript():
            return shapes.environment(value, known)
        case ast.List() | ast.Set() | ast.Tuple() | ast.Dict():
            return _container(value, known, declared)
        case _:
            return _computed(value, known, declared)


def _from_call(value: ast.Call, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a call by what it calls: a builtin, a library's function or class, or the project's own.

    Returns:
      The inference, or `None`.

    """
    return (
        decided.builtin(
            value,
            known,
            lambda arg: inference(arg, known, declared),
            lambda arg: looped(arg, known, declared),
        )
        or shapes.cast(value, known.names.casts)
        or opened(value, known)
        or library_class(value, known)
        or library_call(value, known, lambda arg: inference(arg, known, declared))
        or installed_call(value, known, lambda arg: inference(arg, known, declared))
        or _returns(value, known)
        or shapes.class_of(value, known, lambda arg: inference(arg, known, declared))
        or _called(value, known)
        or called.result(value, known, declared, lambda arg: inference(arg, known, declared))
        or shapes.partly(value, known, lambda arg: inference(arg, known, declared))
        or shapes.attribute_of(value, known, lambda arg: inference(arg, known, declared))
    )


def _returns(value: ast.expr, known: Known) -> Inference | None:
    """Infer a call to an unannotated function (the module's, or imported) whose `return`s decide its type.

    Returns:
      The inference, or `None`.

    """
    func: ast.expr
    callee: str | None
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (
            callee := dotted(func)
        ) in known.returned.calls and callee not in known.calls:
            return Inference(
                known.returned.calls[callee or ""],
                f"`{callee}`'s `return`s",
                frozenset({RETURNED}),
            )
        case _:
            return None


def _computed(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a value computed from others whose types are known.

    `a if c else b` when both agree, or one is `None`; `a or b` and `a and b` of one type (see
    `constricter.fix.values.shapes`); arithmetic on builtin scalars, and their comparisons (`_operated`);
    a list, set or dict comprehension whose elements' type is known, its targets typed as a loop's;
    `sorted`, `list`, `set`, `frozenset` or `tuple` of something whose elements are known; and
    `await` of a call to one of the module's `async def`s.

    Returns:
      The inference, or `None`.

    """
    name: str
    first: ast.expr
    keywords: list[ast.keyword]
    match value:
        case ast.IfExp() | ast.BoolOp():
            return _joined(value, known, declared)
        case ast.BinOp() | ast.Compare() | ast.UnaryOp(op=ast.USub() | ast.UAdd() | ast.Invert()):
            return _operated(value, known, declared)
        case ast.ListComp() | ast.SetComp() | ast.DictComp():
            return _comprehension(value, known, declared)
        case ast.Call(func=ast.Name(id=name), args=[first], keywords=keywords) if (
            name in CONTAINER_BUILDERS
            and known.is_builtin(name)
            # `sorted`'s keywords only order what it gives.
            and (not keywords or (name in SAME_ELEMENTS and iterator_call(value) is not None))
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
        case _:
            # What awaiting a checked file's or a standard-library coroutine's call gives, or nothing.
            return awaited(value, known, lambda arg: inference(arg, known, declared))


def _operated(
    value: ast.BinOp | ast.Compare | ast.UnaryOp,
    known: Known,
    declared: Mapping[str, str],
) -> Inference | None:
    """Infer an operator's result on builtin values: arithmetic, a comparison, or a number's sign.

    Returns:
      The inference, or `None`.

    """
    if isinstance(value, ast.BinOp):
        return _arithmetic(value, known, declared)
    if isinstance(value, ast.Compare):
        return _compared(value, known, declared)
    return decided.unary(value, lambda operand: inference(operand, known, declared))


def _joined(value: ast.IfExp | ast.BoolOp, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer `a if c else b`, and `a or b`: the one type their parts have (see `shapes`).

    A conditional's both sides', or one side's and `None`.

    Returns:
      The inference, or `None` if the parts' types differ, or one isn't known.

    """
    if isinstance(value, ast.BoolOp):
        return shapes.boolean(value, lambda part: inference(part, known, declared))
    sides: tuple[Inference | None, Inference | None] = (
        inference(value.body, known, declared),
        inference(value.orelse, known, declared),
    )
    if sides[0] and sides[1] and sides[0].annotation == sides[1].annotation:
        return Inference(
            sides[0].annotation,
            "both sides of a conditional",
            _kinds(*sides, kind="conditional"),
        )
    return shapes.optional(value, lambda part: inference(part, known, declared)) or shapes.emptied(
        value,
        lambda part: inference(part, known, declared),
    )


def _arithmetic(value: ast.BinOp, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer arithmetic on builtin values, whose operators nothing can overload (see `operated`).

    And a `pathlib` path's `/` with a `str` or another (`stdlib.joins_path`).

    Returns:
      The inference, or `None` for any other operator or operand.

    """
    sides: tuple[Inference | None, Inference | None] = (
        inference(value.left, known, declared) or _keys(value.left, known, declared),
        inference(value.right, known, declared) or _keys(value.right, known, declared),
    )
    left: str | None = None if sides[0] is None else sides[0].annotation
    right: str | None = None if sides[1] is None else sides[1].annotation
    kinds: frozenset[str] = _kinds(*sides, kind="arithmetic")
    if isinstance(value.op, ast.Div) and left is not None and stdlib.joins_path(left, right, known):
        return Inference(left, "a path joined by `/`", kinds)
    text: str | None = operated.operated(value, left, right, known.limits.max_length)
    builtin: str = "arithmetic on builtin types"
    return library_operator(value.op, sides, known) if text is None else Inference(text, builtin, kinds)


def _keys(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Type a `dict`'s `.keys()` as an operand: its operators give a `set` of its keys, as a `set`'s do.

    Returns:
      The `set[K]`, or `None` if `value` isn't such a call.

    """
    receiver: ast.expr
    match value:
        case ast.Call(func=ast.Attribute(value=receiver, attr="keys"), args=[], keywords=[]):
            found: Inference | None = dict_view(receiver, "keys", known, declared)
            return None if found is None else found._replace(annotation=f"set[{found.annotation}]")
        case _:
            return None


def _compared(value: ast.Compare, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a comparison of builtin values: `n < 3`, `len(xs) == 0`, `name != "x"`.

    Each builtin's own comparison gives a real `bool`, or declines for the other side's to (and one
    both decline is `is`/`is not`, a `bool` too); a class's may give anything (numpy's arrays).

    Returns:
      `bool`, if every operand's type (each member of a union's) is a builtin class; else `None`.

    """
    parts: list[Inference | None] = [
        inference(part, known, declared) for part in (value.left, *value.comparators)
    ]
    builtin: bool = all(
        part is not None
        and all(
            _root(member) in _COMPARABLE and known.is_builtin(_root(member))
            for member in members(part.annotation) or ()
        )
        for part in parts
    )
    return (
        Inference("bool", "a comparison of builtin values", _kinds(*parts, kind="compare"))
        if builtin
        else None
    )


def _root(annotation: str) -> str:
    """Name an annotation's outer type (`list` for `list[int]`).

    Returns:
      Its text before any `[`.

    """
    return annotation.partition("[")[0]


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
            key = key and shapes.sifted(value, value.key, key)
            item: Inference | None = inference(value.value, known, inside)
            item = item and shapes.sifted(value, value.value, item)
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
            element = element and shapes.sifted(value, value.elt, element)
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
            annotation: str | None = None if found is None else found.annotation
            for name, part in unpacked(generator.target, annotation, known.indirect.tuples):
                if part is None:
                    _ = inside.pop(name.id, None)
                else:
                    inside[name.id] = part
    return inside


def scalar(value: ast.expr) -> str | None:
    """Type a value that is what it is whatever its parts are: a literal, an f-string, `not x`, `x is y`.

    Returns:
      Its type, or `None` for any other value.

    """
    constant: str | bytes | bool | int | float | complex | EllipsisType | None
    ops: list[ast.cmpop]
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
        case ast.Compare(ops=ops) if all(isinstance(op, _BOOLEAN_TESTS) for op in ops):
            return "bool"
        case ast.JoinedStr():
            return "str"
        case _:
            return None


def _container(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a list, set, tuple or dict display whose elements' types agree.

    A starred element (`[*names, s]`) gives each of what it unpacks, and `**d` a `dict`'s keys and
    values; a tuple that unpacks one, whose length then isn't known, is a `tuple[T, ...]`.

    Returns:
      The inference, or `None`.

    """
    elements: list[ast.expr]
    keys: list[ast.expr | None]
    values: list[ast.expr]
    found: str | None = None
    parts: list[Inference | None] = []
    mixed: bool = False  # whether the elements' types differ, and are joined
    match value:
        case ast.List(elts=elements) | ast.Set(elts=elements) if elements:
            parts = [_element(element, known, declared) for element in elements]
            element: str | None
            element, mixed = displays.element_type(elements, parts)
            found = f"{'list' if isinstance(value, ast.List) else 'set'}[{element}]" if element else None
        case ast.Tuple(elts=elements) if elements:
            parts = [_element(element, known, declared) for element in elements]
            starred: bool = any(isinstance(element, ast.Starred) for element in elements)
            found = displays.tuple_type(parts, -1 if starred else known.limits.max_length)
        case ast.Dict(keys=keys, values=values) if keys:
            pairs: list[_Pair] = [
                _pair(key, item, known, declared) for key, item in zip(keys, values, strict=True)
            ]
            parts = [part for pair in pairs for part in pair]
            sides: list[tuple[str | None, bool]] = [
                displays.element_type(keys, [pair[0] for pair in pairs]),
                displays.element_type(values, [pair[1] for pair in pairs]),
            ]
            found = f"dict[{sides[0][0]}, {sides[1][0]}]" if sides[0][0] and sides[1][0] else None
            mixed = sides[0][1] or sides[1][1]
        case _:
            pass
    if found is None:
        return None
    kinds: frozenset[str] = _kinds(*parts, kind="container")
    built: str = found.partition("[")[0]
    if mixed:
        return Inference(found, f"a {built} of its elements' types, joined", kinds | {displays.JOINED})
    return Inference(found, f"a {built} whose elements' types agree", kinds)


def _element(element: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Type one element of a display: itself, or each of those a starred one unpacks.

    Returns:
      The inference, or `None`.

    """
    if isinstance(element, ast.Starred):
        return looped(element.value, known, declared)
    return inference(element, known, declared)


def _pair(key: ast.expr | None, item: ast.expr, known: Known, declared: Mapping[str, str]) -> _Pair:
    """Type one entry of a `dict` display: its key and value, or (`**item`) those of a `dict` it unpacks.

    Returns:
      The key's inference and the value's, each `None` if it isn't known.

    """
    if key is not None:
        return inference(key, known, declared), inference(item, known, declared)
    found: Inference | None = inference(item, known, declared)
    types: tuple[str, str] | None = None if found is None else dict_parts(found.annotation)
    if found is None or types is None:
        return None, None
    return found._replace(annotation=types[0]), found._replace(annotation=types[1])


def joined(value: ast.AST, known: Known, declared: Mapping[str, str]) -> bool:
    """Check whether `value` is a display typed by its elements' joined types: a guess.

    A checker joins them too, but not always to the same union (mypy to their common base).

    Returns:
      Whether it is.

    """
    if not isinstance(value, ast.List | ast.Set | ast.Dict):
        return False
    found: Inference | None = _container(value, known, declared)
    return found is not None and displays.JOINED in found.kinds


def _called(value: ast.expr, known: Known) -> Inference | None:
    func: ast.expr
    name: str
    callee: str | None
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (callee := dotted(func)) in known.calls:
            return Inference(
                known.calls[callee or ""],
                f"`{callee}`'s declared return type",
                frozenset({"call"}),
            )
        case ast.Call(func=ast.Name(id=name)) if name in BUILTIN_RETURNS and known.is_builtin(name):
            return Inference(BUILTIN_RETURNS[name], f"`{name}`'s fixed return type", frozenset({"builtin"}))
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (
            (constructs(node_name(func), known.factories) or dotted(func) in known.classes)
            and _type_expression(func, known)
            and stdlib.resolved(func, known.names.stdlib) not in stdlib.FUNCTIONS
        ):
            return Inference(
                ast.unparse(func),
                f"a call to `{ast.unparse(func)}`, taken to construct one",
                frozenset({CONSTRUCTOR}),
            )
        case _:
            return None


def _type_expression(func: ast.Name | ast.Attribute, known: Known) -> bool:
    """Check that a callee can be written as a type: a (dotted) name starting with a class or module.

    Not a call's attribute (`_tables().Filters`), nor through a name the module binds as a value
    somewhere (`Klass = ...`, `jinja2 = import_optional_dependency("jinja2")`, `self`): a type
    checker rejects a variable in a type.

    Returns:
      Whether it can.

    """
    path: str | None = dotted(func)
    plan: ImportPlan | None = known.names.plan
    return path is not None and (plan is None or path.partition(".")[0] not in plan.values)


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
    `x`'s and `y`'s; `reversed(x)`, `sorted(x)` and `iter(x)` what `x` does; `map(f, x)` what `f`
    returns; a generator expression its element; a `dict`'s `.keys()`, `.values()` and `.items()`
    its keys, values and pairs; and anything else
    whose type is inferred, its elements: a `list`, `set`, `frozenset` or `tuple[T, ...]`'s `T`, a
    tuple's parts where they agree, a `dict`'s keys, a `str`'s `str`s and a `bytes`'s `int`s, and a
    standard-library class's by its `__iter__` (a file's lines). `os.walk(top)` gives a directory's
    path, with its directories' names and its files', as `top` is typed (see `walks.walked`).

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
        case ast.GeneratorExp():
            return _generated(iterable, known, declared)
        case _:
            found: Inference | None
            if (found := inference(iterable, known, declared)) is None:
                return walks.walked(iterable, known, lambda top: inference(top, known, declared))
            kinds: frozenset[str] = _kinds(found, kind="loop")
            # Of an `X | None`, the `X`'s: `None` has none. A builtin container's or an
            # `Iterable[T]`'s, else a standard-library class's own.
            held: str = rebased(present(found.annotation, ""), "__iter__", known)
            element: Inference | None = overloads.library_element(held, known)
            return element_type(held, f"the elements of {found.reason}", kinds) or (
                None if element is None else element._replace(kinds=kinds | element.kinds)
            )


def _iterator(name: str, args: list[ast.expr], known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer what one of `ITERATORS`, called with `args`, yields.

    Returns:
      Its elements' annotation and reason, or `None` if an argument's elements aren't known.

    """
    if name == RANGE:
        return Inference("int", "`range`, which yields `int`s", frozenset({"loop"}))
    if name == MAP:
        return _mapped(args[0], known)
    if name in SAME_ELEMENTS or name == ITER:
        return looped(args[0], known, declared) if name != ITER or len(args) == 1 else None
    parts: list[Inference | None] = [looped(arg, known, declared) for arg in counted(name, args)]
    found: list[Inference] = [part for part in parts if part is not None]
    if len(found) != len(parts):
        return None
    annotations: list[str] = ["int"] * (name == ENUMERATE) + [part.annotation for part in found]
    return Inference(f"tuple[{', '.join(annotations)}]", f"`{name}`'s tuples", _kinds(*found, kind="loop"))


def _generated(value: ast.GeneratorExp, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer what a generator expression yields: its element, its targets typed as a loop's are.

    Not one with a condition whose element's type has a union in it, which the condition may narrow.

    Returns:
      The inference, or `None`.

    """
    found: Inference | None = inference(value.elt, known, comprehended(value, known, declared))
    found = found and shapes.sifted(value, value.elt, found)
    filtered: bool = any(generator.ifs for generator in value.generators)
    if found is None or (filtered and _UNION.search(found.annotation)):
        return None
    loops: list[Inference | None] = [looped(g.iter, known, declared) for g in value.generators]
    return Inference(
        found.annotation,
        "a generator expression's elements",
        _kinds(found, *loops, kind="comprehension"),
    )


def _mapped(function: ast.expr, known: Known) -> Inference | None:
    """Infer what `map(function, ...)` yields: what `function` returns, whatever it's given.

    Returns:
      A fixed-return builtin's type (`map(int, parts)`), or a function's declared return; `None`
      for any other callable.

    """
    found: Inference | None = _called(ast.copy_location(ast.Call(function, [], []), function), known)
    if found is None or CONSTRUCTOR in found.kinds:
        return None
    return Inference(found.annotation, f"`map`, which yields {found.reason}", _kinds(found, kind="loop"))


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
    types: tuple[str, str] | None
    if (types := None if found is None else dict_parts(rebased(found.annotation, view, known))) is None:
        return None
    by_view: dict[str, str] = {
        "keys": types[0],
        "values": types[1],
        "items": f"tuple[{types[0]}, {types[1]}]",
    }
    return Inference(by_view[view], f"a `dict`'s `.{view}()`", _kinds(found, kind="loop"))
