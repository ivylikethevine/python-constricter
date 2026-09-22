# SPDX-License-Identifier: MIT
"""The rules as a pylint plugin (C9101-C9111); reports the codes the level makes errors."""

from typing import IO, TYPE_CHECKING, NamedTuple, cast, final

from astroid import nodes
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from pylint.typing import Options

from constricter.jsonc import as_text
from constricter.noqa import lines, unsuppressed
from constricter.offences import (
    COMMENT_TYPED_TARGET,
    LEVELS,
    LONG_TUPLE,
    MAX_LENGTH,
    MESSAGES,
    MISMATCHED_TYPE,
    NARROWABLE_TYPE,
    NESTED_TYPE,
    NESTING,
    REDUNDANT_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    UNUSED_UNION_MEMBER,
    VAGUE_TYPE,
    Checks,
    Level,
    Offence,
)
from constricter.rules.checker import check_source
from constricter.rules.flow import parse_narrower

if TYPE_CHECKING:
    from typing_extensions import override  # `typing.override` is 3.12+
else:

    def override(func: object) -> object:
        """Mark an override (for type checkers only).

        Returns:
          `func`, unchanged.

        """
        return func


class Message(NamedTuple):
    """A code's pylint message id and symbol."""

    msg_id: str
    symbol: str


SYMBOLS: dict[str, Message] = {
    UNANNOTATED: Message("C9101", "unannotated-local-variable"),
    UNTYPED_TARGET: Message("C9102", "untyped-for-or-match-variable"),
    COMMENT_TYPED_TARGET: Message("C9103", "comment-typed-for-variable"),
    UNANNOTATED_MEMBER: Message("C9104", "unannotated-module-or-class-variable"),
    VAGUE_TYPE: Message("C9105", "vague-annotation"),
    NESTED_TYPE: Message("C9106", "deeply-nested-annotation"),
    REDUNDANT_TYPE: Message("C9107", "redundant-annotation"),
    NARROWABLE_TYPE: Message("C9108", "narrowable-annotation"),
    MISMATCHED_TYPE: Message("C9109", "mismatched-value-type"),
    UNUSED_UNION_MEMBER: Message("C9110", "unused-union-member"),
    LONG_TUPLE: Message("C9111", "long-tuple-annotation"),
}


@final
class ConstricterChecker(BaseRawFileChecker):
    """pylint's checker, run once per module on its raw source."""

    name: str = "constricter"
    options: Options = (
        (
            "constricter-level",
            {
                "default": "strict",
                "type": "choice",
                "choices": list(LEVELS),
                "metavar": "<level>",
                "help": "Which codes are reported.",
            },
        ),
        (
            "constricter-type-comments",
            {"default": False, "type": "yn", "metavar": "<y or n>", "help": "Count `# type:` comments."},
        ),
        (
            "constricter-all-scopes",
            {"default": False, "type": "yn", "metavar": "<y or n>", "help": "Check module and class bodies."},
        ),
        (
            "constricter-nesting",
            {
                "default": NESTING,
                "type": "int",
                "metavar": "<n>",
                "help": "Report an annotation nested this deep.",
            },
        ),
        (
            "constricter-max-length",
            {
                "default": MAX_LENGTH,
                "type": "int",
                "metavar": "<n>",
                "help": "Report a fixed-length tuple annotation listing more than this many types.",
            },
        ),
        (
            "constricter-narrower",
            {
                "default": "",
                "type": "string",
                "metavar": "<B=A, ...>",
                "help": "Your own type hierarchy (LVA008-LVA010): B=A, B narrower than A.",
            },
        ),
    )

    def __init__(self, linter: PyLinter) -> None:
        """Register the messages with `linter`."""
        super().__init__(linter)
        self.msgs = {
            message.msg_id: (
                MESSAGES[code].format(name="%r", detail="%s"),
                message.symbol,
                f"See constricter's {code}.",
            )
            for code, message in SYMBOLS.items()
        }

    @override
    def process_module(self, node: nodes.Module) -> None:
        """Report the module's error-level offences."""
        opened: IO[bytes] | None
        if (opened := node.stream()) is None:  # no file behind the module
            return
        stream: IO[bytes]
        with opened as stream:
            source: bytes = stream.read()
        level: Level = LEVELS[cast("str", self.linter.config.constricter_level)]
        checks: Checks = Checks(
            type_comments=cast("bool", self.linter.config.constricter_type_comments),
            all_scopes=cast("bool", self.linter.config.constricter_all_scopes),
            nesting=cast("int", self.linter.config.constricter_nesting),
            max_length=cast("int", self.linter.config.constricter_max_length),
            narrower=parse_narrower(cast("str", self.linter.config.constricter_narrower)),
        )
        text: str = as_text(source)
        offences: list[Offence] = check_source(text, node.file or "<unknown>", checks)
        o: Offence
        for o in unsuppressed(offences, lines(text)):  # suppression comments, as the CLI reads them
            if o.is_error(level):
                # A message names the variable, then (LVA009's) its `detail`, as `msgs` spells them.
                args: tuple[str, ...] = (o.name, o.detail) if o.detail else (o.name,)
                self.add_message(SYMBOLS[o.code].symbol, line=o.line, col_offset=o.col, args=args)


def register(linter: PyLinter) -> None:
    """Register the checker (pylint's plugin hook)."""
    linter.register_checker(ConstricterChecker(linter))
