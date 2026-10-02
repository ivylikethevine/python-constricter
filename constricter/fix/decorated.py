# SPDX-License-Identifier: MIT
"""Declared returns under decorators another module defines: kept where it gives the function back.

A module alone vouches for the standard library's such decorators and its own (see
`constricter.rules.decorators`); with the index, for those it imports from a checked file or an
installed package too (`@set_module("pandas")`, declared `-> Callable[[F], F]`), once the type
variables their signatures name are found to be ones.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING

from constricter.fix import project
from constricter.fix.modules import SUFFIX, Index, Module, module_name
from constricter.fix.project import DECORATOR

if TYPE_CHECKING:
    from constricter.fix.known import Origin
    from constricter.rules.decorators import Pass


def passed(catalog: Index) -> Index:
    """Add to each module's functions' declared returns those under decorators the index vouches for.

    Returns:
      The index, with them among each module's `returns`, and named in its `vouched`.

    """
    found: dict[str, Module] = {}
    module: Module
    for module in catalog.modules.values():
        vouched: frozenset[str] = frozenset(_vouched(catalog, module)) if module.held else frozenset()
        more: dict[str, str] = {
            name: held.returns for name, held in module.held.items() if vouched.issuperset(held.decorators)
        }
        if more:
            found[module.name] = module._replace(
                returns={**module.returns, **more},
                vouched=frozenset(more),
            )
    return Index({**catalog.modules, **found}, catalog.names) if found else catalog


def _vouched(catalog: Index, module: Module) -> Iterator[str]:
    """Spell the decorators `module` uses that give a function back, by the index: its own, and imported.

    Yields:
      Each, as `decorators.spelled` reads its use.

    """
    name: str
    read: Pass
    for name, read in module.passes.items():
        if all(project.is_type_var(catalog.modules, module, word) for word in read.type_vars):
            yield read.spelled(name)
    key: str
    origin: Origin
    for key, origin in project.spellings(catalog, module, DECORATOR):
        defined: tuple[Module, str] | None
        if (defined := project.definition(catalog.modules, origin, DECORATOR)) is not None:
            read = defined[0].passes[defined[1]]
            if all(project.is_type_var(catalog.modules, defined[0], word) for word in read.type_vars):
                yield read.spelled(key)


def own(catalog: Index, path: Path) -> dict[str, str]:
    """Return, for the file at `path`, its own functions' returns the index vouched for (see `passed`).

    Returns:
      Each one's name and declared return; nothing for a file `catalog` doesn't have.

    """
    module: Module | None
    if path.suffix != SUFFIX or (module := catalog.modules.get(module_name(path))) is None:
        return {}
    return {name: module.returns[name] for name in module.vouched}
