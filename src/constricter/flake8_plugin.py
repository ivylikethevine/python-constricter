"""The rule as a flake8 plugin (`LVA` prefix)."""

import ast
from collections.abc import Iterator
from typing import final

from constricter import __version__
from constricter.checker import CODE, check_tree


@final
class ConstricterChecker:
    name: str = "constricter"
    version: str = __version__

    def __init__(self, tree: ast.Module) -> None:
        self.tree: ast.Module = tree

    def run(self) -> Iterator[tuple[int, int, str, type["ConstricterChecker"]]]:
        """Yield flake8's `(line, col, message, type)` per offence."""
        for o in check_tree(self.tree):
            yield o.line, o.col, f"{CODE} {o.message}", type(self)
