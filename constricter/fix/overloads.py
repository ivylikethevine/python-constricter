# SPDX-License-Identifier: MIT
"""Standard-library calls whose arguments decide their type: the signatures a call may match.

`tables/overloads.json` holds each such function's signatures, in order, as each platform and Python
version reads them (see `tests/typeshed/overloads.py`): every parameter's kind, whether it has a
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

from constricter.fix import stdlib
from constricter.fix.known import Inference, Known
from constricter.fix.signatures import (
    CLASS_BINDS,
    CLASS_VERDICT,
    CONTAINER_BINDS,
    CONTAINER_VERDICTS,
    ELEMENT_VERDICTS,
    Accepts,
    Constant,
    Parameter,
    ReadSignature,
)
from constricter.rules.walked import walk

SCALARS: Final = ("str", "LiteralString", "bytes", "bytearray", "int", "float", "complex", "bool", "None")
_COLUMNS: Final = {scalar: index for index, scalar in enumerate(SCALARS)}
_LITERAL_STRING: Final = "LiteralString"  # the type of a `str` literal
_NONE: Final = "None"
_YES: Final = "y"
_NO: Final = "n"
_MAYBE: Final = "?"
_POSITIONAL: Final = frozenset({"p", "e"})
_KEYWORD: Final = frozenset({"e", "k"})
_STAR: Final = "a"
_STARS: Final = "w"
_BUILTINS: Final = frozenset({*dir(builtins), _NONE})
_KIND: Final = "stdlib"
_TUPLE: Final = "tuple"
_ANYTHING: Final = "t"  # `Accepts`' key for a parameter any argument binds
_RETURNED: Final = "r"  # `Accepts`' key for a callable parameter a function's return binds
_CALL: Final = "call"  # the fix kind of a declared return
# The builtin containers whose type arguments bind a parameter's type variable (`Iterable[_T]`'s).
CONTAINERS: Final = ("list", _TUPLE, "set", "frozenset", "dict")  # in the `scalars` table's order
_CONTAINERS: Final = frozenset(CONTAINERS)
_SELF: Final = "self"  # a signature's key for the type arguments its method's instance must have
_SELF_TYPE: Final = "Self"  # a method's receiver's type, in `stdlib.Method.types`
_ANY_PATH: Final = "typing.Any"  # a receiver pattern's anything
_TUPLE_PATH: Final = "builtins.tuple"
_BUILTINS_PATH: Final = "builtins."
_UNFOLLOWED: Final = "?"  # a lineage's base that can't be followed
_CLASHING: Final = "?"  # a type variable a receiver's type binds two ways
_REPEATED: Final = 2  # `tuple[int, ...]`'s arguments
_Infer: TypeAlias = Callable[[ast.expr], Inference | None]
# A signature that may be the one: its return template and its type variables' types (`None`:
# a return `--fix` can't write).
_Picked: TypeAlias = tuple[str, dict[str, str]] | None


class Argument(NamedTuple):
    """One argument of a call: its type among `SCALARS` (`None` if it's none of them, or unknown).

    `constant`: the literal it is, if it is one (in a 1-tuple, as its value may be `None`);
    `found`: what `--fix` inferred it to be, whose kinds the call's type rests on too; `elements`:
    for a builtin container (`list[str]`), its name and type arguments (`tuple[str, ...]`'s `str`);
    `reads`: the names, attributes and subscripts in it, as source text; `returns`: for a function
    the module knows the declared return of (`helper`, `u.helper`), that return; `klass`: for a class
    passed as it is (`np.float64`), its name as written.
    """

    type: str | None
    constant: tuple[Constant] | None = None
    found: Inference | None = None
    elements: tuple[str, tuple[str, ...]] | None = None
    reads: tuple[str, ...] = ()
    returns: Inference | None = None
    klass: str | None = None

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

    `name` is an entry of `OVERLOADS`, or `method_signatures` for a `method`'s call on an instance
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
        for picked in _picked(variant, read, instance, None if method is None else _receiver(method, known))
    ]
    found: set[str | None] = {None if picked is None else _written(picked, known) for picked in picks}
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
    annotation: str | None = _written((found[1], found[2]), known)
    return (
        None
        if annotation is None
        else Inference(annotation, f"`{found[0]}.{name}`'s annotation in typeshed", frozenset({_KIND}))
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
    tree: ast.expr = _parsed(template)
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
    return _parsed(types[value.id]) if isinstance(value, ast.Name) and value.id in types else value


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
    match value:
        case ast.Constant(value=bool() | int() | float() | complex() | str() | bytes() | None as constant):
            kind: str = _LITERAL_STRING if isinstance(constant, str) else type(constant).__name__
            return Argument(_NONE if constant is None else kind, (constant,))
        case ast.Name() | ast.Attribute() if (
            ast.unparse(value) in known.classes or ast.unparse(value) in known.names.classes
        ):
            return Argument(None, reads=(ast.unparse(value),), klass=ast.unparse(value))
        case _:
            found: Inference | None = infer(value)
            typed: str | None = None if found is None else found.annotation
            return Argument(
                typed if typed in _COLUMNS and typed != _LITERAL_STRING else None,
                found=found,
                elements=None if typed is None else _elements(typed, known),
                reads=tuple(
                    ast.unparse(node)
                    for node in walk(value)
                    if isinstance(node, ast.Name | ast.Attribute | ast.Subscript)
                ),
                returns=_function_return(value, known),
            )


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
    variants: list[stdlib.Variant] = stdlib.OVERLOADS.get(name) or stdlib.method_signatures()[name]
    return tuple(
        tuple(
            ReadSignature(
                tuple(_parameter(param) for param in signature["params"]),
                signature["returns"],
                signature.get("self"),
            )
            for signature in variant
        )
        for variant in variants
    )


def _parameter(written: Parameter | str) -> Parameter:
    """Read a parameter as the tables write it (`"name kind="`: one every signature has alike).

    Returns:
      It in full.

    """
    if not isinstance(written, str):
        return written
    name: str
    kind: str
    name, _, kind = written.partition(" ")
    return name, kind.removesuffix("="), kind.endswith("="), None


def _picked(
    variant: Sequence[ReadSignature],
    read: Arguments,
    instance: Sequence[str] | None,
    receiver: "_Receiver | None",
) -> Iterator[_Picked]:
    """Find the signatures a call may match: up to the first that certainly takes its arguments.

    `instance`: for a method, its receiver's type arguments (`Pattern[str]`'s), if it has them; a
    signature for another instance type (`self: Pattern[bytes]`) refuses it. An installed method's
    signature declaring its `self` is matched against `receiver`'s type (see `_Receiver`).

    Yields:
      Each one that doesn't certainly refuse them: its return template and type variables' types.

    """
    signature: ReadSignature
    for signature in variant:
        verdict: str
        bound: dict[str, str]
        verdict, bound = _matched(signature.params, read)
        if signature.instance is not None and signature.instance != instance:
            verdict = _NO if instance is not None else _MAYBE if verdict == _YES else verdict
        if signature.receiver is not None and verdict != _NO:
            verdict = _both(verdict, _MAYBE if receiver is None else _matches(receiver, signature, bound))
        if verdict != _NO:
            yield None if signature.returns is None else (signature.returns, bound)
        if verdict == _YES:
            return


def _both(first: str, second: str) -> str:
    """Combine two verdicts that must both hold.

    Returns:
      `_NO` if either is, `_MAYBE` if either is, else `_YES`.

    """
    return _NO if _NO in {first, second} else _MAYBE if _MAYBE in {first, second} else _YES


class _Receiver(NamedTuple):
    """A method call's receiver, matched against an installed method's `self` (`ReadSignature.receiver`).

    Its type (`Self` in `stdlib.Method.types`), as the module writes it, or as the class an alias
    stands for (`Method.matched`); and what the module knows, whose `LibraryNames.lineage` a class
    it names is compared with a pattern's by (where each is defined, and its ancestors). `own`, for
    an alias's: what a type variable may be bound to, the parts the module wrote; the alias's own
    are paths, which it can't.
    """

    text: str | None
    known: Known
    own: frozenset[str] | None = None


def _receiver(method: stdlib.Method, known: Known) -> _Receiver:
    written: str | None = method.types.get(_SELF_TYPE)
    if method.matched is None or written is None:
        return _Receiver(written, known)
    return _Receiver(
        method.matched,
        known,
        frozenset(ast.unparse(node) for node in ast.walk(_parsed(written)) if isinstance(node, ast.expr)),
    )


def _matches(receiver: _Receiver, signature: ReadSignature, bound: dict[str, str]) -> str:
    """Match the receiver's type against `signature`'s `self`, binding its type variables into `bound`.

    Returns:
      `_YES`, `_NO`, or `_MAYBE`.

    """
    found: dict[str, str] = {}
    verdict: str = _unified(
        receiver,
        _parsed(cast("str", signature.receiver)),  # `_picked` asks only where there's one
        _parsed(cast("str", receiver.text)),  # an installed method's receiver always has a type
        dict(signature.bounds),
        found,
    )
    # A variable bound two ways (by two parts, or by the arguments too) is left unbound: a type
    # checker would widen it, or reject the call. So is one bound to what an alias wrote.
    clashing: set[str] = {
        name
        for name, text in found.items()
        if text == _CLASHING
        or bound.get(name, text) != text
        or (receiver.own is not None and text not in receiver.own)
    }
    name: str
    for name in clashing:
        _ = bound.pop(name, None)
        del found[name]
    bound.update(found)
    return _MAYBE if clashing and verdict == _YES else verdict


def _unified(
    receiver: _Receiver,
    pattern: ast.expr,
    actual: ast.expr,
    bounds: dict[str, str],
    found: dict[str, str],
) -> str:
    """Match one part of the receiver's type against a pattern's.

    Returns:
      The verdict.

    """
    left: ast.expr
    right: ast.expr
    name: str
    match pattern:
        case ast.BinOp(left=left, op=ast.BitOr(), right=right):
            return _either(receiver, [left, right], actual, bounds, found)
        case ast.Name(id=name):  # a type variable: bound to it (see `_matches` for two ways)
            text: str = ast.unparse(actual)
            if found.setdefault(name, text) != text:
                found[name] = _CLASHING
            return _YES if name not in bounds else _either(receiver, [_parsed(bounds[name])], actual, {}, {})
        case ast.Subscript():
            return _subscript(receiver, pattern, actual, bounds, found)
        case _:
            return _class(receiver, ast.unparse(pattern), actual)


def _either(
    receiver: _Receiver,
    members: Sequence[ast.expr],
    actual: ast.expr,
    bounds: dict[str, str],
    found: dict[str, str],
) -> str:
    """Match against a union: `_YES` if a member matches (its bindings kept), `_NO` if none can.

    Returns:
      The verdict.

    """
    verdicts: set[str] = set()
    member: ast.expr
    for member in [part for each in members for part in _union(each)]:
        bound: dict[str, str] = dict(found)
        verdict: str
        if (verdict := _unified(receiver, member, actual, bounds, bound)) == _YES:
            found.update(bound)
            return _YES
        verdicts.add(verdict)
    return _NO if verdicts == {_NO} else _MAYBE


def _subscript(
    receiver: _Receiver,
    pattern: ast.Subscript,
    actual: ast.expr,
    bounds: dict[str, str],
    found: dict[str, str],
) -> str:
    """Match a generic class's pattern (`ndarray[tuple[Any, ...], dtype[ScalarT]]`) argument by argument.

    Returns:
      The verdict: `_MAYBE` for a subclass, or the receiver's type without arguments.

    """
    related: str = _class(
        receiver,
        ast.unparse(pattern.value),
        actual.value if isinstance(actual, ast.Subscript) else actual,
    )
    if (
        related != _YES
        or not isinstance(actual, ast.Subscript)
        or ast.unparse(pattern.value) != _defined(receiver, actual.value)
    ):
        return _MAYBE if related == _YES else related
    wanted: list[ast.expr] = _arguments_of(pattern)
    given: list[ast.expr] = _arguments_of(actual)
    if _repeated(wanted) and _repeated(given):  # `tuple[int, ...]` both: their elements
        wanted, given = wanted[:1], given[:1]
    elif _repeated(given):
        return _MAYBE  # its length unknown
    elif _repeated(wanted):
        wanted = [wanted[0]] * len(given)
    if len(wanted) != len(given):
        return _NO if ast.unparse(pattern.value) == _TUPLE_PATH else _MAYBE
    verdict: str = _YES
    part: ast.expr
    other: ast.expr
    for part, other in zip(wanted, given, strict=True):
        verdict = _both(verdict, _unified(receiver, part, other, bounds, found))
    return verdict


def _repeated(args: Sequence[ast.expr]) -> bool:
    return len(args) == _REPEATED and isinstance(args[1], ast.Constant) and args[1].value is Ellipsis


def _class(receiver: _Receiver, path: str, actual: ast.expr) -> str:
    """Compare a pattern's class (`numpy.floating`) with the receiver's (`np.float64`), by its lineage.

    Returns:
      `_YES` if it's that class or a subclass, `_NO` if its lineage is known and doesn't have it.

    """
    if path == _ANY_PATH:
        return _YES
    lineage: tuple[str, ...] = _lineage(
        receiver,
        actual.value if isinstance(actual, ast.Subscript) else actual,
    )
    if path in lineage:
        return _YES
    return _MAYBE if not lineage or _UNFOLLOWED in lineage else _NO


def _defined(receiver: _Receiver, actual: ast.expr) -> str:
    lineage: tuple[str, ...] = _lineage(receiver, actual)
    return lineage[0] if lineage else ""


def _lineage(receiver: _Receiver, actual: ast.expr) -> tuple[str, ...]:
    """Find where a class the receiver's type names is defined, and its ancestors.

    Returns:
      Them; none for anything else. A builtin's, just it and `object`.

    """
    text: str = ast.unparse(actual)
    if isinstance(actual, ast.Name) and receiver.known.is_builtin(text):
        return (f"builtins.{text}", "builtins.object")
    if text.startswith(_BUILTINS_PATH):  # an alias's expansion's (`builtins.tuple`)
        return (text, "builtins.object")
    return tuple(receiver.known.names.lineage.get(text, ()))


def _union(pattern: ast.expr) -> list[ast.expr]:
    """Split a union pattern into its members.

    Returns:
      Them.

    """
    if isinstance(pattern, ast.BinOp) and isinstance(pattern.op, ast.BitOr):
        return [*_union(pattern.left), *_union(pattern.right)]
    return [pattern]


def _arguments_of(node: ast.Subscript) -> list[ast.expr]:
    return list(node.slice.elts) if isinstance(node.slice, ast.Tuple) else [node.slice]


def _parsed(text: str) -> ast.expr:
    return ast.parse(text, mode="eval").body


def _matched(params: Sequence[Parameter], read: Arguments) -> tuple[str, dict[str, str]]:
    """Match a call's arguments to one signature's parameters.

    Returns:
      Whether it takes them (`_YES`, `_NO`, `_MAYBE`), and the type variables they bind.

    """
    pairs: list[tuple[Parameter, Argument]] | None
    if (pairs := _bound(params, read)) is None:
        return _NO, {}
    verdicts: set[str] = set()
    types: dict[str, str] = {}
    clashing: set[str] = set()  # type variables two arguments bind differently: unwritable
    param: Parameter
    arg: Argument
    for param, arg in pairs:
        verdict: str = _verdict(param[3], arg)
        verdicts.add(verdict)
        bound: tuple[str, str] | None
        if (bound := None if verdict != _YES else _binding(param[3], arg)) is not None:
            variable: str
            text: str
            variable, text = bound
            if types.setdefault(variable, text) != text:
                verdicts.add(_MAYBE)
                clashing.add(variable)
    if _NO in verdicts:
        return _NO, {}
    return (_MAYBE if _MAYBE in verdicts else _YES), {
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
    if accepts is None or arg.klass is not None:  # a class binds `type[T]`'s `T` (`kv`), or nothing
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
    ):
        if named is not None and text is not None:
            return named, text
    of: dict[str, int] = accepts.get("of", {})
    elements: tuple[str, tuple[str, ...]] | None = arg.elements
    if elements is not None and elements[0] in of:
        return accepts.get("e", ""), elements[1][of[elements[0]]]
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
      `_YES`, `_NO`, or `_MAYBE` (its type unknown, or not enough to tell).

    """
    if accepts is None:
        return _YES
    if arg.klass is not None:
        return accepts.get(CLASS_VERDICT, _MAYBE)
    if arg.constant is not None and any(_same(arg.constant[0], value) for value in accepts.get("lit", [])):
        return _YES
    table: str = accepts.get("c", accepts["v"]) if arg.constant is not None else accepts["v"]
    if arg.type is not None:
        return table[_COLUMNS[arg.type]]
    taken: bool = (
        (_ANYTHING in accepts and arg.text is not None)
        or (arg.elements is not None and arg.elements[0] in accepts.get("of", {}))
        or (_RETURNED in accepts and arg.returns is not None)
    )
    return _YES if taken else _container_verdict(accepts, arg)


def _container_verdict(accepts: Accepts, arg: Argument) -> str:
    """Decide whether a parameter takes a builtin container argument, by its elements' type where it says.

    Returns:
      The verdict: `_MAYBE` for any other argument, or a parameter that doesn't say.

    """
    elements: tuple[str, tuple[str, ...]] | None
    if (elements := arg.elements) is None:
        return _MAYBE
    verdict: str = accepts.get(CONTAINER_VERDICTS, {}).get(elements[0], _MAYBE)
    of: str | None = accepts.get(ELEMENT_VERDICTS, {}).get(elements[0])
    if verdict != _YES or of is None:
        return verdict
    element: str = elements[1][0]
    return of[_COLUMNS[element]] if element in _COLUMNS else _MAYBE


def _same(constant: Constant, value: Constant) -> bool:
    """Compare a literal argument with a `Literal[...]`'s value, types too (`True` isn't `1`).

    Returns:
      Whether they're the same.

    """
    return type(constant) is type(value) and constant == value


def _written(picked: tuple[str, dict[str, str]], known: Known) -> str | None:
    """Write a return template as the module can: its type variables bound, its classes spelled.

    Returns:
      The annotation, each union member once; or `None` if a type variable is unbound, a builtin
      rebound, or a class can't be named.

    """
    template: str
    types: dict[str, str]
    template, types = picked
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
