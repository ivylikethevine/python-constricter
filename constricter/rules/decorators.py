# SPDX-License-Identifier: MIT
"""Decorators that give back the function they decorate, whose declared return still types its calls.

One the standard library has (`functools.cache`, `abc.abstractmethod`, ...), or a function whose own
signature says so: it takes `F` and returns `F`, or (a factory, called to decorate) returns a
`Callable[[F], F]`, where `F` is a type variable, or a `Callable[P, T]` returning one.
"""

import ast
import re
from typing import Final, NamedTuple, TypeAlias

from constricter.rules.syntax import import_bindings

_CALLED: Final = "()"  # after a decorator's name, as it's spelled when it's called to decorate
_CALLABLE: Final = "Callable"
_DOTTED: Final = re.compile(r"[^\W\d]\w*(?:\.[^\W\d]\w*)*")  # `name`, `pkg.util.name`
_Use: TypeAlias = tuple[bool, bool]  # whether a decorator decorates bare, and called
_Uses: TypeAlias = dict[str, _Use]  # each decorator's, by its name
# The standard library's, by where each is from.
_BARE: Final = (True, False)
_EITHER: Final = (True, True)
_FACTORY: Final = (False, True)
_LIBRARY: Final[dict[str, _Uses]] = {
    "functools": {"cache": _BARE, "lru_cache": _EITHER, "wraps": _FACTORY},
    "abc": {"abstractmethod": _BARE},
    "typing": {"final": _BARE, "override": _BARE},
    "typing_extensions": {"final": _BARE, "override": _BARE, "deprecated": _FACTORY},
    "warnings": {"deprecated": _FACTORY},
}


class Pass(NamedTuple):
    """A function that gives back what it decorates, by its signature.

    `called`: whether it's a factory, called to decorate (`@named("x")`); `type_vars`: the names its
    signature takes for type variables, which it is one only if they are.
    """

    called: bool
    type_vars: frozenset[str]

    def spelled(self, name: str) -> str:
        """Spell its use as a decorator, as `spelled` reads one.

        Returns:
          `name`, with `()` after it for a factory.

        """
        return f"{name}{_CALLED}" if self.called else name


class Held(NamedTuple):
    """A function's declared return, held back for decorators its module can't vouch for alone.

    `decorators`: those, as `spelled` reads them.
    """

    returns: str
    decorators: tuple[str, ...]


def spelled(decorator: ast.expr) -> str | None:
    """Spell a decorator as written: `cache`, `functools.cache`, and `named()` for one that's called.

    Returns:
      It, or `None` for anything but a dotted name or a call of one.

    """
    func: ast.expr
    match decorator:
        case ast.Call(func=func):
            name: str | None = _dotted(func)
            return None if name is None else f"{name}{_CALLED}"
        case _:
            return _dotted(decorator)


def _dotted(node: ast.expr) -> str | None:
    """Spell a name, or a chain of attributes on one, as written.

    Returns:
      It, or `None` if `node` is anything else.

    """
    text: str = ast.unparse(node)
    return text if _DOTTED.fullmatch(text) else None


def passes(tree: ast.Module) -> dict[str, Pass]:
    """Find the module's own top-level functions that give back the function they decorate.

    A plain `def`, defined once, undecorated: one parameter annotated as its return is (bare), or a
    return of `Callable[[A], A]` (a factory), where `A` is a name or a `Callable[..., T]`.

    Returns:
      Each one's name, and how it's used (see `Pass`).

    """
    counts: dict[str, int] = {}
    found: dict[str, Pass] = {}
    stmt: ast.stmt
    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef):
            counts[stmt.name] = counts.get(stmt.name, 0) + 1
            read: Pass | None = _pass(stmt) if isinstance(stmt, ast.FunctionDef) else None
            if read is not None and not stmt.decorator_list:
                found[stmt.name] = read
    return {name: read for name, read in found.items() if counts[name] == 1}


def _pass(func: ast.FunctionDef) -> Pass | None:
    """Read a function's signature as a decorator's that gives back what it's given.

    Returns:
      How it's used, or `None` if its signature doesn't say so.

    """
    back: ast.expr | None = func.returns
    taken: ast.expr | None = _only(func.args)
    bare: bool = back is not None and taken is not None and ast.dump(taken) == ast.dump(back)
    given: ast.expr | None = back if bare else _decorated(back)
    names: frozenset[str] | None = None if given is None else _type_vars(given)
    return None if names is None else Pass(called=not bare, type_vars=names)


def _decorated(returns: ast.expr | None) -> ast.expr | None:
    """Read what a factory's declared return says its decorator takes and gives back.

    Returns:
      `Callable[[A], A]`'s `A`, or `None` for any other annotation.

    """
    given: ast.expr
    back: ast.expr
    match returns:
        case ast.Subscript(slice=ast.Tuple(elts=[ast.List(elts=[given]), back])) if (
            _dotted(returns.value) or ""
        ).endswith(_CALLABLE) and ast.dump(given) == ast.dump(back):
            return given
        case _:
            return None


def _only(args: ast.arguments) -> ast.expr | None:
    """Read the annotation of a signature's one parameter.

    Returns:
      It, or `None` if it has more than one parameter, or the one isn't annotated.

    """
    plain: bool = not (args.kwonlyargs or args.vararg or args.kwarg)
    named: list[ast.arg] = [*args.posonlyargs, *args.args]
    return named[0].annotation if plain and len(named) == 1 else None


def _type_vars(annotation: ast.expr) -> frozenset[str] | None:
    """Name what an annotation a decorator takes and gives back must have for type variables.

    Returns:
      The name itself (`F`); or, of a `Callable[P, T]`, `T` and (if it's a name) `P`; `None` for any
      other annotation.

    """
    name: str
    taken: ast.expr
    match annotation:
        case ast.Name(id=name):
            return frozenset({name})
        case ast.Subscript(slice=ast.Tuple(elts=[taken, ast.Name(id=name)])) if (
            _dotted(annotation.value) or ""
        ).endswith(_CALLABLE):
            return frozenset({name, taken.id} if isinstance(taken, ast.Name) else {name})
        case _:
            return None


def passing(tree: ast.Module, type_vars: frozenset[str]) -> frozenset[str]:
    """Spell the decorators the module alone vouches for: its uses of them a declared return survives.

    The standard library's, as it imports them, and its own (see `passes`) whose type variables are
    all among `type_vars`, the module's.

    Returns:
      Each one as `spelled` reads it: `cache`, `functools.lru_cache()`.

    """
    found: set[str] = {
        read.spelled(name) for name, read in passes(tree).items() if read.type_vars <= type_vars
    }
    bound: str
    origin: str
    for bound, origin, _ in import_bindings(tree.body):
        module: str
        name: str
        module, _, name = origin.rpartition(".")
        uses: _Uses = (
            {f"{bound}.{known}": use for known, use in _LIBRARY[origin].items()}
            if origin in _LIBRARY
            else {bound: _LIBRARY[module][name]}
            if name in _LIBRARY.get(module, {})
            else {}
        )
        text: str
        bare: bool
        called: bool
        for text, (bare, called) in uses.items():
            found.update([text] * bare + [f"{text}{_CALLED}"] * called)
    return frozenset(found)
