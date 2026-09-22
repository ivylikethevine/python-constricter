"""The rule as a flake8 plugin, registered under the `LVA` prefix by the package's
`flake8.extension` entry point. flake8 handles `# noqa`, `--select` and `--per-file-ignores`."""

import ast
from collections.abc import Iterator

from constricter import __version__
from constricter.checker import CODE, check_tree


class ConstricterChecker:
    name: str = "constricter"
    version: str = __version__

    def __init__(self, tree: ast.Module) -> None:
        self.tree: ast.Module = tree

    def run(self) -> Iterator[tuple[int, int, str, type["ConstricterChecker"]]]:
        for o in check_tree(self.tree):
            yield o.line, o.col, f"{CODE} {o.message}", type(self)
