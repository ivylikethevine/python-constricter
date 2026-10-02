# SPDX-License-Identifier: MIT
"""What a finished function's scope says its `return`s, `yield`s and `self.x = value`s give.

Recorded for `constricter.fix.returned`, which types the function's calls and its class's attributes
from them.
"""

import ast
from typing import Final

from constricter.fix import returned
from constricter.fix.inference import RETURNED, inference, looped
from constricter.fix.known import ImportPlan, Inference
from constricter.fix.targets import iterated
from constricter.rules.scope import Scope, guesses_in
from constricter.rules.syntax import FunctionDef, own_nodes
from constricter.rules.walked import walk

_GENERATOR: Final = "collections.abc.Generator"


def returns(scope: Scope, func: FunctionDef, module: ast.Module) -> list[returned.Recorded]:
    """Record a finished function's `return` statements; a generator's one type instead (see `_generator`).

    `module`: the function's, whose `yield`s say which functions to look in for one.

    Returns:
      Each one's value.

    """
    if isinstance(func, ast.FunctionDef) and returned.is_generator(module, func):
        return _generator(scope, func)
    return [
        (None, frozenset()) if value is None else _recorded(scope, value) for value in scope.inferred.returns
    ]


def assigned(scope: Scope) -> list[returned.Assigned]:
    """Record a finished function's `self.x = value` assignments, each value as a `return`'s is.

    But a value reading a local bound more than once is unknown: the scope's type for it is its last
    binding's, not what reaches the assignment (`x = None`, `if c: x = 1`, then `self.x = x`).

    Returns:
      Each attribute, and its value's inference and guesses.

    """
    return [
        (attr, (None, frozenset()) if _rebound_in(scope, value) else _recorded(scope, value))
        for attr, value in scope.inferred.assigned
    ]


def _recorded(scope: Scope, value: ast.expr) -> returned.Recorded:
    """Record a value as its finished function's scope sees it.

    Returns:
      Its inference (`None` for an unknown value), and what that rests on if it's a guess.

    """
    found: Inference | None = inference(value, scope.settings.known, scope.inferred.types)
    # What it rests on counts only for a typed value (see `returned`).
    return found, frozenset() if found is None else guesses_in(scope, [value])[1]


def _generator(scope: Scope, func: ast.FunctionDef) -> list[returned.Recorded]:
    """Record what calling a generator function gives, if its `yield`s decide it.

    Each a statement of its own (nothing is sent in), all of one type `T`, and no `return` of a
    value: a `Generator[T, None, None]`, named as the module can.

    Returns:
      That type, as a lone `return`'s value; or nothing.

    """
    nodes: list[ast.AST] = list(own_nodes(func.body))
    statements: set[int] = {id(node.value) for node in nodes if isinstance(node, ast.Expr)}
    yields: list[ast.Yield | ast.YieldFrom] = [
        node for node in nodes if isinstance(node, ast.Yield | ast.YieldFrom)
    ]
    if any(value is not None for value in scope.inferred.returns) or any(
        id(node) not in statements for node in yields
    ):
        return []
    found: list[returned.Recorded] = [_yielded(scope, node) for node in yields]
    types: set[str | None] = {None if part is None else part.annotation for part, _ in found}
    element: str | None = next(iter(types)) if len(types) == 1 else None
    plan: ImportPlan | None = scope.settings.known.names.plan
    spelled: str | None
    if (spelled := None if plan is None or element is None else plan.spell(_GENERATOR)) is None:
        return []
    typed: Inference = Inference(f"{spelled}[{element}, None, None]", "its `yield`s", frozenset({RETURNED}))
    return [(typed, frozenset[str]().union(*(origins for _, origins in found)))]


def _yielded(scope: Scope, node: ast.Yield | ast.YieldFrom) -> returned.Recorded:
    """Record what one `yield` gives: its value, or (`yield from`) each element of it.

    Unknown for a bare `yield`, and a value reading a local bound more than once (see `assigned`).

    Returns:
      Its inference, and what that rests on if it's a guess.

    """
    value: ast.expr | None = node.value
    if value is None or _rebound_in(scope, value):
        return None, frozenset()
    if isinstance(node, ast.Yield):
        return _recorded(scope, value)
    found: Inference | None = looped(value, scope.settings.known, scope.inferred.types)
    return found, frozenset() if found is None else guesses_in(scope, iterated(value))[1]


def _rebound_in(scope: Scope, value: ast.expr) -> bool:
    """Check whether `value` reads a local of `scope` bound more than once.

    Returns:
      Whether it does.

    """
    return any(
        isinstance(node, ast.Name) and node.id in scope.flow and len(scope.flow[node.id].bindings) > 1
        for node in walk(value)
    )
