# SPDX-License-Identifier: MIT
"""What `--fix` infers a value's type from: literals, calls, and the locals a scope already typed."""

import ast
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, NamedTuple

from constricter.rules.annotations import GENERICS, node_name

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


# Builtins whose return type is fixed by the language, whatever their argument: safe to infer, not
# a guess (unlike a capitalised call, which could really be a generic class or a factory function).
_BUILTIN_RETURNS: Final = {
    "bool": "bool",
    "bytes": "bytes",
    "callable": "bool",
    "chr": "str",
    "complex": "complex",
    "float": "float",
    "hasattr": "bool",
    "hash": "int",
    "id": "int",
    "int": "int",
    "isinstance": "bool",
    "issubclass": "bool",
    "len": "int",
    "ord": "int",
    "repr": "str",
    "str": "str",
}


# `str`/`bytes` methods whose return type is fixed by the language, whatever their arguments: safe
# to infer for a call on an already-typed local, not a guess.
_STR_METHODS: Final = {
    "capitalize": "str",
    "casefold": "str",
    "center": "str",
    "count": "int",
    "encode": "bytes",
    "endswith": "bool",
    "expandtabs": "str",
    "find": "int",
    "format": "str",
    "format_map": "str",
    "index": "int",
    "isalnum": "bool",
    "isalpha": "bool",
    "isascii": "bool",
    "isdecimal": "bool",
    "isdigit": "bool",
    "isidentifier": "bool",
    "islower": "bool",
    "isnumeric": "bool",
    "isprintable": "bool",
    "isspace": "bool",
    "istitle": "bool",
    "isupper": "bool",
    "join": "str",
    "ljust": "str",
    "lower": "str",
    "lstrip": "str",
    "removeprefix": "str",
    "removesuffix": "str",
    "replace": "str",
    "rfind": "int",
    "rindex": "int",
    "rjust": "str",
    "rsplit": "list[str]",
    "rstrip": "str",
    "split": "list[str]",
    "splitlines": "list[str]",
    "startswith": "bool",
    "strip": "str",
    "swapcase": "str",
    "title": "str",
    "translate": "str",
    "upper": "str",
    "zfill": "str",
}


_BYTES_METHODS: Final = {
    "capitalize": "bytes",
    "center": "bytes",
    "count": "int",
    "decode": "str",
    "endswith": "bool",
    "expandtabs": "bytes",
    "find": "int",
    "hex": "str",
    "index": "int",
    "isalnum": "bool",
    "isalpha": "bool",
    "isascii": "bool",
    "isdigit": "bool",
    "islower": "bool",
    "isspace": "bool",
    "istitle": "bool",
    "isupper": "bool",
    "join": "bytes",
    "ljust": "bytes",
    "lower": "bytes",
    "lstrip": "bytes",
    "removeprefix": "bytes",
    "removesuffix": "bytes",
    "replace": "bytes",
    "rfind": "int",
    "rindex": "int",
    "rjust": "bytes",
    "rsplit": "list[bytes]",
    "rstrip": "bytes",
    "split": "list[bytes]",
    "splitlines": "list[bytes]",
    "startswith": "bool",
    "strip": "bytes",
    "swapcase": "bytes",
    "title": "bytes",
    "translate": "bytes",
    "upper": "bytes",
    "zfill": "bytes",
}


_METHOD_RETURNS: Final = {"str": _STR_METHODS, "bytes": _BYTES_METHODS}


@dataclass(frozen=True)
class Known:
    """What a module declares that `--fix` can infer a value's type from.

    `calls`: its functions' return types (`returns`, plus other modules', see `project.calls`).
    `factories`: names that build a class or special form rather than an instance of it (see
    `factories`), so a call to one is never guessed to construct one. `classes` and `methods`: each
    class's annotated attributes (see `classes`) and methods' return types (see `method_returns`).
    """

    calls: Mapping[str, str]
    factories: frozenset[str]
    classes: Mapping[str, Mapping[str, str]]
    methods: Mapping[str, Mapping[str, str]]


def _method_return(
    receiver: str,
    call: ast.Call,
    method: str,
    known_methods: Mapping[str, Mapping[str, str]],
) -> str | None:
    """Look up the type of `call`, a `method` call on a receiver whose own type is `receiver`, as text.

    A fixed-return `str`/`bytes` method (`_METHOD_RETURNS`), a method of a class defined in the
    module (`known_methods`, see `method_returns`), or a `list`/`set`/`dict` method whose return is the
    receiver's own element type (`_element_method`).

    Returns:
      The annotation as source text, or `None` if none of those decides one.

    """
    return (
        _METHOD_RETURNS.get(receiver, {}).get(method)
        or known_methods.get(receiver, {}).get(method)
        or _element_method(receiver, call, method)
    )


def _element_method(receiver: str, call: ast.Call, method: str) -> str | None:
    """Infer a `list`, `set` or `dict` method call's type from the receiver's own type parameters.

    `copy()` is the receiver's type; `pop()` a `list`'s or `set`'s element (with an optional index
    for a `list`); `pop(key)`, `setdefault(key, value)` and `get(key)` a `dict`'s value (`get` as
    `V | None`); `popitem()` its `tuple[K, V]`. A call with any other arguments (`pop(key, default)`,
    a keyword) can return something else, so it decides nothing.

    Returns:
      The annotation as source text, or `None` if the call doesn't decide one.

    """
    # `receiver` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(receiver, mode="eval").body
    call_shape: tuple[str, int | None] = (method, None if call.keywords else len(call.args))
    element: ast.expr
    key: ast.expr
    match root:
        case ast.Subscript(value=ast.Name(id="list" | "List" | "set" | "Set" | "dict" | "Dict")) if (
            call_shape == ("copy", 0)
        ):
            return receiver
        case ast.Subscript(value=ast.Name(id="list" | "List"), slice=element) if call_shape in {
            ("pop", 0),
            ("pop", 1),
        }:
            return ast.unparse(element)
        case ast.Subscript(value=ast.Name(id="set" | "Set"), slice=element) if call_shape == ("pop", 0):
            return ast.unparse(element)
        case ast.Subscript(value=ast.Name(id="dict" | "Dict"), slice=ast.Tuple(elts=[key, element])):
            return _dict_method(call_shape, key, element)
        case _:
            return None


