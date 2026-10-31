"""How a file writes what other checked files define: their functions' returns and their types.

`calls` gives a file the return type of each function it imports (`from m import f`, `import m as a`
then `a.f()`), `returned` what its unannotated ones return once checked, each spelled as the file
can write it (`spelled_in`): every name in the type meaning the same in the file as where it was
written, through a re-export's canonical origin (`canonical_origin`) or its public one
(`public_origin`), else no fix. `portable` and `generic_portable` spell a type another file wrote.
"""

import ast
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Final

from constricter.fix.core.known import Guarded, Origin, Returns
from constricter.fix.index.modules import (
    Index,
    Module,
    classes_under,
    exported,
    module_at,
    takes,
    written_under,
)
from constricter.fix.index.project import (
    ALIAS,
    BUILTINS,
    CLASS,
    DOT,
    FUNCTION,
    HOPS,
    PARTIAL,
    RETURNED,
    STDLIB,
    UNANNOTATED,
    definition,
    is_type_var,
    kind_of,
    starred_names,
    starred_origin,
)
from constricter.fix.index.strings import quoted
from constricter.fix.index.stubs.atoms import private_name
from constricter.source.annotations import roots
from constricter.source.declarations import GenericClass

_BUILTINS_MODULE: Final = "builtins"


_UNDERSCORE: Final = "_"
_NO_NAMES: Final[frozenset[str]] = frozenset()  # no names left as they are (see `spelled_in`)
_SELF: Final = "Self"  # a generic class's method returning its receiver (see `GenericClass`)
_FOLLOWED: Final = frozenset({FUNCTION, RETURNED})  # the kinds followed through a package's re-exports


_TYPES: Final = frozenset({CLASS, ALIAS})  # the kinds a fix may write a name of that the file doesn't
_REEXPORTED: Final = "re-exported"  # in the memo's key after a kind: what a package names of its submodules'


def _origin(module: Module, name: str) -> Origin | None:
    if name in module.names:
        return module.names[name]
    return (_BUILTINS_MODULE, name) if name in BUILTINS else None


def calls(catalog: Index, path: Path, guarded: dict[str, Guarded] | None = None) -> dict[str, str]:
    """Return, for the file at `path`, the return type of each function it imports whose type it can name.

    Returns:
      Each call's name as written (`helper`, `u.helper`, `pkg.util.helper`), mapped to its type; nothing
      for a file `catalog` doesn't have (a notebook, standard input). Without `guarded` to record the
      names its types need imported for type checking (see `Guarded`), only types needing none.

    """
    return {key: annotation for key, annotation, _ in typed_calls(catalog, path, FUNCTION, guarded)}


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
    for key, annotation, defined in typed_calls(catalog, path, RETURNED, guarded):
        types[key] = annotation
        if defined[1] in defined[0].returned.guesses:
            guesses[key] = defined[0].returned.guesses[defined[1]]
    return Returns(types, guesses)


