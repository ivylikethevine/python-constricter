# SPDX-License-Identifier: MIT
"""Cross-module `--fix`: the functions and classes other checked files define.

`index` reads every file once for its module name, its top-level functions' declared return types
(as `annotations.returns` picks them), its classes' attributes and methods' returns (as `classes`
and `method_returns` do), and what each top-level name refers to. `calls` then gives a file the
return type of each function it imports (`from m import f`, `import m as a` then `a.f()`), and
`imported` those and each imported class's attributes and methods, but only where every name in a
type means the same thing in the file as where it was written: otherwise the fix would name
something undefined, or something else.

What a module's unannotated functions return is known only once it's checked: the CLI checks the
files in `order.plan`'s order, each after those whose unannotated functions it calls (`needs`), and
adds each module's (`with_returned`) to the index for the files after it.
"""

import ast
import bisect
import builtins
import itertools
from collections.abc import Iterable, Iterator, Mapping, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.known import Classes, Returns
from constricter.fix.returned import unannotated
from constricter.rules import parsed
from constricter.rules.annotations import Tables, defined_type_vars, dotted, module_tables
from constricter.rules.walked import of_type

_BUILTINS: Final = frozenset(dir(builtins))
_PACKAGE: Final = "__init__"
_SUFFIX: Final = ".py"
_HOPS: Final = 5  # how many re-exports (`from .util import f` in an `__init__`) to follow
_FUNCTION: Final = "function"
_CLASS: Final = "class"
_TYPE_VAR: Final = "type variable"
_RETURNED: Final = "returned"  # an unannotated function its `return`s type
_UNANNOTATED: Final = "unannotated"  # an unannotated function, typed or not
# What a name refers to: a module and an attribute of it (`None`: the module itself).
Origin: TypeAlias = tuple[str, str | None]


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


class Imported(NamedTuple):
    """What a file's imports from other checked files offer `--fix`, each keyed as the file spells it."""

    calls: dict[str, str]
    classes: Classes
    returned: Returns = Returns()


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
    if path.suffix != _SUFFIX or not path.is_file():
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


def _defined(
    modules: Mapping[str, Module],
    origin: Origin,
    kind: str,
    hops: int = _HOPS,
) -> tuple[Module, str] | None:
    """Follow `origin` (through re-exports) to the module that defines it as a `kind` (function, class).

    Returns:
      That module and the name, or `None`.

    """
    module: Module | None = modules.get(origin[0])
    attribute: str | None = origin[1]
    if module is None or attribute is None or not hops:
        return None
    if attribute in _kind(module, kind):
        return module, attribute
    onward: Origin | None = module.names.get(attribute)
    return _defined(modules, onward, kind, hops - 1) if onward and onward[0] != module.name else None


def _kind(module: Module, kind: str) -> Iterable[str]:
    """List what `module` defines of a `kind`: functions (declared or typed by their `return`s), classes...

    Returns:
      Their names.

    """
    match kind:
        case "function":
            return module.returns
        case "class":
            return module.classes
        case "returned":
            return module.returned.calls
        case "unannotated":
            return module.unannotated
        case _:
            return module.type_vars


