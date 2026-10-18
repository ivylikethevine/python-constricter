# SPDX-License-Identifier: MIT
"""Standard-library calls whose arguments decide their type: the signatures a call may match.

`tables/overloads.json` holds each such function's signatures, in order, as each platform and Python
version reads them (see `stdlib_tables/overloads.py`): every parameter's kind, whether it has a
default, and which argument types (`SCALARS`) it certainly takes or refuses; and the return, as a
template naming classes by their dotted paths and type variables by their names.

A type checker picks the first overload whose parameters take a call's arguments. `--fix` types the
call only when that's certain enough: every signature that may be the one (not certainly refusing
them, up to the first that certainly takes them; an argument whose type isn't known, or a verdict
that depends on more than its type, leaves one open) gives the same type, in every variant. A call
none takes is left to the type checker, which rejects it anyway.
"""

import ast
import builtins
from collections.abc import Callable, Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.known import SPELLED, Inference, Known
from constricter.fix.core.signatures import (
    AWAIT,
    CLASS_BINDS,
    CLASS_BOUNDED,
    CLASS_TUPLE,
    CLASS_VERDICT,
    CONTAINER_BINDS,
    CONTAINER_VERDICTS,
    ELEMENT_VERDICTS,
    FUTURE_BINDS,
    OWN,
    OWN_ELEMENTS,
    Accepts,
    Constant,
    Parameter,
    ReadSignature,
    Signature,
    Variant,
)
from constricter.fix.libraries import stdlib
from constricter.fix.libraries.receivers import (
    MAYBE,
    NO,
    SELF_TYPE,
    UNFOLLOWED,
    YES,
    Receiver,
    both,
    matches,
    parsed,
    receiver_of,
)
from constricter.rules.walked import walk

SCALARS: Final = ("str", "LiteralString", "bytes", "bytearray", "int", "float", "complex", "bool", "None")
_COLUMNS: Final = {scalar: index for index, scalar in enumerate(SCALARS)}
_LITERAL_STRING: Final = "LiteralString"  # the type of a `str` literal
_NONE: Final = "None"
_POSITIONAL: Final = frozenset({"p", "e"})
_KEYWORD: Final = frozenset({"e", "k"})
_STAR: Final = "a"
_STARS: Final = "w"
_BUILTINS: Final = frozenset({*dir(builtins), _NONE})
_KIND: Final = "stdlib"
# The builtin numbers a type checker takes where each of these is declared.
_PROMOTED: Final = {
    "int": ("bool",),
    "float": ("int", "bool"),
    "complex": ("float", "int", "bool"),
}
_GENERATOR: Final = "collections.abc.Generator"
_ITERATOR: Final = "collections.abc.Iterator"
_TUPLE: Final = "tuple"
_ANYTHING: Final = "t"  # `Accepts`' key for a parameter any argument binds
_RETURNED: Final = "r"  # `Accepts`' key for a callable parameter a function's return binds
_Taken: TypeAlias = tuple[str, dict[str, str]]  # whether an operand is taken, and what it binds
_NESTED: Final = "ei"  # `Accepts`' key for an iterable of iterables' inner containers
_AWAITED: Final = "w"  # and for an awaitable one, which what awaiting a coroutine's call gives binds
_CALL: Final = "call"  # the fix kind of a declared return
# The builtin containers whose type arguments bind a parameter's type variable (`Iterable[_T]`'s).
CONTAINERS: Final = ("list", _TUPLE, "set", "frozenset", "dict")  # in the `scalars` table's order
_CONTAINERS: Final = frozenset(CONTAINERS)
_SELF: Final = "self"  # a signature's key for the type arguments its method's instance must have
# The builtin classes, each a class as an argument (`assertRaises(ValueError)`).
_BUILTIN_CLASSES: Final = frozenset(
    name for name in dir(builtins) if isinstance(cast("object", getattr(builtins, name)), type)
)
_SEQUENCES: Final = frozenset({"list", "tuple", "set", "frozenset"})  # whose elements `own_e` is asked of
_TYPE_OF: Final = "type["  # the annotation of a class as a value
_Infer: TypeAlias = Callable[[ast.expr], Inference | None]
# A signature that may be the one: its return template and its type variables' types (`None`:
# a return `--fix` can't write).
_Picked: TypeAlias = tuple[str, dict[str, str]] | None


