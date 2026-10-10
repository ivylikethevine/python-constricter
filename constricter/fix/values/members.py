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
from typing import TYPE_CHECKING, Final, TypeAlias

from constricter.fix.core.imports import added_dotted
from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.core.signatures import AWAIT
from constricter.fix.libraries import overloads, stdlib
from constricter.fix.libraries.library import library_awaited
from constricter.fix.values.returns import METHOD_RETURNS, element_method, uniform_method
from constricter.fix.values.targets import sole
from constricter.rules.annotations import dotted, node_name, roots, vague_fits
from constricter.rules.keys import key, optional
from constricter.rules.quoted import unqualified

if TYPE_CHECKING:
    from constricter.fix.core.inherited import Lineage

_ATTRIBUTE: Final = "attribute"  # the fix kind of an attribute's annotation
_METHOD: Final = "method"  # the fix kind of a method's return type
_AWAIT: Final = "await"  # and of what awaiting a checked file's `async def` gives
_RETURNED: Final = "returned"  # and of what `return`s alone decide
_GENERIC: Final = "["  # in a base's text: a generic class's arguments
_SLICE: Final = "slice"  # an index of this type slices
_INT: Final = "int"
_STR: Final = "str"
_SUBSCRIPT: Final = "subscript"  # the fix kind of a subscript
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


@lru_cache(maxsize=4096)  # a module's fixes are a few types, each asked again and again
def fits(annotation: str, level: int) -> bool:
    """Check that a type, as text, is no vaguer than `level` allows (see `vague_fits`).

    Returns:
      Whether it is.

    """
    return vague_fits(parsed(annotation), level)


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
    """Type a `str`, `bytes`, `int` or `float` method with a fixed return type (`METHOD_RETURNS`).

    Returns:
      Its inference, or `None`.

    """
    found: str | None = None if call is None else METHOD_RETURNS.get(receiver, {}).get(name)
    return (
        None
        if found is None
        else Inference(found, f"`{receiver}.{name}`'s fixed return type", frozenset({_METHOD}))
    )


def _declared(
    receiver: str,
    name: str,
    call: ast.Call | None,
    known: Known,
    prefix: str = "",
) -> Inference | None:
    """Type an annotated attribute or property, or a method's declared return, of a known class.

    One this module defines, or another checked file does (see `Known.classes`, `Known.methods`). A
    member the class doesn't define is the base's that does (see `Lineage`); one declared to return
    `Self` there gives the receiver's own class, and one of another file's class returning that
    class, which may be its `Self`, nothing. `prefix`: before a method's name in the tables, for an
    `async def`'s (`AWAIT`): what awaiting its call gives.

    Returns:
      Its inference, or `None`.

    """
    found: str | None
    if (found := None if call is not None else known.classes.get(receiver, {}).get(name)) is not None:
        return _attribute(found, receiver, name)
    lineage: Lineage = known.class_side.lineage
    owner: str | None = _declarer(receiver, name, known) if call is None else lineage.definer(receiver, name)
    found = (known.methods if call is not None else known.classes).get(owner or "", {}).get(prefix + name)
    if found is None or owner is None:
        return None
    if call is None:
        # Another file's base's: not one typed as that class, which may be its property's `Self`.
        return None if found == owner else _attribute(found, owner, name)
    if owner != receiver and name in lineage.selfish.get(owner, ()):
        found = receiver
    elif owner != receiver and owner not in lineage.bound and found == owner:
        return None  # another file's class, or its `Self`: the receiver's own class
    return Inference(found, _declared_return(owner, name), frozenset({_METHOD}))


def _attribute(found: str, owner: str, name: str) -> Inference | None:
    """Offer an attribute's declared type, less the `ClassVar` or `Final` around it.

    The tables keep those: a subclass's variable a base declares a `ClassVar` isn't one to annotate.

    Returns:
      The inference; `None` for a bare `Final`, which leaves the type to the value.

    """
    text: str = unqualified(parsed(found))
    return Inference(text, _annotation_of(owner, name), frozenset({_ATTRIBUTE})) if text else None


def awaited(value: ast.expr, known: Known, infer: Callable[[ast.expr], Inference | None]) -> Inference | None:
    """Infer `await` of a call: a checked file's `async def`'s, or a standard-library coroutine's.

    A function's by its declared return (`known.indirect.awaits`), and a method's on a receiver whose
    type `infer` knows, the class's own or the base's that defines it (see `_declared`); else as
    `library_awaited` has it.

    Returns:
      The inference, or `None`.

    """
    func: ast.expr
    receiver: ast.expr
    name: str
    match value:
        case ast.Await(value=ast.Call(func=ast.Name() | ast.Attribute() as func)) if (
            dotted(func) in known.indirect.awaits
        ):
            spelled: str = ast.unparse(func)
            reason: str = f"`{spelled}`'s declared return type, awaited"
            return Inference(known.indirect.awaits[spelled], reason, frozenset({_AWAIT}))
        case ast.Await(value=ast.Call(func=ast.Attribute(value=receiver, attr=name) as func)):
            owner: Inference | None = infer(receiver)
            found: Inference | None = (
                None
                if owner is None
                else _declared(present(owner.annotation, name), name, ast.Call(func, [], []), known, AWAIT)
            )
            if owner is not None and found is not None:
                kinds: frozenset[str] = found.kinds | {_AWAIT} | owner.kinds - {"copy"}
                return found._replace(reason=f"{found.reason}, awaited", kinds=kinds)
        case _:
            pass
    return _awaited_returns(value, known, infer) or library_awaited(value, known, infer)


