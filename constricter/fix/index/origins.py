"""Where each of a checked module's top-level names comes from (`Origin`), for `modules.read`.

What it imports, under a top-level `if` or `try` too, and what it binds itself.
"""

import ast
from collections.abc import Iterator, Mapping
from typing import Final, cast

from constricter.fix.core.known import Origin

_PYTEST: Final = "pytest"
_IMPORTORSKIP: Final = "importorskip"
_MODNAME: Final = "modname"  # its parameter


def absolute(name: str, module: str | None, level: int, *, is_package: bool) -> str:
    """Resolve `from <.level><module> import ...` in module `name`.

    Returns:
      The absolute module name; one past the top package, as Python refuses it, as written (`..x`),
      which names no module.

    """
    if not level:
        return module or ""
    package: list[str] = name.split(".") if is_package else name.split(".")[:-1]
    if level - 1 >= len(package):
        return "." * level + (module or "")
    base: list[str] = package[: len(package) - (level - 1)]
    return ".".join([*base, *([module] if module else [])])


def origins_of(tree: ast.Module, name: str, *, is_package: bool) -> dict[str, Origin]:
    """Map module `name`'s top-level names (the last binding wins).

    Returns:
      What each refers to.

    """
    names: dict[str, Origin] = {}
    stmt: ast.stmt
    for stmt in tree.body:
        match stmt:
            case ast.Import() | ast.ImportFrom():
                names.update(_imported(stmt, name, is_package=is_package))
            case _:
                names.update((bound, (name, bound)) for bound in _bound(stmt))
    return names


def _imported(stmt: ast.Import | ast.ImportFrom, name: str, *, is_package: bool) -> dict[str, Origin]:
    """Map the names one import in module `name` binds.

    Returns:
      What each refers to.

    """
    names: dict[str, Origin] = {}
    alias: ast.alias
    if isinstance(stmt, ast.Import):
        for alias in stmt.names:
            if alias.asname:
                names[alias.asname] = (alias.name, None)
            else:  # `import a.b` binds `a`
                names[alias.name.split(".")[0]] = (alias.name.split(".")[0], None)
        return names
    for alias in stmt.names:
        names[alias.asname or alias.name] = (
            absolute(name, stmt.module, stmt.level, is_package=is_package),
            alias.name,
        )
    return names


def guarded_origins(tree: ast.Module, name: str, *, is_package: bool) -> dict[str, Origin]:
    """Map the names module `name` imports under a top-level `if` or `try` (`if TYPE_CHECKING:`).

    Not what it binds at run time (`origins_of`): a type variable imported only for the checker is a type
    variable all the same. Not a name two of them bind to different things (one in each branch of an
    `if`): which it is, another file can't say.

    Returns:
      What each refers to.

    """
    found: dict[str, Origin] = {}
    either: set[str] = set()
    node: ast.AST
    bound: str
    origin: Origin
    for node in (
        n for stmt in tree.body if isinstance(stmt, ast.If | ast.Try | ast.TryStar) for n in ast.walk(stmt)
    ):
        if isinstance(node, ast.Import | ast.ImportFrom):
            for bound, origin in _imported(node, name, is_package=is_package).items():
                if found.setdefault(bound, origin) != origin:
                    either.add(bound)
    return {bound: origin for bound, origin in found.items() if bound not in either}


