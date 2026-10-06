# SPDX-License-Identifier: MIT
"""Which of `--fix`'s inferences are guesses (`--unsafe-fixes`), and what each rests on."""

import ast
from collections.abc import Iterator, Mapping
from typing import Final

from constricter.fix.core.known import Known
from constricter.fix.libraries import stdlib
from constricter.fix.libraries.library import installed_method, library_class
from constricter.fix.libraries.opened import opened
from constricter.fix.values import called, decided, displays, shapes
from constricter.fix.values.inference import (
    COMPREHENSIONS,
    CONTAINER_BUILDERS,
    RETURNED,
    dict_view,
    inference,
    inferred,
    joined,
    scalar,
    targets_typed,
)
from constricter.fix.values.members import assigned_attribute, class_variable, member, returned_method
from constricter.fix.values.returns import BUILTIN_RETURNS
from constricter.fix.values.targets import DICT_VIEWS, ITERATORS
from constricter.offences import CONSTRUCTOR, MEMBER
from constricter.rules.annotations import dotted
from constricter.rules.walked import children

# Builtins whose call is certain (when the module doesn't rebind the name): see `_is_guess`.
_CERTAIN_BUILTINS: Final = frozenset(
    BUILTIN_RETURNS.keys() | CONTAINER_BUILDERS.keys() | ITERATORS | {"type", "getattr"},
)


def guessed(
    value: ast.expr,
    known: Known,
    guesses: frozenset[str],
    declared: Mapping[str, str],
) -> bool:
    """Whether `inferred`'s annotation for `value` is a guess (`--unsafe-fixes`): it calls a class.

    A capitalised call may construct a generic class (`Box(1)` is really `Box[int]`) or be a factory
    function; literals, calls to a module function, a fixed-return builtin (`len`, `isinstance`,
    ...) or a method `members.member` types on a value whose type is known, and another local this
    scope already typed, are certain. Copying a local `inferred` itself only
    guessed (`guesses`) is no more certain than the guess it copies, unless the value's type is the
    same without it (see `_rests`).

    Returns:
      Whether any call in `value` is to something other than such a certain callee, or its type
      rests on a name in it that copies such a guess.

    """
    return guessing(value, known, guesses, {}, declared)[0]


def _deciding(value: ast.AST, known: Known, declared: Mapping[str, str]) -> Iterator[ast.AST]:
    """Walk what decides `value`'s type: all of it, but not the arguments of a call they can't change.

    `open(path, "rb")` is a file object by its mode, `logging.getLogger(name)` a `Logger`, whatever
    `path` or `name` are: a guess there doesn't make the call's type one; nor in `x.kind is None`, a
    `bool` whatever `x.kind` is, or an f-string. Nor does it in a call to a
    fixed-return builtin (`len(Box())`), a function declaring its return, or a method a certain
    source types (`"{}".format(Box())`, `self.items.get(key())`), though its receiver still counts.

    Yields:
      Each node.

    """
    # A stack, not a recursion: a nested generator passes each node up through every level above it.
    waiting: list[ast.AST | None] = [None, value]  # `None` at its bottom ends it
    node: ast.AST
    for node in iter(waiting.pop, None):
        yield node
        if isinstance(node, ast.expr) and scalar(node) is not None:
            continue
        if isinstance(node, ast.Call) and (opened(node, known) or library_class(node, known)):
            continue
        if isinstance(node, ast.Call) and _fixed_by_callee(node, known, declared):
            waiting.append(node.func)
        else:
            waiting.extend(reversed(children(node)))


def _fixed_by_callee(call: ast.Call, known: Known, declared: Mapping[str, str]) -> bool:
    """Check whether `call`'s type is its callee's alone, whatever its arguments are.

    Returns:
      Whether it is: a fixed-return builtin the module doesn't rebind, a function declaring its
      return (`Known.calls`), or a method a certain source types (see `certain_method`).

    """
    name: str
    func: ast.expr
    match call:
        case ast.Call(func=ast.Name(id=name)) if name in BUILTIN_RETURNS and known.is_builtin(name):
            return True
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (
            dotted(func) in known.calls or dotted(func) in known.indirect.partial.calls
        ):
            return True
        case _:
            return certain_method(call, known, declared)


