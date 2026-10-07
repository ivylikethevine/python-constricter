# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for `await` of a call to another checked file's `async def`.

Found through the calling file's imports and the re-exports between them (`await load(url)`,
`await client.load(url)` after `import pkg.client as client`); its declared return types the
awaited call where the file can write it (see `project.portable`). A method's is its class's
(see `rules.tables`).
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Final

from constricter.fix.core.known import Guarded, Origin
from constricter.fix.index import project, sides
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name

_HOPS: Final = 5  # how many re-exports to follow


def calls(catalog: Index, path: Path, guarded: dict[str, Guarded]) -> dict[str, str]:
    """Type what awaiting the calls the file at `path` makes to other checked files' `async def`s gives.

    `guarded`: the names its imported types need imported for type checking (see `Guarded`), which
    these types' are added to.

    Returns:
      Each call's name as written (`load`, `client.load`), mapped to its type; none for a file
      `catalog` doesn't have.

    """
    found: dict[str, str] = {}
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return found
    spelled: str
    for spelled in target.called:
        origin: Origin | None = sides.named(target, spelled)
        defined: tuple[Module, str] | None = (
            None if origin is None else _defined(catalog.modules, origin, _HOPS)
        )
        if defined is not None:
            declared: dict[str, str] = {spelled: defined[0].awaits[defined[1]]}
            found.update(project.portable(catalog.modules, (target, defined), spelled, declared, guarded))
    return found


def _defined(modules: Mapping[str, Module], origin: Origin, hops: int) -> tuple[Module, str] | None:
    """Follow `origin` (through re-exports) to the module that defines it as an `async def`.

    Returns:
      That module and the name, or `None`.

    """
    module: Module | None = modules.get(origin[0])
    name: str | None = origin[1]
    if module is None or name is None or not hops:
        return None
    if name in module.awaits:
        return module, name
    onward: Origin | None = module.names.get(name)
    return _defined(modules, onward, hops - 1) if onward and onward[0] != module.name else None
