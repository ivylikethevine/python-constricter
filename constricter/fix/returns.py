# SPDX-License-Identifier: MIT
"""Return types the language fixes: builtins', and `str`, `bytes`, `list`, `set` and `dict` methods'."""

import ast
from collections.abc import Mapping
from typing import Final

# Builtins whose return type is fixed by the language, whatever their argument: safe to infer, not
# a guess (unlike a capitalised call, which could really be a generic class or a factory function).
BUILTIN_RETURNS: Final = {
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


METHOD_RETURNS: Final = {"str": _STR_METHODS, "bytes": _BYTES_METHODS}


def method_return(
    receiver: str,
    call: ast.Call,
    method: str,
    known_methods: Mapping[str, Mapping[str, str]],
) -> str | None:
    """Look up the type of `call`, a `method` call on a receiver whose own type is `receiver`, as text.

    A fixed-return `str`/`bytes` method (`METHOD_RETURNS`), a method of a class defined in the
    module (`known_methods`, see `method_returns`), or a `list`/`set`/`dict` method whose return is the
    receiver's own element type (`_element_method`).

    Returns:
      The annotation as source text, or `None` if none of those decides one.

    """
    return (
        METHOD_RETURNS.get(receiver, {}).get(method)
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
