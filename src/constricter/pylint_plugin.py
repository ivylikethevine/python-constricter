# SPDX-License-Identifier: MIT
"""The rules as a pylint plugin (C9101-C9103); reports the codes the level makes errors."""

from typing import IO, NamedTuple, cast, final, override

from astroid import nodes
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from pylint.typing import Options

from constricter.checker import (
  COMMENT_TYPED_TARGET,
  LEVELS,
  MESSAGES,
  UNANNOTATED,
  UNTYPED_TARGET,
  Level,
  Offence,
  check_source,
)


class Message(NamedTuple):
  """A code's pylint message id and symbol."""

  msg_id: str
  symbol: str


SYMBOLS: dict[str, Message] = {
  UNANNOTATED: Message("C9101", "unannotated-local-variable"),
  UNTYPED_TARGET: Message("C9102", "untyped-for-or-match-variable"),
  COMMENT_TYPED_TARGET: Message("C9103", "comment-typed-for-variable"),
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
    opened: IO[bytes] | None
    if (opened := node.stream()) is None:  # no file behind the module
      return
    stream: IO[bytes]
    with opened as stream:
      source: bytes = stream.read()
    level: Level = LEVELS[cast("str", self.linter.config.constricter_level)]
    type_comments: bool = cast("bool", self.linter.config.constricter_type_comments)
    o: Offence
    for o in check_source(source, node.file or "<unknown>", type_comments=type_comments):
      if o.is_error(level):
        self.add_message(SYMBOLS[o.code].symbol, line=o.line, col_offset=o.col, args=(o.name,))


def register(linter: PyLinter) -> None:
  """Register the checker (pylint's plugin hook)."""
  linter.register_checker(ConstricterChecker(linter))
