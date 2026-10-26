"""Cross-module `--fix` for a classmethod or staticmethod called on its class: `Row.make()`.

A class another checked file defines, found through the calling file's imports and the re-exports
between them (`MultiIndex.from_arrays(...)`, `pd.MultiIndex.from_arrays(...)`); the method's declared
return types the call where the file can write it (see `spelling.portable`). And one of the file's
own classes that takes the method from such a base (`Sub.make()`): a `Self` return is that class.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Final

from constricter.fix.core.known import Guarded, Origin
from constricter.fix.index import project, spelling
from constricter.fix.index.modules import Index, Module, module_at

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
    if (target := module_at(catalog, path)) is None:
        return found, needed
    spelled: str
    for spelled in target.called:
        receiver: str
        method: str
        receiver, _, method = spelled.rpartition(_DOT)
        base: str | None = _base(target, receiver, method, project.DEPTH)
        defined: tuple[Module, str] | None = _class_named(catalog.modules, target, base or receiver)
        if defined is None or method not in defined[0].sides.get(defined[1], {}):
            continue
        if base is not None and method in defined[0].selfish.get(defined[1], ()):
            found[spelled] = receiver  # its `Self`: the file's own class
            continue
        declared: dict[str, str] = {spelled: defined[0].sides[defined[1]][method]}
        found.update(
            spelling.portable(catalog.modules, (target, defined), base or receiver, declared, needed),
        )
    return found, needed


def _base(target: Module, receiver: str, method: str, depth: int) -> str | None:
    """Find the base another module defines that one of `target`'s own classes takes `method` from.

    Its first base, through the file's own classes, that the file doesn't define: `None` for a
    class that isn't the file's, one that binds `method` itself, or a name the file binds as a
    value too.

    Returns:
      The base, as the file writes it.

    """
    if (
        receiver not in target.bases
        or receiver in target.shadowed
        or method in target.bound.get(receiver, frozenset[str]())
    ):
        return None
    written: str
    for written in target.bases[receiver] if depth else ():
        if written not in target.bases:
            return written
        if method in target.bound.get(written, frozenset[str]()):
            return None  # the file's own: its tables have it
        found: str | None
        if (found := _base(target, written, method, depth - 1)) is not None:
            return found
    return None


def _class_named(modules: Mapping[str, Module], target: Module, spelled: str) -> tuple[Module, str] | None:
    """Find the class another module defines that `target` writes as `spelled` (`Row`, `m.Row`, `pkg.Row`).

    Returns:
      The module defining it and its name there, through imports and re-exports; or `None`.

    """
    origin: Origin | None = project.written_origin(target, spelled)
    return None if origin is None else project.definition(modules, origin, project.CLASS)
