"""The rule as a pylint plugin: C9101 `unannotated-local-variable`."""

import ast
from typing import IO, final, override

from astroid import nodes
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter
from pylint.typing import MessageDefinitionTuple

from constricter.checker import MESSAGE, check_tree

SYMBOL = "unannotated-local-variable"


@final
class ConstricterChecker(BaseRawFileChecker):
    name: str = "constricter"
    msgs: dict[str, MessageDefinitionTuple] = {  # noqa: RUF012 (typed as BaseChecker declares it)
        "C9101": (MESSAGE.replace("{name!r}", "%r"), SYMBOL, "Annotate each local where it's first bound."),
    }

    @override
    def process_module(self, node: nodes.Module) -> None:
        opened: IO[bytes] | None = node.stream()
        if opened is None:  # no file behind the module
            return
        stream: IO[bytes]
        with opened as stream:
            source: bytes = stream.read()
        for o in check_tree(ast.parse(source, node.file or "<unknown>")):
            self.add_message(SYMBOL, line=o.line, col_offset=o.col, args=(o.name,))


def register(linter: PyLinter) -> None:
    """Register the checker (pylint's plugin hook)."""
    linter.register_checker(ConstricterChecker(linter))
