# SPDX-License-Identifier: MIT
"""Where each of a checked module's top-level names comes from (`Origin`), for `modules.read`.

What it imports, under a top-level `if` or `try` too, and what it binds itself.
"""

import ast
from collections.abc import Iterator

from constricter.fix.core.known import Origin


def absolute(name: str, module: str | None, level: int, *, is_package: bool) -> str:
    """Resolve `from <.level><module> import ...` in module `name`.

    Returns:
      The absolute module name.

    """
    if not level:
        return module or ""
    package: list[str] = name.split(".") if is_package else name.split(".")[:-1]
    base: list[str] = package[: len(package) - (level - 1)] if level > 1 else package
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