def typed_calls(
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
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if (target := module_at(catalog, path)) is None:
        return
    # Only what it calls, or (declaring its return) passes on (`partial(helper, 1)`): all that reads one.
    wanted: frozenset[str] = target.called | target.passed if kind == FUNCTION else target.called
    key: str
    origin: Origin
    for key, origin in spellings(catalog, target, kind):
        found: tuple[str, tuple[Module, str]] | None
        if key in wanted and (found := _portable_call(modules, target, origin, kind, guarded)) is not None:
            yield key, *found


def spellings(catalog: Index, target: Module, kind: str) -> Iterator[tuple[str, Origin]]:
    """Find what `target` imports that other modules may define as a `kind`, as it spells each call.

    Yields:
      Each name as written (`helper`, `u.helper`, `pkg.util.helper`), and where it's from: a module's
      function, or a declared one it imports in turn (`pd.array`), only where the file writes it.

    """
    local: str
    origin: Origin
    for local, origin in resolved(catalog, target.names):
        if origin[1] is not None and origin[0] != target.name:
            yield local, origin
        elif origin[1] is None:  # a module: `u.f()`, or `pkg.util.f()` after `import pkg.util`
            if kind in _TYPES:  # a fix may write one the file doesn't yet: every one
                yield from classes_under(catalog, local, origin[0], kind)
                yield from _named_under(catalog, local, origin[0], kind)
                continue
            key: str
            sub: str
            function: str
            for key, sub, function in written_under(target, local):  # of all it has, those the file calls
                other: Module | None = catalog.modules.get(origin[0] + sub)
                # A function the package re-exports (`pd.date_range`, `nx.complement` by a `*` import):
                # declared, or typed by its `return`s.
                followed: bool = (
                    kind in _FOLLOWED
                    and other is not None
                    and (
                        takes(other, function) or starred_origin(catalog.modules, other, function) is not None
                    )
                )
                if other is not None and (followed or function in kind_of(other, kind)):
                    yield key, (other.name, function)


def _named_under(catalog: Index, local: str, package: str, kind: str) -> Iterator[tuple[str, Origin]]:
    """Spell the classes (or aliases) `package` imports from its submodules, as a file importing it may.

    `local`: the name the file imports it as.

    `pd.DataFrame`, by `from pandas.core.api import DataFrame` in `pandas/__init__.py`: the class
    `pandas.core.frame` defines, which `classes_under` spells only by its own module.

    Returns:
      Each spelling, and the module that defines it and its name there.

    """
    key: tuple[str, str] = (package, f"{kind} {_REEXPORTED}")
    found: list[tuple[str, Origin]] | None
    if (found := None if catalog.memo is None else catalog.memo.under.get(key)) is None:
        top: Module | None = catalog.modules.get(package)
        named: Iterable[tuple[str, Origin]] = (
            () if top is None else {**starred_names(catalog.modules, top), **exported(top)}.items()
        )
        found = []
        name: str
        origin: Origin
        for name, origin in named:
            defined: tuple[Module, str] | None
            if not origin[0].startswith(package + DOT):
                continue
            if defined := definition(catalog.modules, origin, kind):
                found.append((f"{DOT}{name}", (defined[0].name, defined[1])))
        if catalog.memo is not None:
            catalog.memo.under[key] = found
    return ((f"{local}{suffix}", origin) for suffix, origin in found)


def resolved(catalog: Index, names: Mapping[str, Origin]) -> Iterator[tuple[str, Origin]]:
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
                and any(origin[1] in kind_of(package, kind) for kind in (FUNCTION, UNANNOTATED, CLASS))
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
    """Type a call to `origin`, a function of a `kind`, if `target` can write its type (see `spelled_in`).

    Returns:
      Its type, as `target` writes it, and the module and name that define it; or `None`.

    """
    defined: tuple[Module, str] | None
    if (defined := definition(modules, origin, kind)) is None:
        return None
    declared: dict[str, Mapping[str, str]] = {FUNCTION: defined[0].returns, PARTIAL: defined[0].partial}
    annotation: str = declared.get(kind, defined[0].returned.calls)[defined[1]]
    respelled: str | None = spelled_in(modules, (target, defined[0]), annotation, guarded)
    return None if respelled is None else (respelled, defined)


def spelled_in(
    modules: Mapping[str, Module],
    where: tuple[Module, Module],
    annotation: str,
    guarded: dict[str, Guarded] | None,
    free: frozenset[str] = _NO_NAMES,
) -> str | None:
    """Write a type from module `defined` in `target` (`where`).

    As it is, if every name in it means the same in both; else, with `guarded` to record them in,
    each other name as `target` imports what it refers to (under any name), or by an import to add
    under `if TYPE_CHECKING:` (see `Guarded`), if nothing else in `target` has that name. Never one
    naming a type variable (see `is_type_var`), an alias its module assigns twice (a variable, to a
    type checker), a builtin `target` rebinds, what `defined` doesn't import at its top level (nor
    define), a checked file's generic class without its arguments, or
    in a string left inside it (an `Annotated`'s metadata) what means anything else in `target`.
    `free`: names left as they are, a generic class's type parameters that its receiver binds.

    Returns:
      The type, or `None`.

    """
    target: Module
    defined: Module
    target, defined = where
    names: frozenset[str] = roots(annotation) - free
    if _refused(modules, where, annotation, free):
        return None
    differing: set[str]
    if not (differing := {root for root in names if not _same(target, defined, root)}):
        return annotation
    if guarded is None:
        return None
    written: dict[str, str] = {}
    found: dict[str, Guarded] = {}
    root: str
    for root in differing:
        origin: Origin | None = _where(defined, root)
        origin = None if origin is None else public_origin(modules, origin)
        name: str | None
        if (
            origin is None
            or origin[0] == _BUILTINS_MODULE
            or (name := _named(modules, target, origin, root, {**guarded, **found})) is None
        ):
            return None
        written[root] = name
        needed: Guarded | None
        if (needed := _import_for(target, origin, name, {**found, **guarded})) is not None:
            found[name] = needed
    guarded.update(found)
    return renamed(annotation, written)


def _refused(
    modules: Mapping[str, Module],
    where: tuple[Module, Module],
    annotation: str,
    free: frozenset[str] = _NO_NAMES,
) -> bool:
    """Check whether a type from `defined` is one never written in `target` (`where`, see `spelled_in`).

    Returns:
      Whether it is.

    """
    target: Module
    defined: Module
    target, defined = where
    return (
        any(
            is_type_var(modules, defined, root) or _is_rebound(modules, defined, root)
            for root in roots(annotation) - free
        )
        or _bare(modules, defined, annotation)
        # A name in a string left inside it stays as it is: no import is added for it, and it isn't renamed.
        or any(not _same(target, defined, root) for root in quoted(annotation))
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
    if DOT in name or name in target.names:
        return None
    return known.get(name) or Guarded(origin, _statement(origin, name))


def _is_rebound(modules: Mapping[str, Module], defined: Module, name: str) -> bool:
    """Check whether `name`, in module `defined`, is one its own module assigns twice (see `Module.rebound`).

    Returns:
      Whether it is: `defined`'s own, or what it imports from an indexed module.

    """
    origin: Origin | None = _where(defined, name)
    found: Origin | None = None if origin is None else canonical_origin(modules, origin)
    return name in defined.rebound or (
        found is not None and found[0] in modules and found[1] in modules[found[0]].rebound
    )


def _bare(modules: Mapping[str, Module], defined: Module, annotation: str) -> bool:
    """Check whether a type from module `defined` names a checked file's generic class unsubscripted.

    Returns:
      Whether it does: the class's arguments are missing.

    """
    return any(is_generic(modules, _where(defined, bare)) for bare in _unsubscripted(annotation))


def is_generic(modules: Mapping[str, Module], origin: Origin | None) -> bool:
    """Check whether `origin` is (through re-exports) an indexed module's generic class.

    Returns:
      Whether it is.

    """
    found: Origin | None = None if origin is None else canonical_origin(modules, origin)
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
    return (
        module.guarded.get(name)
        or module.returned.names.get(name)
        or ((_BUILTINS_MODULE, name) if name in BUILTINS else None)
    )


@dataclass
class _Memo:
    """What `canonical_origin` and `public_origin` found, for the index they were last asked about.

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
    """Follow `origin` through checked modules' re-exports to where it's defined.

    Returns:
      That origin, or `origin` itself when it isn't a re-export of a checked module.

    """
    found: dict[Origin, Origin] = _MEMO.of(modules).canonical
    if origin not in found:
        found[origin] = _followed(modules, origin, HOPS)
    return found[origin]


def _followed(modules: Mapping[str, Module], origin: Origin, hops: int) -> Origin:
    """Follow `origin` through up to `hops` re-exports (see `canonical_origin`).

    Returns:
      Where it leads.

    """
    module: Module | None = modules.get(origin[0])
    if module is None or origin[1] is None or not hops:
        return origin
    onward: Origin | None = (
        module.names.get(origin[1])
        or module.guarded.get(origin[1])
        or starred_origin(modules, module, origin[1])
    )
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
    wanted: Origin = canonical_origin(modules, origin)
    known: dict[str, Origin] = {**target.guarded, **{n: g.origin for n, g in guarded.items()}, **target.names}
    matches: list[str] = sorted(
        (local for local, where in known.items() if canonical_origin(modules, where) == wanted),
        key=lambda local: local != name,
    )
    if matches:
        return matches[0]
    module: Module | None = modules.get(origin[0])
    # The module `origin` names has it when it runs, not for type checking alone.
    runs: bool = module is not None and origin[1] in module.names
    through: str | None = _through(modules, target, wanted) or (
        _through(modules, target, origin) if runs else None
    )
    if through is not None:
        return through
    public: bool = module is not None and not (module.installed and private_name(origin[0]))
    resolves: bool = public or origin[0].partition(".")[0] in STDLIB
    return None if name in known or name in BUILTINS or not resolves else name


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


def public_origin(modules: Mapping[str, Module], origin: Origin) -> Origin:
    """Find where an installed package's public module re-exports what `origin` names from a private one.

    `numpy._core.multiarray`'s `ndarray` as `numpy`'s: its shortest public module binding the name to
    the same thing.

    Returns:
      That origin; `origin` itself if it isn't in an installed package's private module, or no
      public one re-exports it.

    """
    module: Module | None = modules.get(origin[0])
    if module is None or not module.installed or origin[1] is None or not private_name(origin[0]):
        return origin
    found: dict[Origin, Origin] = _MEMO.of(modules).public
    if origin not in found:
        found[origin] = _reexported(modules, origin)
    return found[origin]


def _reexported(modules: Mapping[str, Module], origin: Origin) -> Origin:
    """Find the shortest public module of an installed package re-exporting `origin` (see `public_origin`).

    The package's own, or the one its private twin is for (`pytest`, for `_pytest`).

    Returns:
      Its origin, or `origin` itself if there's none.

    """
    wanted: Origin = canonical_origin(modules, origin)
    top: str = origin[0].partition(DOT)[0].lstrip(_UNDERSCORE)
    found: list[str] = sorted(
        (
            name
            for name, other in modules.items()
            if other.installed
            and name.partition(DOT)[0].lstrip(_UNDERSCORE) == top
            and not private_name(name)
            and origin[1] in other.names
            and (
                other.declared is None
                or other.declared.exports is None
                or origin[1] in other.declared.exports
            )
            and canonical_origin(modules, other.names[origin[1]]) == wanted
        ),
        key=lambda name: (name.count("."), name),
    )
    return (found[0], origin[1]) if found else origin


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


def renamed(annotation: str, names: Mapping[str, str]) -> str:
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


def portable(
    modules: Mapping[str, Module],
    where: tuple[Module, tuple[Module, str]],
    key: str,
    types: Mapping[str, str],
    guarded: dict[str, Guarded],
) -> dict[str, str]:
    """Keep the types a class's members have that the file (`where[0]`) can write (see `spelled_in`).

    One that is the class itself (`where[1]`) is written as the file spells it (`key`).

    Returns:
      Each kept member's type.

    """
    return _portable(modules, where, key, types, (guarded, _NO_NAMES))


def generic_portable(
    modules: Mapping[str, Module],
    where: tuple[Module, tuple[Module, str]],
    key: str,
    klass: GenericClass,
    guarded: dict[str, Guarded],
) -> GenericClass:
    """Keep the members of a generic class the file (`where[0]`) takes of something, as it can write them.

    As `portable` keeps a plain class's, but its type parameters and `Self` stay as they are, for the
    receiver to bind; its bases, another file's names, aren't followed.

    Returns:
      The class's parameters, and those members' types.

    """
    used: frozenset[str] = where[0].attributes
    writing: tuple[dict[str, Guarded], frozenset[str]] = (guarded, frozenset(klass.params) | {_SELF})
    tables: list[dict[str, str]] = [
        _portable(
            modules,
            where,
            key,
            {name: typed for name, typed in table.items() if name in used},
            writing,
        )
        for table in (klass.attributes, klass.methods)
    ]
    return GenericClass(klass.params, tables[0], tables[1], bound=klass.bound)


def _portable(
    modules: Mapping[str, Module],
    where: tuple[Module, tuple[Module, str]],
    key: str,
    types: Mapping[str, str],
    writing: tuple[dict[str, Guarded], frozenset[str]],
) -> dict[str, str]:
    """Keep the types `portable` keeps (`writing`: where to record imports, and names left as they are).

    Returns:
      Each kept member's type.

    """
    guarded: dict[str, Guarded]
    free: frozenset[str]
    guarded, free = writing
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
        elif (respelled := spelled_in(modules, (target, defined[0]), annotation, guarded, free)) is not None:
            kept[member] = respelled
    return kept
