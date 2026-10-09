# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for an empty container passed to another checked file's function.

Found through the calling file's imports and the re-exports between them (`add(names, "a")`,
`util.add(names, "a")`); a parameter the function declares a builtin container (`names: list[str]`)
types what's passed to it, where the file can write that type (see `project.portable`, and
`constricter.fix.values.fills`).
"""

from pathlib import Path

from constricter.fix.core.known import Guarded, Takers
from constricter.fix.index import project, sides
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name


def calls(catalog: Index, path: Path, guarded: dict[str, Guarded]) -> dict[str, Takers]:
    """Find the parameters the functions the file at `path` calls declare a builtin container.

    `guarded`: the names its imported types need imported for type checking (see `Guarded`), which
    these types' are added to.

    Returns:
      Each call's name as written (`add`, `util.add`), mapped to those parameters (see `Takers`),
      each type as the file can write it; none for a file `catalog` doesn't have.

    """
    target: Module | None = catalog.modules.get(module_name(path)) if path.suffix == SUFFIX else None
    found: dict[str, Takers] = {}
    if target is None:
        return found
    spelled: str
    defined: tuple[Module, str]
    for spelled, defined in sides.called(catalog.modules, target, lambda module, name: name in module.takers):
        declared: Takers = defined[0].takers[defined[1]]
        kept: dict[str, str] = project.portable(
            catalog.modules,
            (target, defined),
            spelled,
            {name: taken[2] for name, taken in declared.items()},
            guarded,
        )
        if kept:
            found[spelled] = {name: (*declared[name][:2], text) for name, text in kept.items()}
    return found
