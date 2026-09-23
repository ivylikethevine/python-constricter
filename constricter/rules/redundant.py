# SPDX-License-Identifier: MIT
"""LVA007: a name annotated again with the type it already has, in the same straight-line block."""

import ast
from collections.abc import Callable, Iterator
from typing import Final

from constricter.offences import REDUNDANT_TYPE, Edit, Fix, FixPolicy, Offence, at
from constricter.rules.syntax import child_statements
from constricter.rules.walked import nodes

_KINDS: Final = frozenset({"redundant"})


def redundant(tree: ast.Module, policy: FixPolicy | None = None) -> list[Offence]:
    """Find a name annotated again with the type it already has, in the same straight-line block.

    Every block (a function, module or class body; an `if`'s body and its `orelse`; ...) is checked
    on its own: two branches that never run in the same pass typing a name the same way isn't
    redundant, so they're not compared against each other. Each gets a fix, if `policy` allows it,
    dropping the annotation (see `_dropped`).

    Returns:
      One offence (LVA007) per redundant re-annotation.

    """
    offences: list[Offence] = []
    node: ast.AST
    block: list[ast.stmt]
    fixing: bool = (policy or FixPolicy()).allows(_KINDS)
    in_class: set[int] = _class_level(tree)
    for node in nodes(tree):
        for block in _blocks(node):
            offences += _redundant_in(block, lambda stmt: fixing and id(stmt) not in in_class)
    return offences


def _class_level(tree: ast.Module) -> set[int]:
    """Find the statements of every class body, through `if`/`try`/..., not in its methods.

    `--fix` never edits them: a dataclass's annotations are its fields.

    Returns:
      Their `id`s.

    """
    return {id(stmt) for node in nodes(tree) if isinstance(node, ast.ClassDef) for stmt in _nested(node.body)}


def _nested(body: list[ast.stmt]) -> Iterator[ast.stmt]:
    """Walk `body`'s statements, and theirs through `if`/`try`/... (not a function's or class's).

    Yields:
      Each statement.

    """
    stmt: ast.stmt
    for stmt in body:
        yield stmt
        yield from _nested(child_statements(stmt))


def _blocks(node: ast.AST) -> Iterator[list[ast.stmt]]:
    """Find the straight-line blocks of statements directly in `node`.

    Yields:
      Each one (an `if`'s body and its `orelse` separately, and likewise for the other compound
      statements with more than one: they run in different passes, if at all).

    """
    body: list[ast.stmt]
    orelse: list[ast.stmt]
    handlers: list[ast.ExceptHandler]
    finalbody: list[ast.stmt]
    handler: ast.ExceptHandler
    cases: list[ast.match_case]
    case: ast.match_case
    match node:
        case (
            ast.Module(body=body)
            | ast.FunctionDef(body=body)
            | ast.AsyncFunctionDef(body=body)
            | ast.ClassDef(body=body)
            | ast.With(body=body)
            | ast.AsyncWith(body=body)
        ):
            yield body
        case (
            ast.If(body=body, orelse=orelse)
            | ast.For(body=body, orelse=orelse)
            | ast.AsyncFor(body=body, orelse=orelse)
            | ast.While(body=body, orelse=orelse)
        ):
            yield body
            yield orelse  # empty when there's no `else`, which is harmless: nothing to find in it
        case (
            ast.Try(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)
            | ast.TryStar(body=body, handlers=handlers, orelse=orelse, finalbody=finalbody)
        ):
            yield body
            for handler in handlers:
                yield handler.body
            yield orelse
            yield finalbody
        case ast.Match(cases=cases):
            for case in cases:
                yield case.body
        case _:
            pass


def _redundant_in(block: list[ast.stmt], fixable: Callable[[ast.stmt], bool]) -> list[Offence]:
    """Find a name in `block` annotated the same way twice.

    Returns:
      One offence per repeat, at the later statement, with a fix where `fixable` says so.

    """
    offences: list[Offence] = []
    seen: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    annotation: ast.expr
    for stmt in block:
        match stmt:
            case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation):
                text: str = ast.unparse(annotation)
                if seen.get(name) == text:
                    edit: Fix | None = _dropped(stmt) if fixable(stmt) else None
                    offences.append(Offence(*at(stmt), name, REDUNDANT_TYPE, edit))
                seen[name] = text
            case _:
                pass
    return offences


def _dropped(stmt: ast.AnnAssign) -> Fix | None:
    """Drop a repeated annotation: `x: int = 2` becomes `x = 2`.

    Returns:
      The fix (writing nothing over `: int`), or `None` for a bare declaration (`x: int`, whose
      whole statement would have to go) or one spread over lines.

    """
    if stmt.value is None or stmt.annotation.end_lineno != stmt.target.lineno:
        return None
    return Fix(
        "",
        "the type it already has",
        edit=Edit.REPLACE,
        span=(stmt.target.end_col_offset or 0, stmt.annotation.end_col_offset or 0),
        kinds=_KINDS,
    )
