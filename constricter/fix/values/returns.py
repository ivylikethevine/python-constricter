"""Return types the language fixes: builtins', and `str`, `bytes`, `list`, `set` and `dict` methods'."""

import ast
from typing import Final, TypeAlias, cast

from constricter.fix.values.targets import sole
from constricter.source.annotations import dotted

# Builtins whose return type is fixed by the language, whatever their argument: safe to infer, not
# a guess (unlike a capitalised call, which could really be a generic class or a factory function).
BUILTIN_RETURNS: Final = {
    "all": "bool",
    "any": "bool",
    "ascii": "str",
    "bin": "str",
    "bool": "bool",
    "bytearray": "bytearray",
    "bytes": "bytes",
    "callable": "bool",
    "chr": "str",
    "complex": "complex",
    "dir": "list[str]",
    "float": "float",
    "format": "str",
    "hasattr": "bool",
    "hash": "int",
    "hex": "str",
    "id": "int",
    "input": "str",
    "int": "int",
    "isinstance": "bool",
    "issubclass": "bool",
    "len": "int",
    "object": "object",
    "oct": "str",
    "ord": "int",
    "range": "range",
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
    "partition": "tuple[str, str, str]",
    "removeprefix": "str",
    "removesuffix": "str",
    "replace": "str",
    "rfind": "int",
    "rindex": "int",
    "rjust": "str",
    "rpartition": "tuple[str, str, str]",
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
    "partition": "tuple[bytes, bytes, bytes]",
    "removeprefix": "bytes",
    "removesuffix": "bytes",
    "replace": "bytes",
    "rfind": "int",
    "rindex": "int",
    "rjust": "bytes",
    "rpartition": "tuple[bytes, bytes, bytes]",
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


_INT_METHODS: Final = {
    "as_integer_ratio": "tuple[int, int]",
    "bit_count": "int",
    "bit_length": "int",
    "conjugate": "int",
    "to_bytes": "bytes",
}
_FLOAT_METHODS: Final = {
    "as_integer_ratio": "tuple[int, int]",
    "conjugate": "float",
    "hex": "str",
    "is_integer": "bool",
}
METHOD_RETURNS: Final = {
    "str": _STR_METHODS,
    "bytes": _BYTES_METHODS,
    "int": _INT_METHODS,
    "float": _FLOAT_METHODS,
}
# Methods that give the same type whatever their container holds, and whatever they're passed.
_COUNTS: Final = frozenset({"count", "index"})  # a `list`'s or a `tuple`'s: an `int`
_SET_TESTS: Final = frozenset({"isdisjoint", "issubset", "issuperset"})  # a `bool`
_SET_KEEPS: Final = frozenset({"difference", "intersection"})  # the receiver's own type
_SET_METHODS: Final = _SET_TESTS | _SET_KEEPS
_DEFAULTED: Final = frozenset({"get", "pop"})  # a `dict`'s methods given a key and a default
_WITH_DEFAULT: Final = 2
_NONE: Final = "None"
_OPTIONAL: Final = frozenset({"Optional", "typing.Optional", "t.Optional"})
_UNION: Final = frozenset({"Union", "typing.Union", "t.Union"})
# What each literal's type is accepted as, where it's the default: a checker picks `get`'s overload
# taking `V`, and `0` is a `float`'s and a `complex`'s too.
_ACCEPTS: Final = {
    "None": frozenset({_NONE, "object"}),
    "int": frozenset({"int", "float", "complex", "object"}),
    "float": frozenset({"float", "complex", "object"}),
    "complex": frozenset({"complex", "object"}),
    "bool": frozenset({"bool", "int", "float", "complex", "object"}),
    "str": frozenset({"str", "object"}),
    "bytes": frozenset({"bytes", "object"}),
}
_ITERABLES: Final = frozenset({"Iterable", "Collection", "Container", "Sized", "object"})
_SEQUENCES: Final = frozenset({"Sequence"}) | _ITERABLES
# The types an empty display (or the builtin's call) is an instance of, by its kind.
_DISPLAY_TYPES: Final = {
    "list": frozenset({"list", "List", "MutableSequence"}) | _SEQUENCES,
    "tuple": frozenset({"tuple", "Tuple"}) | _SEQUENCES,
    "set": frozenset({"set", "Set", "MutableSet", "AbstractSet"}) | _ITERABLES,
    "frozenset": frozenset({"frozenset", "FrozenSet", "AbstractSet"}) | _ITERABLES,
    "dict": frozenset({"dict", "Dict", "Mapping", "MutableMapping"}) | _ITERABLES,
}
_Kind: TypeAlias = type[ast.expr]
_DISPLAYS: Final[dict[_Kind, str]] = {ast.List: "list", ast.Tuple: "tuple", ast.Set: "set", ast.Dict: "dict"}


def element_method(root: ast.expr, receiver: str, call: ast.Call, method: str) -> str | None:
    """Infer a `list`, `set` or `dict` method call's type from the receiver's own type parameters.

    `receiver` is the receiver's type as text, and `root` that parsed.

    `copy()` is the receiver's type; `pop()` a `list`'s or `set`'s element (with an optional index
    for a `list`); `pop(key)`, `setdefault(key, value)` and `get(key)` a `dict`'s value (`get` as
    `V | None`); `popitem()` its `tuple[K, V]`; `get(key, default)` and `pop(key, default)` by the
    default, where it's a literal or an empty display (see `_defaulted`). A call with any other
    arguments (a keyword, a default of another kind) decides nothing.

    Returns:
      The annotation as source text, or `None` if the call doesn't decide one.

    """
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
            return ast.unparse(sole(element))
        case ast.Subscript(value=ast.Name(id="set" | "Set"), slice=element) if call_shape == ("pop", 0):
            return ast.unparse(sole(element))
        case ast.Subscript(value=ast.Name(id="dict" | "Dict"), slice=ast.Tuple(elts=[key, element])):
            return _dict_method(call_shape, key, element) or _defaulted(call_shape, element, call.args)
        case _:
            return None


def uniform_method(root: ast.expr, receiver: str, method: str) -> str | None:
    """Infer a builtin container's method call that gives one type whatever it holds, or is passed.

    A `list`'s or `tuple`'s `count` and `index` are `int`s, a `set`'s or `frozenset`'s `issubset`
    and its like `bool`s, and its `difference` and `intersection` the receiver's own type.

    Returns:
      The annotation as source text, or `None` for any other method or receiver.

    """
    match root:
        case ast.Subscript(value=ast.Name(id="list" | "List" | "tuple" | "Tuple")) if method in _COUNTS:
            return "int"
        case ast.Subscript(value=ast.Name(id="set" | "Set" | "frozenset" | "FrozenSet")) if (
            method in _SET_METHODS
        ):
            return "bool" if method in _SET_TESTS else receiver
        case _:
            return None


def _defaulted(call_shape: tuple[str, int | None], value: ast.expr, args: list[ast.expr]) -> str | None:
    """Infer a `dict[K, V]`'s `get(key, default)` or `pop(key, default)` by its default, as a checker would.

    `V` where the default is one (`[]` for a `list[str]`, `0` for an `int` or a `float`); else
    `V | T`, `T` a literal default's own type (`None`, `0`, `""`); nothing for an empty display `V`
    isn't (its elements unknown), nor a default of any other kind.

    Returns:
      The annotation as source text, or `None`.

    """
    if call_shape[0] not in _DEFAULTED or call_shape[1] != _WITH_DEFAULT:
        return None
    default: ast.expr = args[1]
    kinds: frozenset[str] = _union_names(value)
    written: str = ast.unparse(value)
    display: str | None
    if (display := _DISPLAYS.get(type(default))) is not None or _empty_call(default):
        accepted: frozenset[str] = _DISPLAY_TYPES[display or ast.unparse(cast("ast.Call", default).func)]
        return written if kinds & accepted and _empty(default) else None
    scalar: str | None = _scalar(default)
    if scalar is None or any(
        isinstance(node, ast.Constant) and isinstance(node.value, str) for node in ast.walk(value)
    ):
        return None  # a string (forward-reference) value type can't take `| T` where it's evaluated
    return written if kinds & _ACCEPTS[scalar] else f"{written} | {scalar}"


def _union_names(annotation: ast.expr) -> frozenset[str]:
    """Name the classes a type is a union of: each member's class, bare or subscripted (`list[str]`'s `list`).

    Returns:
      Them; `object` for `object`, and none for anything else (a string, a call).

    """
    left: ast.expr
    right: ast.expr
    base: ast.expr
    inner: ast.expr
    members: list[ast.expr]
    match annotation:
        case ast.BinOp(op=ast.BitOr(), left=left, right=right):
            return _union_names(left) | _union_names(right)
        case ast.Subscript(value=base, slice=inner) if dotted(base) in _OPTIONAL:
            return _union_names(inner) | {_NONE}
        case ast.Subscript(value=base, slice=ast.Tuple(elts=members)) if dotted(base) in _UNION:
            return frozenset[str]().union(*(_union_names(member) for member in members))
        case ast.Subscript(value=base):
            return frozenset({(dotted(base) or "").rpartition(".")[2]})
        case ast.Constant(value=None):
            return frozenset({_NONE})
        case _:
            return frozenset({(dotted(annotation) or "").rpartition(".")[2]})


def _scalar(default: ast.expr) -> str | None:
    """Name a literal default's type (`None`, `int`, `str`, ...).

    Returns:
      It, or `None` for anything else (a negative number's too: `-1` is an `int`).

    """
    negated: bool = isinstance(default, ast.UnaryOp) and isinstance(default.op, ast.USub)
    node: ast.expr = cast("ast.UnaryOp", default).operand if negated else default
    if not isinstance(node, ast.Constant) or node.value is Ellipsis:
        return None
    return _NONE if node.value is None else type(node.value).__name__


def _empty(default: ast.expr) -> bool:
    """Check whether a display, or a `list()`, `dict()`, `set()` or `tuple()` call, is empty.

    Returns:
      Whether it is.

    """
    match default:
        case ast.List(elts=[]) | ast.Tuple(elts=[]) | ast.Set(elts=[]) | ast.Dict(keys=[]):
            return True
        case ast.Call(args=[], keywords=[]):
            return True
        case _:
            return False


def _empty_call(default: ast.expr) -> bool:
    """Check whether a default is a call of `list`, `dict`, `set`, `frozenset` or `tuple`, the builtin.

    Returns:
      Whether it is (`_empty` says whether it's given anything).

    """
    return (
        isinstance(default, ast.Call)
        and isinstance(default.func, ast.Name)
        and default.func.id in _DISPLAY_TYPES
    )


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
