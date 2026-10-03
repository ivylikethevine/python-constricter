# SPDX-License-Identifier: MIT
"""The tuples a file's names stand for, other checked files': a named tuple's fields, an alias's tuple.

What an unpacking splits a value of one of them by (see `targets.named_tuples`), spelled as the file
can write it.
"""

from collections.abc import Mapping
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
    modules: dict[str, Module] = catalog.modules
    named: list[tuple[str, Origin]] = [
        *((key, each.origin) for key, each in guarded.items()),
        *((key, origin) for key, origin in target.names.items() if origin[0] != target.name),
    ]
    found: dict[str, str] = {}
    key: str
    origin: Origin
    for key, origin in named:
        defined: tuple[Module, str] | None = definition(modules, origin, CLASS) or definition(
            modules,
            origin,
            ALIAS,
        )
        found.update({} if defined is None else _fields(modules, target, key, defined, guarded))
        module: Module | None
        # `shapes.Pair`, after `import pkg.shapes as shapes`
        if origin[1] is None and (module := modules.get(origin[0])) is not None:
            found.update(_module_fields(modules, target, key, module, guarded))
    return found


def _module_fields(
    modules: Mapping[str, Module],
    target: Module,
    key: str,
    module: Module,
    guarded: dict[str, Guarded],
) -> dict[str, str]:
    """Spell the fields of the tuples a module the file imports as `key` names.

    Returns:
      Each one's name through `key`, and the tuple unpacking one gives.

    """
    found: dict[str, str] = {}
    name: str
    for name in module.tuples:
        found.update(_fields(modules, target, f"{key}.{name}", (module, name), guarded))
    return found


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
