# SPDX-License-Identifier: MIT
"""Cross-module `--fix`: the functions and classes other checked files define.

`index` reads every file once (see `constricter.fix.modules`). `calls` then gives a file the
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
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Final, NamedTuple

from constricter.fix.known import Classes, Guarded, Origin, Returns
from constricter.fix.modules import SUFFIX, Index, Module, index, indexed, module_name, read
from constricter.rules.annotations import roots

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
_FUNCTION: Final = "function"
_CLASS: Final = "class"
_TYPE_VAR: Final = "type variable"
_RETURNED: Final = "returned"  # an unannotated function its `return`s type
_UNANNOTATED: Final = "unannotated"  # an unannotated function, typed or not
OPEN: Final = "open"  # a function with a parameter left unannotated (see `modules.open_functions`)


class Imported(NamedTuple):
    """What a file's imports from other checked files offer `--fix`, each keyed as the file spells it."""

    calls: dict[str, str]
    classes: Classes
    returned: Returns = Returns()
    guarded: Mapping[str, Guarded] = {}  # names their types need imported to type check (pickled: a `dict`)
    generics: frozenset[str] = frozenset()  # its generic classes, as the file spells them


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
    match kind:
        case "function":
            return module.returns
        case "class":
            return module.classes
        case "returned":
            return module.returned.calls
        case "unannotated":
            return module.unannotated
        case "open":
            return module.open
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
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
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
    key: str
    origin: Origin
    for key, origin in spellings(catalog, target, kind):
        found: tuple[str, tuple[Module, str]] | None
        # Only what it calls: the modules `plan` put it after, whatever else is checked by then.
        if (kind != _RETURNED or key in target.called) and (
            found := _portable_call(modules, target, origin, kind, guarded)
        ) is not None:
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
    guarded: dict[str, Guarded] | None,
) -> tuple[str, tuple[Module, str]] | None:
    """Type a call to `origin`, a function of a `kind`, if `target` can write its type (see `_respelled`).

    Returns:
      Its type, as `target` writes it, and the module and name that define it; or `None`.

    """
    defined: tuple[Module, str] | None
    if (defined := definition(modules, origin, kind)) is None:
        return None
    annotation: str = (defined[0].returns if kind == _FUNCTION else defined[0].returned.calls)[defined[1]]
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
    naming a type variable (see `_is_type_var`), a builtin `target` rebinds, what `defined` doesn't
    import at its top level (nor define), or a checked file's generic class without its arguments.

    Returns:
      The type, or `None`.

    """
    names: frozenset[str] = roots(annotation)
    if any(_is_type_var(modules, defined, root) for root in names) or _bare(modules, defined, annotation):
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
        if name in target.guarded:
            found[name] = Guarded(target.guarded[name], None)
        elif name not in target.names:
            found[name] = guarded.get(name) or found.get(name) or Guarded(origin, _statement(origin, name))
    guarded.update(found)
    return _renamed(annotation, renamed)


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
    tree: ast.expr = _unquoted(annotation)
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

    A new import only from a module certain to resolve: a checked file's, an installed package's public
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
    public: bool = module is not None and not (module.installed and _private(origin[0]))
    resolves: bool = public or origin[0].partition(".")[0] in _STDLIB
    return None if name in known or name in _BUILTINS or not resolves else name


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

    Returns:
      Its origin, or `origin` itself if there's none.

    """
    wanted: Origin = _canonical(modules, origin)
    top: str = origin[0].partition(".")[0]
    found: list[str] = sorted(
        (
            name
            for name, other in modules.items()
            if other.installed
            and name.partition(".")[0] == top
            and not _private(name)
            and origin[1] in other.names
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
    """Rename names in an annotation (maybe a string one, which comes back unquoted).

    Returns:
      The annotation.

    """
    tree: ast.expr = _unquoted(annotation)
    node: ast.AST
    for node in ast.walk(tree):  # a fresh tree: renamed in place
        if isinstance(node, ast.Name):
            node.id = names.get(node.id, node.id)
    return ast.unparse(tree)


def _unquoted(annotation: str) -> ast.expr:
    """Parse an annotation, and a string one's text.

    Returns:
      Its expression.

    """
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    if isinstance(tree, ast.Constant) and isinstance(tree.value, str):
        return ast.parse(tree.value, mode="eval").body
    return tree


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
      Them, and the names their types need imported for type checking alone (see `Guarded`); nothing
      for a file `catalog` doesn't have (a notebook, standard input).

    """
    name: str = module_name(path)
    modules: dict[str, Module] = catalog.modules
    attributes: dict[str, dict[str, str]] = {}
    methods: dict[str, dict[str, str]] = {}
    guarded: dict[str, Guarded] = {}
    generics: set[str] = set()
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(name)) is None:
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
            generics.update(_reexported_generics(modules, local, origin[0]))
        key: str
        where: Origin
        for key, where in spelled:
            defined: tuple[Module, str] | None
            if (defined := definition(modules, where, _CLASS)) is not None:
                if defined[1] in defined[0].generics:
                    generics.add(key)
                attributes[key] = _portable(
                    modules,
                    (target, defined),
                    key,
                    defined[0].classes[defined[1]],
                    guarded,
                )
                methods[key] = _portable(
                    modules,
                    (target, defined),
                    key,
                    defined[0].methods.get(defined[1], {}),
                    guarded,
                )
    return Imported(
        calls(catalog, path, guarded),
        Classes(attributes, methods),
        returned(catalog, path, guarded),
        guarded,
        frozenset(generics),
    )


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
            and (defined := definition(modules, origin, _CLASS)) is not None
            and defined[1] in defined[0].generics
        ):
            yield f"{local}.{reexported}"


def _portable(
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
    for key, origin in spellings(catalog, module, _UNANNOTATED):
        defined: tuple[Module, str] | None
        if (
            key in module.called
            and (defined := definition(catalog.modules, origin, _UNANNOTATED)) is not None
        ):
            found.add(defined[0].name)
    found.discard(module.name)
    return found
