"""How a function binds a name again, which `late.rebinds` reads to leave a first binding's fix out.

By a conversion (`converted`: a call on itself), an operator with an operand of a type that isn't
known (`operated`, `unites`), an empty display whose class the fix doesn't name (`emptied`), in
another arm of an `if` (`apart`), or as a loop's target past the loop (`looped`).
"""

import ast
from collections.abc import Mapping
from functools import lru_cache
from typing import Final, TypeAlias

from constricter.offences import (
    UNIONS,
    at,
)
from constricter.rules.scope import Scope
from constricter.source.flow import members
from constricter.source.syntax import NESTED_SCOPES, FunctionDef
from constricter.source.walked import walk

# The arms a binding is in: each branching statement around it (by `id()`), and which of its arms.
_Arms: TypeAlias = tuple[tuple[int, int], ...]


def unites(scope: Scope, name: str) -> bool:
    """Check whether `name`'s values of several types may be declared their union (`fix-widen`'s `unions`).

    Returns:
      Whether they may: where it's asked for, in a function, of a name it doesn't change in place
      (`name += more`, which no union of its types need take).

    """
    function: FunctionDef | None = scope.kind.function
    return (
        UNIONS in scope.settings.checks.fixes.widen
        and function is not None
        and name not in _augmented(function)
    )


@lru_cache(maxsize=64)  # asked of each of a function's names bound again
def _augmented(function: FunctionDef) -> frozenset[str]:
    """Name what a function changes in place: `name += more`.

    Returns:
      Each such name.

    """
    return frozenset(
        node.target.id
        for node in walk(function)
        if isinstance(node, ast.AugAssign) and isinstance(node.target, ast.Name)
    )


@lru_cache(maxsize=1024)  # asked of each of a function's names bound again
def converted(function: FunctionDef) -> frozenset[tuple[int, int]]:
    """Find where a function binds a name to a call on the name itself.

    One that takes it (`item = proper(item)`) or is its method (`match = match.groupdict()`), alone
    or as an operand of `or` or of a conditional expression (`code = table.get(code) or SYNTAX`).

    Returns:
      Where each such name is bound.

    """
    found: set[tuple[int, int]] = set()
    node: ast.AST
    target: ast.expr
    for node in walk(function):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and _on_itself(target.id, node.value):
                    found.add(at(target))
    return frozenset(found)


def _on_itself(name: str, value: ast.expr) -> bool:
    """Check whether `value` is a call on `name` (see `converted`), or an operand of one is.

    Returns:
      Whether it is.

    """
    values: list[ast.expr]
    body: ast.expr
    orelse: ast.expr
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    match value:
        case ast.BoolOp(values=values):
            return any(_on_itself(name, each) for each in values)
        case ast.IfExp(body=body, orelse=orelse):
            return _on_itself(name, body) or _on_itself(name, orelse)
        case ast.Call(func=func, args=args, keywords=keywords):
            return any(
                isinstance(each, ast.Name) and each.id == name
                for each in (_base(func), *args, *(keyword.value for keyword in keywords))
            )
        case _:
            return False


def _base(node: ast.expr) -> ast.expr:
    """Find what a chain of attributes is read from: `self` in `self.table.get`.

    Returns:
      It; `node` itself, if it isn't an attribute.

    """
    return _base(node.value) if isinstance(node, ast.Attribute) else node


# The classes whose call with no arguments is an empty display.
_EMPTY: Final = frozenset({"dict", "list", "set", "tuple"})


@lru_cache(maxsize=1024)  # asked of each of a function's names bound again
def emptied(function: FunctionDef) -> Mapping[tuple[int, int], str]:
    """Find where a function binds a name to an empty display: `{}`, `[]`, `()` or `set()`, `dict()`.

    Returns:
      Where each such name is bound, and the display's class.

    """
    found: dict[tuple[int, int], str] = {}
    node: ast.AST
    target: ast.expr
    kind: str | None
    for node in walk(function):
        if isinstance(node, ast.Assign) and (kind := _empty(node.value)) is not None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    found[at(target)] = kind
    return found


def _empty(value: ast.expr) -> str | None:
    """Name the class of an empty display, or of a call of its class with no arguments.

    Returns:
      It, or `None` for any other value.

    """
    name: str
    match value:
        case ast.Dict(keys=[]):
            return "dict"
        case ast.List(elts=[]):
            return "list"
        case ast.Tuple(elts=[]):
            return "tuple"
        case ast.Call(func=ast.Name(id=name), args=[], keywords=[]) if name in _EMPTY:
            return name
        case _:
            return None


