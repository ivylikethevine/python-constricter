# SPDX-License-Identifier: MIT
"""A module's own tables `--fix` reads, read once for the cross-file index and the check."""

import ast
from collections import Counter
from collections.abc import Mapping
from typing import NamedTuple

from constricter.fix.imports import taken_names
from constricter.fix.inherited import Lineage, lineage
from constricter.fix.targets import named_tuples
from constricter.rules import walked
from constricter.rules.annotations import (
    class_methods,
    classes,
    held,
    held_class_methods,
    method_returns,
    partial_method_returns,
    partial_returns,
    returns,
    self_returns,
)
from constricter.rules.decorators import Held, Pass, passes


class Tables(NamedTuple):
    """A module's own tables (see `returns`, `classes`, `method_returns`, `class_methods`).

    Its functions' declared returns, and its classes' attributes and methods' returns (their
    classmethods' and staticmethods' too, which an instance has as well); `held`, the functions other
    modules' decorators may give back, and `passes`, its own such decorators; `sides`, its classes'
    classmethods' and staticmethods' returns, those each takes from the module's other classes
    included (see `Lineage`), and `held_sides`, those other modules' decorators may give back;
    `side_calls`, `sides` as called on the class (see `_side_calls`). `partial` and
    `partial_methods`: its functions' and methods' returns that are tuples with a vague part.
    `tuples`: its named tuples, each with the tuple unpacking one gives (see `named_tuples`).
    """

    returns: dict[str, str]
    classes: dict[str, dict[str, str]]
    methods: dict[str, dict[str, str]]
    held: dict[str, Held]
    passes: dict[str, Pass]
    sides: dict[str, dict[str, str]]
    held_sides: dict[str, dict[str, Held]]
    side_calls: dict[str, str]
    partial: dict[str, str]
    partial_methods: dict[str, dict[str, str]]
    order: Lineage  # its classes' ancestry, as far as the module alone sees
    tuples: dict[str, str]


def module_tables(tree: ast.Module) -> Tables:
    """Read the module's own tables, once for the cross-file index and the check (see `parsed.keep`).

    Returns:
      Them.

    """
    own: dict[str, dict[str, str]] = class_methods(tree)
    order: Lineage = lineage(tree, self_returns(tree), frozenset())
    sides: dict[str, dict[str, str]] = order.flattened(own)
    return Tables(
        returns(tree),
        classes(tree),
        {owner: {**own.get(owner, {}), **methods} for owner, methods in method_returns(tree).items()},
        held(tree),
        passes(tree),
        sides,
        held_class_methods(tree),
        _side_calls(tree, sides),
        partial_returns(tree),
        partial_method_returns(tree),
        order,
        named_tuples(tree),
    )


def _side_calls(tree: ast.Module, sides: Mapping[str, Mapping[str, str]]) -> dict[str, str]:
    """Spell the calls to the module's classes' classmethods and staticmethods on the class itself.

    `Box.make()`, for a top-level class defined once whose name nothing in the module binds as a
    value (see `imports.taken_names`): there, the name is the class.

    Returns:
      Each call's name as written (`Box.make`), and its declared return.

    """
    if not any(sides.values()):  # most modules: no class-side method declares a return
        return {}
    values: frozenset[str] = taken_names(tree)[1]
    counts: Counter[str] = Counter(node.name for node in walked.classes(tree))
    return {
        f"{stmt.name}.{name}": annotation
        for stmt in tree.body
        if isinstance(stmt, ast.ClassDef) and counts[stmt.name] == 1 and stmt.name not in values
        for name, annotation in sides.get(stmt.name, {}).items()
    }
