# SPDX-License-Identifier: MIT
"""Parse a module once: the cross-file index and the check share its tree, in the same process.

The CLI reads every file to index what it offers other files (`fix.project`), then checks each; both
parse it the same way (`parse`), and the index's tree is kept (`keep`) for the check to take
(`take`), which frees it. What's kept is capped (`budget`): a tree takes about 26 bytes of memory for
each byte of source, so past the cap a file is parsed again, as it always was.
"""

import ast
import io
import tokenize
import warnings
from dataclasses import dataclass, field
from typing import Final

BUDGET: Final = 40 << 20  # bytes of source whose trees a run keeps, over all its processes (about 1 GB)


@dataclass
class _Kept:
    """The trees kept in this process, by their source's text, and what's left of its share."""

    trees: dict[str, ast.Module] = field(default_factory=dict)
    left: int = BUDGET


_KEPT: Final = _Kept()


def budget(processes: int) -> None:
    """Share the budget among `processes`: each keeps its part (a worker's initializer, or the CLI's own)."""
    _KEPT.trees.clear()
    _KEPT.left = BUDGET // max(processes, 1)


def parse(source: str | bytes, filename: str = "<unknown>") -> ast.Module:
    """Parse `source` with its `# type:` comments; without them if one is misplaced.

    Python's warnings about the source (an invalid escape sequence in a string) are left unsaid: they're
    about the code checked, not findings, and it's the checked project's to see them when it runs.

    Returns:
      The module. Raises `SyntaxError`.

    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        warnings.simplefilter("ignore", DeprecationWarning)  # what Python 3.11 warns about them with
        try:
            return ast.parse(source, filename, type_comments=True)
        except SyntaxError:  # a misplaced `# type:` comment, or a real error raised again here
            return ast.parse(source, filename)


def text(data: bytes) -> str:
    """Decode a module's bytes as Python finds their encoding (a PEP 263 declaration, a BOM, else UTF-8).

    Returns:
      Its text. Raises `SyntaxError` for an unknown or contradictory encoding, and
      `UnicodeDecodeError` for bytes it doesn't hold.

    """
    return data.decode(tokenize.detect_encoding(io.BytesIO(data).readline)[0])


def keep(source: str, tree: ast.Module) -> None:
    """Keep `source`'s tree for the check to take, if this process's share of the budget allows it."""
    if len(source) <= _KEPT.left and source not in _KEPT.trees:
        _KEPT.trees[source] = tree
        _KEPT.left -= len(source)


def take(source: str) -> ast.Module | None:
    """Take the tree kept for `source`, freeing it (two files alike in every byte share one).

    Returns:
      It, or `None` if none was kept.

    """
    tree: ast.Module | None
    if (tree := _KEPT.trees.pop(source, None)) is not None:
        _KEPT.left += len(source)
    return tree
