# SPDX-License-Identifier: MIT
"""Builtins and operators `--fix` types by their operands' types, as typeshed's `builtins.pyi` has them.

`abs`, `round`, `divmod` and `sum` of builtin numbers; `min` and `max` of values of one type (or of
numbers, the wider one), or of something's elements; `next` of what yields a known type; `dict` of a
mapping, of pairs or of keywords, and `dict.fromkeys`; `enumerate`, `zip`, `map` and `reversed`, of
what they yield; the builtin classes' classmethods with a fixed return (`bytes.fromhex`); and `-n`,
`+n` and `~n`. `infer` types a value as
`constricter.fix.values.inference` does, and `loop` what iterating it gives.
"""

import ast
from collections.abc import Callable, Mapping, Sequence
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.values.shapes import Infer, is_none, or_none, typed
from constricter.fix.values.targets import dict_parts, iterator_call
from constricter.rules.annotations import dotted
from constricter.rules.flow import members

_KIND: Final = "builtin"  # the fix kind
_INT: Final = "int"
_FLOAT: Final = "float"
_COMPLEX: Final = "complex"
_INTEGERS: Final = frozenset({"bool", _INT})
_REALS: Final = _INTEGERS | {_FLOAT}
_KEY: Final = "key"  # `min`'s and `max`'s keyword that only orders
_DEFAULT: Final = "default"  # theirs for an empty iterable
_START: Final = "start"  # `sum`'s
_PAIR: Final = 2  # `divmod`'s arguments, and the most `round` and `next` take
_ANY_LENGTH: Final = "..."  # a `tuple[T, ...]`'s second part
_ENUMERATE: Final = "enumerate"
_ZIP: Final = "zip"
_ZIPPED: Final = 5  # the most iterables typeshed's `zip` overloads type part by part
_ITERATOR: Final = "collections.abc.Iterator"  # what `iter` gives


class _Call(NamedTuple):
    """One call to a builtin: its name, positional arguments and keywords, and how to type their parts."""

    name: str
    args: Sequence[ast.expr]
    keywords: Mapping[str, ast.expr]
    infer: Infer
    loop: Infer
    plan: ImportPlan | None  # how the module names a library class, one it's still to import too


_Rule: TypeAlias = Callable[[_Call], Inference | None]


def _made(call: _Call, annotation: str, *parts: Inference) -> Inference:
    """Write a call's inference, resting on its `parts`'.

    Returns:
      It.

    """
    return Inference(
        annotation,
        f"`{call.name}` of {parts[0].reason}",
        frozenset({_KIND}).union(*(part.kinds for part in parts)),
        tuple(read for part in parts for read in part.reads),
    )


def _numbers(call: _Call, count: int) -> list[Inference] | None:
    """Type a call's arguments, `count` of them and no keyword, each a builtin number.

    Returns:
      Their inferences, or `None` if it's called otherwise or one isn't an `int`, `bool` or `float`.

    """
    if call.keywords or len(call.args) != count:
        return None
    found: list[Inference | None] = [call.infer(arg) for arg in call.args]
    numbers: list[Inference] = [part for part in found if part is not None and part.annotation in _REALS]
    return numbers if len(numbers) == count else None


def _wider(parts: Sequence[Inference]) -> str:
    """Name the type arithmetic on builtin numbers gives.

    Returns:
      `float` if any of them is one, else `int`.

    """
    return _FLOAT if any(part.annotation == _FLOAT for part in parts) else _INT


def _abs(call: _Call) -> Inference | None:
    """Type `abs(x)`: an `int`'s is an `int`, a `float`'s or a `complex`'s a `float`.

    Returns:
      The inference, or `None`.

    """
    found: Inference | None = call.infer(call.args[0]) if len(call.args) == 1 and not call.keywords else None
    if found is None or found.annotation not in _REALS | {_COMPLEX}:
        return None
    return _made(call, _INT if found.annotation in _INTEGERS else _FLOAT, found)


def _round(call: _Call) -> Inference | None:
    """Type `round(x)`, an `int`, and `round(x, digits)`, a number of `x`'s type.

    Returns:
      The inference, or `None`.

    """
    digits: bool = len(call.args) == _PAIR and not is_none(call.args[1])
    found: list[Inference] | None = _numbers(call._replace(args=call.args[:1]), 1)
    if found is None or len(call.args) > _PAIR or call.keywords:
        return None
    return _made(call, _wider(found) if digits else _INT, *found)


def _divmod(call: _Call) -> Inference | None:
    """Type `divmod(a, b)` of builtin numbers: a pair of `int`s, or of `float`s if either is one.

    Returns:
      The inference, or `None`.

    """
    found: list[Inference] | None = _numbers(call, _PAIR)
    return None if found is None else _made(call, f"tuple[{_wider(found)}, {_wider(found)}]", *found)


