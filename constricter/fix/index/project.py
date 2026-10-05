# SPDX-License-Identifier: MIT
"""Cross-module `--fix`: the functions and classes other checked files define.

`index` reads every file once (see `constricter.fix.index.modules`). `calls` then gives a file the
return type of each function it imports (`from m import f`, `import m as a` then `a.f()`), and
`imported` those and each imported class's attributes and methods, but only where every name in a
type means the same thing in the file as where it was written: otherwise the fix would name
something undefined, or something else. A name the file doesn't bind that way is imported where
the type is written from under `if TYPE_CHECKING:` (`Guarded`): that import can't make a cycle.

What a module's unannotated functions return is known only once it's checked: the CLI checks the
files in `order.plan`'s order, each after those whose unannotated functions it calls (`needs`), and
adds each module's (`with_returned`) to the index for the files after it.
"""

import ast
import bisect
import builtins
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.known import Classes, Guarded, Origin, Partial, Returns
from constricter.fix.index.modules import SUFFIX, Index, Module, index, indexed, module_name, read
from constricter.rules.annotations import node_name, roots

__all__ = [
    "Imported",
    "Index",
    "Module",
    "index",
    "indexed",
    "module_name",
    "read",
]  # the index's, re-exported

_BUILTINS: Final = frozenset(dir(builtins))
_STDLIB: Final = sys.stdlib_module_names
_BUILTINS_MODULE: Final = "builtins"
_HOPS: Final = 5  # how many re-exports (`from .util import f` in an `__init__`) to follow
_DOT: Final = "."
_UNDERSCORE: Final = "_"
_FUNCTION: Final = "function"
DECORATOR: Final = "decorator"  # a function that gives back the one it decorates
_LITERAL: Final = "Literal"
CLASS: Final = "class"
ALIAS: Final = "alias"  # a type alias (see `modules.Module.aliases`)
_TYPE_VAR: Final = "type variable"
_RETURNED: Final = "returned"  # an unannotated function its `return`s type
_UNANNOTATED: Final = "unannotated"  # an unannotated function, typed or not
_PARTIAL: Final = "partial"  # a function whose declared return only an unpacking can use
OPEN: Final = "open"  # a function with a parameter left unannotated (see `modules.open_functions`)


class Imported(NamedTuple):
    """What a file's imports from other checked files offer `--fix`, each keyed as the file spells it."""

    calls: dict[str, str]
    classes: Classes
    returned: Returns = Returns()
    guarded: Mapping[str, Guarded] = {}  # names their types need imported to type check (pickled: a `dict`)
    generics: frozenset[str] = frozenset()  # its generic classes, as the file spells them
    # Its plain classes' variables typed by their values, by class (see `constricter.fix.values.classvars`).
    members: Mapping[str, Mapping[str, str]] = {}
    partial: Partial = Partial()  # the returns only an unpacking can use


def _origin(module: Module, name: str) -> Origin | None:
    if name in module.names:
        return module.names[name]
    return (_BUILTINS_MODULE, name) if name in _BUILTINS else None