def guessing(
    value: ast.expr,
    known: Known,
    guesses: frozenset[str],
    origins: Mapping[str, frozenset[str]],
    declared: Mapping[str, str],
) -> tuple[bool, frozenset[str]]:
    """Work out, in one pass, whether `value`'s type is a guess (see `guessed`), and what it rests on.

    `origins` holds what each guessed local (of `guesses`) rests on.

    Returns:
      Whether it's a guess; and if it is, its guessing mechanisms (`FIX_KINDS`): `returned` for a
      method typed only by its `return`s, `constructor` for any other guessed call, and each guessed
      local's own.

    """
    # One walk, for both: the comprehensions whose targets the rest may use, then each node.
    walked: list[ast.AST] = list(_deciding(value, known, declared))
    inside: Mapping[str, str] = targets_typed(
        [node for node in walked if isinstance(node, COMPREHENSIONS)],
        known,
        declared,
    )
    unsafe: bool = False
    named: bool = True  # only names are guesses, so far
    found: set[str] = set()
    node: ast.AST
    for node in walked:
        if joined(node, known, declared):
            unsafe, named = True, False
            found.add(displays.JOINED)
        if _is_guess(node, known, guesses, inside):
            unsafe = True
            named = named and isinstance(node, ast.Name)
            if isinstance(node, ast.Call):
                found.update(_guessed_by(node, known, inside))
            elif isinstance(node, ast.Attribute):
                found.update(_assigned_origins(node, known, inside) or ())
        if isinstance(node, ast.Name) and node.id in origins:
            found.update(origins[node.id])
    if not unsafe or (named and not _rests(value, known, guesses, declared)):
        return False, frozenset()
    return True, frozenset(found)


def _rests(value: ast.expr, known: Known, guesses: frozenset[str], declared: Mapping[str, str]) -> bool:
    """Check whether `value`'s type rests on the guessed names in it.

    `os.path.join(root, "x")` is a `str` by its literal, whatever `root` is: a guessed `root` doesn't
    make it a guess.

    Returns:
      Whether it has another type, or none, with those names' types unknown.

    """
    sure: dict[str, str] = {name: text for name, text in declared.items() if name not in guesses}
    return inferred(value, known, sure) != inferred(value, known, declared)


def certain_method(call: ast.expr, known: Known, declared: Mapping[str, str]) -> bool:
    """Check whether `call` is a method call a certain source types on its receiver's type.

    A member `members.member` knows, or a `dict`'s `.keys()`, `.values()` or `.items()`; its
    arguments can't change it (the receiver itself may still be a guess).

    Returns:
      Whether it is.

    """
    receiver: ast.expr
    method: str
    match call:
        case ast.Call(func=ast.Attribute(value=receiver, attr=method)):
            typed: str | None = inferred(receiver, known, declared)
            return typed is not None and (
                member(typed, method, call, known) is not None
                or (method in DICT_VIEWS and dict_view(receiver, method, known, declared) is not None)
            )
        case _:
            return False


def _overloaded_method(call: ast.Call, known: Known, declared: Mapping[str, str]) -> bool:
    """Check whether `call` calls a method its arguments type: the standard library's, or `dict.get`.

    See `stdlib.overloaded_method` and `shapes.defaulted`. Its arguments are walked as its parts: a
    guessed one makes it a guess.

    Returns:
      Whether it does.

    """
    receiver: ast.expr
    method: str
    match call:
        case ast.Call(func=ast.Attribute(value=receiver, attr=method)):
            typed: str | None = inferred(receiver, known, declared)
            base: str = known.class_side.lineage.definer(typed or "", method) or typed or ""
            return typed is not None and (
                stdlib.overloaded_method(typed, method, known) is not None
                or stdlib.overloaded_method(base, method, known) is not None  # a library base's
                or installed_method(typed, method, known) is not None
                or shapes.defaulted(typed, call, lambda arg: inference(arg, known, declared)) is not None
            )
        case _:
            return False


