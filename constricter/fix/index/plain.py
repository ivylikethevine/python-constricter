# SPDX-License-Identifier: MIT
"""Which of the checked files' classes are plain, settled across them all.

See `constricter.fix.values.classvars`, which settles one module's.

A module alone can't see past a base another file defines: the index can, through imports and
re-exports, to what that base inherits from and what it declares.
"""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final

from constricter.fix.index.modules import SUFFIX, Index, Module, module_name
from constricter.fix.index.project import CLASS, definition
from constricter.fix.values import classvars

if TYPE_CHECKING:
    from constricter.fix.core.known import Origin

_DOT: Final = "."


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
    return catalog._replace(
        modules={
            name: module._replace(
                plain=frozenset(
                    each
                    for each in module.bases
                    if f"{name}.{each}" in plain and _unheld(f"{name}.{each}", module, found, declared)
                ),
            )
            for name, module in catalog.modules.items()
        },
    )


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
    return not classvars.reserved(key, found) & typed.keys() and classvars.agreeing(typed, above) == typed


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


def classes(catalog: Index, path: Path) -> frozenset[str] | None:
    """Find which classes of the file at `path` the index settled as plain (see `settled`).

    Returns:
      Their names; `None` for a file `catalog` doesn't have, whose own classes say.

    """
    target: Module | None = catalog.modules.get(module_name(path)) if path.suffix == SUFFIX else None
    return None if target is None else target.plain
