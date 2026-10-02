# SPDX-License-Identifier: MIT
"""A module's own tables `--fix` reads, read once for the cross-file index and the check."""

import ast
from collections import Counter
from collections.abc import Mapping
from typing import NamedTuple

from constricter.fix.imports import taken_names
from constricter.rules import walked
from constricter.rules.annotations import (
    class_methods,
    classes,
    held,
    held_class_methods,
    method_returns,
    returns,
)
from constricter.rules.decorators import Held, Pass, passes


class Tables(NamedTuple):
    """A module's own tables (see `returns`, `classes`, `method_returns`, `class_methods`).

    Its functions' declared returns, and its classes' attributes and methods' returns; `held`, the
    functions other modules' decorators may give back, and `passes`, its own such decorators;
    `sides`, its classes' classmethods' and staticmethods' returns, and `held_sides`, those other
    modules' decorators may give back; `side_calls`, `sides` as called on the class (see `_side_calls`).
    """

    returns: dict[str, str]
    classes: dict[str, dict[str, str]]
    methods: dict[str, dict[str, str]]
    held: dict[str, Held]
    passes: dict[str, Pass]
    sides: dict[str, dict[str, str]]
    held_sides: dict[str, dict[str, Held]]
    side_calls: dict[str, str]


def module_tables(tree: ast.Module) -> Tables:
    """Read the module's own tables, once for the cross-file index and the check (see `parsed.keep`).

    Returns:
      Them.

    """
    sides: dict[str, dict[str, str]] = class_methods(tree)
    return Tables(
        returns(tree),
        classes(tree),
        method_returns(tree),
        held(tree),
        passes(tree),
        sides,
        held_class_methods(tree),
        _side_calls(tree, sides),
    )


def _side_calls(tree: ast.Module, sides: Mapping[str, Mapping[str, str]]) -> dict[str, str]:
    """Spell the calls to the module's classes' classmethods and staticmethods on the class itself.

    `Box.make()`, for a top-level class defined once whose name nothing in the module binds as a
    value (see `imports.taken_names`): there, the name is the class.

    Returns:
      Each call's name as written (`Box.make`), and its declared return.

    """
    values: frozenset[str] = taken_names(tree)[1]
    counts: Counter[str] = Counter(node.name for node in walked.classes(tree))
    return {
        f"{stmt.name}.{name}": annotation
        for stmt in tree.body
        if isinstance(stmt, ast.ClassDef) and counts[stmt.name] == 1 and stmt.name not in values
        for name, annotation in sides.get(stmt.name, {}).items()
    }
