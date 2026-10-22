"""Where a type checker narrows a value: the lines a test governs, and what it tests there.

An `if` or `while` narrows what its condition tests in its body (and, negated, in its `else`); a
`match` its subject in each case; an `assert`, and an `if` whose body always leaves (`return`,
`raise`, `continue`, `break`), what they test for the rest of their block. A copy of a narrowed
value there has the narrowed type, not its declared one: `--fix` offers it none (see `scope`). A
check (`isinstance`, a `TypeGuard`, a `match`) narrows any type; a truth test or a comparison only
a union (`int | None`).

What a test leaves of a union there is the narrowed read's type (`left`): `if x is None: return`
leaves `x` its members but `None` for the rest of the block, `isinstance(x, C)` the members of class
`C`, a truth test its members but `None`.
"""

import ast
from collections.abc import Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.rules.walked import walk

# What a test leaves of a union's members: those it keeps (by class, `None` for all of them), less
# those it drops; `None` where it narrows otherwise (a comparison, a `TypeGuard`, a `match`).
Left: TypeAlias = tuple[frozenset[str] | None, frozenset[str]]
_ALL: Final[Left] = (None, frozenset())
_NONE: Final = "None"


class Region(NamedTuple):
    """The lines a test governs (first and last, from 1), for a value it narrows there."""

    start: int
    end: int
    check: bool  # whether it's a check, which narrows any type (a truth test or comparison only a union)
    left: Left | None = None  # what it leaves of the value's union there (see `Left`)


Regions: TypeAlias = Mapping[str, tuple[Region, ...]]
_LEAVING: Final = (ast.Return, ast.Raise, ast.Continue, ast.Break)
_GUARDS: Final = frozenset({"isinstance", "issubclass", "callable", "hasattr"})
_READS: Final = (ast.Name, ast.Attribute, ast.Subscript)
_SCOPES: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def regions(tree: ast.Module) -> Regions:
    """Find every region a test narrows a value in, in a module.

    Returns:
      Each value's regions.

    """
    found: dict[str, list[Region]] = {}
    text: str
    region: Region
    for text, region in _block(tree.body):
        found.setdefault(text, []).append(region)
    return {text: tuple(spans) for text, spans in found.items()}


def narrowed_at(found: Regions, value: ast.expr, line: int, *, union: bool) -> bool:
    """Check whether a read (`x`, `self.x`, `d[k]`) is narrowed at `line` by a test around it.

    `union`: whether its type is one, which a truth test or a comparison narrows too.

    Returns:
      Whether it is.

    """
    return isinstance(value, _READS) and read_narrowed(found, ast.unparse(value), line, union=union)


def read_narrowed(found: Regions, read: str, line: int, *, union: bool) -> bool:
    """Check whether a read, as text, is narrowed at `line` (see `narrowed_at`).

    Returns:
      Whether it is.

    """
    return any(each.start <= line <= each.end and (each.check or union) for each in found.get(read, ()))


def narrowed_to(
    found: Regions,
    read: str,
    line: int,
    members: Sequence[str],
    function: ast.AST,
) -> list[str] | None:
    """Find what the tests around a read (as text) at `line` in `function` leave of its union's `members`.

    A test outside the function (around a function inside another) narrows nothing in it to every
    checker; nor does one before a store of the read, or of what it's read of (`self.conn`, for
    `self.conn.pool`), between the test and the read, or after the read in a loop inside the test's
    region, which comes back round to it.

    Returns:
      The members left, in their order; `None` where a test narrows it otherwise, or leaves none.

    """
    left: list[str] = list(members)
    first: int = getattr(function, "lineno", 0)
    stores: list[int] = [
        at for text, lines in _stores(function).items() if _under(read, text) for at in lines
    ]
    each: Region
    for each in found.get(read, ()):
        if not each.start <= line <= each.end:
            continue
        if each.left is None or each.start < first or _lost(each, line, stores, _loops(function)):
            return None
        keep: frozenset[str] | None
        drop: frozenset[str]
        keep, drop = each.left
        left = [m for m in left if (keep is None or _class(m) in keep) and m not in drop]
    return left or None


def _under(read: str, stored: str) -> bool:  # whether storing `stored` stores `read`, or what it's read of
    return read == stored or read.startswith((f"{stored}.", f"{stored}["))


