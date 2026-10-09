# SPDX-License-Identifier: MIT
"""The tuples a file's names stand for, other checked files': a named tuple's fields, an alias's tuple.

What an unpacking splits a value of one of them by (see `targets.named_tuples`), spelled as the file
can write it; and the unions its names for their aliases stand for (see `targets.aliased_unions`).
"""

from collections.abc import Callable, Iterator, Mapping
from pathlib import Path

from constricter.fix.core.known import Guarded, Origin
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name
from constricter.fix.index.project import ALIAS, CLASS, definition, portable


def fields(catalog: Index, path: Path, guarded: dict[str, Guarded]) -> dict[str, str]:
    """Find the tuples the file at `path` can name, by how it names them.

    Those the types written for it name, which it needn't import itself (a property's type, a
    function's return; see `Guarded`), those it imports, and those a module it imports has.

    Returns:
      Each name, and the tuple unpacking a value of it gives; nothing for a file `catalog` doesn't
      have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return {}
    found: dict[str, str] = {}
    key: str
    defined: tuple[Module, str]
    for key, defined in _named(catalog.modules, target, guarded, _tuples):
        found.update(_fields(catalog.modules, target, key, defined, guarded))
    return found


def unions(catalog: Index, path: Path, guarded: dict[str, Guarded]) -> dict[str, str]:
    """Find the unions the file at `path` names by other files' type aliases, by how it names them.

    The aliases `fields` would find, were they tuples'.

    Returns:
      Each name, and the union as its own module writes it: read for its members, never written.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return {}
    return {
        key: defined[0].unions[defined[1]]
        for key, defined in _named(catalog.modules, target, guarded, _unions)
        if defined[1] in defined[0].unions
    }


def _tuples(module: Module) -> Mapping[str, str]:
    return module.tuples


def _unions(module: Module) -> Mapping[str, str]:
    return module.unions


def _named(
    modules: Mapping[str, Module],
    target: Module,
    guarded: Mapping[str, Guarded],
    held: Callable[[Module], Mapping[str, str]],
) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the classes and aliases a file (`target`) names, and those of a module it imports that `held` has.

    Yields:
      Each one's name as the file spells it (`Pair`, or `shapes.Pair` after
      `import pkg.shapes as shapes`), and where it's defined.

    """
    named: list[tuple[str, Origin]] = [
        *((key, each.origin) for key, each in guarded.items()),
        *target.guarded.items(),  # under `if TYPE_CHECKING:`
        *((key, origin) for key, origin in target.names.items() if origin[0] != target.name),
    ]
    key: str
    origin: Origin
    for key, origin in named:
        defined: tuple[Module, str] | None = definition(modules, origin, CLASS) or definition(
            modules,
            origin,
            ALIAS,
        )
        if defined is not None:
            yield key, defined
        module: Module | None
        if origin[1] is None and (module := modules.get(origin[0])) is not None:
            yield from ((f"{key}.{name}", (module, name)) for name in held(module))


def _fields(
    modules: Mapping[str, Module],
    target: Module,
    key: str,
    defined: tuple[Module, str],
    guarded: dict[str, Guarded],
) -> dict[str, str]:
    """Spell one tuple type's tuple (see `targets.named_tuples`) for the file (`target`) naming it `key`.

    Returns:
      `key`, and the tuple; nothing for any other class or alias, or types the file can't write.

    """
    tuple_type: str | None = defined[0].tuples.get(defined[1])
    return {} if tuple_type is None else portable(modules, (target, defined), key, {key: tuple_type}, guarded)
