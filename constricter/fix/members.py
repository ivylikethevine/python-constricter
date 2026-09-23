# SPDX-License-Identifier: MIT
"""What a member of a value whose type is known gives: an attribute, a method call, a subscript.

`inference` works out the receiver's type (a local, `self.index`, `f()`, `x[0]`, anything it can
type), and `member` looks the member up on it through `SOURCES`, in order: the first that knows it
decides. Each source is certain, whatever the call's arguments are; a receiver that's only guessed
makes its member a guess too, as `guesses` judges.
"""

import ast
from collections.abc import Callable
from functools import lru_cache
from typing import Final, TypeAlias

from constricter.fix import stdlib
from constricter.fix.known import Inference, Known
from constricter.fix.returns import METHOD_RETURNS, element_method
from constricter.fix.targets import sole

_ATTRIBUTE: Final = "attribute"  # the fix kind of an attribute's annotation
_METHOD: Final = "method"  # the fix kind of a method's return type
_SLICE: Final = "slice"  # an index of this type slices
# One way to type a member: given the receiver's type as text, the member's name, and the call
# (`None` for an attribute), its inference, or `None` if this source doesn't know it.
MemberSource: TypeAlias = Callable[[str, str, ast.Call | None, Known], Inference | None]


@lru_cache(maxsize=4096)
def parsed(annotation: str) -> ast.expr:
    """Parse an annotation `--fix` wrote or read, once for all its lookups.

    `annotation` is always `ast.unparse`'s own output (an annotation, or an earlier inference),
    never user text, so it's always valid Python. The tree is shared: only read it.

    Returns:
      Its expression.

    """
    return ast.parse(annotation, mode="eval").body


def class_of(receiver: str) -> str | None:
    """Read the class a `type[C]` names (what `cls` is in a classmethod of `C`).

    Returns:
      `C`, or `None` if `receiver` isn't a `type[...]` of a plain name.

    """
    name: str
    match parsed(receiver):
        case ast.Subscript(value=ast.Name(id="type"), slice=ast.Name(id=name)):
            return name
        case _:
            return None


def _class_side(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type a class's own attribute or classmethod, on a `type[C]` (`cls.limit`, `cls.build()`).

    Returns:
      Its inference, or `None`.

    """
    owner: str | None
    if (owner := class_of(receiver)) is None:
        return None
    if call is None:
        found: str | None = known.class_side.attributes.get(owner, {}).get(name)
        return (
            None
            if found is None
            else Inference(found, _annotation_of(receiver, name), frozenset({_ATTRIBUTE}))
        )
    found = known.class_side.methods.get(owner, {}).get(name)
    return None if found is None else Inference(found, _declared_return(receiver, name), frozenset({_METHOD}))


def _fixed(receiver: str, name: str, call: ast.Call | None, _known: Known) -> Inference | None:
    """Type a `str` or `bytes` method with a fixed return type (`METHOD_RETURNS`).

    Returns:
      Its inference, or `None`.

    """
    found: str | None = None if call is None else METHOD_RETURNS.get(receiver, {}).get(name)
    return (
        None
        if found is None
        else Inference(found, f"`{receiver}.{name}`'s fixed return type", frozenset({_METHOD}))
    )


def _declared(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type an annotated attribute or property, or a method's declared return, of a known class.

    One this module defines, or another checked file does (see `Known.classes`, `Known.methods`).

    Returns:
      Its inference, or `None`.

    """
    if call is None:
        found: str | None = known.classes.get(receiver, {}).get(name)
        return (
            None
            if found is None
            else Inference(found, _annotation_of(receiver, name), frozenset({_ATTRIBUTE}))
        )
    found = known.methods.get(receiver, {}).get(name)
    return None if found is None else Inference(found, _declared_return(receiver, name), frozenset({_METHOD}))


def _elements(receiver: str, name: str, call: ast.Call | None, _known: Known) -> Inference | None:
    """Type a `list`, `set` or `dict` method whose return is the receiver's own element type.

    Returns:
      Its inference, or `None` (see `element_method`).

    """
    found: str | None = None if call is None else element_method(parsed(receiver), receiver, call, name)
    return (
        None
        if found is None
        else Inference(found, f"`{receiver}.{name}` on its element types", frozenset({_METHOD}))
    )


# Where a member's type can come from, in the order they're asked: the one place to add another.
SOURCES: Final[tuple[MemberSource, ...]] = (_class_side, _fixed, _declared, _elements, stdlib.library_member)


def member(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type the member `name` of a value typed `receiver`: an attribute, or (`call`) a method's call.

    Returns:
      The first of `SOURCES`' inferences, or `None` if none knows it.

    """
    source: MemberSource
    found: Inference | None
    for source in SOURCES:
        if (found := source(receiver, name, call, known)) is not None:
            return found
    return None


def returned_method(receiver: str, name: str, known: Known) -> str | None:
    """Look up a method of a value typed `receiver` typed only by its `return`s (a guess, see `Returned`).

    Returns:
      Its type, or `None` if it isn't one (a certain source is asked first, see `member`).

    """
    return known.returned.methods.get(receiver, {}).get(name)


def subscripted(container: str, node: ast.Subscript, index: str | None) -> str | None:
    """Infer `container[...]`'s type, given `container`'s own type as text, and the index's (`index`).

    A slice (`x[1:2]`, or an index typed `slice`) of a `list`, `str` or `bytes` is the same type as
    `container` itself; a plain
    index into one is its element type, as is any index into a `dict` (its value type) or a
    homogeneous `tuple[T, ...]`. A fixed-length `tuple[T1, T2]`'s element only varies with the index,
    which isn't worth resolving.

    Returns:
      The annotation as source text, or `None` if the subscript doesn't decide one.

    """
    sliced: bool = isinstance(node.slice, ast.Slice) or index == _SLICE
    element: ast.expr
    last: ast.expr
    match parsed(container):
        case ast.Name(id="str" | "bytes"):
            return container
        case ast.Subscript(value=ast.Name(id="list" | "List"), slice=element):
            return container if sliced else ast.unparse(sole(element))
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


def _annotation_of(receiver: str, name: str) -> str:
    return f"the annotation of `{receiver}.{name}`"


def _declared_return(receiver: str, name: str) -> str:
    return f"`{receiver}.{name}`'s declared return type"
