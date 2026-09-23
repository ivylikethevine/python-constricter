# SPDX-License-Identifier: MIT
"""Walking the syntax the rules read: functions and methods, nested statements, binding targets."""

import ast
import re
from collections.abc import Iterator, Sequence
from typing import Final, TypeAlias

from constricter.offences import at

# A `# type:` comment, as a loop header writes one (LVA003).
_TYPE_COMMENT: Final = re.compile(rb"#\s*type:")

FunctionDef: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef
FUNCTION_DEFS: tuple[type[ast.FunctionDef], type[ast.AsyncFunctionDef]] = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
)
_FUTURE: Final = "__future__"
# `from __future__` features only code that also runs on Python 2 imports: its type comments count.
_PYTHON2_FUTURES: frozenset[str] = frozenset(
    {
        "nested_scopes",
        "generators",
        "division",
        "absolute_import",
        "with_statement",
        "print_function",
        "unicode_literals",
    },
)


def python2_compatible(tree: ast.Module) -> bool:
    """Check for a `from __future__` import only Python 2 needs.

    Returns:
      Whether it marks the module as written for Python 2.

    """
    return any(
        isinstance(stmt, ast.ImportFrom)
        and stmt.module == _FUTURE
        and any(alias.name in _PYTHON2_FUTURES for alias in stmt.names)
        for stmt in tree.body
    )


def collect_functions(body: list[ast.stmt], into: list[FunctionDef]) -> None:
    """Collect functions in a module or class body, through compound statements and classes."""
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, FUNCTION_DEFS):
            into.append(stmt)
        elif isinstance(stmt, ast.ClassDef):
            collect_functions(stmt.body, into)
        else:
            collect_functions(child_statements(stmt), into)


def owners(tree: ast.Module) -> dict[int, str]:
    """Map each direct method of a class to that class's name, by the method's `id`.

    For `--fix` to type a method's `self`. A method is a function directly in a class's body,
    however deep through `if`/`try`/..., but not through a nested class's or function's own body.

    Returns:
      Each such function, by `id()`, mapped to its class's name.

    """
    found: dict[int, str] = {}
    node: ast.AST
    methods: list[FunctionDef]
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = []
            _direct_methods(node.body, methods)
            found.update((id(method), node.name) for method in methods)
    return found


def _direct_methods(body: list[ast.stmt], into: list[FunctionDef]) -> None:
    """Collect the functions directly in a class's body, through compound statements.

    A nested class's own methods aren't included.
    """
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, FUNCTION_DEFS):
            into.append(stmt)
        elif not isinstance(stmt, ast.ClassDef):
            _direct_methods(child_statements(stmt), into)


def child_statements(stmt: ast.stmt) -> list[ast.stmt]:
    """Collect the statements nested directly in `stmt`.

    Returns:
      Them, in source order.

    """
    children: list[ast.stmt] = []
    handler: ast.ExceptHandler
    case: ast.match_case
    match stmt:
        case ast.If() | ast.For() | ast.AsyncFor() | ast.While():
            children += stmt.body + stmt.orelse
        case ast.With() | ast.AsyncWith():
            children += stmt.body
        case ast.Try() | ast.TryStar():
            children += stmt.body
            for handler in stmt.handlers:
                children += handler.body
            children += stmt.orelse + stmt.finalbody
        case ast.Match():
            for case in stmt.cases:
                children += case.body
        case _:
            pass
    return children


def expressions(stmt: ast.stmt) -> Iterator[ast.AST]:
    """Walk the parts of `stmt` that aren't statements.

    Yields:
      Each, as where a `:=` can bind.

    """
    child: ast.AST
    for child in ast.iter_child_nodes(stmt):
        if isinstance(child, ast.match_case | ast.ExceptHandler):
            yield from (part for part in ast.iter_child_nodes(child) if not isinstance(part, ast.stmt))
        elif not isinstance(child, ast.stmt):
            yield child


def target_names(target: ast.expr) -> Iterator[ast.Name]:
    """Walk an assignment target.

    Yields:
      Each plain name it binds.

    """
    elements: list[ast.expr]
    element: ast.expr
    value: ast.expr
    match target:
        case ast.Name():
            yield target
        case ast.Tuple(elts=elements) | ast.List(elts=elements):
            for element in elements:
                yield from target_names(element)
        case ast.Starred(value=value):
            yield from target_names(value)
        case _:
            return


def captures(pattern: ast.pattern, lines: Sequence[str]) -> Iterator[tuple[str, tuple[int, int]]]:
    """Walk a `case` pattern.

    Yields:
      Each name it captures, with where it's bound.

    """
    node: ast.AST
    name: str
    for node in ast.walk(pattern):
        match node:
            case ast.MatchAs(name=str() as name) | ast.MatchStar(name=str() as name):
                yield name, at(node)
            case ast.MatchMapping(rest=str() as name):
                yield name, _rest_at(node, name, lines)
            case _:
                pass


_REST: Final = re.compile(rb"\*\*\s*(\w+)\b")


def _rest_at(node: ast.MatchMapping, name: str, lines: Sequence[str]) -> tuple[int, int]:
    """Find `**name` in a mapping pattern's source.

    Returns:
      Its position (as `ast` gives it, a byte column), or else the pattern's start.

    """
    target: bytes = name.encode()
    number: int
    encoded: bytes
    start: int
    found: re.Match[bytes]
    for number in range(node.lineno, min(node.end_lineno or node.lineno, len(lines)) + 1):
        encoded = lines[number - 1].encode()
        start = node.col_offset if number == node.lineno else 0
        for found in _REST.finditer(encoded, start):
            if found.group(1) == target:
                return number, found.start(1)
    return at(node)


def comment_type(comment: str) -> str | None:
    """Read a loop's `# type:` comment as an annotation (`int, str` is a tuple's parts).

    Returns:
      It, or `None` if it doesn't parse as one.

    """
    text: str = comment.split("#", 1)[0].strip()  # a comment after it (`# noqa`) isn't part of it
    try:
        parsed: ast.expr = ast.parse(text, mode="eval").body
    except SyntaxError:
        return None
    if isinstance(parsed, ast.Tuple):
        return f"tuple[{', '.join(ast.unparse(part) for part in parsed.elts)}]"
    return ast.unparse(parsed)


def type_comment_span(lines: Sequence[str], stmt: ast.For | ast.AsyncFor) -> tuple[int, int] | None:
    """Find the columns (UTF-8 bytes) of a one-line loop header's `# type:` comment, to delete it.

    From the end of the header's code (or, with a comment after it, `# type: int  # noqa`, from the
    `#`), up to that comment or the end of the line, so the other comment stays.

    Returns:
      Them, or `None` if the header spans lines or the comment isn't found after the iterable.

    """
    if not lines or stmt.body[0].lineno == stmt.lineno or stmt.iter.end_lineno != stmt.lineno:
        return None
    raw: bytes = lines[stmt.lineno - 1].encode()
    found: re.Match[bytes] | None
    if (found := _TYPE_COMMENT.search(raw, stmt.iter.end_col_offset or 0)) is None:
        return None
    after: int
    if (after := raw.find(b"#", found.end())) >= 0:
        return found.start(), after
    return len(raw[: found.start()].rstrip()), len(raw.rstrip(b"\r\n"))
