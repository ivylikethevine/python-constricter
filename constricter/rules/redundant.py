# SPDX-License-Identifier: MIT
"""LVA007: a name annotated again with the type it already has, in the same straight-line block."""

import ast
from collections.abc import Iterator

from constricter.offences import REDUNDANT_TYPE, Offence, at


def redundant(tree: ast.Module) -> list[Offence]:
    """Find a name annotated again with the type it already has, in the same straight-line block.

    Every block (a function, module or class body; an `if`'s body and its `orelse`; ...) is checked
    on its own: two branches that never run in the same pass typing a name the same way isn't
    redundant, so they're not compared against each other.

    Returns:
      One offence (LVA007) per redundant re-annotation.

    """
    offences: list[Offence] = []
    node: ast.AST
    block: list[ast.stmt]
    for node in ast.walk(tree):
        for block in _blocks(node):
            offences += _redundant_in(block)
    return offences


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


def _redundant_in(block: list[ast.stmt]) -> list[Offence]:
    """Find a name in `block` annotated the same way twice.

    Returns:
      One offence per repeat, at the later statement.

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
                    offences.append(Offence(*at(stmt), name, REDUNDANT_TYPE))
                seen[name] = text
            case _:
                pass
    return offences
