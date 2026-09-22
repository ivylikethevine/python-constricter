# SPDX-License-Identifier: MIT
"""The rule as a pylint plugin: C9101 `unannotated-local-variable`."""

import ast
from typing import IO, cast, final, override

from astroid import nodes
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from pylint.typing import Options

from constricter.checker import MESSAGE, check_tree

SYMBOL = "unannotated-local-variable"


@final
class ConstricterChecker(BaseRawFileChecker):
    """pylint's checker, run once per module on its raw source."""

    name: str = "constricter"
    options: Options = (
        (
            "constricter-type-comments",
            {"default": False, "type": "yn", "metavar": "<y or n>", "help": "Count `# type:` comments."},
        ),
    )

    def __init__(self, linter: PyLinter) -> None:
        """Register the message with `linter`."""
        super().__init__(linter)
        self.msgs = {
            "C9101": (MESSAGE.format(name="%r"), SYMBOL, "Annotate each local where it's first bound."),
        }

    @override
    def process_module(self, node: nodes.Module) -> None:
        opened: IO[bytes] | None
        if (opened := node.stream()) is None:  # no file behind the module
            return
        stream: IO[bytes]
        with opened as stream:
            source: bytes = stream.read()
        type_comments: bool = cast("bool", self.linter.config.constricter_type_comments)
        for o in check_tree(ast.parse(source, node.file or "<unknown>", type_comments=type_comments)):
            self.add_message(SYMBOL, line=o.line, col_offset=o.col, args=(o.name,))


def register(linter: PyLinter) -> None:
    """Register the checker (pylint's plugin hook)."""
    linter.register_checker(ConstricterChecker(linter))