class Argument(NamedTuple):
    """One argument of a call: its type among `SCALARS` (`None` if it's none of them, or unknown).

    `constant`: the literal it is, if it is one (in a 1-tuple, as its value may be `None`);
    `found`: what `--fix` inferred it to be, whose kinds the call's type rests on too; `elements`:
    for a builtin container (`list[str]`), its name and type arguments (`tuple[str, ...]`'s `str`),
    and `inner`, the same of its first one (a `list[list[int]]`'s `list[int]`);
    `reads`: the names, attributes and subscripts in it, as source text; `returns`: for a function
    the module knows the declared return of (`helper`, `u.helper`), that return; `klass`: for a class
    passed as it is (`np.float64`), its name as written; `awaited`: for a coroutine's call, what
    awaiting it gives.
    """

    type: str | None
    constant: tuple[Constant] | None = None
    found: Inference | None = None
    elements: tuple[str, tuple[str, ...]] | None = None
    inner: tuple[str, tuple[str, ...]] | None = None  # its first type argument's, a container too
    reads: tuple[str, ...] = ()
    returns: Inference | None = None
    klass: str | None = None
    awaited: Inference | None = None
    own: tuple[str, ...] = ()  # its class's lineage, for a class the module names (`LibraryNames.lineage`)
    own_elements: tuple[str, ...] = ()  # a builtin sequence's or set's elements' class's
    # Whether `klass` is a library's class (a standard-library one, or what a value typed `type[C]`
    # is), which may be outside a `type[T]`'s bound as a builtin one may, and is a class only to a
    # parameter that speaks of classes: to another, it's the value `found` says.
    library: bool = False
    several: bool = False  # whether `klass` is the union of a tuple of classes (`(OSError, ValueError)`)

    @property
    def text(self) -> str | None:
        """Its type as the module writes it, or `None` if unknown (a literal's is its `type`)."""
        return None if self.found is None else self.found.annotation


class Arguments(NamedTuple):
    """A call's arguments: positional, then by keyword."""

    args: list[Argument]
    keywords: dict[str, Argument]


def chosen(
    name: str,
    call: ast.Call,
    known: Known,
    infer: _Infer,
    method: stdlib.Method | None = None,
) -> Inference | None:
    """Type a call to standard-library function `name` by the signatures its arguments may match.

    `name` is an entry of `OVERLOADS` (of `AWAITED_OVERLOADS`, after `AWAIT`: an `async def`'s call,
    awaited), or `method_signatures` for a `method`'s call on an instance
    (whose type binds its class's type parameters); or an installed package's function, as the
    module calls it (`np.empty`: see `LibraryNames.installed`). `infer` types an argument.

    Returns:
      The inference, its classes spelled (and imported, if they must be) as the module can; or
      `None` if they don't all agree, or its type can't be written.

    """
    read: Arguments | None
    if (read := _arguments(call, infer, known)) is None:
        return None
    installed: tuple[ReadSignature, ...] | None = known.names.installed.get(name)
    variants: tuple[tuple[ReadSignature, ...], ...] = _signatures(name) if installed is None else (installed,)
    instance: list[str] | None = None if method is None else method.instance
    picks: list[_Picked] = [
        _receiving(picked, method)
        for variant in variants
        for picked in _picked(
            variant,
            read,
            instance,
            None if method is None else receiver_of(method, known),
        )
    ]
    found: set[str | None] = {None if picked is None else write(picked, known) for picked in picks}
    if len(found) > 1 and None not in found:
        # Where Python versions differ only in which iterator they declare: the one all of them are.
        found = {None if picked is None else write(_iterator(picked), known) for picked in picks}
    annotation: str | None
    if (annotation := found.pop() if len(found) == 1 else None) is None:  # none, or several that disagree
        return None
    parts: list[Argument] = [*read.args, *read.keywords.values()]
    return Inference(
        annotation,
        f"`{name}`'s return type, for its arguments",
        frozenset({_KIND if installed is None else _CALL}).union(
            *(part.found.kinds for part in parts if part.found is not None),
            *(part.returns.kinds for part in parts if part.returns is not None),
        ),
        # What a type variable may take as its type: an argument of any type but a scalar's.
        tuple(text for part in parts if part.type is None for text in part.reads),
    )


def _iterator(picked: tuple[str, dict[str, str]]) -> tuple[str, dict[str, str]]:
    """Write a pick whose template is a `Generator[T, ...]` as the `Iterator[T]` every generator is.

    Returns:
      It; any other pick as it is.

    """
    head: ast.expr
    index: ast.expr
    match ast.parse(picked[0].removeprefix(SPELLED), mode="eval").body:
        case ast.Subscript(value=ast.Attribute() as head, slice=index) if ast.unparse(head) == _GENERATOR:
            first: ast.expr = index.elts[0] if isinstance(index, ast.Tuple) else index
            return f"{_ITERATOR}[{ast.unparse(first)}]", picked[1]
        case _:
            return picked


