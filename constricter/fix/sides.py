# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for a classmethod or staticmethod called on its class: `Row.make()`.

A class another checked file defines, found through the calling file's imports and the re-exports
between them (`MultiIndex.from_arrays(...)`, `pd.MultiIndex.from_arrays(...)`); the method's declared
return types the call where the file can write it (see `project.portable`).
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Final

from constricter.fix import project
from constricter.fix.known import Guarded, Origin
from constricter.fix.modules import SUFFIX, Index, Module, module_name

_DOT: Final = "."


def calls(
    catalog: Index,
    path: Path,
    guarded: Mapping[str, Guarded],
) -> tuple[dict[str, str], dict[str, Guarded]]:
    """Type the calls the file at `path` makes to other checked files' classes' class-side methods.

    `guarded`: the names its other imported types need imported for type checking (see `Guarded`).

    Returns:
      Each call's name as written (`Row.make`, `m.Row.make`), mapped to its type; and `guarded`,
      with the names these types need too. No call for a file `catalog` doesn't have.

    """
    needed: dict[str, Guarded] = dict(guarded)
    found: dict[str, str] = {}
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return found, needed
    spelled: str
    for spelled in target.called:
        receiver: str
        method: str
        receiver, _, method = spelled.rpartition(_DOT)
        defined: tuple[Module, str] | None = _class_named(catalog.modules, target, receiver)
        if defined is not None and method in defined[0].sides.get(defined[1], {}):
            declared: dict[str, str] = {spelled: defined[0].sides[defined[1]][method]}
            found.update(project.portable(catalog.modules, (target, defined), receiver, declared, needed))
    return found, needed


def _class_named(modules: Mapping[str, Module], target: Module, spelled: str) -> tuple[Module, str] | None:
    """Find the class another module defines that `target` writes as `spelled` (`Row`, `m.Row`, `pkg.Row`).

    Returns:
      The module defining it and its name there, through imports and re-exports; or `None`.

    """
    first: str
    rest: str
    first, _, rest = spelled.partition(_DOT)
    origin: Origin | None = target.names.get(first)
    if origin is None or origin[0] == target.name or first in target.shadowed:
        return None
    path: list[str] = [origin[0], *([origin[1]] if origin[1] else []), *(rest.split(_DOT) if rest else [])]
    return project.definition(modules, (_DOT.join(path[:-1]), path[-1]), project.CLASS)
