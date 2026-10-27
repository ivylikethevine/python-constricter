"""LVA014: a function that declares no return type, fixed by what its own `return`s give (opt-in).

A plain function or method (a `def` directly in the module or a class body, not decorated) with no
return annotation is reported where it's asked for (`--extend-select LVA014`: ruff's ANN201 reports
the same, this is for its fix). The fix writes ` -> T` before the `:` ending its header: `T` is what
`returned` read from its `return`s (`Returned.calls`, certain for a module's function;
`Returned.methods`, a guess for a method, which a subclass may override), or `None` for one that can
only fall off its end or `return` bare (a method's a guess too); or, for one those don't decide,
what a traced run saw it return (`--infer-from`, a guess). None for a generator `returned` didn't
type, one that only raises, a stub (a body of `...`, `pass`, a docstring or `raise
NotImplementedError`), or a type naming what the module can't use without an import.
"""

import ast
import builtins
import itertools
import tokenize
from collections.abc import Callable, Iterator, Mapping, Sequence
from functools import partial
from typing import Final, NamedTuple, TypeAlias

from constricter.empty import Empty
from constricter.fix.core.known import Offered, Returned
from constricter.fix.core.signatures import AWAIT
from constricter.fix.values.bodies import is_generator, terminates
from constricter.fix.values.hinted import TRACED
from constricter.fix.values.inference import RETURNED
from constricter.offences import UNANNOTATED_RETURN, Edit, Fix, FixPolicy, Offence
from constricter.source.annotations import roots
from constricter.source.syntax import FUNCTION_DEFS, FunctionDef, own_returns

_NONE: Final = "None"
_TRUSTING_NONE: Final = FixPolicy()  # the policy a tree checked alone has: no guess trusted
Traced: TypeAlias = Mapping[tuple[int, int], Offered]  # what a traced run saw each function return
_UNTRACED: Final[Traced] = Empty()  # a tree checked with no trace
_BUILTINS: Final = frozenset(dir(builtins))
_OPENING: Final = frozenset("([{")
_CLOSING: Final = frozenset(")]}")
_COLON: Final = ":"
_STUB: Final = (ast.Pass,)  # a body of only these (and a docstring, `...`) declares nothing it does


def unannotated(
    tree: ast.Module,
    found: Returned,
    lines: Sequence[str],
    policy: FixPolicy = _TRUSTING_NONE,
    traced: Traced = _UNTRACED,
) -> list[Offence]:
    """Report each plain function with no return annotation, with the fix its returns decide.

    `policy`: which guesses are trusted (`unsafe-fix-select`), as a binding's fix has it. `traced`:
    what a traced run saw each function return, by where its `def` starts (`--infer-from`, see
    `traced.hints`): a guess (`traced`) for one its `return`s don't decide, where the type names
    only what the module binds.

    Returns:
      The offences, by the `def`.

    """
    usable: frozenset[str] = _BUILTINS | _bound(tree.body)
    offences: list[Offence] = []
    owner: str | None
    func: FunctionDef
    for owner, func in _plain(tree):
        if func.returns is not None:
            continue
        fix: Fix | None = None
        typed: tuple[str, bool] | None = _typed(tree, func, owner, found)
        seen: Offered | None = traced.get((func.lineno, func.col_offset)) if typed is None else None
        kinds: frozenset[str] = frozenset({RETURNED}) | found.guesses.get(_key(func, owner), frozenset())
        reason: str = "what its `return`s give"
        if typed is None and seen is not None:
            typed, kinds, reason = (seen.text, True), frozenset({TRACED}), "what a traced run saw it return"
        colon: tuple[int, int] | None = _colon(lines, func) if typed is not None else None
        if typed is not None and roots(typed[0]) <= usable and colon is not None:
            reason = "it returns nothing" if typed[0] == _NONE and seen is None else reason
            # A guess rests on its `return`s' guesses too, or the trace: a set the policy may trust.
            fix = Fix(typed[0], reason, typed[1] and not policy.trusts(kinds), Edit.SIGNATURE, colon, kinds)
        offences.append(Offence(func.lineno, func.col_offset, func.name, UNANNOTATED_RETURN, fix))
    return offences


def _plain(tree: ast.Module) -> Iterator[tuple[str | None, FunctionDef]]:
    """Yield the module's plain functions, then each top-level class's plain methods, with the class.

    Yields:
      `None` and a function, or a class's name and its method.

    """
    statement: ast.stmt
    for statement in tree.body:
        if isinstance(statement, FUNCTION_DEFS) and not statement.decorator_list:
            yield None, statement
        elif isinstance(statement, ast.ClassDef):
            member: ast.stmt
            for member in statement.body:
                if isinstance(member, FUNCTION_DEFS) and not member.decorator_list:
                    yield statement.name, member


