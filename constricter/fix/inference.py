# SPDX-License-Identifier: MIT
"""What `--fix` infers a value's type from: literals, calls, and the locals a scope already typed."""

import ast
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Final

from constricter.fix import stdlib
from constricter.fix.known import Inference, Known
from constricter.fix.returns import BUILTIN_RETURNS, METHOD_RETURNS, method_return
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
_RETURNED: Final = "returned"  # the fix kind of an unannotated function's `return`s
_STR: Final = "str"
_WITH_DEFAULT: Final = 2  # `os.environ.get(key, default)`'s arguments
# Builtins that build a container of their argument's elements, and the type they build.
_CONTAINER_BUILDERS: Final = {
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
    """Infer from another local this scope already typed: a copy, a subscript, an attribute, a method.

    Returns:
      The inference, or `None`.

    """
    name: str
    attr: str
    found: str | None
    match value:
        case ast.Name(id=name) if name in declared:
            return Inference(declared[name], f"a copy of `{name}`", frozenset({"copy"}))
        case ast.Subscript(value=ast.Name(id=name)) if name in declared and (
            found := _subscripted(declared[name], value)
        ):
            return Inference(
                found,
                f"a subscript of `{name}`, a `{declared[name]}`",
                frozenset({"subscript"}),
            )
        case ast.Attribute(value=ast.Name(id=name), attr=attr) if name in declared and (
            found := _attribute(declared[name], attr, known)
        ):
            return Inference(found, f"the annotation of `{declared[name]}.{attr}`", frozenset({"attribute"}))
        case ast.Call(func=ast.Attribute(value=ast.Name(id=name), attr=attr)) if (
            name in declared
            and (found := known.returned.methods.get(declared[name], {}).get(attr))
            and not _method(declared[name], value, attr, known)
        ):
            return Inference(found, f"`{declared[name]}.{attr}`'s `return`s", frozenset({_RETURNED}))
        case ast.Call(func=ast.Attribute(value=ast.Name(id=name), attr=attr)) if name in declared and (
            found := _method(declared[name], value, attr, known)
        ):
            return Inference(
                found,
                _method_reason(declared[name], attr, known.methods),
                frozenset({"method"}),
            )
        case _:
            return None


def _class_of(receiver: str) -> str | None:
    """Read the class a `type[C]` names (what `cls` is in a classmethod of `C`).

    Returns:
      `C`, or `None` if `receiver` isn't a `type[...]` of a plain name.

    """
    # `receiver` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(receiver, mode="eval").body
    name: str
    match root:
        case ast.Subscript(value=ast.Name(id="type"), slice=ast.Name(id=name)):
            return name
        case _:
            return None


def _attribute(receiver: str, attr: str, known: Known) -> str | None:
    """Look up `attr` on a value typed `receiver`: an instance's attribute or property, or a class's own.

    Returns:
      Its annotation as text, or `None` if it isn't known.

    """
    owner: str | None
    if (owner := _class_of(receiver)) is not None:
        return known.class_side.attributes.get(owner, {}).get(attr)
    return known.classes.get(receiver, {}).get(attr)


def _method(receiver: str, call: ast.Call, method: str, known: Known) -> str | None:
    """Look up a `method` call's type on a value typed `receiver` (a `type[C]`: its class-side methods).

    Returns:
      Its annotation as text, or `None` if it isn't known (see `method_return`).

    """
    owner: str | None
    if (owner := _class_of(receiver)) is not None:
        return known.class_side.methods.get(owner, {}).get(method)
    return method_return(receiver, call, method, known.methods)


def _method_reason(receiver: str, method: str, known_methods: Mapping[str, Mapping[str, str]]) -> str:
    """Say which of `method_return`'s sources typed a `method` call on a `receiver`.

    Returns:
      The reason.

    """
    if method in METHOD_RETURNS.get(receiver, {}):
        return f"`{receiver}.{method}`'s fixed return type"
    if method in known_methods.get(receiver, {}):
        return f"`{receiver}.{method}`'s declared return type"
    return f"`{receiver}.{method}` on its element types"


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
        or _library(value, known, declared)
        or _returns(value, known)
        or _called(value, known.calls, known.factories)
    )