def skipped(tree: ast.Module, names: Mapping[str, Origin]) -> dict[str, Origin]:
    """Map each name the module binds to `pytest.importorskip("mod")` to that module, as an import binds it.

    Wherever it's bound, in a function too: the name is the module (`import mod as name`) when every
    binding of it in the module is such a call for that one module. `names`: the module's top-level
    names (`origins_of`), which say how it imports `pytest`.

    Returns:
      Each such name, mapped to the module's origin.

    """
    if (_PYTEST, None) not in names.values() and (_PYTEST, _IMPORTORSKIP) not in names.values():
        return {}  # no call can be it (see `_skipped_module`): most modules don't import pytest
    found: dict[str, set[str]] = {}
    calls: set[int] = set()
    node: ast.AST
    for node in ast.walk(tree):
        target: str
        stored: ast.Name
        call: ast.Call
        module: str | None
        match node:
            case ast.Assign(targets=[ast.Name(id=target) as stored], value=ast.Call() as call) if (
                module := _skipped_module(call, names)
            ) is not None:
                found.setdefault(target, set()).add(module)
                calls.add(id(stored))
            case _:
                pass
    if not found:
        return {}
    others: set[str] = set(_bindings(tree, calls))
    stmt: ast.Import | ast.ImportFrom
    for stmt in (each for each in ast.walk(tree) if isinstance(each, ast.Import | ast.ImportFrom)):
        alias: ast.alias
        for alias in stmt.names:
            bound: str = alias.asname or alias.name.partition(".")[0]
            # `import mod` (or `import mod.sub as name`) binds the module it skips for: no other binding.
            same: bool = isinstance(stmt, ast.Import) and found.get(bound) == {
                alias.name if alias.asname else bound,
            }
            if not same:
                others.add(bound)
    return {
        target: (next(iter(modules)), None)
        for target, modules in found.items()
        if len(modules) == 1 and target not in others
    }


def _bindings(tree: ast.Module, skipping: set[int]) -> Iterator[str]:
    """Walk every name the module binds anywhere but by the `importorskip` calls (`skipping`, their targets).

    Yields:
      Each name: a store, a parameter, a definition or an `except`'s.

    """
    node: ast.AST
    for node in ast.walk(tree):
        match node:
            case ast.Name(ctx=ast.Store() | ast.Del()) if id(node) not in skipping:
                yield node.id
            case ast.arg():
                yield node.arg
            case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
                yield node.name
            case ast.ExceptHandler(name=str()) | ast.MatchAs(name=str()) | ast.MatchStar(name=str()):
                yield cast("str", node.name)
            case _:
                pass


def _skipped_module(call: ast.Call, names: Mapping[str, Origin]) -> str | None:
    """Find the module `pytest.importorskip(...)` imports: its first argument, a literal.

    Returns:
      Its name, or `None` for any other call, or a name that isn't a literal.

    """
    func: ast.expr = call.func
    owner: str
    attr: str
    bound: str
    origin: Origin | None
    match func:
        case ast.Attribute(value=ast.Name(id=owner), attr=attr) if attr == _IMPORTORSKIP:
            origin = None if names.get(owner) != (_PYTEST, None) else (_PYTEST, _IMPORTORSKIP)
        case ast.Name(id=bound):
            origin = names.get(bound)
        case _:
            origin = None
    if origin != (_PYTEST, _IMPORTORSKIP):
        return None
    named: list[ast.expr] = [*call.args[:1], *(k.value for k in call.keywords if k.arg == _MODNAME)]
    module: str
    match named:
        case [ast.Constant(value=str() as module)] if all(part.isidentifier() for part in module.split(".")):
            return module
        case _:
            return None


def starred(tree: ast.Module, name: str, *, is_package: bool) -> tuple[str, ...]:
    """List the modules module `name` imports everything from (`from .main import *`), in order.

    At its top level, or under a top-level `if` or `try` (pydantic's `__init__`, for type checking).

    Returns:
      Their absolute names.

    """
    nodes: Iterator[ast.AST] = (
        node
        for stmt in tree.body
        for node in (ast.walk(stmt) if isinstance(stmt, ast.If | ast.Try | ast.TryStar) else (stmt,))
    )
    return tuple(
        absolute(name, node.module, node.level, is_package=is_package)
        for node in nodes
        if isinstance(node, ast.ImportFrom) and [alias.name for alias in node.names] == ["*"]
    )


def _bound(stmt: ast.stmt) -> Iterator[str]:
    """Walk a top-level statement other than an import.

    Yields:
      Each name it binds.

    """
    node: ast.AST
    match stmt:
        case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
            yield stmt.name
        case ast.Assign() | ast.AnnAssign() | ast.AugAssign():
            targets: list[ast.expr] = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            for node in (n for target in targets for n in ast.walk(target)):
                if isinstance(node, ast.Name):
                    yield node.id
        case _:
            pass
