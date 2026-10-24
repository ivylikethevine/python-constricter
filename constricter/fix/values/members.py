"""What a member of a value whose type is known gives: an attribute, a method call, a subscript.

`inference` works out the receiver's type (a local, `self.index`, `f()`, `x[0]`, anything it can
type), and `member` looks the member up on it through `SOURCES`, in order: the first that knows it
decides. Each source is certain, whatever the call's arguments are; a receiver that's only guessed
makes its member a guess too, as `guesses` judges.
"""

import ast
from collections.abc import Callable, Mapping, Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.imports import added_dotted
from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.core.signatures import AWAIT
from constricter.fix.libraries import generics, overloads, stdlib
from constricter.fix.libraries.library import library_awaited
from constricter.fix.values.returns import METHOD_RETURNS, element_method, uniform_method
from constricter.fix.values.targets import sole
from constricter.rules.annotations import dotted, node_name, roots, vague_fits, words
from constricter.rules.declarations import GenericClass
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
_SELF_TYPE: Final = "Self"  # a generic class's method returning its receiver (see `GenericClass`)
_DEEPEST: Final = 8  # how many generic bases up a member is looked for
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
    if receiver in known.generic:  # its members' types depend on its arguments (see `_own_generic`)
        return None
    if (found := None if call is not None else known.classes.get(receiver, {}).get(name)) is not None:
        return _attribute(found, receiver, name, known)
    lineage: Lineage = known.class_side.lineage
    owner: str | None = _declarer(receiver, name, known) if call is None else lineage.definer(receiver, name)
    found = (known.methods if call is not None else known.classes).get(owner or "", {}).get(prefix + name)
    if found is None or owner is None:
        return None
    if call is None:
        # Another file's base's: not one typed as that class, which may be its property's `Self`.
        return None if found == owner else _attribute(found, owner, name, known)
    if owner != receiver and name in lineage.selfish.get(owner, ()):
        found = receiver
    elif owner != receiver and owner not in lineage.bound and found == owner:
        return None  # another file's class, or its `Self`: the receiver's own class
    return Inference(found, _declared_return(owner, name), frozenset({_METHOD}))


def _attribute(found: str, owner: str, name: str, known: Known) -> Inference | None:
    """Offer an attribute's declared type, less the `ClassVar` or `Final` around it, read through an instance.

    The tables keep those: a subclass's variable a base declares a `ClassVar` isn't one to annotate.
    A descriptor's is what its `__get__` gives (see `through_instance`).

    Returns:
      The inference; `None` for a bare `Final`, which leaves the type to the value, and for a
      descriptor whose `__get__` can't be read.

    """
    text: str | None = through_instance(unqualified(parsed(found)), known)
    return Inference(text, _annotation_of(owner, name), frozenset({_ATTRIBUTE})) if text else None


def through_instance(annotation: str, known: Known) -> str | None:
    """Read an attribute of type `annotation` through an instance: a descriptor's is its `__get__`'s return.

    Returns:
      The type: `annotation` but for a descriptor's (see `Known.descriptors`); `None` for one whose
      `__get__` can't be read (overloaded, say), whose instance's attribute is no fix.

    """
    return known.descriptors.get(annotation, annotation)


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
        return None if call is not None else generics.generic_member(owner, name, call, known)
    return stdlib.library_member(owner, name, call, known, inherited=True)


