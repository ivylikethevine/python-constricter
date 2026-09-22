# SPDX-License-Identifier: MIT
"""The rules as a flake8 plugin (`LVA` prefix); reports the codes the level makes errors."""

import argparse
import ast
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, ClassVar, Final, cast, final

from constricter import __version__
from constricter.offences import LEVELS, MAX_LENGTH, NESTING, Checks, Level, Offence
from constricter.rules.checker import check_source, check_tree
from constricter.rules.flow import Narrower, parse_narrower

if TYPE_CHECKING:
    from flake8.options.manager import OptionManager

_TYPE_COMMENT: Final = "type:"


@final
class ConstricterChecker:
    """flake8's checker: one instance per file."""

    name: str = "constricter"
    version: str = __version__
    level: ClassVar[Level] = Level.STRICT
    type_comments: ClassVar[bool] = False
    all_scopes: ClassVar[bool] = False
    nesting: ClassVar[int] = NESTING
    max_length: ClassVar[int] = MAX_LENGTH
    narrower: ClassVar[tuple[Narrower, ...]] = ()

    def __init__(self, tree: ast.Module, lines: Sequence[str]) -> None:
        """Take the file flake8 parsed, and its lines."""
        self.tree: ast.Module = tree
        self.lines: Sequence[str] = lines

    @classmethod
    def add_options(cls, parser: "OptionManager") -> None:
        """Register the options (flake8's plugin hook)."""
        parser.add_option(
            "--constricter-level",
            choices=list(LEVELS),
            default="strict",
            parse_from_config=True,
            help="which LVA codes are reported (default: strict)",
        )
        parser.add_option(
            "--constricter-type-comments",
            action="store_true",
            parse_from_config=True,
            help="count `x = 1  # type: int` as annotated",
        )
        parser.add_option(
            "--constricter-all-scopes",
            action="store_true",
            parse_from_config=True,
            help="also check module and class bodies (LVA004)",
        )
        parser.add_option(
            "--constricter-nesting",
            type=int,
            default=NESTING,
            parse_from_config=True,
            help=f"report an annotation nested this deep (LVA006; default: {NESTING})",
        )
        parser.add_option(
            "--constricter-max-length",
            type=int,
            default=MAX_LENGTH,
            parse_from_config=True,
            help=f"report a fixed-length tuple annotation listing more types (LVA011; default: {MAX_LENGTH})",
        )
        parser.add_option(
            "--constricter-narrower",
            default="",
            parse_from_config=True,
            help="your own type hierarchy for LVA008-LVA010, as `B=A, C=A, int=` (B is narrower than A)",
        )

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        """Read the parsed options (flake8's plugin hook)."""
        cls.level = LEVELS[cast("str", options.constricter_level)]
        cls.type_comments = cast("bool", options.constricter_type_comments)
        cls.all_scopes = cast("bool", options.constricter_all_scopes)
        cls.nesting = cast("int", options.constricter_nesting)
        cls.max_length = cast("int", options.constricter_max_length)
        cls.narrower = parse_narrower(cast("str", options.constricter_narrower))

    def run(self) -> Iterator[tuple[int, int, str, type["ConstricterChecker"]]]:
        """Check the file.

        Yields:
          flake8's `(line, col, message, type)` per error-level offence.

        """
        source: str = "".join(self.lines)
        # flake8's tree has no `# type:` comments; reparse only when the file might have one.
        checks: Checks = Checks(
            type_comments=self.type_comments,
            all_scopes=self.all_scopes,
            nesting=self.nesting,
            max_length=self.max_length,
            narrower=self.narrower,
        )
        offences: list[Offence] = (
            check_source(source, checks=checks)
            if _TYPE_COMMENT in source
            else check_tree(self.tree, checks, lines=self.lines)
        )
        o: Offence
        for o in offences:
            if o.is_error(self.level):
                yield o.line, o.col, f"{o.code} {o.message}", type(self)
