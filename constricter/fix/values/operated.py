# SPDX-License-Identifier: MIT
"""Binary operators `--fix` types by their operands' builtin types, whose operators nothing can overload.

Numbers: `/` gives a `float`; `+`, `-`, `*`, `//` and `%` a `float` if either side is one, else an
`int`; `<<` and `>>` of integers an `int`, as their `&`, `|` and `^` are (of two `bool`s, a `bool`);
`**` an `int` by a literal exponent (never negative, which gives a `float`), and a `float`'s by an
integer a `float`. `str` and `bytes`: `+` of two, `*` by an integer on either side, and `%`
formatting give the same type back; so do a `list[T]`'s `+` of another and `*` by an integer.
Tuples: `+` gives both sides' parts, and `*` by an integer a `tuple[T, ...]` of the one type they
have. A `set[T]`'s or a `frozenset[T]`'s `|`, `&`, `-` and `^` with another, and a `dict[K, V]`'s
`|`, give that type.
"""

import ast
from typing import Final, cast

_INT: Final = "int"
_FLOAT: Final = "float"
_BOOL: Final = "bool"
_INTEGERS: Final = frozenset({_BOOL, _INT})
_NUMBERS: Final = _INTEGERS | {_FLOAT}
_TEXTS: Final = frozenset({"str", "bytes"})
_LIST: Final = "list"
_TUPLE: Final = "tuple"
_SETS: Final = frozenset({"set", "frozenset"})
_DICT: Final = "dict"
_SAME_TYPE: Final = (ast.Add, ast.Sub, ast.Mult, ast.FloorDiv, ast.Mod)  # an `int`'s, or a `float`'s
_SHIFTS: Final = (ast.LShift, ast.RShift)
_BITWISE: Final = (ast.BitAnd, ast.BitOr, ast.BitXor)
_SET_OPERATORS: Final = (ast.BitOr, ast.BitAnd, ast.Sub, ast.BitXor)
_ANY_LENGTH: Final = 2  # `tuple[T, ...]`'s two parts: the element type and the ellipsis
_ELLIPSIS: Final = "..."


def operated(value: ast.BinOp, left: str | None, right: str | None, max_length: int) -> str | None:
    """Type `value`, a binary operator between values typed `left` and `right` (see the module docstring).

    `max_length`: the longest tuple written part by part.

    Returns:
      The annotation, or `None` for any other operator or operand.

    """
    if left is None:
        return None
    if left in _NUMBERS and right in _NUMBERS:
        return _number(value, left, right or "")
    if left in _INTEGERS and isinstance(value.op, ast.Mult):
        return _repeated(right or "", left)  # `3 * "ab"`: the sequence's own `*`, reflected
    if _root(left) == _TUPLE:
        return _tuple(value.op, left, right or "", max_length)
    if _root(left) in _SETS | {_DICT}:
        return _same(value.op, left, right)
    text: str | None = left if left in _TEXTS or _root(left) == _LIST else None
    return text if text is not None and _keeps_text(value.op, text, right) else None


def _root(annotation: str) -> str:
    """Name a subscripted annotation's outer type (`list` for `list[int]`).

    Returns:
      Its text before the `[`, or nothing for one that isn't subscripted.

    """
    head: str
    bracket: str
    head, bracket, _ = annotation.partition("[")
    return head if bracket else ""


def _number(value: ast.BinOp, left: str, right: str) -> str | None:
    """Type an operator between two builtin numbers.

    Returns:
      The annotation, or `None` for an operator whose result their types don't decide.

    """
    op: ast.operator = value.op
    floating: bool = _FLOAT in {left, right}
    if isinstance(op, ast.Div):
        return _FLOAT
    if isinstance(op, _SAME_TYPE):
        return _FLOAT if floating else _INT
    if isinstance(op, ast.Pow):
        return _power(value.right, left, right)
    if floating:
        return None
    if isinstance(op, _SHIFTS):
        return _INT
    both: bool = left == right == _BOOL
    return (_BOOL if both else _INT) if isinstance(op, _BITWISE) else None