def _guessed_by(call: ast.Call, known: Known, declared: Mapping[str, str]) -> frozenset[str]:
    """Name what makes one guessed call a guess.

    Returns:
      A method typed by its `return`s: `returned`, and what those rest on; a function whose
      `return`s are guesses: what they rest on; anything else: `constructor`.

    """
    func: ast.expr
    callee: str | None
    receiver: ast.expr
    method: str
    typed: str | None
    defined: tuple[str, str] | None
    match call:
        case ast.Call(func=ast.Name() | ast.Attribute() as func) if (
            callee := dotted(func)
        ) in known.returned.guesses:
            return known.returned.guesses[callee or ""]
        case ast.Call(func=ast.Attribute(value=receiver, attr=method)) if (
            typed := inferred(receiver, known, declared)
        ) is not None and (defined := returned_method(typed, method, known)) is not None:
            return frozenset({RETURNED}) | known.returned.guesses.get(f"{defined[0]}.{method}", frozenset())
        case _:
            return frozenset({CONSTRUCTOR})


def _assigned_origins(
    node: ast.Attribute,
    known: Known,
    declared: Mapping[str, str],
) -> frozenset[str] | None:
    """Name what an attribute nothing declares rests on: its assignments, or its class's body.

    One typed only by its assignments (see `Returned.attributes`), or a plain class's variable typed
    by its value (see `ClassSide.variables`).

    Returns:
      `assigned`, and what its values' guesses rest on, or `member`; or `None` if it isn't one (a
      certain source types it, or nothing does).

    """
    if not any(
        node.attr in attributes
        for attributes in (*known.returned.attributes.values(), *known.class_side.variables.values())
    ):
        return None  # most attributes: no receiver to type
    typed: str | None = inferred(node.value, known, declared)
    if typed is None or member(typed, node.attr, None, known) is not None:
        return None
    if assigned_attribute(typed, node.attr, known) is not None:
        return known.returned.guesses[f"{typed}.{node.attr}"]
    return None if class_variable(typed, node.attr, known) is None else frozenset({MEMBER})


def _is_guess(
    node: ast.AST,
    known: Known,
    guesses: frozenset[str],
    declared: Mapping[str, str],
) -> bool:
    name: str
    func: ast.expr
    match node:
        case ast.Call(func=ast.Name(id=name)) if (
            name in _CERTAIN_BUILTINS and known.is_builtin(name)
        ) or name in known.indirect.awaits:
            return False
        case ast.Call(func=func) if (
            _returned_certainly(func, known)
            or decided.decides(func, known)
            or dotted(func) in known.names.casts
            or stdlib.resolved(func, known.names.stdlib) in stdlib.KNOWN
            or dotted(func) in known.names.installed
            or opened(node, known) is not None
            or certain_method(node, known, declared)
            or _overloaded_method(node, known, declared)
            or called.result(node, known, declared, lambda arg: inference(arg, known, declared)) is not None
            or shapes.vaguely(node, known, lambda arg: inference(arg, known, declared)) is not None
        ):
            return False
        case ast.Call(func=func):
            return dotted(func) not in known.calls
        case ast.Name(id=name):
            return name in guesses
        case ast.Attribute():
            return _assigned_origins(node, known, declared) is not None
        case _:
            return False


def _returned_certainly(func: ast.expr, known: Known) -> bool:
    """Check whether `func` is an unannotated function (own or imported) certain of its `return`s' type.

    Returns:
      Whether it is.

    """
    callee: str | None = dotted(func)
    return callee in known.returned.calls and callee not in known.returned.guesses
