# SPDX-License-Identifier: MIT
"""A module's own tables `--fix` reads, read once for the cross-file index and the check."""

import ast
from typing import NamedTuple

from constricter.rules.annotations import classes, held, method_returns, returns
from constricter.rules.decorators import Held, Pass, passes


class Tables(NamedTuple):
    """A module's own tables (see `returns`, `classes`, `method_returns`).

    Its functions' declared returns, and its classes' attributes and methods' returns; `held`, the
    functions other modules' decorators may give back, and `passes`, its own such decorators.
    """

    returns: dict[str, str]
    classes: dict[str, dict[str, str]]
    methods: dict[str, dict[str, str]]
    held: dict[str, Held]
    passes: dict[str, Pass]


def module_tables(tree: ast.Module) -> Tables:
    """Read the module's own tables, once for the cross-file index and the check (see `parsed.keep`).

    Returns:
      Them.

    """
    return Tables(returns(tree), classes(tree), method_returns(tree), held(tree), passes(tree))