def _awaited_returns(
    value: ast.expr,
    known: Known,
    infer: Callable[[ast.expr], Inference | None],
) -> Inference | None:
    """Infer `await` of a call to a checked file's `async def` declaring no return, by its `return`s.

    A function's, or a method's on a receiver whose type `infer` knows (see `awaited_origins`).

    Returns:
      The inference, or `None`.

    """
    call: ast.Call
    match value:
        case ast.Await(value=ast.Call() as call):
            found: tuple[str, str, frozenset[str] | None] | None
            if (found := _loose_await(call, known, infer)) is None:
                return None
            reason: str = f"`{found[0].replace(AWAIT, '')}`'s `return`s, awaited"
            return Inference(found[1], reason, (found[2] or frozenset()) | {_RETURNED})
        case _:
            return None


def awaited_origins(
    call: ast.Call,
    known: Known,
    infer: Callable[[ast.expr], Inference | None],
) -> frozenset[str] | None:
    """Name what awaiting `call` rests on as a guess, where an `async def`'s `return`s type it.

    A function's `return`s' own guesses; a method's too, and `returned`: a subclass may override it.

    Returns:
      Them (none: it's certain), or `None` for any other call.

    """
    found: tuple[str, str, frozenset[str] | None] | None
    if (found := _loose_await(call, known, infer)) is None:
        return None
    rests: frozenset[str] = known.returned.guesses.get(found[0], frozenset())
    return rests if found[2] is None else rests | {_RETURNED}


def _loose_await(
    call: ast.Call,
    known: Known,
    infer: Callable[[ast.expr], Inference | None],
) -> tuple[str, str, frozenset[str] | None] | None:
    """Find the `async def` declaring no return that `call` calls, typed by its `return`s (see `returned`).

    Returns:
      Its key in `Returned.guesses`, what awaiting it gives, and for a method the fix kinds its
      receiver adds (`None`: a function); or `None`.

    """
    receiver: ast.expr
    name: str
    callee: str | None = dotted(call.func)
    if callee is not None and f"{AWAIT}{callee}" in known.returned.calls:
        return f"{AWAIT}{callee}", known.returned.calls[f"{AWAIT}{callee}"], None
    match call.func:
        case ast.Attribute(value=receiver, attr=name) if any(
            f"{AWAIT}{name}" in methods for methods in known.returned.methods.values()
        ):
            owner: Inference | None = infer(receiver)
            defined: tuple[str, str] | None = (
                None
                if owner is None
                else returned_method(present(owner.annotation, name), f"{AWAIT}{name}", known)
            )
            if owner is None or defined is None:
                return None
            return f"{defined[0]}.{AWAIT}{name}", defined[1], owner.kinds - {"copy"}
        case _:
            return None


def _declarer(receiver: str, name: str, known: Known) -> str | None:
    """Find the base whose declared attribute `name` an instance of `receiver` has.

    The first of its order that declares it (in a method too, `self.x: T`, which no class body
    binds), unless `receiver` or a class of the module's before it binds the name another way.

    Returns:
      It, or `None`.

    """
    lineage: Lineage = known.class_side.lineage
    if name in lineage.bound.get(receiver, ()):
        return None
    base: str
    for base in lineage.order.get(receiver, ()):
        if name in known.classes.get(base, {}):
            return base
        if name in lineage.bound.get(base, ()):
            break
    return None


def _elements(receiver: str, name: str, call: ast.Call | None, _known: Known) -> Inference | None:
    """Type a builtin container's method by the receiver's type: its element's, or one all of them give.

    Returns:
      Its inference, or `None` (see `element_method`, `uniform_method`).

    """
    root: ast.expr = parsed(receiver)
    found: str | None = (
        None
        if call is None
        else element_method(root, receiver, call, name) or uniform_method(root, receiver, name)
    )
    return (
        None
        if found is None
        else Inference(found, f"`{receiver}.{name}` on its element types", frozenset({_METHOD}))
    )


