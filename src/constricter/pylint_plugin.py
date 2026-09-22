"""The rule as a pylint plugin: `--load-plugins=constricter.pylint_plugin`, reported as
C9101 `unannotated-local-variable`. pylint handles `# pylint: disable=unannotated-local-variable`.

It reads the module's source and runs the same `ast` check the CLI and flake8 use, rather than
walking astroid's tree, so all three report exactly the same lines."""

import ast
from typing import IO

from astroid import nodes
from pylint.checkers import BaseRawFileChecker
from pylint.lint import PyLinter

from constricter.checker import MESSAGE, check_tree

SYMBOL = "unannotated-local-variable"


class ConstricterChecker(BaseRawFileChecker):
    name = "constricter"
    msgs = {  # noqa: RUF012 (pylint's own class-attribute convention)
        "C9101": (
            MESSAGE.replace("{name!r}", "%r"),
            SYMBOL,
            "Every local variable is annotated where it's first bound (`name: T = ...`), or "
            "declared first (`name: T`). Loop targets, `except ... as`, match captures and "
            "imports are exempt.",
        )
    }

    def process_module(self, node: nodes.Module) -> None:
        opened: IO[bytes] | None = node.stream()
        if opened is None:  # a module astroid built without a file behind it
            return
        stream: IO[bytes]
        with opened as stream:
            source: bytes = stream.read()
        for o in check_tree(ast.parse(source, node.file or "<unknown>")):
            self.add_message(SYMBOL, line=o.line, col_offset=o.col, args=(o.name,))


def register(linter: PyLinter) -> None:
    linter.register_checker(ConstricterChecker(linter))
