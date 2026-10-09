# SPDX-License-Identifier: MIT
"""The order a module's functions are checked in: each after those it calls, whose `return`s then type it."""

import ast
from collections.abc import Iterator, Sequence
from typing import TypeAlias

from constricter.fix.values import returned
from constricter.rules.syntax import FunctionDef

# The functions by name: the module's (`[False]`), then the classes' methods (`[True]`).
_Named: TypeAlias = tuple[dict[str, list[FunctionDef]], dict[str, list[FunctionDef]]]
# One function to put in call order, and its callees still to put in before it.
_Visit: TypeAlias = tuple[FunctionDef, Iterator[FunctionDef]]


def in_call_order(module: ast.Module, functions: Sequence[FunctionDef]) -> list[FunctionDef]:
    """Order `functions` so that each comes after the functions it calls (a cycle's, in any order).

    Its callees: the module's functions it calls by name, and every method named as it calls one
    (`x.m()`: any class's `m`), as `called` counts them.

    Returns:
      Them, callees first; otherwise in their own order.

    """
    named: _Named = ({}, {})
    func: FunctionDef
    for func in functions:
        slot: returned.Slot | None
        if (slot := returned.slots(module).get(id(func))) is not None:
            named[slot.owner is not None].setdefault(slot.name, []).append(func)
    ordered: list[FunctionDef] = []
    seen: set[int] = set()
    for func in functions:
        if id(func) not in seen:
            seen.add(id(func))
            _after_callees(module, func, named, (ordered, seen))
    return ordered


def _after_callees(
    module: ast.Module,
    func: FunctionDef,
    named: _Named,
    into: tuple[list[FunctionDef], set[int]],
) -> None:
    """Put `func` in the order after its callees, depth first, with a stack: a call chain can be long."""
    ordered: list[FunctionDef]
    seen: set[int]
    ordered, seen = into
    # Each entry: a function, and its callees still to put in before it; `None` at the bottom ends it.
    waiting: list[_Visit | None] = [None, (func, _callees(module, func, named))]
    entry: _Visit
    for entry in iter(waiting.pop, None):
        callee: FunctionDef | None
        if (callee := next((one for one in entry[1] if id(one) not in seen), None)) is None:
            ordered.append(entry[0])
        else:
            seen.add(id(callee))
            waiting.extend([entry, (callee, _callees(module, callee, named))])


def _callees(module: ast.Module, func: FunctionDef, named: _Named) -> Iterator[FunctionDef]:
    """Find the functions of `named` that `func` calls: the module's by name, methods by attribute.

    Yields:
      Each, in the order of its calls.

    """
    name: str | None
    attr: str | None
    for name, attr in returned.callees_in(module, func):
        yield from named[False].get(name, []) if name is not None else named[True].get(attr or "", [])
