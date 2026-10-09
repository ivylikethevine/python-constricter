# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for `await` of a call to another checked file's `async def`.

Found through the calling file's imports and the re-exports between them (`await load(url)`,
`await client.load(url)` after `import pkg.client as client`); its declared return types the
awaited call where the file can write it (see `project.portable`), or else its `return`s do, once
its file is checked (see `constricter.fix.values.returned`). A method's is its class's (see
`rules.tables`).
"""

from pathlib import Path

from constricter.fix.core.known import Guarded, Returns
from constricter.fix.core.signatures import AWAIT
from constricter.fix.index import project, sides
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name


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
    defined: tuple[Module, str]
    for spelled, defined in sides.called(catalog.modules, target, _awaitable):
        if defined[1] in defined[0].awaits:
            declared: dict[str, str] = {spelled: defined[0].awaits[defined[1]]}
            found.update(project.portable(catalog.modules, (target, defined), spelled, declared, guarded))
    return found


def returned(catalog: Index, path: Path, guarded: dict[str, Guarded], found: Returns) -> Returns:
    """Add what awaiting the file's calls to other checked files' undeclared `async def`s gives to `found`.

    By their `return`s, for modules already checked, each under `AWAIT` before the call's name as
    written, with what it rests on if it's a guess.

    Returns:
      `found`, with them; `found` itself for a file `catalog` doesn't have, or one that calls none.

    """
    awaited: dict[str, str] = {}
    guesses: dict[str, frozenset[str]] = {}
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return found
    spelled: str
    defined: tuple[Module, str]
    for spelled, defined in sides.called(catalog.modules, target, _awaitable):
        key: str
        if (key := f"{AWAIT}{defined[1]}") not in defined[0].returned.calls:
            continue
        typed: dict[str, str] = {spelled: defined[0].returned.calls[key]}
        kept: dict[str, str]
        if kept := project.portable(catalog.modules, (target, defined), spelled, typed, guarded):
            awaited[f"{AWAIT}{spelled}"] = kept[spelled]
            if key in defined[0].returned.guesses:
                guesses[f"{AWAIT}{spelled}"] = defined[0].returned.guesses[key]
    if not awaited:
        return found
    return found._replace(calls={**found.calls, **awaited}, guesses={**found.guesses, **guesses})


def needs(catalog: Index, module: Module) -> set[str]:
    """Find the other modules whose `async def`s `module` calls that only their `return`s could type.

    Returns:
      Their names: checked before it, what awaiting each gives is known.

    """
    return {
        defined[0].name
        for _, defined in sides.called(catalog.modules, module, _awaitable)
        if defined[1] in defined[0].unawaited
    } - {module.name}


def _awaitable(module: Module, name: str) -> bool:  # whether it defines an `async def` of the name
    return name in module.awaits or name in module.unawaited