def heads(annotation: str) -> frozenset[str]:
    """Name the classes of an annotation's union's members: `dict` for `dict[str, int] | None`.

    Returns:
      Them; none, if it can't be read.

    """
    return frozenset(member.split("[", 1)[0] for member in members(annotation) or ())


@lru_cache(maxsize=1024)  # asked of each of a function's names bound again
def operated(function: FunctionDef) -> frozenset[tuple[int, int]]:
    """Find where a function binds a name by an augmented assignment: `factor *= other`.

    Returns:
      Where each such name is bound.

    """
    node: ast.AST
    target: ast.Name
    found: set[tuple[int, int]] = set()
    for node in walk(function):
        match node:
            case ast.AugAssign(target=ast.Name() as target):
                found.add(at(target))
            case _:
                pass
    return frozenset(found)


@lru_cache(maxsize=1024)  # asked of each of a function's names bound again
def looped(function: FunctionDef) -> Mapping[tuple[int, int], int]:
    """Find a function's loops' targets: `for name in names`, `for key, value in pairs`.

    Returns:
      Where each target name is bound, and its loop's last line.

    """
    found: dict[tuple[int, int], int] = {}
    node: ast.AST
    target: ast.AST
    for node in walk(function):
        if isinstance(node, ast.For | ast.AsyncFor):
            for target in ast.walk(node.target):
                if isinstance(target, ast.Name):
                    found[at(target)] = node.end_lineno or node.lineno
    return found


def apart(function: FunctionDef, first: tuple[int, int], later: tuple[int, int]) -> bool:
    """Check whether two bindings of a function's are in different arms of one statement.

    Returns:
      Whether they are: only one of them runs.

    """
    arms: Mapping[tuple[int, int], _Arms] = _arms(function)
    taken: dict[int, int] = dict(arms.get(first, ()))
    return any(taken.get(branch, arm) != arm for branch, arm in arms.get(later, ()))


@lru_cache(maxsize=64)  # asked of each of a function's names bound again
def _arms(function: FunctionDef) -> Mapping[tuple[int, int], _Arms]:
    """Find, for each name a function's branches bind, the arms its binding is in.

    An `if`'s body and its `else`, a `try`'s body and each handler, a `match`'s cases.

    Returns:
      Where each such name is bound, and each branching statement around it (by `id()`) with which
      of its arms that's in.

    """
    found: dict[tuple[int, int], _Arms] = {}
    # Each statement still to read, and the arms it's in; `None` ends it.
    waiting: list[tuple[ast.stmt, _Arms] | None] = [
        None,
        *((stmt, ()) for stmt in function.body),
    ]
    stmt: ast.stmt
    inside: _Arms
    for stmt, inside in iter(waiting.pop, None):
        if isinstance(stmt, NESTED_SCOPES):
            continue
        if inside:
            found.update(
                (at(name), inside)
                for target in _targets(stmt)
                for name in ast.walk(target)
                if isinstance(name, ast.Name)
            )
        blocks: list[list[ast.stmt]] = _blocks(stmt)
        arm: int
        block: list[ast.stmt]
        for arm, block in enumerate(blocks):
            within: tuple[tuple[int, int], ...] = (
                (*inside, (id(stmt), arm)) if _alternatives(stmt) else inside
            )
            waiting.extend([(child, within) for child in block])
    return found


def _alternatives(stmt: ast.stmt) -> bool:  # whether only one of its blocks runs, of those `_blocks` lists
    return isinstance(stmt, ast.If | ast.Match | ast.Try | ast.TryStar)


def _targets(stmt: ast.stmt) -> list[ast.expr]:  # what a statement assigns to
    match stmt:
        case ast.Assign():
            return stmt.targets
        case ast.AnnAssign() | ast.AugAssign():
            return [stmt.target]
        case _:
            return []


def _blocks(stmt: ast.stmt) -> list[list[ast.stmt]]:
    """List a statement's blocks, those of which only one runs each as an arm.

    Returns:
      An `if`'s body and its `else`, a `try`'s body (with its `else`) and each handler's, a
      `match`'s cases; any other statement's blocks.

    """
    match stmt:
        case ast.If():
            return [stmt.body, stmt.orelse]
        case ast.Try() | ast.TryStar():
            return [[*stmt.body, *stmt.orelse], *(handler.body for handler in stmt.handlers), stmt.finalbody]
        case ast.Match():
            return [case.body for case in stmt.cases]
        case ast.For() | ast.AsyncFor() | ast.While():
            return [stmt.body, stmt.orelse]
        case ast.With() | ast.AsyncWith():
            return [stmt.body]
        case _:
            return []