def definition(
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
    return definition(modules, onward, kind, hops - 1) if onward and onward[0] != module.name else None


def _kind(module: Module, kind: str) -> Iterable[str]:
    """List what `module` defines of a `kind`: functions (declared or typed by their `return`s), classes...

    Returns:
      Their names.

    """
    found: _Defined | None = _KINDS.get(kind)
    return module.type_vars if found is None else found(module)


_Defined: TypeAlias = Callable[[Module], Iterable[str]]  # what a module defines of one kind
# What a module defines of each kind (see `_kind`): any other kind is its type variables.
_KINDS: Final[Mapping[str, _Defined]] = {
    _FUNCTION: lambda module: module.returns,
    CLASS: lambda module: module.classes,
    ALIAS: lambda module: module.aliases,
    _RETURNED: lambda module: module.returned.calls,
    _UNANNOTATED: lambda module: module.unannotated,
    OPEN: lambda module: module.open,
    _PARTIAL: lambda module: module.partial,
    DECORATOR: lambda module: module.passes,
    "signatures": lambda module: module.overloads if module.declared is None else module.declared.signatures,
}


def type_vars(catalog: Index, path: Path) -> frozenset[str]:
    """Find the names the file at `path` imports that are type variables where they're defined.

    Followed through re-exports, as calls are; for the checker to leave alone the file's own
    functions whose declared return mentions one (`def f(x: T) -> T`, with `from ._typing import T`).

    Returns:
      Them, as the file binds them; none for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return frozenset()
    return frozenset(
        local for local in {*target.names, *target.guarded} if is_type_var(catalog.modules, target, local)
    )


def is_type_var(modules: Mapping[str, Module], module: Module, name: str) -> bool:
    """Check whether `name` is a type variable in `module`: its own, or one it imports from a checked file.

    Returns:
      Whether it is.

    """
    origin: Origin | None = module.names.get(name) or module.guarded.get(name)
    return name in module.type_vars or (
        origin is not None and origin[0] != module.name and definition(modules, origin, _TYPE_VAR) is not None
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


def calls(catalog: Index, path: Path, guarded: dict[str, Guarded] | None = None) -> dict[str, str]:
    """Return, for the file at `path`, the return type of each function it imports whose type it can name.

    Returns:
      Each call's name as written (`helper`, `u.helper`, `pkg.util.helper`), mapped to its type; nothing
      for a file `catalog` doesn't have (a notebook, standard input). Without `guarded` to record the
      names its types need imported for type checking (see `Guarded`), only types needing none.

    """
    return {key: annotation for key, annotation, _ in _typed_calls(catalog, path, _FUNCTION, guarded)}


def returned(catalog: Index, path: Path, guarded: dict[str, Guarded] | None = None) -> Returns:
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
    for key, annotation, defined in _typed_calls(catalog, path, _RETURNED, guarded):
        types[key] = annotation
        if defined[1] in defined[0].returned.guesses:
            guesses[key] = defined[0].returned.guesses[defined[1]]
    return Returns(types, guesses)


def _typed_calls(
    catalog: Index,
    path: Path,
    kind: str,
    guarded: dict[str, Guarded] | None,
) -> Iterator[tuple[str, str, tuple[Module, str]]]:
    """Find the functions of a `kind` (declared or `returned`) the file at `path` imports, typed.

    Yields:
      Each call's name as written, its type, and the module and name that define it, for each whose
      type the file can write (see `_portable_call`).

    """
    name: str = module_name(path)
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(name)) is None:
        return
    # Only what it calls, or (declaring its return) passes on (`partial(helper, 1)`): all that reads one.
    wanted: frozenset[str] = target.called | target.passed if kind == _FUNCTION else target.called
    key: str
    origin: Origin
    for key, origin in spellings(catalog, target, kind):
        found: tuple[str, tuple[Module, str]] | None
        if key in wanted and (found := _portable_call(modules, target, origin, kind, guarded)) is not None:
            yield key, *found


def spellings(catalog: Index, target: Module, kind: str) -> Iterator[tuple[str, Origin]]:
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
                and any(origin[1] in _kind(package, kind) for kind in (_FUNCTION, _UNANNOTATED, CLASS))
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
    guarded: dict[str, Guarded] | None,
) -> tuple[str, tuple[Module, str]] | None:
    """Type a call to `origin`, a function of a `kind`, if `target` can write its type (see `_respelled`).

    Returns:
      Its type, as `target` writes it, and the module and name that define it; or `None`.

    """
    defined: tuple[Module, str] | None
    if (defined := definition(modules, origin, kind)) is None:
        return None
    declared: dict[str, Mapping[str, str]] = {_FUNCTION: defined[0].returns, _PARTIAL: defined[0].partial}
    annotation: str = declared.get(kind, defined[0].returned.calls)[defined[1]]
    respelled: str | None = _respelled(modules, target, defined[0], annotation, guarded)
    return None if respelled is None else (respelled, defined)


def _respelled(
    modules: Mapping[str, Module],
    target: Module,
    defined: Module,
    annotation: str,
    guarded: dict[str, Guarded] | None,
) -> str | None:
    """Write a type from module `defined` in `target`.

    As it is, if every name in it means the same in both; else, with `guarded` to record them in,
    each other name as `target` imports what it refers to (under any name), or by an import to add
    under `if TYPE_CHECKING:` (see `Guarded`), if nothing else in `target` has that name. Never one
    naming a type variable (see `is_type_var`), an alias its module assigns twice (a variable, to a
    type checker), a builtin `target` rebinds, what `defined` doesn't import at its top level (nor
    define), a checked file's generic class without its arguments, or
    in a string left inside it (an `Annotated`'s metadata) what means anything else in `target`.

    Returns:
      The type, or `None`.

    """
    names: frozenset[str] = roots(annotation)
    if _refused(modules, target, defined, annotation):
        return None
    if all(_same(target, defined, root) for root in names):
        return annotation
    if guarded is None:
        return None
    renamed: dict[str, str] = {}
    found: dict[str, Guarded] = {}
    root: str
    for root in {root for root in names if not _same(target, defined, root)}:
        origin: Origin | None = _where(defined, root)
        origin = None if origin is None else _public(modules, origin)
        name: str | None
        if (
            origin is None
            or origin[0] == _BUILTINS_MODULE
            or (name := _named(modules, target, origin, root, {**guarded, **found})) is None
        ):
            return None
        renamed[root] = name
        needed: Guarded | None
        if (needed := _import_for(target, origin, name, {**found, **guarded})) is not None:
            found[name] = needed
    guarded.update(found)
    return _renamed(annotation, renamed)


def spelled_in(
    catalog: Index,
    target: Module,
    defined: Module,
    annotation: str,
    guarded: dict[str, Guarded],
) -> str | None:
    """Write a type from module `defined` in `target` (see `_respelled`).

    Returns:
      The type, or `None`.

    """
    return _respelled(catalog.modules, target, defined, annotation, guarded)


def _refused(modules: Mapping[str, Module], target: Module, defined: Module, annotation: str) -> bool:
    """Check whether a type from module `defined` is one never written in `target` (see `_respelled`).

    Returns:
      Whether it is.

    """
    return (
        any(
            is_type_var(modules, defined, root) or _is_rebound(modules, defined, root)
            for root in roots(annotation)
        )
        or _bare(modules, defined, annotation)
        # A name in a string left inside it stays as it is: no import is added for it, and it isn't renamed.
        or any(not _same(target, defined, root) for root in _quoted(annotation))
    )


def _import_for(target: Module, origin: Origin, name: str, known: Mapping[str, Guarded]) -> Guarded | None:
    """Find the import for type checking a type's `name`, as `_named` spells `origin`, takes in `target`.

    `known`: those other types' names take already.

    Returns:
      It: the file's own (no statement), or one to add; `None` for a name an import it runs binds,
      or one written through a module it imports (`m.Row`).

    """
    if name in target.guarded:
        return Guarded(target.guarded[name], None)
    if _DOT in name or name in target.names:
        return None
    return known.get(name) or Guarded(origin, _statement(origin, name))


@lru_cache(maxsize=4096)
def _quoted(annotation: str) -> frozenset[str]:
    """Find the names in the strings left inside an annotation: `meta` in `Annotated[int, 'meta']`.

    A quoted type is read as its text before it gets here (see `annotations.written`). Not a
    `Literal`'s strings, nor a whole annotation's own quotes (see `roots`).

    Returns:
      The names.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    found: set[str] = set()
    waiting: list[ast.AST | None] = [None, tree]  # `None` at its bottom ends it
    node: ast.AST
    for node in iter(waiting.pop, None):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node is not tree:
            found.update(_names_in(node.value))
        elif not (isinstance(node, ast.Subscript) and node_name(node.value) == _LITERAL):
            waiting.extend(ast.iter_child_nodes(node))
    return frozenset(found)


def _names_in(text: str) -> set[str]:
    """Read the names a quoted part of an annotation is written with.

    Returns:
      Them; none if it isn't an expression.

    """
    try:
        return {node.id for node in ast.walk(ast.parse(text, mode="eval")) if isinstance(node, ast.Name)}
    except SyntaxError:
        return set()


def _is_rebound(modules: Mapping[str, Module], defined: Module, name: str) -> bool:
    """Check whether `name`, in module `defined`, is one its own module assigns twice (see `Module.rebound`).

    Returns:
      Whether it is: `defined`'s own, or what it imports from an indexed module.

    """
    origin: Origin | None = _where(defined, name)
    found: Origin | None = None if origin is None else _canonical(modules, origin)
    return name in defined.rebound or (
        found is not None and found[0] in modules and found[1] in modules[found[0]].rebound
    )


def _bare(modules: Mapping[str, Module], defined: Module, annotation: str) -> bool:
    """Check whether a type from module `defined` names a checked file's generic class unsubscripted.

    Returns:
      Whether it does: the class's arguments are missing.

    """
    return any(_is_generic(modules, _where(defined, bare)) for bare in _unsubscripted(annotation))


def _is_generic(modules: Mapping[str, Module], origin: Origin | None) -> bool:
    """Check whether `origin` is (through re-exports) an indexed module's generic class.

    Returns:
      Whether it is.

    """
    found: Origin | None = None if origin is None else _canonical(modules, origin)
    return found is not None and found[0] in modules and found[1] in modules[found[0]].generics


@lru_cache(maxsize=4096)
def _unsubscripted(annotation: str) -> tuple[str, ...]:
    """Name the names an annotation writes without type arguments (`Box` in `list[Box]`, not `list`).

    Returns:
      Them, in order.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    subscripted: set[int] = {id(node.value) for node in ast.walk(tree) if isinstance(node, ast.Subscript)}
    return tuple(
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name) and id(node) not in subscripted
    )


def _where(module: Module, name: str) -> Origin | None:
    """Find what `name` refers to in `module`: at run time, for type checking alone, or a builtin.

    Returns:
      Its origin, or `None`.

    """
    if name in module.names:
        return module.names[name]
    return module.guarded.get(name) or module.returned.names.get(name) or _origin(module, name)


@dataclass
class _Memo:
    """What `_canonical` and `_public` found, for the index they were last asked about.

    Each file's `imported` asks them about the same origins again (every member of every class it
    imports): with installed packages indexed too, that was most of a run's time.
    """

    modules: Mapping[str, Module] | None = None
    canonical: dict[Origin, Origin] = field(default_factory=dict[Origin, Origin])
    public: dict[Origin, Origin] = field(default_factory=dict[Origin, Origin])

    def of(self, modules: Mapping[str, Module]) -> "_Memo":
        """Keep what's found for `modules` alone (an index changes as files are checked).

        Returns:
          This memo, emptied if it was another index's.

        """
        if modules is not self.modules:
            self.modules = modules
            self.canonical = {}
            self.public = {}
        return self


_MEMO: Final = _Memo()


def canonical_origin(modules: Mapping[str, Module], origin: Origin) -> Origin:
    """Follow `origin` through indexed modules' re-exports to where it's defined (see `_canonical`).

    Returns:
      That origin.

    """
    return _canonical(modules, origin)


def public_origin(modules: Mapping[str, Module], origin: Origin) -> Origin:
    """Find where an installed package's public module re-exports `origin` (see `_public`).

    Returns:
      That origin, or `origin` itself.

    """
    return _public(modules, origin)


def _canonical(modules: Mapping[str, Module], origin: Origin) -> Origin:
    """Follow `origin` through checked modules' re-exports to where it's defined.

    Returns:
      That origin, or `origin` itself when it isn't a re-export of a checked module.

    """
    found: dict[Origin, Origin] = _MEMO.of(modules).canonical
    if origin not in found:
        found[origin] = _followed(modules, origin, _HOPS)
    return found[origin]


def _followed(modules: Mapping[str, Module], origin: Origin, hops: int) -> Origin:
    """Follow `origin` through up to `hops` re-exports (see `_canonical`).

    Returns:
      Where it leads.

    """
    module: Module | None = modules.get(origin[0])
    if module is None or origin[1] is None or not hops:
        return origin
    onward: Origin | None = module.names.get(origin[1]) or module.guarded.get(origin[1])
    return _followed(modules, onward, hops - 1) if onward and onward[0] != module.name else origin


def _named(
    modules: Mapping[str, Module],
    target: Module,
    origin: Origin,
    name: str,
    guarded: Mapping[str, Guarded],
) -> str | None:
    """Name `origin` in `target`: as an import it has names it (preferring `name`), else `name` if free.

    An import of the thing itself, else of a module that has it (`core_schema.CoreSchema`, as a type
    checker's hint is written; `pytest.MonkeyPatch`, by the public module `origin` names). A new
    import only from a module certain to resolve: a checked file's, an installed package's public
    one (not `numpy._typing`), or the standard library's (a third-party one the type's file imports
    may not be installed where the type checker runs).

    Returns:
      The name, or `None` if `target` imports nothing for it and binds `name` to something else, or
      what it's from may not resolve.

    """
    wanted: Origin = _canonical(modules, origin)
    known: dict[str, Origin] = {**target.guarded, **{n: g.origin for n, g in guarded.items()}, **target.names}
    matches: list[str] = sorted(
        (local for local, where in known.items() if _canonical(modules, where) == wanted),
        key=lambda local: local != name,
    )
    if matches:
        return matches[0]
    module: Module | None = modules.get(origin[0])
    # The module `origin` names has it when it runs, not for type checking alone.
    exported: bool = module is not None and origin[1] in module.names
    through: str | None = _through(modules, target, wanted) or (
        _through(modules, target, origin) if exported else None
    )
    if through is not None:
        return through
    public: bool = module is not None and not (module.installed and _private(origin[0]))
    resolves: bool = public or origin[0].partition(".")[0] in _STDLIB
    return None if name in known or name in _BUILTINS or not resolves else name


def _through(modules: Mapping[str, Module], target: Module, wanted: Origin) -> str | None:
    """Name `wanted` through the module defining it, if `target` imports that module to run.

    `m.Row`, after `import pkg.m as m` or `from pkg import m`. Not a module's own name, which
    importing its package needn't bind; nor through a name `target` binds as a value somewhere (a
    local `m`), which isn't the module there.

    Returns:
      The dotted name, or `None` if `target` imports no such module.

    """
    if wanted[1] is None or f"{wanted[0]}.{wanted[1]}" in modules:
        return None
    local: str
    where: Origin
    for local, where in target.names.items():
        if local not in target.shadowed and wanted[0] == (
            where[0] if where[1] is None else f"{where[0]}.{where[1]}"
        ):
            return f"{local}.{wanted[1]}"
    return None


def _public(modules: Mapping[str, Module], origin: Origin) -> Origin:
    """Find where an installed package's public module re-exports what `origin` names from a private one.

    `numpy._core.multiarray`'s `ndarray` as `numpy`'s: its shortest public module binding the name to
    the same thing.

    Returns:
      That origin; `origin` itself if it isn't in an installed package's private module, or no
      public one re-exports it.

    """
    module: Module | None = modules.get(origin[0])
    if module is None or not module.installed or origin[1] is None or not _private(origin[0]):
        return origin
    found: dict[Origin, Origin] = _MEMO.of(modules).public
    if origin not in found:
        found[origin] = _reexported(modules, origin)
    return found[origin]


def _reexported(modules: Mapping[str, Module], origin: Origin) -> Origin:
    """Find the shortest public module of an installed package re-exporting `origin` (see `_public`).

    The package's own, or the one its private twin is for (`pytest`, for `_pytest`).

    Returns:
      Its origin, or `origin` itself if there's none.

    """
    wanted: Origin = _canonical(modules, origin)
    top: str = origin[0].partition(_DOT)[0].lstrip(_UNDERSCORE)
    found: list[str] = sorted(
        (
            name
            for name, other in modules.items()
            if other.installed
            and name.partition(_DOT)[0].lstrip(_UNDERSCORE) == top
            and not _private(name)
            and origin[1] in other.names
            and (
                other.declared is None
                or other.declared.exports is None
                or origin[1] in other.declared.exports
            )
            and _canonical(modules, other.names[origin[1]]) == wanted
        ),
        key=lambda name: (name.count("."), name),
    )
    return (found[0], origin[1]) if found else origin


def _private(module: str) -> bool:
    """Check whether a module's path has a private part (`numpy._typing`).

    Returns:
      Whether it has.

    """
    return any(part.startswith("_") for part in module.split("."))


def _statement(origin: Origin, name: str) -> str:
    """Write the import that binds `name` to `origin`.

    Returns:
      It: `from m import T`, `from m import T as U`, `import m`, `import m as n`.

    """
    module: str
    attribute: str | None
    module, attribute = origin
    if attribute is None:
        return f"import {module}" + ("" if module == name else f" as {name}")
    return f"from {module} import {attribute}" + ("" if attribute == name else f" as {name}")


def _renamed(annotation: str, names: Mapping[str, str]) -> str:
    """Rename names in an annotation.

    Returns:
      The annotation.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    node: ast.AST
    for node in ast.walk(tree):  # a fresh tree: renamed in place
        if isinstance(node, ast.Name):
            node.id = names.get(node.id, node.id)
    return ast.unparse(tree)


