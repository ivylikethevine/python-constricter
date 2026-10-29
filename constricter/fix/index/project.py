"""Cross-module `--fix`: the functions and classes other checked files define.

`index` reads every file once (see `constricter.fix.index.modules`); this finds where a name is
defined through the re-exports (`definition`), and what kind of thing it is. `spelling.calls` then
gives a file the return type of each function it imports (`from m import f`, `import m as a` then
`a.f()`), and `crossed.imported` those and each imported class's attributes and methods, but only
where every name in a type means the same thing in the file as where it was written: otherwise the
fix would name something undefined, or something else. A name the file doesn't bind that way is
imported where the type is written from under `if TYPE_CHECKING:` (`Guarded`): that import can't
make a cycle.

What a module's unannotated functions return is known only once it's checked: the CLI checks the
files in `order.plan`'s order, each after those whose unannotated functions it calls (`needs`), and
adds each module's (`with_returned`) to the index for the files after it.
"""

import builtins
import sys
from collections.abc import Callable, Iterable, Iterator, Mapping
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

from constricter.empty import Empty
from constricter.fix.core.known import Classes, Guarded, Origin, Partial, Returns
from constricter.fix.index.modules import (
    Index,
    Module,
    concrete_in,
    defaulted_in,
    exported,
    index,
    indexed,
    module_at,
    module_name,
    read,
    spliced,
)
from constricter.source.declarations import GenericClass

__all__ = [
    "Imported",
    "Index",
    "Module",
    "index",
    "indexed",
    "module_name",
    "read",
    "spliced",
]  # the index's, re-exported

BUILTINS: Final = frozenset(dir(builtins))
STDLIB: Final = sys.stdlib_module_names
NO_TYPE: Final = ""  # a class variable's type the file reading it can't write
HOPS: Final = 5  # how many re-exports (`from .util import f` in an `__init__`) to follow
DEPTH: Final = 8  # how many classes a line of bases is followed through
DOT: Final = "."
_UNDERSCORE: Final = "_"
_STAR: Final = "*"  # what a `from m import *` binds, as the index records it
FUNCTION: Final = "function"
DECORATOR: Final = "decorator"  # a function that gives back the one it decorates
CLASS: Final = "class"
ALIAS: Final = "alias"  # a type alias (see `modules.Module.aliases`)
_TYPE_VAR: Final = "type variable"
RETURNED: Final = "returned"  # an unannotated function its `return`s type
UNANNOTATED: Final = "unannotated"  # an unannotated function, typed or not
PARTIAL: Final = "partial"  # a function whose declared return only an unpacking can use
OPEN: Final = "open"  # a function with a parameter left unannotated (see `params.open_functions`)
SIGNATURES: Final = "signatures"  # a function with its signatures as written (see `Module.signatures`)


class Imported(NamedTuple):
    """What a file's imports from other checked files offer `--fix`, each keyed as the file spells it."""

    calls: dict[str, str]
    classes: Classes
    returned: Returns = Returns()
    guarded: Mapping[str, Guarded] = (
        Empty()
    )  # names their types need imported to type check (pickled: a `dict`)
    generics: frozenset[str] = frozenset()  # its generic classes, as the file spells them
    # Its plain classes' variables typed by their values, by class (see `constricter.fix.values.classvars`).
    members: Mapping[str, Mapping[str, str]] = Empty()
    partial: Partial = Partial()  # the returns only an unpacking can use
    # Its generic classes' type parameters and the members it takes of them (see `GenericClass`).
    generic: Mapping[str, GenericClass] = Empty()
    # Its descriptors, each with what an instance's attribute of it gives (see `Module.descriptors`).
    descriptors: Mapping[str, str | None] = Empty()


def definition(
    modules: Mapping[str, Module],
    origin: Origin,
    kind: str,
    hops: int = HOPS,
) -> tuple[Module, str] | None:
    """Follow `origin` (through re-exports) to the module that defines it as a `kind` (function, class).

    As `canonical_origin` does: through what a module imports for type checking alone too, as a
    package's `__init__` does what it imports only when it's asked for (pydantic's `TypeAdapter`).

    Returns:
      That module and the name, or `None`.

    """
    module: Module | None = modules.get(origin[0])
    attribute: str | None = origin[1]
    if module is None or attribute is None or not hops:
        return None
    if attribute in kind_of(module, kind):
        return module, attribute
    onward: Origin | None = (
        module.names.get(attribute)
        or module.guarded.get(attribute)
        or starred_origin(modules, module, attribute)
    )
    return definition(modules, onward, kind, hops - 1) if onward and onward[0] != module.name else None


def starred_origin(
    modules: Mapping[str, Module],
    module: Module,
    name: str,
    hops: int = HOPS,
) -> Origin | None:
    """Find which module `module` takes `name` from by importing everything from it (`from .main import *`).

    The last that binds it, as the imports run, itself or by importing everything from another in
    turn (`networkx` from `networkx.algorithms`, which takes it from `.operators`); a name with a
    leading underscore no such import takes.

    Returns:
      The name there, or `None`.

    """
    if not hops or name.startswith(_UNDERSCORE):
        return None
    star: str
    for star in reversed(module.stars):
        other: Module | None = modules.get(star)
        if other is not None and (name in exported(other) or starred_origin(modules, other, name, hops - 1)):
            return star, name
    return None