def _lost(region: Region, line: int, stores: Sequence[int], loops: Sequence[tuple[int, int]]) -> bool:
    """Check whether a store undoes a region's narrowing before a read on `line` (see `narrowed_to`).

    `stores`: the lines the read is stored on (0: in a function inside, whenever it's called).

    Returns:
      Whether one does.

    """
    around: list[tuple[int, int]] = [
        (start, end) for start, end in loops if region.start <= start <= line <= end
    ]
    return any(
        at == 0
        or region.start <= at < line
        or (line < at <= region.end and any(at <= end for _, end in around))
        for at in stores
    )


@lru_cache(maxsize=64)  # asked of each narrowed read in the function
def _stores(function: ast.AST) -> Mapping[str, tuple[int, ...]]:
    """List what a function stores (`x`, `self.x`, `d[k]`), and on which lines: 0 in a function inside.

    Returns:
      Each, as source text, and those lines.

    """
    inside: set[int] = {
        id(node)
        for nested in walk(function)
        if nested is not function and isinstance(nested, _SCOPES)
        for node in walk(nested)
    }
    found: dict[str, set[int]] = {}
    node: ast.AST
    for node in walk(function):
        names: list[str]
        if names := _stored(node):
            at: int = 0 if id(node) in inside else getattr(node, "lineno", 0)
            name: str
            for name in names:
                found.setdefault(name, set()).add(at)
    return {name: tuple(sorted(lines)) for name, lines in found.items()}


def _stored(node: ast.AST) -> list[str]:
    """Name what a node stores: a target, an `except`'s or a pattern's name, an import.

    Returns:
      Each, as source text.

    """
    name: str | None
    names: list[ast.alias]
    match node:
        case ast.Name() | ast.Attribute() | ast.Subscript() if not isinstance(node.ctx, ast.Load):
            return [ast.unparse(node)]
        case ast.ExceptHandler(name=str() as name) | ast.MatchAs(name=str() as name):
            return [name]
        case ast.MatchStar(name=str() as name):
            return [name]
        case ast.Import(names=names) | ast.ImportFrom(names=names):
            return [(each.asname or each.name).split(".", 1)[0] for each in names]
        case _:
            return []


@lru_cache(maxsize=64)  # asked of each narrowed read in the function
def _loops(function: ast.AST) -> tuple[tuple[int, int], ...]:  # every loop's lines in a function
    return tuple(
        (node.lineno, node.end_lineno or node.lineno)
        for node in walk(function)
        if isinstance(node, ast.For | ast.AsyncFor | ast.While)
    )


def _class(member: str) -> str:  # a union member's class: `dict[str, int]`'s `dict`
    return member.split("[", 1)[0]


@lru_cache(maxsize=64)  # asked of each of a function's guessed unions
def tested_lines(function: ast.AST) -> Mapping[str, frozenset[int]]:
    """Find the lines on which a test of a function's own narrows a value it goes on to read.

    A condition's own lines (`if opt and opt.cb:`), a conditional expression's
    (`opt.cb if opt else None`), a filtered comprehension's, and those of an `and` or `or` anywhere
    (`return opt and opt.cb`).

    Returns:
      Each value such a test narrows, as source text, and those lines.

    """
    found: dict[str, set[int]] = {}
    node: ast.AST
    for node in walk(function):
        test: ast.expr
        whole: ast.expr
        for test, whole in _spanned(node):
            lines: range = range(min(test.lineno, whole.lineno), (whole.end_lineno or whole.lineno) + 1)
            text: str
            for text, _ in _narrows(test):
                found.setdefault(text, set()).update(lines)
    return {text: frozenset(lines) for text, lines in found.items()}


def _spanned(node: ast.AST) -> Iterator[tuple[ast.expr, ast.expr]]:
    """Find the tests a node holds, each with the expression whose lines it narrows on.

    Yields:
      Each test, and that expression: the test itself, or what it's part of.

    """
    test: ast.expr
    match node:
        case ast.If(test=test) | ast.While(test=test) | ast.Assert(test=test):
            yield test, test
        case ast.IfExp(test=test):
            yield test, node
        case ast.BoolOp():
            yield node, node
        case ast.ListComp() | ast.SetComp() | ast.DictComp() | ast.GeneratorExp():
            yield from ((test, node) for each in node.generators for test in each.ifs)
        case _:
            pass


