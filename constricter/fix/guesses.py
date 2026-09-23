# SPDX-License-Identifier: MIT
"""Which of `--fix`'s inferences are guesses (`--unsafe-fixes`), and what each rests on."""

import ast
from collections.abc import Iterator, Mapping

from constricter.fix import stdlib
from constricter.fix.inference import (
    COMPREHENSIONS,
    CONTAINER_BUILDERS,
    RETURNED,
    dict_view,
    library_class,
    targets_typed,
    typed_method,
)
from constricter.fix.known import Known
from constricter.fix.opened import opened
from constricter.fix.returns import BUILTIN_RETURNS
from constricter.fix.targets import DICT_VIEWS, ITERATORS
from constricter.offences import CONSTRUCTOR


def guessed(
    value: ast.expr,
    known: Known,
    guesses: frozenset[str],
    declared: Mapping[str, str],
) -> bool:
    """Whether `inferred`'s annotation for `value` is a guess (`--unsafe-fixes`): it calls a class.

    A capitalised call may construct a generic class (`Box(1)` is really `Box[int]`) or be a factory
    function; literals, calls to a module function, a fixed-return builtin (`len`, `isinstance`,
    ...) or a method `method_return` resolves on an already-typed local, and
    another local this scope already typed, are certain. Copying a local `inferred` itself only
    guessed (`guesses`) is no more certain than the guess it copies.

    Returns:
      Whether any call in `value` is to something other than such a certain callee, or any name in
      it copies such a guess.

    """
    walked: list[ast.AST] = list(_deciding(value, known))
    inside: Mapping[str, str] = targets_typed(
        [node for node in walked if isinstance(node, COMPREHENSIONS)],
        known,
        declared,
    )
    return any(_is_guess(node, known, guesses, inside) for node in walked)


def _deciding(value: ast.AST, known: Known) -> Iterator[ast.AST]:
    """Walk what decides `value`'s type: all of it, but not the arguments of a call they can't change.

    `open(path, "rb")` is a file object by its mode, `logging.getLogger(name)` a `Logger`, whatever
    `path` or `name` are: a guess there doesn't make the call's type one.

    Yields:
      Each node.

    """
    # A stack, not a recursion: a nested generator passes each node up through every level above it.
    waiting: list[ast.AST | None] = [None, value]  # `None` at its bottom ends it
    node: ast.AST
    for node in iter(waiting.pop, None):
        yield node
        if not (isinstance(node, ast.Call) and (opened(node, known) or library_class(node, known))):
            waiting.extend(reversed(list(ast.iter_child_nodes(node))))


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
    walked: list[ast.AST] = list(_deciding(value, known))
    inside: Mapping[str, str] = targets_typed(
        [node for node in walked if isinstance(node, COMPREHENSIONS)],
        known,
        declared,
    )
    unsafe: bool = False
    found: set[str] = set()
    node: ast.AST
    for node in walked:
        if _is_guess(node, known, guesses, inside):
            unsafe = True
            if isinstance(node, ast.Call):
                found.update(_guessed_by(node, known, inside))
        if isinstance(node, ast.Name) and node.id in origins:
            found.update(origins[node.id])
    return unsafe, frozenset(found) if unsafe else frozenset()


def _guessed_by(call: ast.Call, known: Known, declared: Mapping[str, str]) -> frozenset[str]:
    """Name what makes one guessed call a guess.

    Returns:
      A method typed by its `return`s: `returned`, and what those rest on; a function whose
      `return`s are guesses: what they rest on; anything else: `constructor`.

    """
    name: str
    receiver: str
    method: str
    match call:
        case ast.Call(func=ast.Name(id=name)) if name in known.returned.guesses:
            return known.returned.guesses[name]
        case ast.Call(func=ast.Attribute(value=ast.Name(id=receiver), attr=method)) if _returned_method(
            call,
            known,
            declared,
        ):
            return frozenset({RETURNED}) | known.returned.guesses.get(
                f"{declared[receiver]}.{method}",
                frozenset(),
            )
        case _:
            return frozenset({CONSTRUCTOR})


def _returned_method(call: ast.Call, known: Known, declared: Mapping[str, str]) -> bool:
    """Check whether `call` is a method typed only by its `return`s (see `Returned`).

    Returns:
      Whether it is.

    """
    receiver: str
    method: str
    match call:
        case ast.Call(func=ast.Attribute(value=ast.Name(id=receiver), attr=method)) if receiver in declared:
            return method in known.returned.methods.get(declared[receiver], {})
        case _:
            return False


def _is_guess(
    node: ast.AST,
    known: Known,
    guesses: frozenset[str],
    declared: Mapping[str, str],
) -> bool:
    name: str
    func: ast.expr
    receiver: str
    method: str
    call: ast.Call
    owner: ast.Name
    match node:
        case ast.Call(func=ast.Name(id=name)) if (
            name in BUILTIN_RETURNS
            or name in CONTAINER_BUILDERS
            or name in ITERATORS
            or name in known.awaits
            or (name in known.returned.calls and name not in known.returned.guesses)
        ):
            return False
        case ast.Call(func=func) if (
            ast.unparse(func) in known.names.casts
            or stdlib.resolved(func, known.names.stdlib) in stdlib.KNOWN
            or opened(node, known) is not None
        ):
            return False
        case ast.Call(func=ast.Attribute(value=ast.Name(id=receiver) as owner, attr=method)) as call if (
            receiver in declared
            and (
                typed_method(declared[receiver], call, method, known) is not None
                or (method in DICT_VIEWS and dict_view(owner, method, known, declared) is not None)
            )
        ):
            return False
        case ast.Call(func=func):
            return ast.unparse(func) not in known.calls
        case ast.Name(id=name):
            return name in guesses
        case _:
            return False
