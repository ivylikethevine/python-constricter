# SPDX-License-Identifier: MIT
"""An annotation as the tables hold it (`Form`): builtins' text, a class, or `AnyStr`.

And what's read of forms alone: a union's, a constrained type variable's, a `Literal`'s, a function's
`AnyStr` overloads, and a class's method resolution order.
"""

import ast
import re
from collections.abc import Iterable, Sequence
from functools import cache
from typing import Final, NamedTuple, TypeAlias

from constricter.offences import MAX_LENGTH, NESTING
from constricter.rules.annotations import depth, is_vague

STR: Final = "str"
_BYTES: Final = "bytes"
NONE: Final = "None"


_TEXT_WORDS: Final = re.compile(r"[A-Za-z_]+")
_EITHER: Final = frozenset({"AnyStr", "Any", "object", "Incomplete"})  # a parameter taking both
_BUFFER: Final = "buffer"  # a `bytes` overload's parameter may take any buffer


class Text(NamedTuple):
    """An annotation spelled with builtins alone (`int`, `list[str]`, `str | None`)."""

    text: str


class ClassRef(NamedTuple):
    """A class, by the module that defines it and its name there."""

    module: str
    name: str


class Special(NamedTuple):
    """`AnyStr`: whichever of `str` and `bytes` the arguments are."""


ANY_STR: Final = Special()
Form: TypeAlias = Text | ClassRef | Special
_TEXTS: Final[frozenset[Form | None]] = frozenset({Text(STR), Text(_BYTES)})
_STR_ONLY: Final[frozenset[Form | None]] = frozenset({Text(STR)})


Defs: TypeAlias = Sequence[ast.FunctionDef | ast.AsyncFunctionDef]  # a function's overloads


def union(parts: Iterable[Form | None]) -> Form | None:
    """Join builtin annotations with `|`, each once, in order.

    Returns:
      The union, or `None` if a part isn't a builtin annotation.

    """
    texts: list[str] = []
    part: Form | None
    for part in parts:
        if not isinstance(part, Text):
            return None
        if part.text not in texts:
            texts.append(part.text)
    return Text(" | ".join(texts)) if texts else None


def constrained(forms: list[Form | None]) -> Form | None:
    """Read a constrained `TypeVar` whose constraints are text: `str` (`LiteralString` too), or `AnyStr`'s.

    Returns:
      `str`, `ANY_STR`, or `None` for any other constraints (or none).

    """
    kinds: frozenset[Form | None]
    if (kinds := frozenset(forms)) == _STR_ONLY:
        return Text(STR)
    return ANY_STR if kinds == _TEXTS else None


def literal(value: ast.expr) -> Form | None:
    """Widen one `Literal[...]` value to its type (`"a"` to `str`, `None` to `None`).

    Returns:
      Its form, or `None` for anything but a builtin constant.

    """
    constant: bool | int | str | bytes | None
    match value:
        case ast.Constant(value=bool() | int() | str() | bytes() | None as constant):
            return Text(NONE if constant is None else type(constant).__name__)
        case _:
            return None


def mentions(defs: Defs, word: str) -> bool:
    """Check whether any parameter annotation of any overload names `word`.

    Returns:
      Whether one does.

    """
    return any(
        word in _TEXT_WORDS.findall(ast.unparse(arg.annotation))
        for node in defs
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
        if arg.annotation is not None
    )


def any_str_overloads(defs: Defs, forms: list[Form | None]) -> bool:
    """Check for overloads that each take and return only `str`, or only `bytes`, with both there.

    Only their required positional parameters are looked at: a call whose arguments are all `str`
    can't match a `bytes` one, and the other way round.

    Returns:
      Whether they're such overloads.

    """
    if frozenset(forms) != _TEXTS:
        return False
    node: ast.FunctionDef | ast.AsyncFunctionDef
    form: Form | None
    for node, form in zip(defs, forms, strict=True):
        positional: list[ast.arg] = [*node.args.posonlyargs, *node.args.args]
        required: list[ast.arg] = positional[: len(positional) - len(node.args.defaults)]
        if not required or not all(
            _takes_only(arg, _BYTES if form == Text(STR) else STR) for arg in required
        ):
            return False
    return True


def _takes_only(arg: ast.arg, other: str) -> bool:
    """Check that a parameter doesn't take `other` (`str` or `bytes`), by the words of its annotation.

    Returns:
      Whether it doesn't (and is annotated).

    """
    words: list[str] = [] if arg.annotation is None else _TEXT_WORDS.findall(ast.unparse(arg.annotation))
    taking: bool = any(
        other in word.lower() or word in _EITHER or (other == _BYTES and _BUFFER in word.lower())
        for word in words
    )
    return bool(words) and not taking


def c3(klass: ClassRef, lines: list[list[ClassRef]]) -> list[ClassRef] | None:
    """Merge the bases' method resolution orders (and the bases, last) by C3, as Python does.

    Returns:
      `klass`'s order, or `None` if there's none (Python would refuse the class).

    """
    merged: list[ClassRef] = [klass]
    pending: list[list[ClassRef]] = [line for line in lines if line]
    for _ in range(sum(len(line) for line in pending)):  # each round takes one class off
        if not pending:
            break
        head: ClassRef | None = next(
            (line[0] for line in pending if not any(line[0] in other[1:] for other in pending)),
            None,
        )
        if head is None:
            return None
        merged.append(head)
        pending = [rest for rest in ([c for c in line if c != head] for line in pending) if rest]
    return merged


def substituted(template: str, names: dict[str, str]) -> str:
    """Replace names in a template: a class's type parameters by what a subclass passes them.

    Returns:
      The template.

    """
    return ast.unparse(_replaced(ast.parse(template, mode="eval").body, names))


def _replaced(node: ast.expr, names: dict[str, str]) -> ast.expr:
    """Replace names in a template's tree, in place (a template is names, subscripts, tuples, unions).

    Returns:
      The tree.

    """
    name: str
    match node:
        case ast.Name(id=name) if name in names:
            return ast.parse(names[name], mode="eval").body
        case ast.Subscript():
            node.value, node.slice = _replaced(node.value, names), _replaced(node.slice, names)
        case ast.Tuple():
            node.elts = [_replaced(element, names) for element in node.elts]
        case ast.BinOp():
            node.left, node.right = _replaced(node.left, names), _replaced(node.right, names)
        case _:
            pass
    return node


@cache
def usable(text: str) -> bool:
    """Check a builtin annotation is one `--fix` may write: not vague, nested or a long tuple, not `None`.

    Returns:
      Whether it is.

    """
    expr: ast.expr = ast.parse(text, mode="eval").body
    long: bool = any(
        isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Tuple)
        and len(node.slice.elts) > MAX_LENGTH
        for node in ast.walk(expr)
    )
    return text != NONE and not is_vague(expr) and depth(expr) < NESTING and not long
