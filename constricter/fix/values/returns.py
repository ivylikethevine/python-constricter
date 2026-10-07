# SPDX-License-Identifier: MIT
"""Return types the language fixes: builtins', and `str`, `bytes`, `list`, `set` and `dict` methods'."""

import ast
from typing import Final

from constricter.fix.values.targets import sole

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


def element_method(root: ast.expr, receiver: str, call: ast.Call, method: str) -> str | None:
    """Infer a `list`, `set` or `dict` method call's type from the receiver's own type parameters.

    `receiver` is the receiver's type as text, and `root` that parsed.

    `copy()` is the receiver's type; `pop()` a `list`'s or `set`'s element (with an optional index
    for a `list`); `pop(key)`, `setdefault(key, value)` and `get(key)` a `dict`'s value (`get` as
    `V | None`); `popitem()` its `tuple[K, V]`. A call with any other arguments (`pop(key, default)`,
    a keyword) can return something else, so it decides nothing.

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
            return _dict_method(call_shape, key, element)
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
            method in _SET_TESTS | _SET_KEEPS
        ):
            return "bool" if method in _SET_TESTS else receiver
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