def generic_member(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type a generic standard-library class's own attribute or property, bound by the receiver's type.

    `m.string` on an `re.Match[str]` is a `str`; a method (`call`) is `method_signatures`' to type.

    Returns:
      The inference, or `None` if the tables don't have it, or a type parameter it names is unbound.

    """
    found: tuple[str, str, dict[str, str]] | None = (
        stdlib.generic_attribute(receiver, name, known) if call is None else None
    )
    if found is None:
        return None
    annotation: str | None = write((found[1], found[2]), known)
    return (
        None
        if annotation is None
        else Inference(annotation, f"`{found[0]}.{name}`'s annotation in typeshed", frozenset({_KIND}))
    )


def operated(
    method: stdlib.Method,
    operands: tuple[str, str],
    known: Known,
    arguments: tuple[str, ...] | None = None,
    *,
    same: bool = False,
) -> Inference | None:
    """Type a binary operator by its left operand's `method` (`__sub__`), for its right operand's type.

    `operands`: both as `stdlib.operand` names them, a generic class's instance by its class. The
    first signature whose operand takes the right one answers, as a type checker picks it: the same
    type, a class under it, or a number promoted to it (an `int` where a `float` is taken).
    `arguments`: the right operand's type arguments, where it's a generic class's instance, which
    bind the operand's own type variables (`Counter.__add__` takes a `Counter[_S]`); `same`: whether
    it's the left one's own type, as an operand of `Self` must be.

    Returns:
      The inference, or `None`: no signature certainly takes it, one before that may, the Python
      versions differ, or the right operand's class is under the left's (its reflected method may
      answer first).

    """
    left: str
    right: str
    left, right = operands
    if left != right and stdlib.inherits(right, left):
        return None
    found: set[str | None] = {
        _answered(
            variant,
            method,
            known,
            lambda member: _taken(member, operands, arguments, method.types, same=same),
        )
        for variant in stdlib.method_signatures()[method.entry]
    }
    annotation: str | None
    if (annotation := found.pop() if len(found) == 1 else None) is None:
        return None
    return Inference(annotation, f"`{method.entry}`'s return type, for its operand", frozenset({_KIND}))


def _answered(
    variant: Variant,
    method: stdlib.Method,
    known: Known,
    taking: Callable[[str], _Taken],
) -> str | None:
    """Type an operator by one variant of its method's signatures (see `operated`); `taking`, `_taken`'s.

    Returns:
      What the first signature taking the right operand returns, or `None`: a signature before it
      can't be read, or may take it.

    """
    signature: Signature
    for signature in variant:
        takes: str | None
        if (takes := signature.get("takes")) is None:
            return None
        taken: list[_Taken] = [taking(member) for member in _members(parsed(takes))]
        if any(verdict == MAYBE for verdict, _ in taken):
            return None
        bound: dict[str, str] | None
        if (bound := next((binds for verdict, binds in taken if verdict == YES), None)) is not None:
            template: str | None = signature["returns"]
            written: str | None = (
                None if template is None else write((template, {**method.types, **bound}), known)
            )
            return None if written is None else _deduplicated(written)
    return None


def _taken(
    member: str,
    operands: tuple[str, str],
    arguments: tuple[str, ...] | None,
    types: Mapping[str, str],
    *,
    same: bool,
) -> _Taken:
    """Decide whether an operand typed `member` takes the right operand, and what that binds.

    A generic class's instance (`arguments`) is taken by `Self` where it's the left one's own type,
    and by its own class's template (`Counter[_S]`) where each type argument the left one's binds
    (`types`) is its own, binding the others; another class's template (a base's) may take it.

    Returns:
      `YES`, `NO` or `MAYBE`, and the type variables it binds.

    """
    left: str
    right: str
    left, right = operands
    if arguments is None:
        return YES if _takes(member, left, right) else NO, {}
    if member == SELF_TYPE:
        return YES if same else NO, {}
    tree: ast.expr = parsed(member)
    # A base's (`dict[_KT, _VT]`, of an `OrderedDict`): the tables may not know it is.
    if ast.unparse(tree.value if isinstance(tree, ast.Subscript) else tree) != right:
        return MAYBE, {}
    params: list[ast.expr] = (
        []
        if not isinstance(tree, ast.Subscript)
        else tree.slice.elts
        if isinstance(tree.slice, ast.Tuple)
        else [tree.slice]
    )
    if len(params) != len(arguments) or not all(isinstance(param, ast.Name) for param in params):
        return MAYBE, {}
    bound: dict[str, str] = {}
    name: str
    argument: str
    for name, argument in zip((cast("ast.Name", param).id for param in params), arguments, strict=True):
        wanted: str | None = types.get(name, bound.get(name))
        if wanted is not None and wanted != argument:
            return NO, {}
        bound[name] = argument
    return YES, bound


def _takes(member: str, left: str, right: str) -> bool:
    """Check whether an operand typed `member` (`Self`: the left operand's own class) takes `right`.

    Returns:
      Whether it does.

    """
    wanted: str = left if member == SELF_TYPE else member
    return right == wanted or right in _PROMOTED.get(wanted, ()) or stdlib.inherits(right, wanted)


def _deduplicated(annotation: str) -> str:
    """Write each union in an annotation with each member once (`Counter[str | str]`: `Counter[str]`).

    Returns:
      The annotation.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    node: ast.AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Subscript):
            slices: list[ast.expr] = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
            joined: list[ast.expr] = [
                ast.parse(" | ".join(dict.fromkeys(_members(part))), mode="eval").body for part in slices
            ]
            node.slice = ast.Tuple(joined, ast.Load()) if isinstance(node.slice, ast.Tuple) else joined[0]
    return ast.unparse(tree)


