"""Cross-module `--fix` for `with` on a call to another checked file's `@contextmanager` function.

Found through the calling file's imports and the re-exports between them (`with temp_dir() as d`,
`with helper.temp_dir() as d`); what it declares it yields types the target where the file can
write it (see `spelling.portable`), or else what its `yield`s give, once its file is checked (see
`constricter.fix.values.entered`).
"""

from pathlib import Path

from constricter.fix.core.known import Guarded, Passed
from constricter.fix.index import project, spelling
from constricter.fix.index.modules import Index, Module, module_at
from constricter.fix.values.entered import ENTERED


def calls(catalog: Index, path: Path, guarded: dict[str, Guarded]) -> dict[str, Passed]:
    """Type what `with` gives of the calls the file at `path` makes to other checked files' managers.

    `guarded`: the names its imported types need imported for type checking (see `Guarded`), which
    these types' are added to.

    Returns:
      Each call's name as written (`temp_dir`, `helper.temp_dir`), mapped to its type and what that
      rests on if it's a guess; none for a file `catalog` doesn't have.

    """
    target: Module | None
    if (target := module_at(catalog, path)) is None:
        return {}
    found: dict[str, Passed] = {}
    spelled: str
    defined: tuple[Module, str]
    for spelled, defined in project.called(catalog.modules, target, _manages):
        key: str = f"{ENTERED}{defined[1]}"
        yielded: str | None = defined[0].managers[defined[1]] or defined[0].returned.calls.get(key)
        kept: dict[str, str] = (
            {}
            if yielded is None
            else spelling.portable(catalog.modules, (target, defined), spelled, {spelled: yielded}, guarded)
        )
        if kept:
            found[spelled] = (kept[spelled], defined[0].returned.guesses.get(key, frozenset()))
    return found


def needs(catalog: Index, module: Module) -> set[str]:
    """Find the other modules whose managers `module` calls that only their `yield`s could type.

    Returns:
      Their names: checked before it, what they yield is known.

    """
    return {
        defined[0].name
        for _, defined in project.called(catalog.modules, module, _manages)
        if not defined[0].managers[defined[1]]
    } - {module.name}


def _manages(module: Module, name: str) -> bool:  # whether it defines a manager of the name
    return name in module.managers
