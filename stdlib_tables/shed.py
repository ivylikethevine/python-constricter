# SPDX-License-Identifier: MIT
"""Typeshed's stubs as `typeshed-client` reads them, bound as `stdlib_tables.stubs` holds them.

`typeshed-client` decides a stub's `sys.platform` and `sys.version_info` blocks for one platform and
Python version (a block under any other condition is read whole, both branches), lists each name a
body binds, and resolves a relative import and a `*`. What it found for a name is bound here in the
stub's own order (`_take`), so a name bound twice is what its last binding makes it.

Imported as a stub is first read (`stubs.Stubs`), not before: a build that finds the tables current
generates none, and has no `typeshed-client`.
"""

import ast
from collections.abc import Callable
from pathlib import Path
from typing import Final, TypeAlias

from typeshed_client import ImportedName, NameDict, NameInfo, OverloadedName, SearchContext, parse_ast
from typeshed_client.finder import ModulePath, get_typeshed_versions

from stdlib_tables.stubs import Imported, Klass, ModuleRef, Namespace, Read, assign, bind, define

_ALL: Final = "__all__"
_DOT: Final = "."
_Found: TypeAlias = ast.AST | ImportedName | OverloadedName  # what `typeshed-client` has for a name


def versions(stdlib: Path) -> dict[str, tuple[int, int | None]]:
    """Read typeshed's `VERSIONS`: each module's first and last Python 3 minor version (`None`: still there).

    Returns:
      Them, by module.

    """
    return {
        module: (span.min[1], None if span.max is None else span.max[1])
        for module, span in get_typeshed_versions(stdlib).items()
    }


def read(body: ast.Module, stub: Read, stdlib: Path, starred: Callable[[str], list[str]]) -> Namespace:
    """Read what `body` binds as `stub`'s configuration sees it: its module's, or a class's of it.

    `starred`: what `from m import *` imports from a module, which a `from m import __all__` takes.

    Returns:
      Its namespace.

    """
    where: SearchContext = SearchContext(
        typeshed=stdlib,
        search_path=[],
        version=(3, stub.config[1]),
        platform=stub.config[0],
    )
    module: ModulePath = ModulePath(tuple(stub.module.split(_DOT)))
    found: NameDict = parse_ast(body, where, module, file_path=stub.path, is_init=stub.package)
    space: Namespace = Namespace()
    name: str
    info: NameInfo
    for name, info in found.items():
        _take(space, name, info.ast, starred, exported=info.is_exported)
    return space


def _take(
    space: Namespace,
    name: str,
    found: _Found,
    starred: Callable[[str], list[str]],
    *,
    exported: bool,
) -> None:
    """Bind `name` to what `typeshed-client` found for it: each of its definitions, in their order.

    An import is exported only `as` its own name or by a `*`, whatever `exported` says of another.
    """
    if isinstance(found, OverloadedName):
        each: ast.AST | ImportedName
        for each in found.definitions:
            _take(space, name, each, starred, exported=exported)
    elif isinstance(found, ImportedName):
        origin: str = _DOT.join(found.module_name)
        if name == _ALL:
            space.all = starred(origin)
        elif found.name is None:
            bind(space, name, ModuleRef(origin), export=exported and name == origin)
        else:
            bind(space, name, Imported(origin, found.name), export=exported and name == found.name)
    elif isinstance(found, ast.FunctionDef | ast.AsyncFunctionDef):
        define(found, space)
    elif isinstance(found, ast.ClassDef):
        bind(space, name, Klass(found))
    elif isinstance(found, ast.stmt):
        assign(found, space)