def _block(body: Sequence[ast.stmt]) -> Iterator[tuple[str, Region]]:
    """Walk a block's statements for the regions their tests narrow, inner blocks included.

    Yields:
      Each narrowed value, and a region.

    """
    end: int = (body[-1].end_lineno or body[-1].lineno) if body else 0
    stmt: ast.stmt
    for stmt in body:
        rest: tuple[int, int] = ((stmt.end_lineno or stmt.lineno) + 1, end)
        text: str
        check: bool
        for text, check in _tested(stmt):
            span: tuple[int, int]
            passed: bool | None
            for span, passed in _governed(stmt, rest):
                test: ast.expr | None = getattr(stmt, "test", None)
                left: Left | None = (
                    None if passed is None or test is None else _left(test, text, passed=passed)
                )
                yield text, Region(*span, check, left)
        inner: list[ast.stmt]
        for inner in _bodies(stmt):
            yield from _block(inner)


def _tested(stmt: ast.stmt) -> frozenset[tuple[str, bool]]:
    """Name what a statement's test narrows.

    Returns:
      Each value, as source text, and whether it's checked (see `Region`).

    """
    test: ast.expr
    subject: ast.expr
    match stmt:
        case ast.If(test=test) | ast.While(test=test) | ast.Assert(test=test):
            return frozenset(_narrows(test))
        case ast.Match(subject=subject) if isinstance(subject, _READS):
            return frozenset({(ast.unparse(subject), True)})
        case _:
            return frozenset()


def _narrows(test: ast.expr) -> Iterator[tuple[str, bool]]:
    """Walk a condition for the values it narrows: a value tested for truth, compared, or checked.

    Yields:
      Each, as source text (`x`, `self.x`), not what it's compared with or checked against; and
      whether it's checked (a call's argument: `isinstance`, a `TypeGuard` function).

    """
    operand: ast.expr
    values: list[ast.expr]
    left: ast.expr
    args: list[ast.expr]
    name: str
    match test:
        case ast.Name() | ast.Attribute() | ast.Subscript():
            yield ast.unparse(test), False
        case ast.UnaryOp(operand=operand):
            yield from _narrows(operand)
        case ast.BoolOp(values=values):
            yield from (found for value in values for found in _narrows(value))
        case ast.Compare(left=left) if isinstance(left, _READS):
            yield ast.unparse(left), False
        case ast.Call(func=ast.Name(id=name), args=args) if name in _GUARDS:
            yield from ((ast.unparse(arg), True) for arg in args[:1] if isinstance(arg, _READS))
        case ast.Call(args=args):  # a `TypeGuard` or `TypeIs` function may narrow any it's passed
            yield from ((ast.unparse(arg), True) for arg in args if isinstance(arg, _READS))
        case _:
            pass


def _governed(stmt: ast.stmt, rest: tuple[int, int]) -> Iterator[tuple[tuple[int, int], bool | None]]:
    """Find the lines a statement's test governs.

    Yields:
      Each region: its branches, and the rest of its block (`rest`) after an `assert`, or after an
      `if` one of whose branches always leaves; and whether the test passed there (`None` for a
      `match`'s case).

    """
    match stmt:
        case ast.Assert():
            yield rest, True
        case ast.If() | ast.While():
            yield from (
                (_span(branch), passed)
                for branch, passed in ((stmt.body, True), (stmt.orelse, False))
                if branch
            )
            if isinstance(stmt, ast.If) and isinstance(stmt.body[-1], _LEAVING):
                yield rest, False
            elif isinstance(stmt, ast.If) and stmt.orelse and isinstance(stmt.orelse[-1], _LEAVING):
                yield rest, True
        case _:  # a `match`, the one other statement `_tested` finds a test in
            yield from ((_span(case.body), None) for case in cast("ast.Match", stmt).cases)


