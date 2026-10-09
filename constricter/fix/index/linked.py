# SPDX-License-Identifier: MIT
"""What the index says of checked modules together: one type's several spellings, and what's checked first.

The ways a file spells one class or alias another module defines (`same`), the names it imports
that are values where they're defined (`values`), the modules whose
unannotated functions a module calls, checked before it (`needs`), those functions as the file
spells them (`untyped`), and the index with what a checked module's functions return
(`with_returned`).
"""

from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path

from constricter.fix.core.known import Guarded, Origin, Returns
from constricter.fix.index import project
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name


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
    # With what it imports for type checking alone: a module so imported spells its types too.
    checking: dict[str, Origin] = {
        **target.guarded,
        **{name: found.origin for name, found in guarded.items()},
    }
    named: Module = replace(target, names={**checking, **target.names})
    groups: dict[Origin, set[str]] = {}
    kind: str
    for kind in (project.CLASS, project.ALIAS):
        name: str
        origin: Origin
        for name, origin in project.spellings(catalog, named, kind):
            defined: tuple[Module, str] | None
            if (defined := project.definition(catalog.modules, origin, kind)) is not None:
                groups.setdefault((defined[0].name, defined[1]), set()).add(name)
    return tuple(frozenset(group) for group in groups.values() if len(group) > 1)


def values(catalog: Index, path: Path) -> frozenset[str]:
    """Find the names the file at `path` imports that another checked module binds by assignment.

    `F`, by `F = duckdb.FunctionExpression` there: a value, whatever its name looks like, and a call
    of it constructs nothing a type can be written for.

    Returns:
      Them, as the file binds them; none for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return frozenset()
    found: set[str] = set()
    local: str
    origin: Origin
    for local, origin in target.names.items():
        where: Origin = project.canonical_origin(catalog.modules, origin)
        defining: Module | None = catalog.modules.get(where[0])
        if defining is not None and where[1] in defining.assigned and where[0] != target.name:
            found.add(local)
    return frozenset(found)


def with_returned(catalog: Index, found: Mapping[str, Returns]) -> Index:
    """Record what checked modules' unannotated functions return (`found`, by module name).

    A module's names from an earlier check are kept: once `--fix` has written an import it added,
    a later check no longer exports the name, and the index doesn't have the new import.

    Returns:
      The index, with them.

    """
    modules: dict[str, Module] = dict(catalog.modules)
    name: str
    returns: Returns
    for name, returns in found.items():
        if name in modules:
            names: dict[str, Origin] = {**modules[name].returned.names, **returns.names}
            modules[name] = replace(modules[name], returned=returns._replace(names=names))
    return catalog._replace(modules=modules)


def needs(catalog: Index, module: Module) -> set[str]:
    """Find the other modules whose unannotated functions `module` calls (see `_spelled`).

    Returns:
      Their names.

    """
    found: set[str] = set()
    key: str
    origin: Origin
    for key, origin in project.spellings(catalog, module, project.UNANNOTATED):
        defined: tuple[Module, str] | None
        if (
            key in module.called
            and (defined := project.definition(catalog.modules, origin, project.UNANNOTATED)) is not None
        ):
            found.add(defined[0].name)
    found.discard(module.name)
    return found


def untyped(catalog: Index, path: Path) -> frozenset[str]:
    """Find the other checked files' functions the file at `path` calls that declare no return.

    A plain `def` (see `returned.unannotated`), no `# type:` comment declaring its return, and no
    fixture: what a type checker reading no body takes each call of for anything.

    Returns:
      Each, as the file spells its call (`helper`, `u.helper`); none for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return frozenset()
    found: set[str] = set()
    key: str
    origin: Origin
    for key, origin in project.spellings(catalog, target, project.UNANNOTATED):
        defined: tuple[Module, str] | None
        if (
            key in target.called
            and (defined := project.definition(catalog.modules, origin, project.UNANNOTATED)) is not None
            and not defined[0].installed
            and defined[1] not in defined[0].returns
            and defined[1] not in defined[0].fixtures
        ):
            found.add(key)
    return frozenset(found)
