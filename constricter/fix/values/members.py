# SPDX-License-Identifier: MIT
"""What a member of a value whose type is known gives: an attribute, a method call, a subscript.

`inference` works out the receiver's type (a local, `self.index`, `f()`, `x[0]`, anything it can
type), and `member` looks the member up on it through `SOURCES`, in order: the first that knows it
decides. Each source is certain, whatever the call's arguments are; a receiver that's only guessed
makes its member a guess too, as `guesses` judges.
"""

import ast
from collections.abc import Callable, Sequence
from functools import lru_cache
from typing import Final, TypeAlias

from constricter.fix.core.known import Inference, Known
from constricter.fix.libraries import overloads, stdlib
from constricter.fix.values.returns import METHOD_RETURNS, element_method
from constricter.fix.values.targets import sole
from constricter.rules.annotations import node_name, roots

_ATTRIBUTE: Final = "attribute"  # the fix kind of an attribute's annotation
_METHOD: Final = "method"  # the fix kind of a method's return type
_SLICE: Final = "slice"  # an index of this type slices
_OPTIONAL: Final = "Optional"
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


def present(receiver: str, attr: str) -> str:
    """Read the `X` of a receiver typed `X | None` (or `Optional[X]`), whose member `attr` is looked up.

    Only an `X` has the member: a type checker has narrowed the receiver to it there, or reports the
    access. Not a member `None` has too (`__class__`), nor a union of more types.

    Returns:
      The `X` as text; any other receiver as it is.

    """
    kept: ast.expr
    head: ast.expr
    match parsed(receiver):
        case _ if attr.startswith("__"):
            return receiver
        case (
            ast.BinOp(left=kept, op=ast.BitOr(), right=ast.Constant(value=None))
            | ast.BinOp(left=ast.Constant(value=None), op=ast.BitOr(), right=kept)
        ) if not isinstance(kept, ast.BinOp):
            return ast.unparse(kept)
        case ast.Subscript(value=head, slice=kept) if node_name(head) == _OPTIONAL:
            return ast.unparse(kept)
        case _:
            return receiver


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

    One this module defines, or another checked file does (see `Known.classes`, `Known.methods`). A
    method the class doesn't define is the base's that does (see `Lineage`); one declared to return
    `Self` there gives the receiver's own class, and one of another file's class returning that
    class, which may be its `Self`, nothing.

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
    owner: str | None = known.class_side.lineage.definer(receiver, name)
    found = known.methods.get(owner or "", {}).get(name)
    if found is None or owner is None:
        return None
    if owner != receiver and name in known.class_side.lineage.selfish.get(owner, ()):
        found = receiver
    elif owner != receiver and owner not in known.class_side.lineage.bound and found == owner:
        return None  # another file's class, or its `Self`: the receiver's own class
    return Inference(found, _declared_return(owner, name), frozenset({_METHOD}))


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


def _library_base(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type a member a class of the module's takes from a standard-library base (see `stdlib.bases`).

    `self.id()` in a `unittest.TestCase`: the base's that the class's order ends at, where no class
    before it binds the name (see `Lineage`).

    Returns:
      Its inference, or `None`.

    """
    owner: str | None = known.class_side.lineage.definer(receiver, name)
    if owner is None or owner == receiver:
        return None
    return stdlib.library_member(owner, name, call, known, inherited=True)


# Where a member's type can come from, in the order they're asked: the one place to add another.
SOURCES: Final[tuple[MemberSource, ...]] = (
    _class_side,
    _fixed,
    _declared,
    _elements,
    stdlib.library_member,
    overloads.generic_member,
    _library_base,
)


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


def returned_method(receiver: str, name: str, known: Known) -> tuple[str, str] | None:
    """Look up a method of a value typed `receiver` typed only by its `return`s (a guess, see `Returned`).

    The receiver's class's own, or the base's that defines it (see `Lineage`): but not one whose
    type names that base, which may be the receiver's own class (`return self`).

    Returns:
      The class that defines it and its type, or `None` if it isn't one (a certain source is asked
      first, see `member`).

    """
    owner: str | None = known.class_side.lineage.definer(receiver, name)
    found: str | None = known.returned.methods.get(owner or "", {}).get(name)
    if found is None or owner is None or (owner != receiver and owner in roots(found)):
        return None
    return owner, found


def partial_method(receiver: str, name: str, known: Known) -> str | None:
    """Look up a method of a value typed `receiver` declared to return a tuple with a vague part.

    The receiver's class's own, or the base's that defines it (see `Lineage`, `Partial`).

    Returns:
      Its return, or `None` if it isn't one.

    """
    owner: str | None = known.class_side.lineage.definer(receiver, name)
    return known.indirect.partial.methods.get(owner or "", {}).get(name)


def assigned_attribute(receiver: str, name: str, known: Known) -> str | None:
    """Look up an attribute of a value typed `receiver` typed by its assignments alone (see `Returned`).

    Returns:
      Its type, or `None` if it isn't one (a certain source is asked first, see `member`).

    """
    return known.returned.attributes.get(receiver, {}).get(name)


def class_variable(receiver: str, name: str, known: Known) -> str | None:
    """Look up a plain class's variable typed by its value alone (see `constricter.fix.values.classvars`).

    On an instance of the class, or the class itself (`type[C]`); one of a base of the module's that
    binds it, too.

    Returns:
      Its type, or `None` if it isn't one (a certain source is asked first, see `member`).

    """
    owner: str | None = known.class_side.lineage.definer(class_of(receiver) or receiver, name)
    return known.class_side.variables.get(owner or "", {}).get(name)


def subscripted(container: str, node: ast.Subscript, index: str | None) -> str | None:
    """Infer `container[...]`'s type, given `container`'s own type as text, and the index's (`index`).

    A slice (`x[1:2]`, or an index typed `slice`) of a `list`, `str`, `bytes` or `tuple[T, ...]` is
    the same type as `container` itself; a plain index into one is its element type, as is any index
    into a `dict` (its value type). A fixed-length `tuple[T1, T2]`'s part is the one a literal index
    names (`pair[0]`, `pair[-1]`).

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
        ) if isinstance(last, ast.Constant) and last.value is Ellipsis:
            return container if sliced else ast.unparse(element)
        case ast.Subscript(value=ast.Name(id="tuple" | "Tuple"), slice=element) if not sliced:
            return _part(element.elts if isinstance(element, ast.Tuple) else [element], node.slice)
        case _:
            return None


def _part(parts: Sequence[ast.expr], index: ast.expr) -> str | None:
    """Pick the part of a fixed-length tuple's type that a literal `index` names (`0`, `-1`).

    Returns:
      It, as text; `None` for any other index, one past the tuple's ends, or a tuple that unpacks
      another (`tuple[int, *Ts]`).

    """
    at: int
    match index:
        case ast.Constant(value=int() as at) if not isinstance(at, bool):
            pass
        case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=int() as at)) if not isinstance(at, bool):
            at = -at
        case _:
            return None
    starred: bool = any(isinstance(part, ast.Starred) for part in parts)
    return None if starred or not -len(parts) <= at < len(parts) else ast.unparse(parts[at])


def _annotation_of(receiver: str, name: str) -> str:
    return f"the annotation of `{receiver}.{name}`"


def _declared_return(receiver: str, name: str) -> str:
    return f"`{receiver}.{name}`'s declared return type"
