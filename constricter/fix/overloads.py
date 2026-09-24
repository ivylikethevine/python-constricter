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
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix import stdlib
from constricter.fix.known import Inference, Known
from constricter.fix.stdlib import Accepts, Constant, Parameter, Signature

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
_SELF: Final = "self"  # a signature's key for the type arguments its method's instance must have
_Infer: TypeAlias = Callable[[ast.expr], Inference | None]
# A signature that may be the one: its return template and its type variables' types (`None`:
# a return `--fix` can't write).
_Picked: TypeAlias = tuple[str, dict[str, str]] | None


class Argument(NamedTuple):
    """One argument of a call: its type among `SCALARS` (`None` if it's none of them, or unknown).

    `constant`: the literal it is, if it is one (in a 1-tuple, as its value may be `None`);
    `found`: what `--fix` inferred it to be, whose kinds the call's type rests on too.
    """

    type: str | None
    constant: tuple[Constant] | None = None
    found: Inference | None = None


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
    (whose type binds its class's type parameters); `infer` types an argument.

    Returns:
      The inference, its classes spelled (and imported, if they must be) as the module can; or
      `None` if they don't all agree, or its type can't be written.

    """
    read: Arguments | None
    if (read := _arguments(call, infer)) is None:
        return None
    variants: list[stdlib.Variant] = stdlib.OVERLOADS.get(name) or stdlib.method_signatures()[name]
    instance: list[str] | None = None if method is None else method.instance
    picks: list[_Picked] = [
        _receiving(picked, {} if method is None else method.types)
        for variant in variants
        for picked in _picked(variant, read, instance)
    ]
    found: set[str | None] = {None if picked is None else _written(picked, known) for picked in picks}
    annotation: str | None
    if (annotation := found.pop() if len(found) == 1 else None) is None:  # none, or several that disagree
        return None
    parts: list[Argument] = [*read.args, *read.keywords.values()]
    return Inference(
        annotation,
        f"`{name}`'s return type, for its arguments",
        frozenset({_KIND}).union(*(part.found.kinds for part in parts if part.found is not None)),
    )


def _receiving(picked: _Picked, types: Mapping[str, str]) -> _Picked:
    """Add what the receiver binds its class's type parameters to (`types`) to a signature picked.

    Returns:
      It, or `None` if an argument binds one differently (the call is an error).

    """
    if picked is None or any(types.get(name, text) != text for name, text in picked[1].items()):
        return None
    return picked[0], {**types, **picked[1]}


def _arguments(call: ast.Call, infer: _Infer) -> Arguments | None:
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
        keywords[keyword.arg] = _argument(keyword.value, infer)
    return Arguments([_argument(arg, infer) for arg in call.args], keywords)


def _argument(value: ast.expr, infer: _Infer) -> Argument:
    constant: Constant
    match value:
        case ast.Constant(value=bool() | int() | float() | complex() | str() | bytes() | None as constant):
            kind: str = _LITERAL_STRING if isinstance(constant, str) else type(constant).__name__
            return Argument(_NONE if constant is None else kind, (constant,))
        case _:
            found: Inference | None = infer(value)
            typed: str | None = None if found is None else found.annotation
            return Argument(typed if typed in _COLUMNS and typed != _LITERAL_STRING else None, found=found)


def _picked(
    variant: Sequence[Signature],
    read: Arguments,
    instance: Sequence[str] | None,
) -> Iterator[_Picked]:
    """Find the signatures a call may match: up to the first that certainly takes its arguments.

    `instance`: for a method, its receiver's type arguments (`Pattern[str]`'s), if it has them; a
    signature for another instance type (`self: Pattern[bytes]`) refuses it.

    Yields:
      Each one that doesn't certainly refuse them: its return template and type variables' types.

    """
    signature: Signature
    for signature in variant:
        verdict: str
        bound: dict[str, str]
        verdict, bound = _matched(signature["params"], read)
        if _SELF in signature and signature["self"] != instance:
            verdict = _NO if instance is not None else _MAYBE if verdict == _YES else verdict
        if verdict != _NO:
            template: str | None = signature["returns"]
            yield None if template is None else (template, bound)
        if verdict == _YES:
            return


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
        if (bound := None if verdict != _YES else _binding(param[3], arg.type)) is not None:
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


def _binding(accepts: Accepts | None, kind: str | None) -> tuple[str, str] | None:
    """Find the type variable an argument of type `kind` binds, taken by a parameter that is one.

    Returns:
      Its name and type, or `None`.

    """
    binds: str | dict[str, list[str]] = {} if accepts is None or kind is None else accepts.get("var", {})
    if isinstance(binds, str):  # each type binds it to itself; a `str` literal to `str`
        return binds, "str" if kind == _LITERAL_STRING else cast("str", kind)
    found: list[str] | None = None if kind is None else binds.get(kind)
    return None if found is None else (found[0], found[1])


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
    if arg.constant is not None and any(_same(arg.constant[0], value) for value in accepts.get("lit", [])):
        return _YES
    table: str = accepts.get("c", accepts["v"]) if arg.constant is not None else accepts["v"]
    return _MAYBE if arg.type is None else table[_COLUMNS[arg.type]]


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
