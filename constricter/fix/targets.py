# SPDX-License-Identifier: MIT
"""Types split over what a loop or an unpacking binds: a container's elements, a tuple's parts."""

import ast
from typing import Final

from constricter.fix.known import Inference

# Builtins that iterate over their (first) argument's elements, one to one.
SAME_ELEMENTS: Final = frozenset({"reversed", "sorted"})
DICT_VIEWS: Final = frozenset({"keys", "values", "items"})
# Containers whose one type parameter is their elements'.
_ONE_ELEMENT_TYPE: Final = frozenset({"list", "List", "set", "Set", "frozenset", "FrozenSet"})
RANGE: Final = "range"
ENUMERATE: Final = "enumerate"
ITERATORS: Final = frozenset({RANGE, ENUMERATE, "zip", *SAME_ELEMENTS})
# `tuple[T, ...]`'s two parts: the element type and the ellipsis.
_ANY_LENGTH: Final = 2


def element_type(container: str, reason: str, kinds: frozenset[str]) -> Inference | None:
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
        case ast.Call(func=ast.Name(id=name), args=args, keywords=[]) if name in ITERATORS and args:
            if name == RANGE:
                return []
            return [part for arg in (args[:1] if name == ENUMERATE else args) for part in iterated(arg)]
        case ast.Call(func=ast.Attribute(value=receiver, attr=view), args=[]) if view in DICT_VIEWS:
            return [receiver]
        case _:
            return [iterable]
