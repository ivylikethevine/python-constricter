"""Which of the checked files' classes are plain, settled across them all.

See `constricter.fix.values.classvars`, which settles one module's.

A module alone can't see past a base another file defines: the index can, through imports and
re-exports, to what that base inherits from and what it declares.
"""

from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeAlias

from constricter.fix.index.modules import Index, Module, module_at
from constricter.fix.index.project import CLASS, INERT, definition
from constricter.fix.values import classvars
from constricter.source import inert

if TYPE_CHECKING:
    from constricter.fix.core.known import Origin

_DOT: Final = "."
_Members: TypeAlias = dict[str, Mapping[str, str]]  # a module's classes' variables' types, by class
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
    # A class only its decorators and metaclass kept from plain, each of them inert where it's defined.
    cleared: frozenset[str] = frozenset(
        f"{module.name}.{name}"
        for module in catalog.modules.values()
        for name, marks in module.marks.items()
        if f"{module.name}.{name}" in found and all(_inert(catalog.modules, module, mark) for mark in marks)
    )
    marked: frozenset[str] = _plain(found, entries)
    found = {
        key: tuple(base for base in bases if base != classvars.SPECIAL) if key in cleared else bases
        for key, bases in found.items()
    }
    plain: frozenset[str] = _plain(found, entries) if cleared else marked
    declared: dict[str, Mapping[str, str]] = {
        f"{module.name}.{name}": module.classes.get(name, {})
        for module in catalog.modules.values()
        for name in module.bases
    }
    held: Index = catalog._replace(
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
    )
    return _joined(_named(held, found), found, (declared, plain - marked))


def _plain(found: Mapping[str, tuple[str, ...]], entries: Sequence[str]) -> frozenset[str]:
    """Settle which classes are plain by their resolved bases (see `classvars.settled`).

    Returns:
      Their keys.

    """
    unlisted: dict[str, tuple[str, ...]] = {
        name: tuple(
            base
            for base in bases
            if base not in classvars.PASSED_OVER and not classvars.listed(base, entries)
        )
        for name, bases in found.items()
    }
    return classvars.settled(unlisted, classvars.allowed)


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


def _joined(
    catalog: Index,
    found: Mapping[str, tuple[str, ...]],
    seen: tuple[Mapping[str, Mapping[str, str]], frozenset[str]],
) -> Index:
    """Type a plain class's variable alike in every checked file's class above and under it that binds it.

    As `classvars.joined` does in one module, across them all, after leaving out what
    `classvars.unshadowed` does. `found`: each checked class's bases, resolved; `seen`: each one's
    annotated attributes, and the classes plain only by their marks.

    Returns:
      The index, each such module with its variables' types joined among its `members`.

    """
    typed: dict[str, Mapping[str, str]] = {}
    bare: dict[str, frozenset[str]] = {}
    defined: dict[str, frozenset[str]] = {}
    module: Module
    for module in catalog.modules.values():
        name: str
        for name in module.plain:
            if name in module.members:
                typed[f"{module.name}.{name}"] = module.members[name]
            if name in module.nulls:
                bare[f"{module.name}.{name}"] = module.nulls[name]
        defined.update({f"{module.name}.{name}": names for name, names in module.defined.items()})
    kept: dict[str, dict[str, str]]
    nones: dict[str, frozenset[str]]
    kept, nones = classvars.unshadowed(typed, bare, (defined, found), seen[1])
    joined: dict[str, dict[str, str]] = classvars.joined(kept, nones, found, seen[0], seen[1])
    return _written(catalog, joined, typed)


def _written(
    catalog: Index,
    joined: Mapping[str, Mapping[str, str]],
    typed: Mapping[str, Mapping[str, str]],
) -> Index:
    """Write each class's joined variables among its module's `members`, where they changed.

    Returns:
      The index, so.

    """
    changed: dict[str, _Members] = {}
    key: str
    each: Mapping[str, str]
    for key, each in joined.items():
        if each != typed.get(key, {}):
            owner: str
            where: str
            where, _, owner = key.rpartition(_DOT)
            changed.setdefault(where, dict(catalog.modules[where].members))[owner] = each
    if not changed:
        return catalog
    return catalog._replace(
        modules={
            **catalog.modules,
            **{where: replace(catalog.modules[where], members=members) for where, members in changed.items()},
        },
    )


def _inert(modules: Mapping[str, Module], module: Module, mark: str) -> bool:
    """Check whether a class's decorator or metaclass (see `inert.marks`) leaves it plain, where it's defined.

    Returns:
      Whether its module, or the standard library, says so (`inert.judged`), or the checked file
      that defines it, through imports and re-exports, has it among its `inert`.

    """
    origins: dict[str, str] = {
        name: _DOT.join(part for part in origin if part) for name, origin in module.names.items()
    }
    judged: bool | None
    if (judged := inert.judged(mark, module.inert, origins)) is not None:
        return judged
    first: str
    rest: str
    first, _, rest = mark.removeprefix(inert.METACLASS).removesuffix("()").partition(_DOT)
    origin: Origin | None
    if (origin := module.names.get(first)) is None:
        return False
    path: list[str] = [part for part in origin if part] + (rest.split(_DOT) if rest else [])
    return len(path) > 1 and definition(modules, (_DOT.join(path[:-1]), path[-1]), INERT) is not None


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