def _left(test: ast.expr, text: str, *, passed: bool) -> Left | None:
    """Find what a test leaves of a value's union where it passed (`passed`) or failed.

    `x is None` keeps only `None`, failed all but `None`; `isinstance(x, C)` keeps class `C`'s
    members (a tuple of classes, theirs); a truth test drops `None`; an ordering (`x > 2`) leaves
    all. `not` turns it round, an `and` that passed (an `or` that failed) is each of its parts'.
    Anything else that narrows the value (`==`, `in`, a failed `isinstance` or truth test, a
    `TypeGuard`) leaves what a checker knows and this doesn't.

    Returns:
      What it leaves (see `Left`); all of it where the test doesn't read the value; `None` where
      it narrows it otherwise.

    """
    if text not in {each for each, _ in _narrows(test)}:
        return _ALL
    operand: ast.expr
    joining: ast.boolop
    values: list[ast.expr]
    left: ast.expr
    classes: ast.expr
    found: Left | None = None
    match test:
        case ast.Name() | ast.Attribute() | ast.Subscript() if passed:
            found = None, frozenset({_NONE})
        case ast.UnaryOp(op=ast.Not(), operand=operand):
            found = _left(operand, text, passed=not passed)
        case ast.BoolOp(op=joining, values=values) if passed == isinstance(joining, ast.And):
            found = _joined([_left(value, text, passed=passed) for value in values])
        case ast.Compare():
            found = _compared(test, passed=passed)
        case ast.Call(func=ast.Name(id="isinstance"), args=[left, classes]) if passed:
            found = _checked(left, classes, text)
        case _:
            pass
    return found


def _compared(test: ast.Compare, *, passed: bool) -> Left | None:
    """Find what a comparison leaves of the union of the value it compares: `x is None`, `x is not None`.

    Returns:
      What it leaves; all of it for an ordering (`x > 2`), which narrows nothing to any checker;
      `None` for any other.

    """
    op: ast.cmpop
    found: Left | None = None
    match test:
        case ast.Compare(ops=[ast.Is() | ast.IsNot() as op], comparators=[ast.Constant(value=None)]):
            kept: bool = passed == isinstance(op, ast.Is)
            found = (frozenset({_NONE}), frozenset()) if kept else (None, frozenset({_NONE}))
        case ast.Compare(ops=[ast.Lt() | ast.LtE() | ast.Gt() | ast.GtE()]):
            found = _ALL
        case _:
            pass
    return found


def _checked(value: ast.expr, classes: ast.expr, text: str) -> Left | None:
    """Find what `isinstance(value, classes)` leaves of a value's union (as `text`) where it passed.

    Returns:
      The members of the classes it names, or `None` for another value or classes it can't name.

    """
    named: list[ast.expr] = classes.elts if isinstance(classes, ast.Tuple) else [classes]
    if ast.unparse(value) != text or not all(isinstance(each, ast.Name | ast.Attribute) for each in named):
        return None
    return frozenset(ast.unparse(each) for each in named), frozenset()


def _joined(parts: Sequence[Left | None]) -> Left | None:
    """Join what each of several tests that all hold leaves.

    Returns:
      What they leave together, `None` if any narrows otherwise.

    """
    keep: frozenset[str] | None = None
    drop: frozenset[str] = frozenset()
    part: Left | None
    for part in parts:
        if part is None:
            return None
        keep = part[0] if keep is None else keep if part[0] is None else keep & part[0]
        drop |= part[1]
    return keep, drop


def _span(body: Sequence[ast.stmt]) -> tuple[int, int]:
    return body[0].lineno, body[-1].end_lineno or body[-1].lineno


def _bodies(stmt: ast.stmt) -> Iterator[list[ast.stmt]]:
    """Find the blocks inside a statement: a function's or class's body, a branch, a handler, a case.

    Yields:
      Each.

    """
    match stmt:
        case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef() | ast.With() | ast.AsyncWith():
            yield stmt.body
        case ast.If() | ast.For() | ast.AsyncFor() | ast.While():
            yield from (block for block in (stmt.body, stmt.orelse) if block)
        case ast.Try() | ast.TryStar():
            yield from (block for block in (stmt.body, stmt.orelse, stmt.finalbody) if block)
            yield from (handler.body for handler in stmt.handlers)
        case ast.Match():
            yield from (case.body for case in stmt.cases)
        case _:
            pass
