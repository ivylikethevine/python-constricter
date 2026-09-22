# SPDX-License-Identifier: MIT
"""The rules as a pylint plugin (C9101-C9107); reports the codes the level makes errors."""

from typing import IO, TYPE_CHECKING, NamedTuple, cast, final

from astroid import nodes
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from pylint.typing import Options

from constricter.checker import (
    COMMENT_TYPED_TARGET,
    LEVELS,
    MESSAGES,
    NESTED_TYPE,
    NESTING,
    REDUNDANT_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    VAGUE_TYPE,
    Checks,
    Level,
    Offence,
    check_source,
)
from constricter.jsonc import as_text
from constricter.noqa import lines, unsuppressed

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
    )

    def __init__(self, linter: PyLinter) -> None:
        """Register the messages with `linter`."""
        super().__init__(linter)
        self.msgs = {
            message.msg_id: (MESSAGES[code].format(name="%r"), message.symbol, f"See constricter's {code}.")
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
        )
        text: str = as_text(source)
        offences: list[Offence] = check_source(text, node.file or "<unknown>", checks)
        o: Offence
        for o in unsuppressed(offences, lines(text)):  # suppression comments, as the CLI reads them
            if o.is_error(level):
                self.add_message(SYMBOLS[o.code].symbol, line=o.line, col_offset=o.col, args=(o.name,))


def register(linter: PyLinter) -> None:
    """Register the checker (pylint's plugin hook)."""
    linter.register_checker(ConstricterChecker(linter))
