# SPDX-License-Identifier: MIT
"""What each checked file offers other files' `--fix`, read once: the cross-file index (`index`).

`read` takes a file's module name, its top-level functions' declared return types (as
`annotations.returns` picks them), its classes' attributes and methods' returns (as `classes` and
`method_returns` do), its generic classes and type variables, and what each top-level name refers
to; `constricter.fix.project` looks things up in it for each file.
"""

import ast
import itertools
from collections.abc import Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Final, NamedTuple, cast

from constricter.fix.known import Origin, Returns
from constricter.fix.returned import unannotated
from constricter.rules import parsed
from constricter.rules.annotations import (
    Tables,
    defined_type_vars,
    dotted,
    generic_classes,
    module_tables,
)
from constricter.rules.walked import of_type

_PACKAGE: Final = "__init__"
SUFFIX: Final = ".py"


class Module(NamedTuple):
    """What one file offers and uses: its name, functions' return types, names' origins, and classes'.

    `classes` and `methods`: each class's attributes and its methods' returns (see `Classes`).
    """

    name: str
    returns: dict[str, str]
    names: dict[str, Origin]
    classes: Mapping[str, Mapping[str, str]] = MappingProxyType({})
    methods: Mapping[str, Mapping[str, str]] = MappingProxyType({})
    type_vars: frozenset[str] = frozenset()  # its module-level type variables
    # What it imports under a top-level `if` or `try` (`if TYPE_CHECKING:`), for `type_vars` alone.
    guarded: Mapping[str, Origin] = MappingProxyType({})
    unannotated: frozenset[str] = frozenset()  # its functions a `return` could type (`returned`)
    called: frozenset[str] = frozenset()  # what it calls through its top-level names (`f`, `u.f`)
    returned: Returns = Returns()  # what they return, once it's checked
    generics: frozenset[str] = frozenset()  # its generic classes, which a type mustn't write bare


class Index(NamedTuple):
    """Every checked file's module, and their names sorted for a module/submodule lookup."""

    modules: dict[str, Module]
    names: list[str]  # modules, sorted by name


def module_name(path: Path) -> str:
    """Name `path`'s module: its package folders (those with an `__init__.py`), then it.

    Returns:
      The dotted module name.

    """
    packages: list[Path] = list(
        itertools.takewhile(
            lambda folder: (folder / f"{_PACKAGE}{SUFFIX}").is_file(),
            path.resolve().parents,
        ),
    )
    return ".".join(
        [*(folder.name for folder in reversed(packages)), *([] if path.stem == _PACKAGE else [path.stem])],
    )


def _absolute(name: str, module: str | None, level: int, *, is_package: bool) -> str:
    """Resolve `from <.level><module> import ...` in module `name`.

    Returns:
      The absolute module name.

    """
    if not level:
        return module or ""
    package: list[str] = name.split(".") if is_package else name.split(".")[:-1]
    base: list[str] = package[: len(package) - (level - 1)] if level > 1 else package
    return ".".join([*base, *([module] if module else [])])


def _names(tree: ast.Module, name: str, *, is_package: bool) -> dict[str, Origin]:
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
            _absolute(name, stmt.module, stmt.level, is_package=is_package),
            alias.name,
        )
    return names


def _guarded(tree: ast.Module, name: str, *, is_package: bool) -> dict[str, Origin]:
    """Map the names module `name` imports under a top-level `if` or `try` (`if TYPE_CHECKING:`).

    Not what it binds at run time (`_names`): a type variable imported only for the checker is a type
    variable all the same.

    Returns:
      What each refers to.

    """
    return {
        bound: origin
        for stmt in tree.body
        if isinstance(stmt, ast.If | ast.Try | ast.TryStar)
        for node in ast.walk(stmt)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for bound, origin in _imported(node, name, is_package=is_package).items()
    }


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


def index(paths: Sequence[Path]) -> Index:
    """Read each `.py` file in `paths` (one that can't be read or parsed is left out).

    Returns:
      Each module's name, mapped to what it offers and uses.

    """
    return indexed(read(path) for path in paths)


def indexed(found: Iterable[Module | None]) -> Index:
    """Index modules already read (`read`'s, in any process): `None`s, for files it couldn't, left out.

    Returns:
      Each module's name, mapped to what it offers and uses.

    """
    modules: dict[str, Module] = {module.name: module for module in found if module is not None}
    return Index(modules, sorted(modules))


def read(path: Path) -> Module | None:
    """Read what one `.py` file offers and uses.

    Returns:
      Its module, or `None` if it isn't a `.py` file, or can't be read or parsed.

    """
    if path.suffix != SUFFIX or not path.is_file():
        return None
    source: str | None
    if (source := _source(path)) is None:
        return None
    try:
        tree: ast.Module = parsed.parse(source, str(path))
    except (SyntaxError, ValueError):  # a null byte is a ValueError
        return None
    own: Tables = module_tables(tree)
    parsed.keep(source, (tree, own))  # for the check to take, rather than parse it and read it again
    name: str = module_name(path)
    names: dict[str, Origin] = _names(tree, name, is_package=path.stem == _PACKAGE)
    return Module(
        name,
        own.returns,
        names,
        own.classes,
        own.methods,
        defined_type_vars(tree),
        _guarded(tree, name, is_package=path.stem == _PACKAGE),
        unannotated(tree.body),
        _called(tree, names),
        generics=generic_classes(tree),
    )


def _called(tree: ast.Module, names: Mapping[str, Origin]) -> frozenset[str]:
    """Find what the module calls through its top-level names: `f()`, `u.f()`, `pkg.util.f()`.

    Returns:
      Each callee, as written.

    """
    callees: Iterator[str | None] = (
        dotted(node.func) for node in cast("list[ast.Call]", of_type(tree, ast.Call))
    )
    return frozenset(callee for callee in callees if callee is not None and callee.partition(".")[0] in names)


def _source(path: Path) -> str | None:
    """Read a module's text.

    Returns:
      It, or `None` if it can't be read, or decoded (`SyntaxError`: an unknown encoding).

    """
    try:
        return parsed.text(path.read_bytes())
    except (OSError, SyntaxError, ValueError):  # UnicodeDecodeError is a ValueError
        return None