def _power(exponent: ast.expr, left: str, right: str) -> str | None:
    """Type `left ** right`: an integer's by a literal that isn't negative, or a `float`'s by an integer.

    Returns:
      The annotation, or `None`: an integer's by a negative one is a `float`, and a negative
      number's by a `float` a `complex`.

    """
    if left == _FLOAT:
        return _FLOAT if right in _INTEGERS else None
    natural: bool = isinstance(exponent, ast.Constant) and isinstance(exponent.value, int)
    return _INT if natural else None


def _repeated(sequence: str, count: str) -> str | None:
    """Type a `str`, `bytes`, `list` or tuple repeated by a value typed `count`.

    Returns:
      The sequence's type (a tuple's as `tuple[T, ...]`), or `None` if it isn't one, or `count`
      isn't an integer.

    """
    if count not in _INTEGERS:
        return None
    if sequence in _TEXTS or _root(sequence) == _LIST:
        return sequence
    parts: list[str] | None = _parts(sequence)
    return None if parts is None else _any_length(parts)


def _keeps_text(op: ast.operator, text: str, right: str | None) -> bool:
    """Check whether `text op right` (`text` a `str`, a `bytes` or a `list[T]`) gives `text` back.

    Returns:
      Whether it does: `+` of two, `*` by an integer, or a `str`'s or `bytes`'s `%` formatting.

    """
    if isinstance(op, ast.Add):
        return right == text
    if isinstance(op, ast.Mult):
        return right in _INTEGERS
    return isinstance(op, ast.Mod) and text in _TEXTS


def _tuple(op: ast.operator, left: str, right: str, max_length: int) -> str | None:
    """Type a tuple's `+` of another, or its `*` by an integer.

    Returns:
      Both tuples' parts, where each has a fixed length and they're no more than `max_length`; a
      `tuple[T, ...]` where every part of both is a `T`; else `None`.

    """
    if isinstance(op, ast.Mult):
        return _repeated(left, right)
    first: list[str] | None = _parts(left)
    second: list[str] | None = _parts(right) if isinstance(op, ast.Add) else None
    if first is None or second is None:
        return None
    fixed: bool = not (_is_any_length(first) or _is_any_length(second))
    if fixed and len(first) + len(second) <= max_length:
        return f"{_TUPLE}[{', '.join(first + second)}]"
    return _any_length(first + second)


def _parts(annotation: str) -> list[str] | None:
    """Read a tuple type's parts (`tuple[int, str]`, `tuple[int, ...]`).

    Returns:
      Them, as text, a `...` included; `None` for any other type, or a tuple that unpacks one.

    """
    if _root(annotation) != _TUPLE:
        return None
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    whole: ast.expr = cast("ast.Subscript", ast.parse(annotation, mode="eval").body).slice
    elements: list[ast.expr] = whole.elts if isinstance(whole, ast.Tuple) else [whole]
    starred: bool = any(isinstance(element, ast.Starred) for element in elements)
    return None if starred or not elements else [ast.unparse(element) for element in elements]


def _is_any_length(parts: list[str]) -> bool:
    return len(parts) == _ANY_LENGTH and parts[1] == _ELLIPSIS


def _any_length(parts: list[str]) -> str | None:
    """Write the `tuple[T, ...]` of tuples' `parts`.

    Returns:
      It, or `None` where they aren't all one type.

    """
    types: set[str] = set(parts) - {_ELLIPSIS}
    return f"{_TUPLE}[{types.pop()}, ...]" if len(types) == 1 else None


def _same(op: ast.operator, left: str, right: str | None) -> str | None:
    """Type a set's operator with another of its type, or a `dict`'s `|` with another of its.

    Returns:
      That type, or `None` for any other operator, or a right side of another type.

    """
    if left != right:
        return None
    merged: bool = isinstance(op, ast.BitOr) if _root(left) == _DICT else isinstance(op, _SET_OPERATORS)
    return left if merged else None