def _returns(value: ast.expr, known: Known) -> Inference | None:
    """Infer a call to one of the module's unannotated functions whose `return`s decide its type.

    Returns:
      The inference, or `None`.

    """
    name: str
    match value:
        case ast.Call(func=ast.Name(id=name)) if name in known.returned.calls and name not in known.calls:
            return Inference(known.returned.calls[name], f"`{name}`'s `return`s", frozenset({_RETURNED}))
        case _:
            return None


def _library(value: ast.expr, known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer a call to a standard-library function the tables type (see `constricter.fix.stdlib`).

    A fixed builtin result; an `AnyStr` function's, when every argument is a `str` (or every one a
    `bytes`); an environment lookup's `str | None` (`str` with a `str` default).

    Returns:
      The inference, or `None` for any other call, or arguments that don't decide it.

    """
    func: ast.expr
    args: list[ast.expr]
    match value:
        case ast.Call(func=func, args=args, keywords=[]):
            pass
        case _:
            return None
    name: str | None = stdlib.resolved(func, known.names.stdlib)
    reason: str = f"`{name}`'s return type"
    kinds: frozenset[str] = frozenset({_STDLIB})
    if name in stdlib.RETURNS:
        return Inference(stdlib.RETURNS[name], reason, kinds)
    parts: list[Inference | None] = [inference(arg, known, declared) for arg in args]
    types: set[str | None] = {None if part is None else part.annotation for part in parts}
    if name in stdlib.ANY_STR and len(types) == 1 and types <= _TEXT_NAMES:
        return Inference(str(next(iter(types))), reason, _kinds(*parts, kind=_STDLIB))
    if name in stdlib.ENVIRONMENT and len(args) == 1:
        return Inference("str | None", reason, kinds)
    if name in stdlib.ENVIRONMENT and len(args) == _WITH_DEFAULT and parts[1] and parts[1].annotation == _STR:
        return Inference(_STR, reason, _kinds(parts[1], kind=_STDLIB))
    return None


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
        case ast.Call(func=ast.Name(id=name), args=[first], keywords=[]) if name in _CONTAINER_BUILDERS:
            found: Inference | None = looped(first, known, declared)
            built: str = _CONTAINER_BUILDERS[name]
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
    inside: dict[str, str] = comprehended(value, known, declared)
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


def comprehended(value: ast.expr, known: Known, declared: Mapping[str, str]) -> dict[str, str]:
    """Type the targets of every comprehension in `value`, as a loop's are, over what's `declared`.

    A target whose type isn't known is dropped (it shadows any outer name of the same name).

    Returns:
      `declared`, with the targets' types.

    """
    inside: dict[str, str] = dict(declared)
    node: ast.AST
    generator: ast.comprehension
    for node in ast.walk(value):
        if isinstance(node, ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp):
            for generator in node.generators:
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


def _subscripted(container: str, node: ast.Subscript) -> str | None:
    """Infer `container[...]`'s type, given `container`'s own type as text.

    A slice (`x[1:2]`) of a `list`, `str` or `bytes` is the same type as `container` itself; a plain
    index into one is its element type, as is any index into a `dict` (its value type) or a
    homogeneous `tuple[T, ...]`. A fixed-length `tuple[T1, T2]`'s element only varies with the index,
    which isn't worth resolving.

    Returns:
      The annotation as source text, or `None` if the subscript doesn't decide one.

    """
    # `container` is always `ast.unparse`'s own output (an annotation, or an earlier `inferred`),
    # never user text, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(container, mode="eval").body
    sliced: bool = isinstance(node.slice, ast.Slice)
    element: ast.expr
    last: ast.expr
    match root:
        case ast.Name(id="str" | "bytes"):
            return container
        case ast.Subscript(value=ast.Name(id="list" | "List"), slice=element):
            return container if sliced else ast.unparse(element)
        case ast.Subscript(
            value=ast.Name(id="dict" | "Dict"),
            slice=ast.Tuple(elts=[_, element]),
        ) if not sliced:
            return ast.unparse(element)
        case ast.Subscript(
            value=ast.Name(id="tuple" | "Tuple"),
            slice=ast.Tuple(elts=[element, last]),
        ) if not sliced and isinstance(last, ast.Constant) and last.value is Ellipsis:
            return ast.unparse(element)
        case _:
            return None


def _called(value: ast.expr, calls: Mapping[str, str], known_factories: frozenset[str]) -> Inference | None:
    func: ast.expr
    name: str
    match value:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if ast.unparse(func) in calls:
            return Inference(
                calls[ast.unparse(func)],
                f"`{ast.unparse(func)}`'s declared return type",
                frozenset({"call"}),
            )
        case ast.Call(func=ast.Name(id=name)) if name in BUILTIN_RETURNS:
            return Inference(BUILTIN_RETURNS[name], f"`{name}`'s fixed return type", frozenset({"builtin"}))
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if _constructs(
            node_name(func),
            known_factories,
        ):
            return Inference(
                ast.unparse(func),
                f"a call to `{ast.unparse(func)}`, taken to construct one",
                frozenset({CONSTRUCTOR}),
            )
        case _:
            return None


def guessed(
    value: ast.expr,
    known: Known,
    guesses: frozenset[str],
    declared: Mapping[str, str],
) -> bool:
    """Whether `inferred`'s annotation for `value` is a guess (`--unsafe-fixes`): it calls a class.

    A capitalised call may construct a generic class (`Box(1)` is really `Box[int]`) or be a factory
    function; literals, calls to a module function, a fixed-return builtin (`len`, `isinstance`,
    ...) or a method `method_return` resolves on an already-typed local, and
    another local this scope already typed, are certain. Copying a local `inferred` itself only
    guessed (`guesses`) is no more certain than the guess it copies.

    Returns:
      Whether any call in `value` is to something other than such a certain callee, or any name in
      it copies such a guess.

    """
    inside: dict[str, str] = comprehended(value, known, declared)
    return any(_is_guess(node, known, guesses, inside) for node in ast.walk(value))


def guess_origins(value: ast.expr, known: Known, declared: Mapping[str, str]) -> frozenset[str]:
    """Name what makes `value`'s calls guesses, for `unsafe-fix-select` to trust or not.

    Returns:
      `returned` for a method typed only by its `return`s, `constructor` for any other guessed call.

    """
    inside: dict[str, str] = comprehended(value, known, declared)
    found: set[str] = set()
    node: ast.AST
    for node in ast.walk(value):
        if isinstance(node, ast.Call) and _is_guess(node, known, frozenset(), inside):
            found.update(_guessed_by(node, known, inside))
    return frozenset(found)


def _guessed_by(call: ast.Call, known: Known, declared: Mapping[str, str]) -> frozenset[str]:
    """Name what makes one guessed call a guess.

    Returns:
      A method typed by its `return`s: `returned`, and what those rest on; a function whose
      `return`s are guesses: what they rest on; anything else: `constructor`.

    """
    name: str
    receiver: str
    method: str
    match call:
        case ast.Call(func=ast.Name(id=name)) if name in known.returned.guesses:
            return known.returned.guesses[name]
        case ast.Call(func=ast.Attribute(value=ast.Name(id=receiver), attr=method)) if _returned_method(
            call,
            known,
            declared,
        ):
            return frozenset({_RETURNED}) | known.returned.guesses.get(
                f"{declared[receiver]}.{method}",
                frozenset(),
            )
        case _:
            return frozenset({CONSTRUCTOR})


def _returned_method(call: ast.Call, known: Known, declared: Mapping[str, str]) -> bool:
    """Check whether `call` is a method typed only by its `return`s (see `Returned`).

    Returns:
      Whether it is.

    """
    receiver: str
    method: str
    match call:
        case ast.Call(func=ast.Attribute(value=ast.Name(id=receiver), attr=method)) if receiver in declared:
            return method in known.returned.methods.get(declared[receiver], {})
        case _:
            return False


def _is_guess(
    node: ast.AST,
    known: Known,
    guesses: frozenset[str],
    declared: Mapping[str, str],
) -> bool:
    name: str
    func: ast.expr
    receiver: str
    method: str
    call: ast.Call
    owner: ast.Name
    match node:
        case ast.Call(func=ast.Name(id=name)) if (
            name in BUILTIN_RETURNS
            or name in _CONTAINER_BUILDERS
            or name in _LOOP_BUILTINS
            or name in known.awaits
            or (name in known.returned.calls and name not in known.returned.guesses)
        ):
            return False
        case ast.Call(func=func) if ast.unparse(func) in known.names.casts or (
            stdlib.resolved(func, known.names.stdlib) in stdlib.KNOWN
        ):
            return False
        case ast.Call(func=ast.Attribute(value=ast.Name(id=receiver) as owner, attr=method)) as call if (
            receiver in declared
            and (
                _method(declared[receiver], call, method, known) is not None
                or (method in _DICT_VIEWS and _view(owner, method, known, declared) is not None)
            )
        ):
            return False
        case ast.Call(func=func):
            return ast.unparse(func) not in known.calls
        case ast.Name(id=name):
            return name in guesses
        case _:
            return False


def _constructs(name: str, known_factories: frozenset[str]) -> bool:
    """Check whether a call to `name` constructs a class, by its capitalised name.

    Returns:
      Whether it does, and is worth annotating: `name` isn't a known factory, by import
      (`known_factories`) or by its bare name (`_FACTORIES`, for one imported some other way).

    """
    return (
        name[:1].isupper() and name not in known_factories and name not in _FACTORIES and name not in GENERICS
    )


# Builtins that iterate over their (first) argument's elements, one to one.
_SAME_ELEMENTS: Final = frozenset({"reversed", "sorted"})
_DICT_VIEWS: Final = frozenset({"keys", "values", "items"})
# Containers whose one type parameter is their elements'.
_ONE_ELEMENT_TYPE: Final = frozenset({"list", "List", "set", "Set", "frozenset", "FrozenSet"})
_RANGE: Final = "range"
_ENUMERATE: Final = "enumerate"
_ITERATORS: Final = frozenset({_RANGE, _ENUMERATE, "zip", *_SAME_ELEMENTS})
_LOOP_BUILTINS: Final = _ITERATORS
# `tuple[T, ...]`'s two parts: the element type and the ellipsis.
_ANY_LENGTH: Final = 2


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
    name: str
    args: list[ast.expr]
    view: str
    receiver: ast.expr
    match iterable:
        case ast.Call(func=ast.Name(id=name), args=args, keywords=[]) if name in _ITERATORS and args:
            return _iterator(name, args, known, declared)
        case ast.Call(func=ast.Attribute(value=receiver, attr=view), args=[]) if view in _DICT_VIEWS:
            return _view(receiver, view, known, declared)
        case _:
            found: Inference | None = inference(iterable, known, declared)
            return (
                None
                if found is None
                else _elements(
                    found.annotation,
                    f"the elements of {found.reason}",
                    _kinds(found, kind="loop"),
                )
            )


def _iterator(name: str, args: list[ast.expr], known: Known, declared: Mapping[str, str]) -> Inference | None:
    """Infer what one of `_ITERATORS`, called with `args`, yields.

    Returns:
      Its elements' annotation and reason, or `None` if an argument's elements aren't known.

    """
    if name == _RANGE:
        return Inference("int", "`range`, which yields `int`s", frozenset({"loop"}))
    if name in _SAME_ELEMENTS:
        return looped(args[0], known, declared)
    counted: list[ast.expr] = args[:1] if name == _ENUMERATE else args
    parts: list[Inference | None] = [looped(arg, known, declared) for arg in counted]
    found: list[Inference] = [part for part in parts if part is not None]
    if len(found) != len(parts):
        return None
    annotations: list[str] = ["int"] * (name == _ENUMERATE) + [part.annotation for part in found]
    return Inference(f"tuple[{', '.join(annotations)}]", f"`{name}`'s tuples", _kinds(*found, kind="loop"))


def _view(receiver: ast.expr, view: str, known: Known, declared: Mapping[str, str]) -> Inference | None:
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


def _elements(container: str, reason: str, kinds: frozenset[str]) -> Inference | None:
    """Infer the elements of a value typed `container`.

    Returns:
      Them, or `None` for a type whose elements aren't known from it alone.

    """
    # `container` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(container, mode="eval").body
    name: str
    item: ast.expr
    key: ast.expr
    last: ast.expr
    match root:
        case ast.Name(id="str"):
            return Inference("str", reason, kinds)
        case ast.Name(id="bytes"):
            return Inference("int", reason, kinds)
        case ast.Subscript(value=ast.Name(id=name), slice=item) if name in _ONE_ELEMENT_TYPE:
            return Inference(ast.unparse(item), reason, kinds)
        case ast.Subscript(value=ast.Name(id="dict" | "Dict"), slice=ast.Tuple(elts=[key, _])):
            return Inference(ast.unparse(key), reason, kinds)
        case ast.Subscript(value=ast.Name(id="tuple" | "Tuple"), slice=ast.Tuple(elts=[item, last])) if (
            isinstance(last, ast.Constant) and last.value is Ellipsis
        ):
            return Inference(ast.unparse(item), reason, kinds)
        case _:
            return None


def _is_ellipsis(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is Ellipsis


def unpacked(target: ast.expr, annotation: str | None) -> list[tuple[ast.Name, str | None]]:
    """Match an unpacking target's names with the parts of a value typed `annotation`.

    A plain name takes the whole type; a tuple or list of targets takes a `tuple[A, B, ...]` of the
    same length part by part, or a `tuple[T, ...]`'s `T` for each. A starred name, or a shape that
    doesn't match, gets `None`.

    Returns:
      Each name the target binds, with its type as text (or `None`).

    """
    elements: list[ast.expr]
    value: ast.expr
    match target:
        case ast.Name():
            return [(target, annotation)]
        case ast.Tuple(elts=elements) | ast.List(elts=elements):
            parts: list[str | None] = _parts(annotation, len(elements))
            return [
                pair
                for element, part in zip(elements, parts, strict=True)
                for pair in unpacked(element, part)
            ]
        case ast.Starred(value=value):
            return unpacked(value, None)
        case _:
            return []


def _parts(annotation: str | None, count: int) -> list[str | None]:
    """Split a tuple type into `count` parts, one per target.

    Returns:
      Each part's type as text; all `None` if `annotation` isn't a tuple of that many (or of any
      length, `tuple[T, ...]`).

    """
    unknown: list[str | None] = [None] * count
    if annotation is None:
        return unknown
    root: ast.expr = ast.parse(annotation, mode="eval").body
    elements: list[ast.expr]
    match root:
        case ast.Subscript(value=ast.Name(id="tuple" | "Tuple"), slice=ast.Tuple(elts=elements)):
            if len(elements) == _ANY_LENGTH and _is_ellipsis(elements[-1]):
                return [ast.unparse(elements[0])] * count
            return [ast.unparse(e) for e in elements] if len(elements) == count else unknown
        case _:
            return unknown


def iterated(iterable: ast.expr) -> list[ast.expr]:
    """Find the values `looped` typed a loop over `iterable` from, to judge whether it guessed.

    Through `enumerate` (its first argument), `zip`, `reversed`, `sorted` and a `dict` view to what
    they iterate; a `range()` iterates nothing typed.

    Returns:
      Those values.

    """
    name: str
    args: list[ast.expr]
    receiver: ast.expr
    view: str
    match iterable:
        case ast.Call(func=ast.Name(id=name), args=args, keywords=[]) if name in _ITERATORS and args:
            if name == _RANGE:
                return []
            return [part for arg in (args[:1] if name == _ENUMERATE else args) for part in iterated(arg)]
        case ast.Call(func=ast.Attribute(value=receiver, attr=view), args=[]) if view in _DICT_VIEWS:
            return [receiver]
        case _:
            return [iterable]
