"""Returns under decorators another module defines: kept where it gives the function back.

A module alone vouches for the standard library's such decorators and its own (see
`constricter.source.decorators`); with the index, for those it imports from a checked file or an
installed package too (`@set_module("pandas")`, declared `-> Callable[[F], F]`), once the type
variables their signatures name are found to be ones. A declared return is kept, and an unannotated
function's `return`s may type its calls (`unannotated`), as an undecorated one's do.
"""

from collections.abc import Iterator, Mapping
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

from constricter.fix.core.known import Returns
from constricter.fix.index import project, spelling
from constricter.fix.index.modules import DECLARED, Index, Module, module_at
from constricter.fix.index.project import DECORATOR

if TYPE_CHECKING:
    from constricter.fix.core.known import Origin
    from constricter.source.decorators import Pass


def passed(catalog: Index) -> Index:
    """Add to each module's functions' declared returns those under decorators the index vouches for.

    Its classes' classmethods' and staticmethods' too; and its unannotated functions under such
    decorators (`decorated`) join those a `return` could type (`unannotated`).

    Returns:
      The index, with them among each module's `returns`, `sides` and `unannotated`, and named in
      its `vouched` and `vouched_sides`.

    """
    found: dict[str, Module] = {}
    module: Module
    for module in catalog.modules.values():
        if not (module.held or module.held_sides or module.decorated):
            continue
        trusted: frozenset[str] = frozenset(_vouched(catalog, module))
        more: dict[str, str] = {
            name: held.returns for name, held in module.held.items() if trusted.issuperset(held.decorators)
        }
        sides: dict[tuple[str, str], str] = {
            (owner, name): held.returns
            for owner, methods in module.held_sides.items()
            for name, held in methods.items()
            if trusted.issuperset(held.decorators)
        }
        freed: frozenset[str] = frozenset(
            name for name, spellings in module.decorated.items() if trusted.issuperset(spellings)
        )
        if module.untyped and (more or freed):
            # An untyped package's: what it declares is a guess (see `installed.as_untyped`).
            found[module.name] = replace(
                module,
                returned=Returns(
                    {**module.returned.calls, **more},
                    {**module.returned.guesses, **dict.fromkeys(more, DECLARED)},
                    module.returned.names,
                    module.returned.methods,
                ),
                unannotated=module.unannotated | freed,
            )
        elif more or sides or freed:
            found[module.name] = replace(
                module,
                returns={**module.returns, **more},
                vouched=frozenset(more),
                sides=_with_sides(module.sides, sides),
                vouched_sides=frozenset(sides),
                unannotated=module.unannotated | freed,
            )
    return catalog._replace(modules={**catalog.modules, **found}) if found else catalog


def vouched(catalog: Index, path: Path) -> frozenset[str]:
    """Spell the decorators the file at `path` uses that give a function back, by the index.

    Returns:
      Each, as `decorators.spelled` reads its use; nothing for a file `catalog` doesn't have.

    """
    module: Module | None
    if (module := module_at(catalog, path)) is None:
        return frozenset()
    return frozenset(_vouched(catalog, module))


def _with_sides(
    sides: Mapping[str, Mapping[str, str]],
    more: Mapping[tuple[str, str], str],
) -> dict[str, dict[str, str]]:
    """Add methods' returns (`more`, by class and name) to classes' (`sides`).

    Returns:
      Each class's, with them.

    """
    found: dict[str, dict[str, str]] = {owner: dict(methods) for owner, methods in sides.items()}
    owner: str
    name: str
    annotation: str
    for (owner, name), annotation in more.items():
        found.setdefault(owner, {})[name] = annotation
    return found


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
    for key, origin in spelling.spellings(catalog, module, DECORATOR):
        defined: tuple[Module, str] | None
        if (defined := project.definition(catalog.modules, origin, DECORATOR)) is not None:
            read = defined[0].passes[defined[1]]
            if all(project.is_type_var(catalog.modules, defined[0], word) for word in read.type_vars):
                yield read.spelled(key)


def own(catalog: Index, path: Path) -> dict[str, str]:
    """Return, for the file at `path`, its own functions' returns the index vouched for (see `passed`).

    Its classes' classmethods' and staticmethods' too, as called on the class (`Box.make`), where
    the class's name is the class throughout the file.

    Returns:
      Each one's name and declared return; nothing for a file `catalog` doesn't have.

    """
    module: Module | None
    if (module := module_at(catalog, path)) is None:
        return {}
    return {
        **{name: module.returns[name] for name in module.vouched},
        **{
            f"{owner}.{name}": module.sides[owner][name]
            for owner, name in module.vouched_sides
            if module.names.get(owner) == (module.name, owner) and owner not in module.shadowed
        },
    }