def _sum(call: _Call) -> Inference | None:
    """Type `sum(xs)` of builtin numbers, with a start of them or none: an `int`, or a `float`.

    Returns:
      The inference, or `None`.

    """
    starts: list[ast.expr] = [*call.args[1:], *call.keywords.values()]
    if not call.args or len(starts) > 1 or call.keywords.keys() - {_START}:
        return None
    parts: list[Inference | None] = [call.loop(call.args[0]), *(call.infer(start) for start in starts)]
    found: list[Inference] = [part for part in parts if part is not None and part.annotation in _REALS]
    return _made(call, _wider(found), *found) if len(found) == len(parts) else None


def _extreme(call: _Call) -> Inference | None:
    """Type `min` and `max`: of several values of one type, that type; of one argument, its elements'.

    Of an `int` and a `float`, a `float`: either fits one.

    With a `default`, one of the elements' type, or `None` (`T | None`).

    Returns:
      The inference, or `None`.

    """
    if not call.args or call.keywords.keys() - {_KEY, _DEFAULT}:
        return None
    default: ast.expr | None = call.keywords.get(_DEFAULT)
    if len(call.args) > 1:
        parts: list[Inference | None] = [typed(arg, call.infer) for arg in call.args]
        found: list[Inference] = [part for part in parts if part is not None]
        if len(found) != len(parts) or default is not None:
            return None
        if len({part.annotation for part in found}) > 1:
            # Numbers of two types: the wider one holds whichever it is.
            mixed: bool = all(part.annotation in _REALS for part in found)
            return _made(call, _wider(found), *found) if mixed else None
        single: bool = len(members(found[0].annotation) or ()) == 1
        return _made(call, found[0].annotation, *found) if single else None
    element: Inference | None = call.loop(call.args[0])
    return None if element is None else _defaulted(call, element, default)


def _next(call: _Call) -> Inference | None:
    """Type `next(it)`: what `it` yields; with a default, of that type, or `None` (`T | None`).

    Returns:
      The inference, or `None`.

    """
    if call.keywords or not 1 <= len(call.args) <= _PAIR:
        return None
    element: Inference | None = call.loop(call.args[0])
    return None if element is None else _defaulted(call, element, (*call.args, None)[1])


def _defaulted(call: _Call, element: Inference, default: ast.expr | None) -> Inference | None:
    """Type a call that gives an `element`, or else its `default` (if any).

    Returns:
      The element's type, a default of it, or with `None` for a `None` one; `None` for any other.

    """
    if default is None:
        return _made(call, element.annotation, element)
    if is_none(default):
        union: str | None = or_none(element.annotation)
        return None if union is None else _made(call, union, element)
    other: Inference | None = call.infer(default)
    same: bool = other is not None and other.annotation == element.annotation
    return _made(call, element.annotation, element, other) if other is not None and same else None


def _dict(call: _Call) -> Inference | None:
    """Type `dict(d)`, by `d`'s keys and values; `dict(pairs)`, by their parts; `dict(a=1)`, a `dict[str, T]`.

    Returns:
      The inference, or `None` for both arguments and keywords, or parts that don't agree.

    """
    if call.keywords and not call.args:
        values: list[Inference | None] = [call.infer(value) for value in call.keywords.values()]
        found: list[Inference] = [value for value in values if value is not None]
        same: bool = len({value.annotation for value in found}) == 1 and len(found) == len(values)
        return _made(call, f"dict[str, {found[0].annotation}]", *found) if same else None
    if call.keywords or len(call.args) != 1:
        return None
    copied: Inference | None = typed(call.args[0], call.infer)
    parts: tuple[str, str] | None = None if copied is None else dict_parts(copied.annotation)
    if copied is not None and parts is not None:
        return _made(call, f"dict[{parts[0]}, {parts[1]}]", copied)
    item: Inference | None = call.loop(call.args[0])
    pair: tuple[str, str] | None = None if item is None else _pair(item.annotation)
    return None if item is None or pair is None else _made(call, f"dict[{pair[0]}, {pair[1]}]", item)


def _pair(annotation: str) -> tuple[str, str] | None:
    """Read a `tuple[K, V]`'s two parts.

    Returns:
      Them, as text; `None` for any other annotation, a `tuple[T, ...]` included.

    """
    key: ast.expr
    value: ast.expr
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    match ast.parse(annotation, mode="eval").body:
        case ast.Subscript(value=ast.Name(id="tuple" | "Tuple"), slice=ast.Tuple(elts=[key, value])) if (
            ast.unparse(value) != _ANY_LENGTH
        ):
            return ast.unparse(key), ast.unparse(value)
        case _:
            return None


def _fromkeys(call: _Call) -> Inference | None:
    """Type `dict.fromkeys(keys, value)`: a `dict` of the keys' elements to the value's type.

    Returns:
      The inference, or `None` without a value (each is then `None`, or anything), or a part unknown.

    """
    if call.keywords or len(call.args) != _PAIR:
        return None
    key: Inference | None = call.loop(call.args[0])
    value: Inference | None = call.infer(call.args[1])
    if key is None or value is None:
        return None
    return _made(call, f"dict[{key.annotation}, {value.annotation}]", key, value)