def library_element(receiver: str, known: Known) -> Inference | None:
    """Type what iterating a standard-library class's instance gives, bound by the receiver's type.

    A `for` loop over an `io.TextIOWrapper` binds a `str`, over an `itertools.chain[int]` an `int`.

    Returns:
      The inference, or `None` if the tables don't have it, or a type parameter it names is unbound.

    """
    found: tuple[str, str, dict[str, str]] | None = stdlib.element(receiver, known)
    annotation: str | None = None if found is None else write((found[1], found[2]), known)
    return (
        None
        if found is None or annotation is None
        else Inference(annotation, f"the elements of a `{found[0]}`", frozenset({_KIND}))
    )


def _receiving(picked: _Picked, method: stdlib.Method | None) -> _Picked:
    """Add what a method's receiver binds its class's type parameters to (`Method.types`) to a pick.

    Through an alias, its return's class parameters are first written as the alias has them
    (`Method.templates`).

    Returns:
      It, or `None` if an argument binds one differently (the call is an error).

    """
    types: Mapping[str, str] = {} if method is None else method.types
    if picked is None or any(types.get(name, text) != text for name, text in picked[1].items()):
        return None
    return (
        picked[0] if method is None else substituted(picked[0], method.templates),
        {**types, **picked[1]},
    )


def substituted(template: str, types: Mapping[str, str]) -> str:
    """Write a template or pattern with each bare name in `types` replaced by its text.

    Returns:
      It.

    """
    if not types:
        return template
    tree: ast.expr = parsed(template)
    if isinstance(tree, ast.Name):
        return types.get(tree.id, template)
    node: ast.AST
    for node in ast.walk(tree):  # a node's children are listed before it's changed: no text is replaced twice
        field: str
        for field in node._fields:
            setattr(node, field, _replaced(cast("object", getattr(node, field, None)), types))
    return ast.unparse(tree)


def _replaced(value: object, types: Mapping[str, str]) -> object:
    """Replace a field's name, or each name in its list, by its text in `types`.

    Returns:
      The field's new value.

    """
    if isinstance(value, list):
        return [_replaced(item, types) for item in cast("list[object]", value)]
    return parsed(types[value.id]) if isinstance(value, ast.Name) and value.id in types else value


def _arguments(call: ast.Call, infer: _Infer, known: Known) -> Arguments | None:
    """Read a call's arguments.

    Returns:
      Them; or `None` for a call unpacking `*args` or `**kwargs`, whose arguments can't be matched.

    """
    if any(isinstance(arg, ast.Starred) for arg in call.args):
        return None
    keywords: dict[str, Argument] = {}
    keyword: ast.keyword
    for keyword in call.keywords:
        if keyword.arg is None:
            return None
        keywords[keyword.arg] = _argument(keyword.value, infer, known)
    return Arguments([_argument(arg, infer, known) for arg in call.args], keywords)


def _argument(value: ast.expr, infer: _Infer, known: Known) -> Argument:
    constant: Constant
    named: tuple[str, bool] | None = _class_named(value, known)
    elts: list[ast.expr]
    match value:
        case ast.Constant(value=None):
            return Argument(_NONE, (None,))
        case ast.Constant(value=bool() | int() | float() | complex() | str() | bytes() as constant):
            kind: str = _LITERAL_STRING if isinstance(constant, str) else type(constant).__name__
            return Argument(kind, (constant,))
        case ast.Name() | ast.Attribute() if named is not None and not named[1]:
            return Argument(None, reads=(named[0],), klass=named[0])
        case ast.Name() | ast.Attribute() if named is not None:
            # A standard-library class, as the module writes it (`csv.Error`, `sqlite.OperationalError`).
            return _inferred(value, infer, known, klass=named[0])
        case ast.Tuple(elts=elts) if elts and all(_class_named(elt, known) is not None for elt in elts):
            # A tuple of classes (`(OSError, ValueError)`): their union, to a parameter that takes one.
            found: list[tuple[str, bool]] = [
                cast("tuple[str, bool]", _class_named(elt, known)) for elt in elts
            ]
            union: str = " | ".join(dict.fromkeys(text for text, _ in found))
            return _inferred(value, infer, known, klass=union)._replace(several=True)
        case _:
            return _inferred(value, infer, known)


