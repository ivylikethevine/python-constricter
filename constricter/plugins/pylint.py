"""The rules as a pylint plugin (C9101-C9114); reports the codes the level makes errors."""

from typing import IO, NamedTuple, Protocol, cast, final

from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from pylint.typing import MessageDefinitionTuple, OptionDict, Options

from constricter.noqa import lines, unsuppressed
from constricter.offences import (
    CAN_BE_FINAL,
    COMMENT_TYPED_TARGET,
    LEVELS,
    LONG_TUPLE,
    MESSAGES,
    MISMATCHED_TYPE,
    NARROWABLE_TYPE,
    NESTED_TYPE,
    OPT_IN,
    REDUNDANT_TYPE,
    UNANNOTATED,
    UNANNOTATED_ATTRIBUTE,
    UNANNOTATED_MEMBER,
    UNANNOTATED_PARAMETER,
    UNANNOTATED_RETURN,
    UNTYPED_TARGET,
    UNUSED_UNION_MEMBER,
    VAGUE_TYPE,
    Checks,
    Level,
    Offence,
)
from constricter.overrides import override
from constricter.plugins import options as table
from constricter.plugins.options import CHOICES, OPTIONS, Option
from constricter.rules.checker import check_source
from constricter.source import parsed
from constricter.source.flow import parse_narrower


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
    CAN_BE_FINAL: Message("C9112", "could-be-final"),
    UNANNOTATED_ATTRIBUTE: Message("C9113", "unannotated-instance-attribute"),
    UNANNOTATED_RETURN: Message("C9114", "missing-return-type"),
    UNANNOTATED_PARAMETER: Message("C9115", "missing-parameter-type"),
}


class _Module(Protocol):  # pylint: disable=too-few-public-methods
    """What the checker reads of a module astroid parsed: the file behind it, and its bytes.

    astroid declares no types (no `py.typed`): naming its `Module` would leave the checker's
    signature unknown to a type checker reading this package.
    """

    file: str | None

    def stream(self) -> IO[bytes] | None:
        """Open the module's bytes, or nothing where no file backs it."""
        ...


def _option(option: Option) -> OptionDict:
    """Describe one of the plugins' options (see `options.OPTIONS`) as pylint takes it.

    Returns:
      Its settings.

    """
    said: OptionDict = {"default": option.default, "help": f"{option.help[0].upper()}{option.help[1:]}."}
    match option.kind:
        case table.LEVEL:
            return said | {"type": "choice", "choices": CHOICES, "metavar": "<level>"}
        case table.FLAG:
            return said | {"type": "yn", "metavar": "<y or n>"}
        case table.WHOLE:
            return said | {"type": "int", "metavar": "<n>"}
        case _:
            return said | {"type": "string", "metavar": "<B=A, ...>"}


@final
class ConstricterChecker(BaseRawFileChecker):
    """pylint's checker, run once per module on its raw source."""

    name: str = "constricter"
    options: Options = tuple((f"constricter-{option.name}", _option(option)) for option in OPTIONS)

    msgs: dict[str, MessageDefinitionTuple]

    def __init__(self, linter: PyLinter) -> None:
        """Register the messages with `linter`."""
        super().__init__(linter)
        # An opt-in code's message is off until enabled (`enable = could-be-final`).
        self.msgs = {
            message.msg_id: (
                MESSAGES[code].format(name="%r", detail="%s"),
                message.symbol,
                f"See constricter's {code}.",
                {"default_enabled": code not in OPT_IN},
            )
            for code, message in SYMBOLS.items()
        }

    @override
    def process_module(self, node: _Module) -> None:
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
            vague=cast("int", self.linter.config.constricter_vague),
            narrower=parse_narrower(cast("str", self.linter.config.constricter_narrower)),
            final=self.linter.is_message_enabled(SYMBOLS[CAN_BE_FINAL].symbol),
            attributes=self.linter.is_message_enabled(SYMBOLS[UNANNOTATED_ATTRIBUTE].symbol),
            returns=self.linter.is_message_enabled(SYMBOLS[UNANNOTATED_RETURN].symbol),
            parameters=self.linter.is_message_enabled(SYMBOLS[UNANNOTATED_PARAMETER].symbol),
        )
        text: str = parsed.text(source)  # by its PEP 263 declaration or BOM, as the CLI decodes it
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