def _own_generic(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type a member of a checked file's generic class, its type parameters bound by the receiver's arguments.

    `rows.first()` on a `Result[Row]` whose `first` returns `T | None` is a `Row | None`; one that
    returns `Self`, the receiver's type. On the class bare (`Result`, its parameters unknown to a
    checker) only a member whose type names none of them; nor one given another number of arguments.
    One the class doesn't bind is its generic bases', bound by its own arguments (`class Sub(Base[T])`),
    and a plain class of the module's under one (`class Rows(Result[Row])`) has the base's.

    Returns:
      Its inference, or `None`.

    """
    return _generic_member(receiver, _Asked(name, call, receiver), known)


class _Asked(NamedTuple):
    """A member asked of a generic class: its name, its call (`None`: an attribute), its receiver."""

    name: str
    call: ast.Call | None
    own: str  # what `Self` is


def _generic_member(receiver: str, asked: _Asked, known: Known, depth: int = 0) -> Inference | None:
    """Type a member of a generic class (see `_own_generic`), up through its bases.

    `depth`: how many bases up this is.

    Returns:
      Its inference, or `None`.

    """
    tree: ast.expr = parsed(receiver)
    klass: GenericClass | None = known.generic.get(
        ast.unparse(tree.value if isinstance(tree, ast.Subscript) else tree),
    )
    if klass is None:
        owner: str | None = known.class_side.lineage.definer(receiver, asked.name)
        above: bool = owner is not None and owner != receiver and _GENERIC in owner and depth < _DEEPEST
        return _generic_member(owner or "", asked, known, depth + 1) if above else None
    bound: dict[str, str] = _arguments(tree, klass.params)
    found: str | None
    if (found := (klass.methods if asked.call is not None else klass.attributes).get(asked.name)) is None:
        return None if asked.name in klass.bound else _inherited(klass, bound, asked, (known, depth))
    if frozenset(words(found)) & set(klass.params) and not bound:
        return None
    text: str = _deduplicated(overloads.substituted(found, {**bound, _SELF_TYPE: asked.own}))
    if asked.call is None:
        return _attribute(text, asked.own, asked.name, known)
    return Inference(text, _declared_return(asked.own, asked.name), frozenset({_METHOD}))


def _deduplicated(annotation: str) -> str:
    """Write a union once each member: `T | None`, `T` bound to `int | None`, is `int | None`.

    Returns:
      It.

    """
    parts: list[str] = []
    text: str
    for text in (ast.unparse(node) for node in _union_members(parsed(annotation))):
        if text not in parts:
            parts.append(text)
    return " | ".join(parts)


def _union_members(node: ast.expr) -> list[ast.expr]:  # a union's members, left to right; else the type
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return [*_union_members(node.left), *_union_members(node.right)]
    return [node]


def _arguments(tree: ast.expr, params: tuple[str, ...]) -> dict[str, str]:
    """Bind a generic class's type parameters to a receiver's type arguments (`Result[Row]`'s `Row`).

    Returns:
      Each parameter's argument, as text; none for a bare receiver, or one of another number.

    """
    args: list[ast.expr] = []
    if isinstance(tree, ast.Subscript):
        args = tree.slice.elts if isinstance(tree.slice, ast.Tuple) else [tree.slice]
    return (
        dict(zip(params, [ast.unparse(arg) for arg in args], strict=True)) if len(args) == len(params) else {}
    )


def _inherited(
    klass: GenericClass,
    bound: Mapping[str, str],
    asked: _Asked,
    where: tuple[Known, int],
) -> Inference | None:
    """Type a member a generic class takes from its generic bases, bound by its own arguments (`bound`).

    `where`: what's known, and how many bases up the class is.

    Returns:
      The first base's that types it, or `None`.

    """
    if where[1] >= _DEEPEST:
        return None
    base: str
    for base in klass.bases:
        # Bare where the receiver is: its parameters, unbound, are no more known than theirs.
        above: str = (
            overloads.substituted(base, bound)
            if bound
            else ast.unparse(cast("ast.Subscript", parsed(base)).value)
        )
        found: Inference | None
        if (found := _generic_member(above, asked, where[0], where[1] + 1)) is not None:
            return found
    return None


# Where a member's type can come from, in the order they're asked: the one place to add another.
SOURCES: Final[tuple[MemberSource, ...]] = (
    _class_side,
    _fixed,
    _own_generic,
    _declared,
    _elements,
    stdlib.library_member,
    generics.generic_member,
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
    binds it, too, a generic one given its arguments (`Base[int]`) included: a value names none.

    Returns:
      Its type, or `None` if it isn't one (a certain source is asked first, see `member`), or is
      one of another file's that this one can't write.

    """
    owner: str | None = known.class_side.lineage.definer(class_of(receiver) or receiver, name)
    return known.class_side.variables.get((owner or "").partition(_GENERIC)[0], {}).get(name) or None


def subscripted(container: str, node: ast.Subscript, index: str | None) -> str | None:
    """Infer `container[...]`'s type, given `container`'s own type as text, and the index's (`index`).

    A slice (`x[1:2]`, or an index typed `slice`) of a `list`, `str`, `bytes` or `tuple[T, ...]` is
    the same type as `container` itself; an index typed `int` into one is its element type (a
    `bytes`'s, an `int`), and one of another or no known type decides nothing: it may be a slice. Any
    index into a `dict` is its value type. A fixed-length `tuple[T1, T2]`'s part is
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
            return container if sliced else ast.unparse(sole(element)) if index == _INT else None
        case ast.Subscript(
            value=ast.Name(id="dict" | "Dict"),
            slice=ast.Tuple(elts=[_, element]),
        ) if not sliced:
            return ast.unparse(element)
        case ast.Subscript(
            value=ast.Name(id="tuple" | "Tuple"),
            slice=ast.Tuple(elts=[element, last]),
        ) if isinstance(last, ast.Constant) and last.value is Ellipsis:
            return container if sliced else ast.unparse(element) if index == _INT else None
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
        case ast.Constant(value=bool()) | ast.UnaryOp(operand=ast.Constant(value=bool())):
            return None  # an `int` to Python, and no index to a type checker
        case ast.Constant(value=int() as at):
            pass
        case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=int() as at)):
            at = -at
        case _:
            return None
    starred: bool = any(isinstance(part, ast.Starred) for part in parts)
    return None if starred or not -len(parts) <= at < len(parts) else ast.unparse(parts[at])


def _annotation_of(receiver: str, name: str) -> str:
    return f"the annotation of `{receiver}.{name}`"


def _declared_return(receiver: str, name: str) -> str:
    return f"`{receiver}.{name}`'s declared return type"