def _class_named(value: ast.expr, known: Known) -> tuple[str, bool] | None:
    """Read a name or dotted path as a class the module knows, as written.

    Returns:
      It, and whether it's a library's (a standard-library class, which may be outside a `type[T]`'s
      bound), or `None` for anything else: the module's own class, an installed package's or a
      builtin, else the standard library's.

    """
    if not isinstance(value, ast.Name | ast.Attribute):
        return None
    written: str = ast.unparse(value)
    if (
        written in known.classes
        or written in known.names.classes
        or (written in _BUILTIN_CLASSES and known.is_builtin(written))
    ):
        return written, False
    return (written, True) if stdlib.class_argument(value, known) is not None else None


def _inferred(value: ast.expr, infer: _Infer, known: Known, klass: str | None = None) -> Argument:
    """Read an argument by what `--fix` infers it to be.

    Returns:
      It; `klass` is the class it is where that's known already, else the class a value typed
      `type[C]` is (`self.failureException`, a `type[BaseException]`).

    """
    found: Inference | None = infer(value)
    typed: str | None = None if found is None else found.annotation
    held: tuple[str, tuple[str, ...]] | None = None if typed is None else _elements(typed, known)
    lineage: Mapping[str, tuple[str, ...]] = known.names.lineage
    return Argument(
        typed if typed in _COLUMNS and typed != _LITERAL_STRING else None,
        found=found,
        elements=held,
        inner=_elements(held[1][0], known) if held and held[1] else None,
        own=lineage.get(typed or "", ()),
        own_elements=lineage.get(held[1][0], ()) if held and held[0] in _SEQUENCES and held[1] else (),
        reads=tuple(
            ast.unparse(node)
            for node in walk(value)
            if isinstance(node, ast.Name | ast.Attribute | ast.Subscript)
        ),
        returns=_function_return(value, known),
        awaited=infer(ast.Await(value)) if isinstance(value, ast.Call | ast.Name) else None,
        klass=_class_of(typed) if klass is None else klass,
        library=True,
    )


def _class_of(typed: str | None) -> str | None:
    """Read the class a value typed `type[C]` is.

    Returns:
      `C`, if `typed` is `type[C]` with `C` a name or dotted path; else `None`.

    """
    if typed is None or not typed.startswith(_TYPE_OF) or not typed.endswith("]"):
        return None
    inner: str = typed[len(_TYPE_OF) : -1]
    named: bool = bool(inner) and inner != SELF_TYPE and all(part.isidentifier() for part in inner.split("."))
    return inner if named else None


def _function_return(value: ast.expr, known: Known) -> Inference | None:
    """Type what a function passed as an argument returns, by its declared return (`partial(helper, x)`).

    Returns:
      The inference, or `None` for anything but a function whose return the module knows.

    """
    name: str = ast.unparse(value)
    if not isinstance(value, ast.Name | ast.Attribute) or name not in known.calls:
        return None
    return Inference(known.calls[name], f"`{name}`'s declared return type", frozenset({_CALL}))


