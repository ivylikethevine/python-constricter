"""An installed method's receiver, matched against the `self` its signature declares (`matches`).

For `constricter.fix.libraries.overloads`, which picks such a signature only where its receiver's
type fits: part by part, a type variable bound to what it stands against (left unbound where it's
bound two ways), a union by either member, a subscript by its arguments, and a class by where it's
defined and its ancestors. Each match is `YES`, `NO` or `MAYBE`.
"""

import ast
from collections.abc import Sequence
from typing import Final, NamedTuple, cast

from constricter.fix.core.known import Known
from constricter.fix.core.signatures import (
    ReadSignature,
)
from constricter.fix.libraries import stdlib

YES: Final = "y"
NO: Final = "n"
MAYBE: Final = "?"


SELF_TYPE: Final = "Self"  # a method's receiver's type, in `stdlib.Method.types`
_ANY_PATH: Final = "typing.Any"  # a receiver pattern's anything
_TUPLE_PATH: Final = "builtins.tuple"
_BUILTINS_PATH: Final = "builtins."


UNFOLLOWED: Final = "?"  # a lineage's base that can't be followed


_CLASHING: Final = "?"  # a type variable a receiver's type binds two ways
_REPEATED: Final = 2  # `tuple[int, ...]`'s arguments


def both(first: str, second: str) -> str:
    """Combine two verdicts that must both hold.

    Returns:
      `NO` if either is, `MAYBE` if either is, else `YES`.

    """
    return NO if NO in {first, second} else MAYBE if MAYBE in {first, second} else YES


class Receiver(NamedTuple):
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


def receiver_of(method: stdlib.Method, known: Known) -> Receiver:
    """Describe a method call's receiver (see `Receiver`).

    Returns:
      It.

    """
    written: str | None = method.types.get(SELF_TYPE)
    if method.matched is None or written is None:
        return Receiver(written, known)
    return Receiver(
        method.matched,
        known,
        frozenset(ast.unparse(node) for node in ast.walk(parsed(written)) if isinstance(node, ast.expr)),
    )


def matches(receiver: Receiver, signature: ReadSignature, bound: dict[str, str]) -> str:
    """Match the receiver's type against `signature`'s `self`, binding its type variables into `bound`.

    Returns:
      `YES`, `NO`, or `MAYBE`.

    """
    found: dict[str, str] = {}
    verdict: str = _unified(
        receiver,
        parsed(cast("str", signature.receiver)),  # `_picked` asks only where there's one
        parsed(cast("str", receiver.text)),  # an installed method's receiver always has a type
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
    return MAYBE if clashing and verdict == YES else verdict


def _unified(
    receiver: Receiver,
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
        case ast.Name(id=name):  # a type variable: bound to it (see `matches` for two ways)
            text: str = ast.unparse(actual)
            if found.setdefault(name, text) != text:
                found[name] = _CLASHING
            return YES if name not in bounds else _either(receiver, [parsed(bounds[name])], actual, {}, {})
        case ast.Subscript():
            return _subscript(receiver, pattern, actual, bounds, found)
        case _:
            return _class(receiver, ast.unparse(pattern), actual)


def _either(
    receiver: Receiver,
    members: Sequence[ast.expr],
    actual: ast.expr,
    bounds: dict[str, str],
    found: dict[str, str],
) -> str:
    """Match against a union: `YES` if a member matches (its bindings kept), `NO` if none can.

    Returns:
      The verdict.

    """
    verdicts: set[str] = set()
    member: ast.expr
    for member in [part for each in members for part in _union(each)]:
        bound: dict[str, str] = dict(found)
        verdict: str
        if (verdict := _unified(receiver, member, actual, bounds, bound)) == YES:
            found.update(bound)
            return YES
        verdicts.add(verdict)
    return NO if verdicts == {NO} else MAYBE


def _subscript(
    receiver: Receiver,
    pattern: ast.Subscript,
    actual: ast.expr,
    bounds: dict[str, str],
    found: dict[str, str],
) -> str:
    """Match a generic class's pattern (`ndarray[tuple[Any, ...], dtype[ScalarT]]`) argument by argument.

    Returns:
      The verdict: `MAYBE` for a subclass, or the receiver's type without arguments.

    """
    related: str = _class(
        receiver,
        ast.unparse(pattern.value),
        actual.value if isinstance(actual, ast.Subscript) else actual,
    )
    if (
        related != YES
        or not isinstance(actual, ast.Subscript)
        or ast.unparse(pattern.value) != _defined(receiver, actual.value)
    ):
        return MAYBE if related == YES else related
    wanted: list[ast.expr] = _arguments_of(pattern)
    given: list[ast.expr] = _arguments_of(actual)
    if _repeated(wanted) and _repeated(given):  # `tuple[int, ...]` both: their elements
        wanted, given = wanted[:1], given[:1]
    elif _repeated(given):
        return MAYBE  # its length unknown
    elif _repeated(wanted):
        wanted = [wanted[0]] * len(given)
    if len(wanted) != len(given):
        return NO if ast.unparse(pattern.value) == _TUPLE_PATH else MAYBE
    verdict: str = YES
    part: ast.expr
    other: ast.expr
    for part, other in zip(wanted, given, strict=True):
        verdict = both(verdict, _unified(receiver, part, other, bounds, found))
    return verdict


def _repeated(args: Sequence[ast.expr]) -> bool:
    return len(args) == _REPEATED and isinstance(args[1], ast.Constant) and args[1].value is Ellipsis


def _class(receiver: Receiver, path: str, actual: ast.expr) -> str:
    """Compare a pattern's class (`numpy.floating`) with the receiver's (`np.float64`), by its lineage.

    Returns:
      `YES` if it's that class or a subclass, `NO` if its lineage is known and doesn't have it.

    """
    if path == _ANY_PATH:
        return YES
    lineage: tuple[str, ...] = _lineage(
        receiver,
        actual.value if isinstance(actual, ast.Subscript) else actual,
    )
    if path in lineage:
        return YES
    return MAYBE if not lineage or UNFOLLOWED in lineage else NO


def _defined(receiver: Receiver, actual: ast.expr) -> str:
    lineage: tuple[str, ...] = _lineage(receiver, actual)
    return lineage[0] if lineage else ""


def _lineage(receiver: Receiver, actual: ast.expr) -> tuple[str, ...]:
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


def parsed(text: str) -> ast.expr:
    """Parse a type's text.

    Returns:
      Its expression.

    """
    return ast.parse(text, mode="eval").body
