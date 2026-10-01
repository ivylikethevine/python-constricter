# SPDX-License-Identifier: MIT
"""`--infer-with`: what a hint may name that the file doesn't bind where its annotations run.

A hint is text, and a name in it may not be a type: basedpyright shows a value that is a module by
the module's name, and a generic class without its arguments when it doesn't know them. So a name
is taken only for a class or a type alias the index of checked files and installed packages
defines: `own`, for what the file imports under `if TYPE_CHECKING:`; `vetted`, for what a hint's
edits would import (the standard library's are `hinted`'s to judge, by its tables).
"""

import ast
import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Final, NamedTuple

from constricter.fix import project, stdlib
from constricter.fix.known import Guarded, Hints, Offered, Origin
from constricter.fix.modules import SUFFIX, absolute

_PACKAGE: Final = "__init__"
_STDLIB: Final = sys.stdlib_module_names


class Own(NamedTuple):
    """The classes and aliases a file imports for type checking alone (`guarded`), and the generic ones."""

    # A plain `dict`, not a `MappingProxyType`: the CLI's worker processes are sent it, pickled.
    guarded: Mapping[str, Guarded] = {}
    generics: frozenset[str] = frozenset()


def own(catalog: project.Index, path: Path) -> Own:
    """Find the classes the file at `path` imports under a top-level `if` (`if TYPE_CHECKING:`) alone.

    Returns:
      Those the index or the standard library's tables define; none for a file `catalog` doesn't have.

    """
    target: project.Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(project.module_name(path))) is None:
        return Own()
    found: dict[str, Guarded] = {}
    generics: set[str] = set()
    name: str
    origin: Origin
    for name, origin in target.guarded.items():
        generic: bool | None = _class(catalog, origin)
        if generic is not None and name not in target.names:
            found[name] = Guarded(origin, None)
            if generic:
                generics.add(name)
    return Own(found, frozenset(generics))


def vetted(catalog: project.Index, path: Path, hints: tuple[Hints, ...]) -> tuple[Hints, ...]:
    """Drop the edits of the file at `path`'s hints that import what isn't a class, or a generic one bare.

    Returns:
      The hints, without them: such a hint is judged by what it shows alone.

    """
    if not any(found.offered for found in hints):
        return hints
    module: tuple[str, bool] = (project.module_name(path), path.stem == _PACKAGE)
    return tuple(
        found._replace(
            offered={
                where: offered
                for where, offered in found.offered.items()
                if _sound(catalog, module, offered, found.types.get(where, ""))
            },
        )
        for found in hints
    )


def _sound(catalog: project.Index, module: tuple[str, bool], offered: Offered, shown: str) -> bool:
    """Check that each import of a hint's edits names a class, and no generic one written bare.

    `module`: the hinted file's module name, and whether it's a package's `__init__`; `shown`: what
    the hint shows, which may write a class bare that its edit's spelling doesn't.

    Returns:
      Whether they do; an `import m`, which names no class, never does, nor an import from an
      installed package's private module (`numpy._core`), which its next release may move.

    """
    statement: str
    for statement in offered.imports:
        node: ast.stmt = ast.parse(statement).body[0]
        if not isinstance(node, ast.ImportFrom):
            return False
        alias: ast.alias = node.names[0]
        origin: Origin = (absolute(module[0], node.module, node.level, is_package=module[1]), alias.name)
        if origin[0].partition(".")[0] in _STDLIB:
            continue
        lone: re.Pattern[str] = re.compile(rf"(?<![\w.]){re.escape(alias.asname or alias.name)}(?![\w\[])")
        generic: bool | None = _class(catalog, origin)
        bare: bool = bool(generic and (lone.search(offered.text) or lone.search(shown)))
        if generic is None or bare or _private(catalog, origin[0]):
            return False
    return True


def _private(catalog: project.Index, name: str) -> bool:
    """Check whether module `name` is an installed package's private one.

    Returns:
      Whether it is.

    """
    module: project.Module | None = catalog.modules.get(name)
    return module is not None and module.installed and any(part.startswith("_") for part in name.split("."))


def _class(catalog: project.Index, origin: Origin) -> bool | None:
    """Find whether `origin` is a class or a type alias: an indexed module's (through re-exports).

    Or a class of the standard library's.

    Returns:
      Whether it's generic, missing its arguments written bare; `None` if it's neither, to anyone's
      knowledge.

    """
    defined: tuple[project.Module, str] | None
    if (defined := project.definition(catalog.modules, origin, project.CLASS)) is not None:
        return defined[1] in defined[0].generics
    if (defined := project.definition(catalog.modules, origin, project.ALIAS)) is not None:
        return defined[0].aliases[defined[1]]
    path: str = f"{origin[0]}.{origin[1]}"
    return stdlib.needs_arguments(path) if stdlib.defines_class(path) else None