def _typed(
    tree: ast.Module,
    func: FunctionDef,
    owner: str | None,
    found: Returned,
) -> tuple[str, bool] | None:
    """Find what `func` returns, and whether that's a guess.

    Returns:
      Its type and whether it's a guess (a method's); `None` where nothing decides it.

    """
    key: str = f"{AWAIT}{func.name}" if isinstance(func, ast.AsyncFunctionDef) else func.name
    given: str | None = found.calls.get(key) if owner is None else found.methods.get(owner, {}).get(key)
    if given is not None:
        # A method's is a guess; a function's too where its `return`s' values are only guessed.
        return given, owner is not None or _key(func, owner) in found.guesses
    if _stub(func.body) or is_generator(tree, func):
        return None
    returns: list[ast.Return] = own_returns(func.body)
    if any(each.value is not None for each in returns) or (terminates(func.body) and not returns):
        return None  # a value nothing typed, or it only raises
    return _NONE, owner is not None


def _key(func: FunctionDef, owner: str | None) -> str:
    """Name `func`'s entry in `Returned.guesses`: a method's after its class, an `async def`'s after `AWAIT`.

    Returns:
      It.

    """
    name: str = f"{AWAIT}{func.name}" if isinstance(func, ast.AsyncFunctionDef) else func.name
    return name if owner is None else f"{owner}.{name}"


def _stub(body: Sequence[ast.stmt]) -> bool:
    """Check whether `body` is a stub's: a docstring, `...`, `pass` or `raise NotImplementedError` alone.

    Returns:
      Whether it does.

    """
    statement: ast.stmt
    for statement in body:
        if isinstance(statement, _STUB):
            continue
        if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
            continue  # a docstring, or `...`
        if isinstance(statement, ast.Raise) and _not_implemented(statement.exc):
            continue
        return False
    return True


def _not_implemented(raised: ast.expr | None) -> bool:
    called: ast.expr | None = raised.func if isinstance(raised, ast.Call) else raised
    return isinstance(called, ast.Name) and called.id == NotImplementedError.__name__


def _bound(statements: Sequence[ast.stmt]) -> frozenset[str]:
    """Collect the names `statements` (a module's top level) bind, in an `if` or `try` there too.

    Returns:
      Them.

    """
    names: set[str] = set()
    statement: ast.stmt
    for statement in statements:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            names.update((alias.asname or alias.name).partition(".")[0] for alias in statement.names)
        elif isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(statement.name)
        elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
            targets: list[ast.expr] = (
                statement.targets if isinstance(statement, ast.Assign) else [statement.target]
            )
            names.update(
                node.id for target in targets for node in ast.walk(target) if isinstance(node, ast.Name)
            )
        elif isinstance(statement, ast.If):
            names |= _bound([*statement.body, *statement.orelse])
        elif isinstance(statement, ast.Try):
            handled: list[ast.stmt] = [each for handler in statement.handlers for each in handler.body]
            names |= _bound([*statement.body, *statement.orelse, *statement.finalbody, *handled])
    return frozenset(names)


def _colon(lines: Sequence[str], func: FunctionDef) -> tuple[int, int] | None:
    """Find the `:` that ends `func`'s header: the first at no depth once its parameters' `(` opened.

    Read from the `def`'s line on, as far as that `:`: a method's later lines, dedented past where
    it starts, are never tokenized.

    Returns:
      Its line (from 1) and UTF-8 byte column; `None` where the source isn't there to read.

    """
    if not lines:
        return None
    first: int = func.lineno - 1
    read: Iterator[str] = (f"{line}\n" for line in itertools.islice(lines, first, None))
    readline: Callable[[], str] = partial(next, read, "")
    row: int
    column: int
    row, column = _header_end(tokenize.generate_tokens(readline))
    line: int = first + row
    return line, len(lines[line - 1][:column].encode())


def _header_end(tokens: Iterator[tokenize.TokenInfo]) -> tuple[int, int]:
    """Find the first `:` at no depth once a `(` has opened: where a `def`'s header ends.

    Read as far as it, no further.

    Returns:
      Its row (from 1, in what was tokenized) and its column, in characters.

    """
    operators: Iterator[tokenize.TokenInfo] = (each for each in tokens if each.type == tokenize.OP)
    states: Iterator[_Depth] = itertools.accumulate(
        operators,
        _deeper,
        initial=_Depth(0, opened=False, colon=None),
    )
    return next(state.colon for state in states if state.colon is not None)


class _Depth(NamedTuple):
    """How deep a header's tokens are so far, whether a `(` has opened, and the `:` the last one is."""

    depth: int
    opened: bool
    colon: tuple[int, int] | None


def _deeper(state: _Depth, token: tokenize.TokenInfo) -> _Depth:
    """Take one more operator token into `state`.

    Returns:
      The state after it.

    """
    if token.string in _OPENING:
        return _Depth(state.depth + 1, opened=True, colon=None)
    if token.string in _CLOSING:
        return _Depth(state.depth - 1, state.opened, None)
    ends: bool = token.string == _COLON and state.opened and not state.depth
    return _Depth(state.depth, state.opened, token.start if ends else None)