def _same(target: Module, defined: Module, name: str) -> bool:
    """Compare what `name` refers to in both modules.

    Returns:
      Whether it's something, and the same thing.

    """
    origin: Origin | None = _origin(target, name)
    return origin is not None and origin == _origin(defined, name)


def imported(
    catalog: Index,
    path: Path,
    seeded: tuple[Mapping[str, Guarded], frozenset[str]] | None = None,
) -> Imported:
    """Return, for the file at `path`, what it imports from other checked files that it can name.

    Each function's return type (`calls`), and each class's attributes and methods' returns, keyed as
    the file spells the class (`Row`, `m.Row`); a type naming the class itself (a `Self` return) is
    spelled that way too. `seeded`: the names its fixtures' types are written with, imported for type
    checking alone (see `fixtures.visible`), whose classes' members it takes as well; and the
    attributes those types take of a module it imports (`MonkeyPatch`, in `pytest.MonkeyPatch`).

    Returns:
      Them, and the names their types need imported for type checking alone (see `Guarded`); nothing
      for a file `catalog` doesn't have (a notebook, standard input).

    """
    modules: dict[str, Module] = catalog.modules
    attributes: dict[str, dict[str, str]] = {}
    methods: dict[str, dict[str, str]] = {}
    guarded: dict[str, Guarded] = {} if seeded is None else dict(seeded[0])
    generics: set[str] = set()
    members: dict[str, Mapping[str, str]] = {}
    partial: dict[str, dict[str, str]] = {}
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(module_name(path))) is None:
        return Imported({}, Classes(attributes, methods))
    named: tuple[Mapping[str, Origin], frozenset[str]] = (
        {**{name: found.origin for name, found in guarded.items()}, **target.names},
        target.attributes if seeded is None else target.attributes | seeded[1],
    )
    key: str
    defined: tuple[Module, str]
    for key, defined in _spelled_classes(catalog, target, named, generics):
        if defined[1] in defined[0].generics:
            generics.add(key)
        if defined[1] in defined[0].plain and defined[1] in defined[0].members:
            members[key] = defined[0].members[defined[1]]
        attributes[key], methods[key], partial[key] = (
            _used(modules, (target, defined), key, table.get(defined[1]), guarded)
            for table in (defined[0].classes, defined[0].methods, defined[0].partial_methods)
        )
    found: tuple[dict[str, str], Returns, Partial] = (
        calls(catalog, path, guarded),
        returned(catalog, path, guarded),
        Partial(
            {name: each for name, each, _ in _typed_calls(catalog, path, _PARTIAL, guarded)},
            {name: each for name, each in partial.items() if each},
        ),
    )
    return Imported(
        found[0],
        Classes(attributes, methods),
        found[1],
        guarded,
        frozenset(generics),
        members,
        found[2],
    )


