"""The rules as a flake8 plugin (`LVA` prefix); reports the codes the level makes errors."""

import argparse
import ast
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, ClassVar, Final, cast, final

from constricter import __version__
from constricter.offences import (
    CAN_BE_FINAL,
    LEVELS,
    MAX_LENGTH,
    NESTING,
    UNANNOTATED_ATTRIBUTE,
    UNANNOTATED_RETURN,
    VAGUE,
    Checks,
    Level,
    Offence,
)
from constricter.plugins import options as table
from constricter.plugins.options import CHOICES, LEVEL, OPTIONS, WHOLE, Option
from constricter.rules.checker import check_source, check_tree
from constricter.source.flow import Narrower, parse_narrower

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
    vague: ClassVar[int] = VAGUE
    narrower: ClassVar[tuple[Narrower, ...]] = ()
    can_be_final: ClassVar[bool] = False  # report LVA012
    attributes: ClassVar[bool] = False  # report LVA013
    returns: ClassVar[bool] = False  # report LVA014

    def __init__(self, tree: ast.Module, lines: Sequence[str]) -> None:
        """Take the file flake8 parsed, and its lines."""
        self.tree: ast.Module = tree
        self.lines: Sequence[str] = lines

    @classmethod
    def add_options(cls, parser: "OptionManager") -> None:
        """Register the options (flake8's plugin hook)."""
        option: Option
        for option in OPTIONS:
            _added(parser, option)

    @classmethod
    def parse_options(cls, options: argparse.Namespace) -> None:
        """Read the parsed options (flake8's plugin hook)."""
        cls.level = LEVELS[cast("str", options.constricter_level)]
        cls.type_comments = cast("bool", options.constricter_type_comments)
        cls.all_scopes = cast("bool", options.constricter_all_scopes)
        cls.nesting = cast("int", options.constricter_nesting)
        cls.max_length = cast("int", options.constricter_max_length)
        cls.vague = cast("int", options.constricter_vague)
        cls.narrower = parse_narrower(cast("str", options.constricter_narrower))
        # An opt-in code only when `select` or `extend-select` names it in full, as the CLI does.
        chosen: list[str] = [
            *(cast("list[str] | None", getattr(options, "select", None)) or []),
            *(cast("list[str] | None", getattr(options, "extend_select", None)) or []),
        ]
        cls.can_be_final = CAN_BE_FINAL in chosen
        cls.attributes = UNANNOTATED_ATTRIBUTE in chosen
        cls.returns = UNANNOTATED_RETURN in chosen

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
            vague=self.vague,
            narrower=self.narrower,
            final=self.can_be_final,
            attributes=self.attributes,
            returns=self.returns,
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


def _added(parser: "OptionManager", option: Option) -> None:
    """Register one of the plugins' options (see `options.OPTIONS`) with flake8."""
    flag: str = f"--constricter-{option.name}"
    said: str = f"{option.help} (default: {option.default})" if option.kind in {LEVEL, WHOLE} else option.help
    match option.kind:
        case table.LEVEL:
            parser.add_option(
                flag,
                choices=CHOICES,
                default=option.default,
                parse_from_config=True,
                help=said,
            )
        case table.FLAG:
            parser.add_option(flag, action="store_true", parse_from_config=True, help=said)
        case table.WHOLE:
            parser.add_option(flag, type=int, default=option.default, parse_from_config=True, help=said)
        case _:
            parser.add_option(flag, default=option.default, parse_from_config=True, help=said)
