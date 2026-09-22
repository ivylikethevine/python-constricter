# SPDX-License-Identifier: MIT
"""The rule as a flake8 plugin (`LVA` prefix)."""

import argparse
import ast
from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar, cast, final

from constricter import __version__
from constricter.checker import CODE, check_tree

if TYPE_CHECKING:
    from flake8.options.manager import OptionManager


@final
class ConstricterChecker:
    """flake8's checker: one instance per file."""

    name: str = "constricter"
    version: str = __version__
    type_comments: ClassVar[bool] = False

    def __init__(self, tree: ast.Module, lines: list[str]) -> None:
        """Take the file flake8 parsed, and its lines."""
        self.tree: ast.Module = tree
        self.lines: list[str] = lines

    @classmethod
    def add_options(cls, parser: "OptionManager") -> None:
        """Register `--constricter-type-comments` (flake8's plugin hook)."""
        parser.add_option(
            "--constricter-type-comments",
            action="store_true",
            parse_from_config=True,
            help="count `x = 1  # type: int` as annotated",
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        """Read the parsed options (flake8's plugin hook)."""
        cls.type_comments = cast("bool", options.constricter_type_comments)

    def run(self) -> Iterator[tuple[int, int, str, type["ConstricterChecker"]]]:
        """Yield flake8's `(line, col, message, type)` per offence."""
        tree: ast.Module = (
            ast.parse("".join(self.lines), type_comments=True) if self.type_comments else self.tree
        )
        for o in check_tree(tree):
            yield o.line, o.col, f"{CODE} {o.message}", type(self)