def _library_base(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type a member a class of the module's takes from a standard-library base (see `stdlib.bases`).

    `self.id()` in a `unittest.TestCase`: the base's that the class's order ends at, where no class
    before it binds the name (see `Lineage`); `self.data` under a `UserDict[str, bytes]`.

    Returns:
      Its inference, or `None`.

    """
    owner: str | None = known.class_side.lineage.definer(receiver, name)
    if owner is None or owner == receiver:
        return None
    if _GENERIC in owner:  # a generic one, given its arguments: they type its attributes
        return None if call is not None else overloads.generic_member(owner, name, call, known)
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


def keyed(receiver: str, index: ast.expr, known: Known) -> Inference | None:
    """Type `d["key"]`, `d` a value typed as a `TypedDict` class: the key's declared type.

    The class's own key, or one it takes from a base (see `keys.key`, `_declared`).

    Returns:
      Its inference, or `None` for any other index or receiver, or a key the class doesn't declare.

    """
    name: str
    match index:
        case ast.Constant(value=str() as name):
            found: Inference | None = _declared(receiver, key(name), None, known)
            reason: str = f"`{receiver}`'s `{name}` key"
            return None if found is None else Inference(found.annotation, reason, frozenset({_SUBSCRIPT}))
        case _:
            return None


def may_miss(receiver: str, index: ast.expr, known: Known) -> bool:
    """Check whether a `TypedDict` class's literal key may be missing (see `keys.optional`).

    Returns:
      Whether it may: `d.get("key")` is then `None` too.

    """
    return isinstance(index, ast.Constant) and (
        _declared(receiver, optional(str(index.value)), None, known) is not None
    )


def returned_method(receiver: str, name: str, known: Known) -> tuple[str, str] | None:
    """Look up a method of a value typed `receiver` typed only by its `return`s (a guess, see `Returned`).

    The receiver's class's own, or the base's that defines it (see `Lineage`): but not one whose
    type names that base, which may be the receiver's own class (`return self`). A class named by
    an import a fix added (`Tool`, by `from tools import Tool`) is looked up as the module spells
    it (`tools.Tool`): it's a standard-library class another checked file defines. An `async def`'s
    is under `AWAIT` before its name: what awaiting its call gives.

    Returns:
      The class that defines it and its type, or `None` if it isn't one (a certain source is asked
      first, see `member`).

    """
    owner: str | None = known.class_side.lineage.definer(receiver, name.removeprefix(AWAIT))
    found: str | None = known.returned.methods.get(owner or "", {}).get(name)
    plan: ImportPlan | None = known.names.plan
    if found is None and owner == receiver and plan is not None and receiver in plan.added:
        found = known.returned.methods.get(added_dotted(plan.added[receiver]), {}).get(name)
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


def assigned_owner(receiver: str, name: str, known: Known) -> str | None:
    """Find the class whose assignments type the attribute `name` of a value typed `receiver`.

    The receiver's own class, or the first of its order that has one, unless a class of the
    module's before it binds the name in its body.

    Returns:
      It, or `None`.

    """
    lineage: Lineage = known.class_side.lineage
    owner: str
    for owner in (receiver, *lineage.order.get(receiver, ())):
        if name in known.returned.attributes.get(owner, {}):
            return owner
        if name in lineage.bound.get(owner, ()):
            break
    return None


def assigned_attribute(receiver: str, name: str, known: Known) -> str | None:
    """Look up an attribute of a value typed `receiver` typed by its assignments alone (see `assigned_owner`).

    Returns:
      Its type, or `None` if it isn't one (a certain source is asked first, see `member`).

    """
    owner: str | None = assigned_owner(receiver, name, known)
    return None if owner is None else known.returned.attributes[owner][name]


def class_variable(receiver: str, name: str, known: Known) -> str | None:
    """Look up a plain class's variable typed by its value alone (see `constricter.fix.values.classvars`).

    On an instance of the class, or the class itself (`type[C]`); one of a base of the module's that
    binds it, too.

    Returns:
      Its type, or `None` if it isn't one (a certain source is asked first, see `member`), or is
      one of another file's that this one can't write.

    """
    owner: str | None = known.class_side.lineage.definer(class_of(receiver) or receiver, name)
    return known.class_side.variables.get(owner or "", {}).get(name) or None


def subscripted(container: str, node: ast.Subscript, index: str | None) -> str | None:
    """Infer `container[...]`'s type, given `container`'s own type as text, and the index's (`index`).

    A slice (`x[1:2]`, or an index typed `slice`) of a `list`, `str`, `bytes` or `tuple[T, ...]` is
    the same type as `container` itself; a plain index into one is its element type (a `bytes`'s, an
    `int`), as is any index into a `dict` (its value type). A fixed-length `tuple[T1, T2]`'s part is
    the one a literal index names (`pair[0]`, `pair[-1]`).

    Returns:
      The annotation as source text, or `None` if the subscript doesn't decide one.

    """
    sliced: bool = isinstance(node.slice, ast.Slice) or index == _SLICE
    element: ast.expr
    last: ast.expr
    name: str
    match parsed(container):
        case ast.Name(id="str" | "bytes" as name):
            # A `bytes`'s plain index is one byte's `int`; an index of unknown type may be a slice.
            return container if sliced or name == _STR else _INT if index == _INT else None
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