def starred_names(modules: Mapping[str, Module], module: Module, hops: int = HOPS) -> dict[str, Origin]:
    """Name what `module` takes by importing everything from others (see `starred_origin`).

    Returns:
      Each public name, and the module it's taken from there (the last import's, as they run).

    """
    found: dict[str, Origin] = {}
    if not hops:
        return found
    star: str
    other: Module | None
    for star in module.stars:
        if (other := modules.get(star)) is not None:
            found.update(
                (name, (star, name))
                for name in (*starred_names(modules, other, hops - 1), *exported(other))
                if not name.startswith(_UNDERSCORE) and name != _STAR
            )
    return found


def type_definition(modules: Mapping[str, Module], origin: Origin) -> tuple[Module, str] | None:
    """Follow `origin` to the module that defines it as a class, else as a type alias (see `definition`).

    Returns:
      That module and the name, or `None`.

    """
    return definition(modules, origin, CLASS) or definition(modules, origin, ALIAS)


def called(
    modules: Mapping[str, Module],
    target: Module,
    has: Callable[[Module, str], bool],
) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the calls `target` makes to what another module defines, as `has` says of a module's name.

    Through its imports, and the re-exports between the modules (`HOPS` of them).

    Yields:
      Each call's name as written (`load`, `client.load`), and the module defining what it calls
      and its name there.

    """
    spelled: str
    for spelled in target.called:
        origin: Origin | None = written_origin(target, spelled)
        defined: tuple[Module, str] | None
        if (defined := None if origin is None else _holding(modules, origin, has, HOPS)) is not None:
            yield spelled, defined


def _holding(
    modules: Mapping[str, Module],
    origin: Origin,
    has: Callable[[Module, str], bool],
    hops: int,
) -> tuple[Module, str] | None:
    """Follow `origin` (through re-exports) to the module that `has` it.

    Returns:
      That module and the name, or `None`.

    """
    module: Module | None = modules.get(origin[0])
    name: str | None = origin[1]
    if module is None or name is None or not hops:
        return None
    if has(module, name):
        return module, name
    onward: Origin | None = module.names.get(name) or starred_origin(modules, module, name)
    return _holding(modules, onward, has, hops - 1) if onward and onward[0] != module.name else None


def written_origin(target: Module, spelled: str) -> Origin | None:
    """Resolve what `target` writes as `spelled` (`Row`, `m.Row`, `pkg.m.load`) through its imports.

    Returns:
      The module it's an attribute of, and its name there; `None` for a name the file doesn't
      import, binds as a value too, or imports from itself.

    """
    first: str
    rest: str
    first, _, rest = spelled.partition(DOT)
    origin: Origin | None = target.names.get(first)
    if origin is None or origin[0] == target.name or first in target.shadowed:
        return None
    path: list[str] = [origin[0], *([origin[1]] if origin[1] else []), *(rest.split(DOT) if rest else [])]
    return DOT.join(path[:-1]), path[-1]


def kind_of(module: Module, kind: str) -> Iterable[str]:
    """List what `module` defines of a `kind`: functions (declared or typed by their `return`s), classes...

    Returns:
      Their names.

    """
    return _KINDS[kind](module)


_Defined: TypeAlias = Callable[[Module], Iterable[str]]  # what a module defines of one kind
# What a module defines of each kind (see `kind_of`).
_KINDS: Final[Mapping[str, _Defined]] = {
    FUNCTION: lambda module: module.returns,
    CLASS: lambda module: module.classes,
    ALIAS: lambda module: module.aliases,
    RETURNED: lambda module: module.returned.calls,
    UNANNOTATED: lambda module: module.unannotated,
    OPEN: lambda module: module.open,
    PARTIAL: lambda module: module.partial,
    DECORATOR: lambda module: module.passes,
    SIGNATURES: lambda module: module.signatures,
    _TYPE_VAR: lambda module: module.type_vars,
}


def type_vars(catalog: Index, path: Path) -> frozenset[str]:
    """Find the names the file at `path` imports that are type variables where they're defined.

    Followed through re-exports, as calls are; for the checker to leave alone the file's own
    functions whose declared return mentions one (`def f(x: T) -> T`, with `from ._typing import T`).

    Returns:
      Them, as the file binds them; none for a file `catalog` doesn't have.

    """
    target: Module | None
    if (target := module_at(catalog, path)) is None:
        return frozenset()
    return frozenset(
        local for local in {*target.names, *target.guarded} if is_type_var(catalog.modules, target, local)
    )


def defaulted(catalog: Index, path: Path) -> frozenset[str]:
    """Name what the file at `path`'s generic classes' bases name that leaves them written bare.

    A type variable with a default where it's defined, or a class or type alias (see
    `modules.settled`): a generic class of its own whose every such name is one is written bare (see
    `generic_classes`), as the index writes it for the other files.

    Returns:
      Them, as the file writes them (`K`, `t.K`); none for a file `catalog` doesn't have.

    """
    target: Module | None
    if (target := module_at(catalog, path)) is None:
        return frozenset()
    named: frozenset[str] = frozenset[str]().union(*target.generic_names.values())
    return frozenset(
        name
        for name in named
        if defaulted_in(catalog.modules, target, name) or concrete_in(catalog.modules, target, name)
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
