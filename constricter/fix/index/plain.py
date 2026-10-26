"""Which of the checked files' classes are plain, settled across them all.

See `constricter.fix.values.classvars`, which settles one module's.

A module alone can't see past a base another file defines: the index can, through imports and
re-exports, to what that base inherits from and what it declares.
"""

from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Final

from constricter.fix.index.modules import Index, Module, module_at
from constricter.fix.index.project import CLASS, definition
from constricter.fix.values import classvars

if TYPE_CHECKING:
    from constricter.fix.core.known import Origin

_DOT: Final = "."
# The bases no class's binding of a name can hide: one a class above another binds is in sight.
_ROOTS: Final = frozenset({classvars.OBJECT, *classvars.BUILTIN_BASES, *classvars.PASSED_OVER})


def settled(catalog: Index, entries: Sequence[str] = ()) -> Index:
    """Settle which of the checked files' classes are plain, across them all.

    As `constricter.fix.values.classvars` has it for one module, a base another checked file defines
    followed there: a class under another file's plain class is plain, and a class that isn't
    makes what it inherits from, in any file, not plain either. A base `entries` list
    (`classvars.listed`) is one a plain class may have even where a checked file defines it, plain
    or not: the framework's own files, checked. So is one passed over (`classvars.PASSED_OVER`).

    Returns:
      The index, each checked module with its plain classes.

    """
    found: dict[str, tuple[str, ...]] = {
        f"{module.name}.{name}": tuple(resolved(catalog.modules, module, base) for base in bases)
        for module in catalog.modules.values()
        for name, bases in module.bases.items()
    }
    if not found:
        return catalog
    unlisted: dict[str, tuple[str, ...]] = {
        name: tuple(
            base
            for base in bases
            if base not in classvars.PASSED_OVER and not classvars.listed(base, entries)
        )
        for name, bases in found.items()
    }
    plain: frozenset[str] = classvars.settled(unlisted, classvars.allowed)
    declared: dict[str, Mapping[str, str]] = {
        f"{module.name}.{name}": module.classes.get(name, {})
        for module in catalog.modules.values()
        for name in module.bases
    }
    return _named(
        catalog._replace(
            modules={
                name: replace(
                    module,
                    plain=frozenset(
                        each
                        for each in module.bases
                        if f"{name}.{each}" in plain and _unheld(f"{name}.{each}", module, found, declared)
                    ),
                )
                for name, module in catalog.modules.items()
            },
        ),
        found,
    )


def _named(catalog: Index, found: Mapping[str, tuple[str, ...]]) -> Index:
    """Type a plain class's variables bound to a checked file's class by name (see `classvars.named`).

    `type[Name]`, where no class above or under it in the checked files binds the variable: a type
    checker holds an override to its base's type once both are declared. Only where every class
    above it is a checked file's, or a builtin or `object`: a framework's base, or one only a star
    import re-exports, may bind it out of sight. `found`: each checked class's bases, resolved.

    Returns:
      The index, each such module with them among its `members`.

    """
    binds: dict[str, frozenset[str]] = {
        f"{module.name}.{name}": names
        for module in catalog.modules.values()
        for name, names in module.bound.items()
    }
    under: dict[str, set[str]] | None = None
    modules: dict[str, Module] = dict(catalog.modules)
    module: Module
    for module in catalog.modules.values():
        added: dict[str, dict[str, str]] = {}
        owner: str
        bound: Mapping[str, str]
        for owner, bound in module.named.items():
            key: str = f"{module.name}.{owner}"
            variable: str
            value: str
            for variable, value in bound.items() if owner in module.plain else ():
                if resolved(catalog.modules, module, value) not in found or not _closed(key, found):
                    continue
                under = _under(found) if under is None else under
                if not any(
                    variable in binds.get(other, ())
                    for other in (*classvars.ancestors(key, found), *under[key])
                ):
                    added.setdefault(owner, {})[variable] = f"type[{value}]"
        if added:
            typed: dict[str, Mapping[str, str]] = dict(module.members)
            typed.update({owner: {**typed.get(owner, {}), **each} for owner, each in added.items()})
            modules[module.name] = replace(module, members=typed)
    return catalog._replace(modules=modules) if under is not None else catalog


def _closed(key: str, found: Mapping[str, tuple[str, ...]]) -> bool:
    """Check that every class above `key` is in sight: a checked file's, or a builtin or `object`.

    Returns:
      Whether it is.

    """
    return all(
        base in found or base in _ROOTS
        for owner in (key, *classvars.ancestors(key, found))
        for base in found[owner]
    )


def _under(found: Mapping[str, tuple[str, ...]]) -> dict[str, set[str]]:
    """Name every checked class under each one, however far.

    Returns:
      Them, by the class above.

    """
    under: dict[str, set[str]] = {name: set() for name in found}
    name: str
    for name in found:
        above: str
        for above in classvars.ancestors(name, found):
            under[above].add(name)
    return under


def _unheld(
    key: str,
    module: Module,
    found: Mapping[str, tuple[str, ...]],
    declared: Mapping[str, Mapping[str, str]],
) -> bool:
    """Check that a class's variables are its own to type, whatever other files' classes it inherits from.

    None hides what a builtin above it has itself, nor what a class above it annotates as another
    type (see `constricter.fix.values.classvars`), which the class's own module can't see past its file.

    Returns:
      Whether they are.

    """
    typed: Mapping[str, str] = module.members.get(key.rpartition(_DOT)[2], {})
    above: list[Mapping[str, str]] = [declared[each] for each in classvars.ancestors(key, found)]
    return not typed.keys() & classvars.reserved(key, found) and classvars.agreeing(typed, above) == typed


def resolved(modules: Mapping[str, Module], module: Module, base: str) -> str:
    """Resolve a class's base, as `module` writes it, to where it's defined (`pkg.models.Row`).

    Returns:
      The defining module and the class, dotted, through imports and re-exports; as far as it's
      known, for one no indexed module defines (`unittest.TestCase`).

    """
    first: str
    rest: str
    first, _, rest = base.partition(_DOT)
    if not rest and first in module.bases:
        return f"{module.name}.{first}"
    origin: Origin | None
    if (origin := module.names.get(first)) is None:
        return base
    path: list[str] = [*([origin[0]] if origin[0] else []), *([origin[1]] if origin[1] else [])]
    path += rest.split(_DOT) if rest else []
    where: Origin = (_DOT.join(path[:-1]), path[-1])
    defined: tuple[Module, str] | None = definition(modules, where, CLASS)
    return _DOT.join(path) if defined is None else f"{defined[0].name}.{defined[1]}"


def members(catalog: Index, path: Path) -> dict[str, Mapping[str, str]]:
    """Find what the index types the variables of the plain classes of the file at `path` as.

    What the file alone types them as, and those bound to a checked file's class by name (`_named`).

    Returns:
      Each class's, by its name; none for a file `catalog` doesn't have.

    """
    target: Module | None = module_at(catalog, path)
    return (
        {}
        if target is None
        else {name: target.members[name] for name in target.plain if name in target.members}
    )


def classes(catalog: Index, path: Path) -> frozenset[str] | None:
    """Find which classes of the file at `path` the index settled as plain (see `settled`).

    Returns:
      Their names; `None` for a file `catalog` doesn't have, whose own classes say.

    """
    target: Module | None = module_at(catalog, path)
    return None if target is None else target.plain