def type_vars(catalog: Index, path: Path) -> frozenset[str]:
    """Find the names the file at `path` imports that are type variables where they're defined.

    Followed through re-exports, as calls are; for the checker to leave alone the file's own
    functions whose declared return mentions one (`def f(x: T) -> T`, with `from ._typing import T`).

    Returns:
      Them, as the file binds them; none for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != _SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return frozenset()
    return frozenset(
        local for local in {*target.names, *target.guarded} if _is_type_var(catalog.modules, target, local)
    )


def _is_type_var(modules: Mapping[str, Module], module: Module, name: str) -> bool:
    """Check whether `name` is a type variable in `module`: its own, or one it imports from a checked file.

    Returns:
      Whether it is.

    """
    origin: Origin | None = module.names.get(name) or module.guarded.get(name)
    return name in module.type_vars or (
        origin is not None and origin[0] != module.name and _defined(modules, origin, _TYPE_VAR) is not None
    )


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
    return {key: annotation for key, annotation, _ in _typed_calls(catalog, path, _FUNCTION)}


def returned(catalog: Index, path: Path) -> Returns:
    """Return, for the file at `path`, what the unannotated functions it imports return, as `calls` does.

    Only those of modules already checked (`Module.returned`), each with what it rests on if a guess.

    Returns:
      Each call's type, and a guessed one's origins; nothing for a file `catalog` doesn't have.

    """
    types: dict[str, str] = {}
    guesses: dict[str, frozenset[str]] = {}
    key: str
    annotation: str
    defined: tuple[Module, str]
    for key, annotation, defined in _typed_calls(catalog, path, _RETURNED):
        types[key] = annotation
        if defined[1] in defined[0].returned.guesses:
            guesses[key] = defined[0].returned.guesses[defined[1]]
    return Returns(types, guesses)


def _typed_calls(catalog: Index, path: Path, kind: str) -> Iterator[tuple[str, str, tuple[Module, str]]]:
    """Find the functions of a `kind` (declared or `returned`) the file at `path` imports, typed.

    Yields:
      Each call's name as written, its type, and the module and name that define it, for each whose
      type means the same in the file (see `_portable_call`).

    """
    name: str = module_name(path)
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if path.suffix != _SUFFIX or (target := modules.get(name)) is None:
        return
    key: str
    origin: Origin
    for key, origin in _spelled(catalog, target, kind):
        found: tuple[str, tuple[Module, str]] | None
        # Only what it calls: the modules `plan` put it after, whatever else is checked by then.
        if (kind != _RETURNED or key in target.called) and (
            found := _portable_call(modules, target, origin, kind)
        ) is not None:
            yield key, *found


def _spelled(catalog: Index, target: Module, kind: str) -> Iterator[tuple[str, Origin]]:
    """Find what `target` imports that other modules may define as a `kind`, as it spells each call.

    Yields:
      Each name as written (`helper`, `u.helper`, `pkg.util.helper`), and where it's from.

    """
    local: str
    origin: Origin
    for local, origin in _resolved(catalog, target.names):
        if origin[1] is not None and origin[0] != target.name:
            yield local, origin
        elif origin[1] is None:  # a module: `u.f()`, or `pkg.util.f()` after `import pkg.util`
            other: Module
            for other in _submodules(catalog, origin[0]):
                prefix: str = local + other.name.removeprefix(origin[0])
                yield from (
                    (f"{prefix}.{function}", (other.name, function)) for function in _kind(other, kind)
                )


def _resolved(catalog: Index, names: Mapping[str, Origin]) -> Iterator[tuple[str, Origin]]:
    """Take each name imported from a package that is its submodule (`from pkg import util`) as that module.

    Unless the package itself defines the name (a function, class or type).

    Yields:
      Each name, and what it refers to.

    """
    local: str
    origin: Origin
    for local, origin in names.items():
        package: Module | None
        submodule: str = f"{origin[0]}.{origin[1]}" if origin[0] else origin[1] or ""
        if (
            origin[1] is not None
            and submodule in catalog.modules
            and not (
                (package := catalog.modules.get(origin[0])) is not None
                and any(origin[1] in _kind(package, kind) for kind in (_FUNCTION, _UNANNOTATED, _CLASS))
            )
        ):
            yield local, (submodule, None)
        else:
            yield local, origin


def _portable_call(
    modules: Mapping[str, Module],
    target: Module,
    origin: Origin,
    kind: str,
) -> tuple[str, tuple[Module, str]] | None:
    """Type a call to `origin`, a function of a `kind`, if every name in its type means the same in `target`.

    Returns:
      Its type, and the module and name that define it; or `None`.

    """
    defined: tuple[Module, str] | None
    if (defined := _defined(modules, origin, kind)) is None:
        return None
    annotation: str = (defined[0].returns if kind == _FUNCTION else defined[0].returned.calls)[defined[1]]
    roots: set[str] = _roots(annotation)
    if all(_same(target, defined[0], root) for root in roots) and not any(
        _is_type_var(modules, defined[0], root) for root in roots
    ):
        return annotation, defined
    return None


def _same(target: Module, defined: Module, name: str) -> bool:
    """Compare what `name` refers to in both modules.

    Returns:
      Whether it's something, and the same thing.

    """
    origin: Origin | None = _origin(target, name)
    return origin is not None and origin == _origin(defined, name)


def imported(catalog: Index, path: Path) -> Imported:
    """Return, for the file at `path`, what it imports from other checked files that it can name.

    Each function's return type (`calls`), and each class's attributes and methods' returns, keyed as
    the file spells the class (`Row`, `m.Row`); a type naming the class itself (a `Self` return) is
    spelled that way too.

    Returns:
      Them; nothing for a file `catalog` doesn't have (a notebook, standard input).

    """
    name: str = module_name(path)
    modules: dict[str, Module] = catalog.modules
    attributes: dict[str, dict[str, str]] = {}
    methods: dict[str, dict[str, str]] = {}
    target: Module | None
    if path.suffix != _SUFFIX or (target := modules.get(name)) is None:
        return Imported({}, Classes(attributes, methods))
    local: str
    origin: Origin
    for local, origin in _resolved(catalog, target.names):
        spelled: list[tuple[str, Origin]] = []
        if origin[1] is not None and origin[0] != name:
            spelled = [(local, origin)]
        elif origin[1] is None:  # a module: `m.Row`, or `pkg.m.Row` after `import pkg.m`
            spelled = [
                (f"{local}{other.name.removeprefix(origin[0])}.{cls}", (other.name, cls))
                for other in _submodules(catalog, origin[0])
                for cls in other.classes
            ]
        key: str
        where: Origin
        for key, where in spelled:
            defined: tuple[Module, str] | None
            if (defined := _defined(modules, where, _CLASS)) is not None:
                attributes[key] = _portable(modules, target, defined, key, defined[0].classes[defined[1]])
                methods[key] = _portable(
                    modules,
                    target,
                    defined,
                    key,
                    defined[0].methods.get(defined[1], {}),
                )
    return Imported(calls(catalog, path), Classes(attributes, methods), returned(catalog, path))


def _portable(
    modules: Mapping[str, Module],
    target: Module,
    defined: tuple[Module, str],
    key: str,
    types: Mapping[str, str],
) -> dict[str, str]:
    """Keep the types a class's members have that `target` can write as they are (see `_same`).

    One that is the class itself is written as `target` spells it (`key`); one that mentions a type
    variable (imported where the class is defined, see `_is_type_var`) is dropped.

    Returns:
      Each kept member's type.

    """
    kept: dict[str, str] = {}
    member: str
    annotation: str
    for member, annotation in types.items():
        if annotation == defined[1]:
            kept[member] = key
        elif all(
            _same(target, defined[0], root) and not _is_type_var(modules, defined[0], root)
            for root in _roots(annotation)
        ):
            kept[member] = annotation
    return kept


def with_returned(catalog: Index, found: Mapping[str, Returns]) -> Index:
    """Record what checked modules' unannotated functions return (`found`, by module name).

    Returns:
      The index, with them.

    """
    modules: dict[str, Module] = dict(catalog.modules)
    name: str
    returns: Returns
    for name, returns in found.items():
        if name in modules:
            modules[name] = modules[name]._replace(returned=returns)
    return Index(modules, catalog.names)


def needs(catalog: Index, module: Module) -> set[str]:
    """Find the other modules whose unannotated functions `module` calls (see `_spelled`).

    Returns:
      Their names.

    """
    found: set[str] = set()
    key: str
    origin: Origin
    for key, origin in _spelled(catalog, module, _UNANNOTATED):
        defined: tuple[Module, str] | None
        if key in module.called and (defined := _defined(catalog.modules, origin, _UNANNOTATED)) is not None:
            found.add(defined[0].name)
    found.discard(module.name)
    return found
