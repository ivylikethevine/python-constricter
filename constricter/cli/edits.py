# SPDX-License-Identifier: MIT
"""`--infer-with`: what a hint's own edits would write (see `Offered`).

An editor that accepts an inlay hint applies its `textEdits`: the annotation, spelled as the file can
write it, and the imports its names take. An import comes as a statement to add
(`from shapes import Shape`), or as names inserted into a `from` import the file has (`, Shape`).
"""

import ast
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import TypeAlias, cast

from constricter.cli.protocol import Json, Object
from constricter.fix.known import Offered
from constricter.rules import parsed

_Where: TypeAlias = tuple[int, int]  # a line (from 1) and a UTF-8 byte column, as `ast` counts
_Locate: TypeAlias = Callable[[Object], _Where | None]  # a position's, or `None` past the file's end


@dataclass
class FromImports:
    """A file's `from` imports (`found`), read from its `lines` when one is first looked for."""

    lines: Sequence[str]
    found: list[ast.ImportFrom] | None = None

    def at(self, where: _Where) -> ast.ImportFrom | None:
        """Find the `from` import `where` is in.

        Returns:
          It, or `None` (always, for a file that doesn't parse).

        """
        if self.found is None:
            self.found = _from_imports(self.lines)
        return next(
            (
                node
                for node in self.found
                if (node.lineno, node.col_offset)
                <= where
                <= (node.end_lineno or node.lineno, node.end_col_offset or 0)
            ),
            None,
        )


def _from_imports(lines: Sequence[str]) -> list[ast.ImportFrom]:
    """Read a file's `from` imports, wherever they are.

    Returns:
      Them; none for a file that doesn't parse.

    """
    try:
        tree: ast.Module = parsed.parse("\n".join(lines))
    except (SyntaxError, ValueError):  # a null byte is a `ValueError` before Python 3.12
        return []
    return [node for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]


def offered(hint: Object, label: str, locate: _Locate, existing: FromImports) -> Offered | None:
    """Read what a variable-type hint (showing `label`) would write: its annotation and its imports.

    Returns:
      Them; `None` for a hint with no edits, one whose edits say no more than its label, or one
      with an edit that is neither.

    """
    text: str = ""
    imports: list[str] = []
    edit: Json
    for edit in cast("list[Json]", hint.get("textEdits") or []):
        new: str = str(cast("Object", edit).get("newText", ""))
        start: Object = cast("Object", cast("Object", cast("Object", edit)["range"])["start"])
        if start == hint["position"] and new.startswith(":"):
            text = new[1:].strip()
            continue
        found: list[str] | None
        if (found := _imports(new.strip(), start, locate, existing)) is None:
            return None
        imports += found
    return Offered(text, tuple(imports)) if text and (imports or text != label) else None


def _imports(new: str, start: Object, locate: _Locate, existing: FromImports) -> list[str] | None:
    """Read an edit that adds imports: whole statements, or names into a `from` import at `start`.

    Returns:
      Each name's import, as a statement of its own; `None` for any other edit.

    """
    try:
        body: list[ast.stmt] = ast.parse(new).body
    except SyntaxError:  # `, Shape`: names for an import the file has
        body = []
    if body and all(isinstance(stmt, ast.Import | ast.ImportFrom) for stmt in body):
        return [statement for stmt in body for statement in _statements(stmt)]
    where: _Where | None = locate(start)
    node: ast.ImportFrom | None = None if where is None else existing.at(where)
    names: list[str] = [name.strip() for name in new.split(",") if name.strip()]
    if node is None or not names or not all(name.isidentifier() for name in names):
        return None
    return [f"from {_module(node)} import {name}" for name in names]


def _statements(stmt: ast.stmt) -> list[str]:
    """Write an import as one statement per name it binds.

    Returns:
      Them.

    """
    prefix: str = f"from {_module(stmt)} import " if isinstance(stmt, ast.ImportFrom) else "import "
    return [
        prefix + alias.name + (f" as {alias.asname}" if alias.asname else "")
        for alias in cast("ast.Import | ast.ImportFrom", stmt).names
    ]


def _module(node: ast.ImportFrom) -> str:
    """Write the module a `from` import names.

    Returns:
      It, a relative one with its dots.

    """
    return "." * node.level + (node.module or "")