def _fixed(call: _Call) -> Inference:
    """Type a builtin class's classmethod whose return is fixed, whatever it's given.

    Returns:
      The inference.

    """
    return Inference(_FIXED[call.name], f"`{call.name}`'s fixed return type", frozenset({_KIND}))


# The builtin classes' classmethods and staticmethods whose return type is fixed, as called on the class.
_FIXED: Final = {
    "bytearray.fromhex": "bytearray",
    "bytes.fromhex": "bytes",
    "bytes.maketrans": "bytes",
    "float.fromhex": "float",
    "int.from_bytes": "int",
}


def _iterating(call: _Call) -> Inference | None:
    """Type `enumerate(xs)`, `zip(xs, ys)`, `map(f, xs)` or `reversed(xs)`: the iterator, of what it yields.

    As a loop over it is typed (`call.loop`): `zip[tuple[str, int]]`, `map[str]`; `enumerate[T]` by
    the `T` it counts.

    Returns:
      The inference, or `None` where a loop's target has none, or `zip` takes more than typeshed
      has overloads for.

    """
    if not call.args or (call.name == _ZIP and len(call.args) > _ZIPPED):
        return None
    whole: ast.Call = ast.copy_location(
        ast.Call(
            ast.Name(call.name, ast.Load()),
            [*call.args],
            [ast.keyword(arg=name, value=value) for name, value in call.keywords.items()],
        ),
        call.args[0],
    )
    if iterator_call(whole) is None:  # a keyword that may change what it yields
        return None
    element: Inference | None = call.loop(call.args[0] if call.name == _ENUMERATE else whole)
    if element is None or (call.name == _ENUMERATE and call.loop(whole) is None):
        return None
    return _made(call, f"{call.name}[{element.annotation}]", element)


def _iter(call: _Call) -> Inference | None:
    """Type `iter(xs)`: an `Iterator` of what a loop over `xs` binds.

    Returns:
      The inference, or `None`: with a sentinel, where a loop's target has no type, or where the
      module can't name `Iterator`.

    """
    element: Inference | None = None if call.keywords or len(call.args) != 1 else call.loop(call.args[0])
    spelled: str | None = None if element is None or call.plan is None else call.plan.spell(_ITERATOR)
    return (
        None
        if element is None or spelled is None
        else _made(call, f"{spelled}[{element.annotation}]", element)
    )


_CALLS: Final[Mapping[str, _Rule]] = {
    "abs": _abs,
    **dict.fromkeys(("enumerate", "map", "reversed", "zip"), _iterating),
    "dict": _dict,
    "dict.fromkeys": _fromkeys,
    "divmod": _divmod,
    "iter": _iter,
    "max": _extreme,
    "min": _extreme,
    "next": _next,
    "round": _round,
    "sum": _sum,
    **dict.fromkeys(_FIXED, _fixed),
}


def decides(func: ast.expr, known: Known) -> bool:
    """Check whether `func` is a builtin, or a builtin class's method, this module types the calls of.

    Returns:
      Whether it is, and the module doesn't bind the name itself.

    """
    spelled: str | None = dotted(func)
    return spelled is not None and spelled in _CALLS and known.is_builtin(spelled.partition(".")[0])


def builtin(value: ast.expr, known: Known, infer: Infer, loop: Infer) -> Inference | None:
    """Infer a call to a builtin its arguments' types decide (see the module docstring).

    Returns:
      The inference, or `None` for any other call, one that unpacks its arguments, a module that
      binds the name itself, or arguments that don't decide it.

    """
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match value:
        case ast.Call(func=func, args=args, keywords=keywords) if (
            decides(func, known)
            and not any(isinstance(arg, ast.Starred) for arg in args)
            and all(keyword.arg for keyword in keywords)
        ):
            named: dict[str, ast.expr] = {keyword.arg or "": keyword.value for keyword in keywords}
            name: str = ast.unparse(func)
            return _CALLS[name](_Call(name, args, named, infer, loop, known.names.plan))
        case _:
            return None


def unary(value: ast.UnaryOp, infer: Infer) -> Inference | None:
    """Infer `-x` and `+x` of a builtin number (its own type, a `bool`'s an `int`), and `~n` of an `int`.

    Not `not x`, a `bool` whatever `x` is.

    Returns:
      The inference, or `None` for any other operand.

    """
    found: Inference | None = infer(value.operand)
    signed: bool = isinstance(value.op, ast.USub | ast.UAdd)
    if found is None or found.annotation not in (_REALS | {_COMPLEX} if signed else _INTEGERS):
        return None
    return Inference(
        _INT if found.annotation in _INTEGERS else found.annotation,
        "arithmetic on builtin types",
        found.kinds | {"arithmetic"},
    )
