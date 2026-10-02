# SPDX-License-Identifier: MIT
"""`--infer-with`: what a hint's own edits would write (see `Offered`).

An editor that accepts an inlay hint applies its `textEdits`: the annotation, spelled as the file can
write it, and the imports its names take. An import comes as a statement to add
(`from shapes import Shape`), or as names inserted into a `from` import the file has (`, Shape`).

A hint with no edits (pyrefly's, for a loop's or an unpacking's names) may say where each class in
its label is defined instead: the import is from the module that file is.
"""

import ast
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Final, TypeAlias, cast
from urllib.parse import urlsplit
from urllib.request import url2pathname

from constricter.cli.protocol import Json, Object
from constricter.fix.core.known import Offered
from constricter.fix.index.modules import SUFFIX, module_name
from constricter.rules import parsed

_Where: TypeAlias = tuple[int, int]  # a line (from 1) and a UTF-8 byte column, as `ast` counts
_Locate: TypeAlias = Callable[[Object], _Where | None]  # a position's, or `None` past the file's end
_SITE: Final = "site-packages"
_BUNDLED: Final = "pyrefly_bundled_typeshed"  # how the folders pyrefly unpacks its stubs into start
_STUBS: Final = "-stubs"  # a stub package's folder, after the package's name
_PACKAGE: Final = "__init__"
_BUILTINS: Final = "builtins"


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
      Them; `None` for a hint whose edits say no more than its label, one with an edit that is
      neither, or one with no edits whose label doesn't say where a class in it is defined.

    """
    edits: list[Json]
    if not (edits := cast("list[Json]", hint.get("textEdits") or [])):
        located: tuple[str, ...] = _located(hint.get("label"))
        return Offered(label, located) if located else None
    text: str = ""
    imports: list[str] = []
    edit: Json
    for edit in edits:
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


def _located(label: Json) -> tuple[str, ...]:
    """Read the imports a label's parts take: each class a part names, from the module its file is.

    Returns:
      A statement for each class whose defining file's module can be named, once; not a builtin's.

    """
    found: dict[str, None] = {}
    part: Json
    for part in label if isinstance(label, list) else []:
        name: str = str(cast("Object", part).get("value", ""))
        location: Json = cast("Object", part).get("location")
        if location is None or not name.isidentifier():
            continue
        uri: str = str(cast("Object", location)["uri"])
        module: str | None = _defined_in(Path(url2pathname(urlsplit(uri).path)))
        if module and module != _BUILTINS:
            found[f"from {module} import {name}"] = None
    return tuple(found)


def _defined_in(path: Path) -> str | None:
    """Name the module a file is: an installed one, one of pyrefly's own stubs, or a project's.

    Returns:
      It, by the folders after `site-packages` or pyrefly's stubs' folder, else by its package
      folders as the project index names it; `None` for a stub anywhere else, or no file at all.

    """
    if not path.name:  # a location that isn't a file's (`untitled:`)
        return None
    parts: tuple[str, ...] = path.with_suffix("").parts
    index: int
    part: str
    for index, part in enumerate(parts[:-1]):
        if part == _SITE or part.startswith(_BUNDLED):
            after: int = index + 2
            inside: list[str] = [parts[index + 1].removesuffix(_STUBS), *parts[after:]]
            return ".".join(inside[:-1] if inside[-1] == _PACKAGE and len(inside) > 1 else inside)
    return module_name(path) if path.suffix == SUFFIX else None


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