def _elements(annotation: str, known: Known) -> tuple[str, tuple[str, ...]] | None:
    """Read a builtin container's type arguments (`dict[str, int]`), one for a tuple of one type.

    Returns:
      Its name and them, or `None` for anything else (a tuple of several types among them).

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    name: str
    index: ast.expr
    match tree:
        case ast.Subscript(value=ast.Name(id=name), slice=index) if name in _CONTAINERS:
            pass
        case _:
            return None
    if not known.is_builtin(name):
        return None
    texts: list[str] = [ast.unparse(arg) for arg in (index.elts if isinstance(index, ast.Tuple) else [index])]
    if name == _TUPLE:  # `tuple[str, ...]`, or `tuple[str, str]`: `str`
        texts = [text for text in texts if text not in {"...", "()"}]
        return (name, (texts[0],)) if len(set(texts)) == 1 else None
    return name, tuple(texts)


@lru_cache(maxsize=512)
def _signatures(name: str) -> tuple[tuple[ReadSignature, ...], ...]:
    """Read a function's (or method's) variants from the tables, once, each parameter in full.

    Returns:
      Each variant's signatures.

    """
    variants: list[Variant] = (
        stdlib.AWAITED_OVERLOADS[name.removeprefix(AWAIT)]
        if name.startswith(AWAIT)
        else stdlib.OVERLOADS.get(name) or stdlib.method_signatures()[name]
    )
    return tuple(
        tuple(
            ReadSignature(
                # Each a list, as JSON holds it, where the tables' types say a tuple.
                tuple(
                    _parameter(param) for param in cast("list[Sequence[object] | str]", signature["params"])
                ),
                signature["returns"],
                signature.get("self"),
            )
            for signature in variant
        )
        for variant in variants
    )


def _parameter(written: Sequence[object] | str) -> Parameter:
    """Read a parameter as the tables write it (`"name kind="`: one every signature has alike).

    Returns:
      It in full.

    """
    if not isinstance(written, str):
        return cast("Parameter", tuple(written))
    name: str
    kind: str
    name, _, kind = written.partition(" ")
    return name, kind.removesuffix("="), kind.endswith("="), None


def _picked(
    variant: Sequence[ReadSignature],
    read: Arguments,
    instance: Sequence[str] | None,
    receiver: Receiver | None,
) -> Iterator[_Picked]:
    """Find the signatures a call may match: up to the first that certainly takes its arguments.

    `instance`: for a method, its receiver's type arguments (`Pattern[str]`'s), if it has them; a
    signature for another instance type (`self: Pattern[bytes]`) refuses it. An installed method's
    signature declaring its `self` is matched against `receiver`'s type (see `Receiver`).

    Yields:
      Each one that doesn't certainly refuse them: its return template and type variables' types.

    """
    signature: ReadSignature
    for signature in variant:
        verdict: str
        bound: dict[str, str]
        verdict, bound = _matched(signature.params, read)
        if signature.instance is not None and signature.instance != instance:
            verdict = NO if instance is not None else MAYBE if verdict == YES else verdict
        if signature.receiver is not None and verdict != NO:
            verdict = both(verdict, MAYBE if receiver is None else matches(receiver, signature, bound))
        if verdict != NO:
            yield None if signature.returns is None else (signature.returns, bound)
        if verdict == YES:
            return


def _matched(params: Sequence[Parameter], read: Arguments) -> tuple[str, dict[str, str]]:
    """Match a call's arguments to one signature's parameters.

    Returns:
      Whether it takes them (`YES`, `NO`, `MAYBE`), and the type variables they bind.

    """
    pairs: list[tuple[Parameter, Argument]] | None
    if (pairs := _bound(params, read)) is None:
        return NO, {}
    verdicts: set[str] = set()
    types: dict[str, str] = {}
    clashing: set[str] = set()  # type variables two arguments bind differently: unwritable
    param: Parameter
    arg: Argument
    for param, arg in pairs:
        verdict: str = _verdict(param[3], arg)
        verdicts.add(verdict)
        bound: tuple[str, str] | None
        if (bound := None if verdict != YES else _binding(param[3], arg)) is not None:
            variable: str
            text: str
            variable, text = bound
            if types.setdefault(variable, text) != text:
                verdicts.add(MAYBE)
                clashing.add(variable)
    if NO in verdicts:
        return NO, {}
    return (MAYBE if MAYBE in verdicts else YES), {
        name: text for name, text in types.items() if name not in clashing
    }


def _binding(accepts: Accepts | None, arg: Argument) -> tuple[str, str] | None:
    """Find the type variable an argument binds, taken by a parameter that is one (or has one).

    A scalar by the parameter's own verdicts (`var`); else anything by its type, for a parameter that
    is an unbounded type variable (`t`), and a builtin container by its type argument, for one that
    is a generic class of one (`e`, `of`).

    Returns:
      Its name and type, or `None`.

    """
    kind: str | None = arg.type
    if accepts is None or (arg.klass is not None and (CLASS_BINDS in accepts or not arg.library)):
        # A class binds `type[T]`'s `T` (`kv`), or nothing; a library's is a value to any other
        # parameter; a tuple of classes binds it to their union (one taking no tuple refused it, see
        # `_verdict`).
        variable: str | None = None if accepts is None else accepts.get(CLASS_BINDS)
        return None if variable is None or arg.klass is None else (variable, arg.klass)
    if kind is not None:
        binds: str | dict[str, list[str]] = accepts.get("var", {})
        if isinstance(binds, str):  # each type binds it to itself; a `str` literal to `str`
            return binds, "str" if kind == _LITERAL_STRING else kind
        found: list[str] | None = binds.get(kind)
        return None if found is None else (found[0], found[1])
    # Anything, by its type (`t`); a function, by its declared return (`r`).
    named: str | None
    text: str | None
    for named, text in (
        (accepts.get(_ANYTHING), arg.text),
        (accepts.get(_RETURNED), None if arg.returns is None else arg.returns.annotation),
        (accepts.get(_AWAITED), None if arg.awaited is None else arg.awaited.annotation),
        (accepts.get(FUTURE_BINDS), None if arg.awaited is None else arg.text),
    ):
        if named is not None and text is not None:
            return named, text
    of: dict[str, int] = accepts.get("of", {})
    elements: tuple[str, tuple[str, ...]] | None = arg.elements
    if elements is not None and elements[0] in of:
        return _element_binding(accepts, arg, elements[1][of[elements[0]]])
    # A bounded type variable a builtin container argument binds, its bound certainly taking it.
    container: str | None = accepts.get(CONTAINER_BINDS)
    return None if container is None or elements is None or arg.text is None else (container, arg.text)


def _bound(params: Sequence[Parameter], read: Arguments) -> list[tuple[Parameter, Argument]] | None:
    """Bind a call's arguments to a signature's parameters, as Python does.

    Returns:
      Each parameter with its argument (a `*args` or `**kwargs` one with each it takes), or `None` if
      they don't fit: too many, an unknown keyword, one bound twice, a required parameter missing.

    """
    positional: list[Parameter] = [param for param in params if param[1] in _POSITIONAL]
    star: Parameter | None = next((param for param in params if param[1] == _STAR), None)
    stars: Parameter | None = next((param for param in params if param[1] == _STARS), None)
    pairs: list[tuple[Parameter, Argument]] = []
    index: int
    arg: Argument
    for index, arg in enumerate(read.args):
        taking: Parameter | None
        if (taking := positional[index] if index < len(positional) else star) is None:
            return None
        pairs.append((taking, arg))
    filled: set[str] = {param[0] for param in positional[: len(read.args)]}
    keyword: str
    for keyword, arg in read.keywords.items():
        named: Parameter | None = next(
            (param for param in params if param[0] == keyword and param[1] in _KEYWORD),
            stars,
        )
        if named is None or keyword in filled:
            return None
        filled.add(keyword)
        pairs.append((named, arg))
    required: list[str] = [param[0] for param in params if not param[2] and param[1] not in {_STAR, _STARS}]
    return pairs if set(required) <= filled else None


def _verdict(accepts: Accepts | None, arg: Argument) -> str:
    """Decide whether a parameter takes an argument.

    Returns:
      `YES`, `NO`, or `MAYBE` (its type unknown, or not enough to tell).

    """
    if accepts is None:
        return YES
    if arg.klass is not None and (CLASS_VERDICT in accepts or CLASS_BOUNDED in accepts or not arg.library):
        # A builtin or library class may be outside a `type[T]`'s bound (`dtype=bool`, `T` a numpy
        # scalar): the signature that takes it then is another's.
        outside: bool = (arg.library or arg.klass in _BUILTIN_CLASSES) and accepts.get(CLASS_BOUNDED, False)
        untaken: bool = arg.several and not accepts.get(CLASS_TUPLE, False)  # a tuple, where one class is
        return NO if untaken else MAYBE if outside else accepts.get(CLASS_VERDICT, MAYBE)
    if arg.constant is not None and any(_same(arg.constant[0], value) for value in accepts.get("lit", [])):
        return YES
    table: str = accepts.get("c", accepts["v"]) if arg.constant is not None else accepts["v"]
    if arg.type is not None:
        return table[_COLUMNS[arg.type]]
    # A checked file's parameter that takes only checked files' classes, by the argument's lineage.
    wanted: list[str] | None
    line: tuple[str, ...]
    for wanted, line in ((accepts.get(OWN), arg.own), (accepts.get(OWN_ELEMENTS), arg.own_elements)):
        if wanted is not None and line:
            return YES if set(wanted) & set(line) else MAYBE if UNFOLLOWED in line else NO
    taken: bool = (
        (_ANYTHING in accepts and arg.text is not None)
        or (FUTURE_BINDS in accepts and arg.awaited is not None and arg.text is not None)
        or (
            arg.elements is not None
            and arg.elements[0] in accepts.get("of", {})
            and (_NESTED not in accepts or _nested(accepts, arg) is not None)
        )
        or (_RETURNED in accepts and arg.returns is not None)
        or (_AWAITED in accepts and arg.awaited is not None)
    )
    return YES if taken else _container_verdict(accepts, arg)


def _element_binding(accepts: Accepts, arg: Argument, element: str) -> tuple[str, str] | None:
    """Bind a parameter's element type variable (`e`) by a container argument's `element`.

    Of an iterable of iterables (`Iterable[Iterable[_S]]`, `ei`): by that element's own.

    Returns:
      The variable's name and type, or `None`.

    """
    if _NESTED not in accepts:
        return accepts.get("e", ""), element
    inner: tuple[str, tuple[str, ...]] | None = _nested(accepts, arg)
    return None if inner is None else (accepts.get("e", ""), inner[1][accepts[_NESTED][inner[0]]])


def _nested(accepts: Accepts, arg: Argument) -> tuple[str, tuple[str, ...]] | None:
    """Find the container an argument's elements are, where a parameter takes an iterable of them (`ei`).

    Returns:
      Its name and type arguments, or `None` if the elements' type isn't one it takes, or the outer
      container's type argument it reads isn't its first.

    """
    of: dict[str, int] = accepts.get("of", {})
    inner: tuple[str, tuple[str, ...]] | None = arg.inner
    first: bool = arg.elements is not None and of.get(arg.elements[0]) == 0
    return inner if first and inner is not None and inner[0] in accepts.get(_NESTED, {}) else None


def _container_verdict(accepts: Accepts, arg: Argument) -> str:
    """Decide whether a parameter takes a builtin container argument, by its elements' type where it says.

    Returns:
      The verdict: `MAYBE` for any other argument, or a parameter that doesn't say.

    """
    elements: tuple[str, tuple[str, ...]] | None
    if (elements := arg.elements) is None:
        # A parameter bounded by a future takes no coroutine's call: awaitable, but no future.
        return NO if FUTURE_BINDS in accepts and arg.awaited is not None else MAYBE
    verdict: str = accepts.get(CONTAINER_VERDICTS, {}).get(elements[0], MAYBE)
    of: str | None = accepts.get(ELEMENT_VERDICTS, {}).get(elements[0])
    if verdict != YES or of is None:
        return verdict
    element: str = elements[1][0]
    return of[_COLUMNS[element]] if element in _COLUMNS else MAYBE


def _same(constant: Constant, value: Constant) -> bool:
    """Compare a literal argument with a `Literal[...]`'s value, types too (`True` isn't `1`).

    Returns:
      Whether they're the same.

    """
    return type(constant) is type(value) and constant == value


def write(picked: tuple[str, dict[str, str]], known: Known) -> str | None:
    """Write a return template as the module can: its type variables bound, its classes spelled.

    Returns:
      The annotation, each union member once; or `None` if a type variable is unbound, a builtin
      rebound, or a class can't be named. A template that's spelled already (`SPELLED`) is its own.

    """
    template: str
    types: dict[str, str]
    template, types = picked
    if template.startswith(SPELLED):
        return template.removeprefix(SPELLED)
    tree: ast.expr | None = _rewritten(ast.parse(template, mode="eval").body, types, known)
    return None if tree is None else " | ".join(dict.fromkeys(_members(tree)))


def _rewritten(node: ast.expr, types: Mapping[str, str], known: Known) -> ast.expr | None:
    """Rewrite a freshly parsed template in place: each name and dotted path as `_spelled` has it.

    A template is names, dotted paths, subscripts, tuples of their arguments, unions and `...`.

    Returns:
      The tree, or `None` if a name can't be spelled.

    """
    text: str | None
    parts: list[ast.expr | None]
    match node:
        case ast.Name() | ast.Attribute():
            return (
                None if (text := _spelled(node, types, known)) is None else ast.parse(text, mode="eval").body
            )
        case ast.Subscript():
            parts = [_rewritten(node.value, types, known), _rewritten(node.slice, types, known)]
            node.value, node.slice = parts[0] or node.value, parts[1] or node.slice
        case ast.Tuple():
            parts = [_rewritten(element, types, known) for element in node.elts]
            node.elts = [part for part in parts if part is not None]
        case ast.BinOp():
            parts = [_rewritten(node.left, types, known), _rewritten(node.right, types, known)]
            node.left, node.right = parts[0] or node.left, parts[1] or node.right
        case _:
            parts = []
    return None if None in parts else node


def _spelled(node: ast.Name | ast.Attribute, types: Mapping[str, str], known: Known) -> str | None:
    """Spell one name of a template: a class's dotted path, a bound type variable, a builtin.

    Returns:
      Its text, or `None`.

    """
    if isinstance(node, ast.Attribute):
        return None if known.names.plan is None else known.names.plan.spell(ast.unparse(node))
    if node.id in types:
        return types[node.id]
    return node.id if node.id in _BUILTINS and (node.id == _NONE or known.is_builtin(node.id)) else None


def _members(tree: ast.expr) -> Iterator[str]:
    """Walk a union's members (`a | b | c`), not into brackets.

    Yields:
      Each one's text.

    """
    if isinstance(tree, ast.BinOp) and isinstance(tree.op, ast.BitOr):
        yield from _members(tree.left)
        yield from _members(tree.right)
    else:
        yield ast.unparse(tree)