def _used(
    modules: Mapping[str, Module],
    where: tuple[Module, tuple[Module, str]],
    key: str,
    members: Mapping[str, str] | None,
    guarded: dict[str, Guarded],
) -> dict[str, str]:
    """Keep the types of a class's `members` that the file (`where[0]`) takes of something, and can write.

    Returns:
      Each kept member's type (see `portable`): none for most classes it can name, whose members it
      doesn't use.

    """
    used: frozenset[str] = where[0].attributes
    taken: dict[str, str] = {name: typed for name, typed in (members or {}).items() if name in used}
    return portable(modules, where, key, taken, guarded) if taken else {}


def _spelled_classes(
    catalog: Index,
    target: Module,
    named: tuple[Mapping[str, Origin], frozenset[str]],
    generics: set[str],
) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the classes other checked files define that `target` names, each as it spells it.

    `named`: the names it's to find them by, and the attributes it takes of anything. `Row` after
    `from m import Row`; `m.Row`, or `pkg.m.Row` after `import pkg.m`, for a module's, and `pkg.Row`
    for one `pkg` re-exports, where `Row` is such an attribute.
    The generic classes a module it imports re-exports are added to `generics`, as it spells them.

    Yields:
      Each spelling, and the module defining the class and its name there.

    """
    local: str
    origin: Origin
    for local, origin in _resolved(catalog, named[0]):
        spelled: list[tuple[str, Origin]] = []
        if origin[1] is not None and origin[0] != target.name:
            spelled = [(local, origin)]
        elif origin[1] is None:
            package: Module | None = catalog.modules.get(origin[0])
            spelled = [
                *(
                    (f"{local}{other.name.removeprefix(origin[0])}.{cls}", (other.name, cls))
                    for other in _submodules(catalog, origin[0])
                    for cls in other.classes
                ),
                *(
                    (f"{local}.{name}", where)
                    for name, where in ({} if package is None else package.names).items()
                    if name in named[1] and where[1] is not None and where[0] != origin[0]
                ),
            ]
            generics.update(_reexported_generics(catalog.modules, local, origin[0]))
        key: str
        where: Origin
        for key, where in spelled:
            defined: tuple[Module, str] | None
            if (defined := definition(catalog.modules, where, CLASS)) is not None:
                yield key, defined


def _reexported_generics(modules: Mapping[str, Module], local: str, name: str) -> Iterator[str]:
    """Spell the generic classes module `name` re-exports (`from ._c import OrderedSet`) as `local.C`.

    Only its own names, not its submodules': a package's `__init__` is where they're re-exported.

    Yields:
      Each spelling.

    """
    module: Module | None = modules.get(name)
    reexported: str
    origin: Origin
    for reexported, origin in ({} if module is None else module.names).items():
        defined: tuple[Module, str] | None
        if (
            origin[1] is not None
            and origin[0] != name
            and (defined := definition(modules, origin, CLASS)) is not None
            and defined[1] in defined[0].generics
        ):
            yield f"{local}.{reexported}"


def portable(
    modules: Mapping[str, Module],
    where: tuple[Module, tuple[Module, str]],
    key: str,
    types: Mapping[str, str],
    guarded: dict[str, Guarded],
) -> dict[str, str]:
    """Keep the types a class's members have that the file (`where[0]`) can write (see `_respelled`).

    One that is the class itself (`where[1]`) is written as the file spells it (`key`).

    Returns:
      Each kept member's type.

    """
    target: Module
    defined: tuple[Module, str]
    target, defined = where
    kept: dict[str, str] = {}
    member: str
    annotation: str
    for member, annotation in types.items():
        respelled: str | None
        if annotation == defined[1]:
            kept[member] = key
        elif (respelled := _respelled(modules, target, defined[0], annotation, guarded)) is not None:
            kept[member] = respelled
    return kept


def same(catalog: Index, path: Path, guarded: Mapping[str, Guarded]) -> tuple[frozenset[str], ...]:
    """Group the ways the file at `path` spells one class or alias another module defines.

    `CoreSchema` and `core_schema.CoreSchema`, in a file importing the name and its module, the name
    perhaps for type checking alone (its own import, or one `guarded` adds): one type, to value flow.

    Returns:
      Each group of two or more spellings.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return ()
    checking: list[tuple[str, Origin]] = [
        *target.guarded.items(),
        *((name, found.origin) for name, found in guarded.items()),
    ]
    groups: dict[Origin, set[str]] = {}
    kind: str
    for kind in (CLASS, ALIAS):
        name: str
        origin: Origin
        for name, origin in (*spellings(catalog, target, kind), *checking):
            defined: tuple[Module, str] | None
            if (defined := definition(catalog.modules, origin, kind)) is not None:
                groups.setdefault((defined[0].name, defined[1]), set()).add(name)
    return tuple(frozenset(group) for group in groups.values() if len(group) > 1)


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
    return catalog._replace(modules=modules)


def needs(catalog: Index, module: Module) -> set[str]:
    """Find the other modules whose unannotated functions `module` calls (see `_spelled`).

    Returns:
      Their names.

    """
    found: set[str] = set()
    key: str
    origin: Origin
    for key, origin in spellings(catalog, module, _UNANNOTATED):
        defined: tuple[Module, str] | None
        if (
            key in module.called
            and (defined := definition(catalog.modules, origin, _UNANNOTATED)) is not None
        ):
            found.add(defined[0].name)
    found.discard(module.name)
    return found
