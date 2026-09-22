# SPDX-License-Identifier: MIT
"""Cross-module `--fix`: the return types of the functions other checked files define.

`index` reads every file once for its module name, its top-level functions' declared return types
(as `annotations.returns` picks them), and what each top-level name refers to. `calls` then gives a
file the return type of each function it imports (`from m import f`, `import m as a` then `a.f()`),
but only where every name in that type means the same thing in the file as where it was written:
otherwise the fix would name something undefined, or something else.
"""

import ast
import bisect
import builtins
import itertools
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

from constricter.rules.annotations import returns

_BUILTINS: Final = frozenset(dir(builtins))
_PACKAGE: Final = "__init__"
_SUFFIX: Final = ".py"
_HOPS: Final = 5  # how many re-exports (`from .util import f` in an `__init__`) to follow
# What a name refers to: a module and an attribute of it (`None`: the module itself).
Origin: TypeAlias = tuple[str, str | None]


class Module(NamedTuple):
    """What one file offers and uses: its name, functions' return types, and names' origins."""

    name: str
    returns: dict[str, str]
    names: dict[str, Origin]


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
            lambda folder: (folder / f"{_PACKAGE}{_SUFFIX}").is_file(),
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
    alias: ast.alias
    module: str | None
    level: int
    for stmt in tree.body:
        match stmt:
            case ast.Import():
                for alias in stmt.names:
                    if alias.asname:
                        names[alias.asname] = (alias.name, None)
                    else:  # `import a.b` binds `a`
                        names[alias.name.split(".")[0]] = (alias.name.split(".")[0], None)
            case ast.ImportFrom(module=module, level=level):
                for alias in stmt.names:
                    names[alias.asname or alias.name] = (
                        _absolute(name, module, level, is_package=is_package),
                        alias.name,
                    )
            case _:
                names.update((bound, (name, bound)) for bound in _bound(stmt))
    return names


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
    modules: dict[str, Module] = {}
    path: Path
    for path in paths:
        if path.suffix != _SUFFIX or not path.is_file():
            continue
        try:
            tree: ast.Module = ast.parse(path.read_bytes(), str(path))
        except (OSError, SyntaxError, ValueError):
            continue
        name: str = module_name(path)
        modules[name] = Module(name, returns(tree), _names(tree, name, is_package=path.stem == _PACKAGE))
    return Index(modules, sorted(modules))


def _origin(module: Module, name: str) -> Origin | None:
    if name in module.names:
        return module.names[name]
    return ("builtins", name) if name in _BUILTINS else None


def _roots(annotation: str) -> set[str]:
    """Find the names an annotation (maybe a string one) starts from.

    Returns:
      The names: `m.Row` gives `m`.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    if isinstance(tree, ast.Constant) and isinstance(tree.value, str):
        tree = ast.parse(tree.value, mode="eval").body
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}


def _function(modules: Mapping[str, Module], origin: Origin, hops: int = _HOPS) -> tuple[Module, str] | None:
    """Follow `origin` (through re-exports) to the module that defines it.

    Returns:
      That module and the function's name, or `None`.

    """
    module: Module | None = modules.get(origin[0])
    attribute: str | None = origin[1]
    if module is None or attribute is None or not hops:
        return None
    if attribute in module.returns:
        return module, attribute
    onward: Origin | None = module.names.get(attribute)
    return _function(modules, onward, hops - 1) if onward and onward[0] != module.name else None


def _submodules(catalog: Index, prefix: str) -> Iterator[Module]:
    """Find the module named `prefix`, and every module dotted under it (`pkg.util` under `pkg`).

    A module's identifier characters all sort after `.`, so the names in `[prefix, prefix + "/")` are
    exactly `prefix` itself and those starting with `prefix + "."` (`/` is the character after `.`).

    Yields:
      Each such module, by name.

    """
    start: int = bisect.bisect_left(catalog.names, prefix)
    stop: int = bisect.bisect_left(catalog.names, f"{prefix}/")
    name: str
    for name in catalog.names[start:stop]:
        yield catalog.modules[name]


def calls(catalog: Index, path: Path) -> dict[str, str]:
    """Return, for the file at `path`, the return type of each function it imports whose type it can name.

    Returns:
      Each call's name as written (`helper`, `u.helper`, `pkg.util.helper`), mapped to its type; nothing
      for a file `catalog` doesn't have (a notebook, standard input).

    """
    name: str = module_name(path)
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if path.suffix != _SUFFIX or (target := modules.get(name)) is None:
        return {}
    found: dict[str, str] = {}
    local: str
    origin: Origin
    for local, origin in target.names.items():
        if origin[1] is not None and origin[0] != name:
            _add(found, modules, target, local, origin)
        elif origin[1] is None:  # a module: `u.f()`, or `pkg.util.f()` after `import pkg.util`
            other: Module
            for other in _submodules(catalog, origin[0]):
                prefix: str = local + other.name.removeprefix(origin[0])
                function: str
                for function in other.returns:
                    _add(found, modules, target, f"{prefix}.{function}", (other.name, function))
    return found


def _add(
    found: dict[str, str],
    modules: Mapping[str, Module],
    target: Module,
    key: str,
    origin: Origin,
) -> None:
    """Record `key`'s return type in `found` if every name in it means the same in `target`."""
    defined: tuple[Module, str] | None
    if (defined := _function(modules, origin)) is None:
        return
    annotation: str = defined[0].returns[defined[1]]
    if all(_same(target, defined[0], root) for root in _roots(annotation)):
        found[key] = annotation


def _same(target: Module, defined: Module, name: str) -> bool:
    """Compare what `name` refers to in both modules.

    Returns:
      Whether it's something, and the same thing.

    """
    origin: Origin | None = _origin(target, name)
    return origin is not None and origin == _origin(defined, name)