def _dict_method(call_shape: tuple[str, int | None], key: ast.expr, value: ast.expr) -> str | None:
    """Infer a `dict[key, value]` method call's type, by its name and positional argument count.

    Returns:
      The annotation as source text, or `None` if the call doesn't decide one.

    """
    match call_shape:
        case ("pop", 1) | ("setdefault", 2):
            return ast.unparse(value)
        case ("get", 1) if not any(
            isinstance(node, ast.Constant) and isinstance(node.value, str) for node in ast.walk(value)
        ):  # a string (forward-reference) value type can't take `| None` where it's evaluated
            return f"{ast.unparse(value)} | None"
        case ("popitem", 0):
            return f"tuple[{ast.unparse(key)}, {ast.unparse(value)}]"
        case _:
            return None


class Inference(NamedTuple):
    """An annotation `--fix` would add, and how the value decided it (for `--show-fixes`)."""

    annotation: str
    reason: str


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
    or a method of a class defined in this module; see `_method_return`).

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
            return Inference(declared[name], f"a copy of `{name}`")
        case ast.Subscript(value=ast.Name(id=name)) if name in declared and (
            found := _subscripted(declared[name], value)
        ):
            return Inference(found, f"a subscript of `{name}`, a `{declared[name]}`")
        case ast.Attribute(value=ast.Name(id=name), attr=attr) if name in declared and (
            found := known.classes.get(declared[name], {}).get(attr)
        ):
            return Inference(found, f"the annotation of `{declared[name]}.{attr}`")
        case ast.Call(func=ast.Attribute(value=ast.Name(id=name), attr=attr)) if name in declared and (
            found := _method_return(declared[name], value, attr, known.methods)
        ):
            return Inference(found, _method_reason(declared[name], attr, known.methods))
        case _:
            return None


def _method_reason(receiver: str, method: str, known_methods: Mapping[str, Mapping[str, str]]) -> str:
    """Say which of `_method_return`'s sources typed a `method` call on a `receiver`.

    Returns:
      The reason.

    """
    if method in _METHOD_RETURNS.get(receiver, {}):
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
        return Inference(found, _scalar_reason(value))
    if found := _container(value, known, declared):
        return Inference(found, f"a {found.partition('[')[0]} whose elements' types agree")
    return _called(value, known.calls, known.factories)


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


def _container(value: ast.expr, known: Known, declared: Mapping[str, str]) -> str | None:
    elements: list[ast.expr]
    keys: list[ast.expr | None]
    values: list[ast.expr]
    parts: list[str | None]
    match value:
        case ast.List(elts=elements) | ast.Set(elts=elements) if elements:
            element: str | None = _uniform(elements, known, declared)
            return f"{'list' if isinstance(value, ast.List) else 'set'}[{element}]" if element else None
        case ast.Tuple(elts=elements) if elements:
            parts = [inferred(element, known, declared) for element in elements]
            return None if None in parts else f"tuple[{', '.join(str(part) for part in parts)}]"
        case ast.Dict(keys=keys, values=values) if keys and None not in keys:
            present: list[ast.expr] = [k for k in keys if k is not None]
            key: str | None = _uniform(present, known, declared)
            item: str | None = _uniform(values, known, declared)
            return f"dict[{key}, {item}]" if key and item else None
        case _:
            return None


def _uniform(elements: Sequence[ast.expr], known: Known, declared: Mapping[str, str]) -> str | None:
    """Find the one type every element has.

    Returns:
      That type, or `None` if they differ or any is unknown.

    """
    types: set[str | None] = {inferred(element, known, declared) for element in elements}
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
            return Inference(calls[ast.unparse(func)], f"`{ast.unparse(func)}`'s declared return type")
        case ast.Call(func=ast.Name(id=name)) if name in _BUILTIN_RETURNS:
            return Inference(_BUILTIN_RETURNS[name], f"`{name}`'s fixed return type")
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if _constructs(
            node_name(func),
            known_factories,
        ):
            return Inference(ast.unparse(func), f"a call to `{ast.unparse(func)}`, taken to construct one")
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
    ...) or a method `_method_return` resolves on an already-typed local, and
    another local this scope already typed, are certain. Copying a local `inferred` itself only
    guessed (`guesses`) is no more certain than the guess it copies.

    Returns:
      Whether any call in `value` is to something other than such a certain callee, or any name in
      it copies such a guess.

    """
    return any(_is_guess(node, known, guesses, declared) for node in ast.walk(value))


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
    match node:
        case ast.Call(func=ast.Name(id=name)) if name in _BUILTIN_RETURNS:
            return False
        case ast.Call(func=ast.Attribute(value=ast.Name(id=receiver), attr=method)) as call if (
            receiver in declared
            and _method_return(declared[receiver], call, method, known.methods) is not None
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
