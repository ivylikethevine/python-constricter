# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for a classmethod or staticmethod called on its class: `Row.make()`.

A class another checked file defines, found through the calling file's imports and the re-exports
between them (`MultiIndex.from_arrays(...)`, `pd.MultiIndex.from_arrays(...)`); the method's declared
return types the call where the file can write it (see `project.portable`). And one of the file's
own classes that takes the method from such a base (`Sub.make()`): a `Self` return is that class.
"""

from collections.abc import Callable, Iterator, Mapping
from pathlib import Path
from typing import Final

from constricter.fix.core.known import Guarded, Origin
from constricter.fix.index import project
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name

_DOT: Final = "."
_DEPTH: Final = 8  # how many of the file's own classes a line of bases is followed through
_HOPS: Final = 5  # how many re-exports a call is followed through


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
        base: str | None = _base(target, receiver, method, _DEPTH)
        defined: tuple[Module, str] | None = _class_named(catalog.modules, target, base or receiver)
        if defined is None or method not in defined[0].sides.get(defined[1], {}):
            continue
        if base is not None and method in defined[0].selfish.get(defined[1], ()):
            found[spelled] = receiver  # its `Self`: the file's own class
            continue
        declared: dict[str, str] = {spelled: defined[0].sides[defined[1]][method]}
        found.update(project.portable(catalog.modules, (target, defined), base or receiver, declared, needed))
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
    origin: Origin | None = named(target, spelled)
    return None if origin is None else project.definition(modules, origin, project.CLASS)


def named(target: Module, spelled: str) -> Origin | None:
    """Resolve what `target` writes as `spelled` (`Row`, `m.Row`, `pkg.m.load`) through its imports.

    Returns:
      The module it's an attribute of, and its name there; `None` for a name the file doesn't
      import, binds as a value too, or imports from itself.

    """
    first: str
    rest: str
    first, _, rest = spelled.partition(_DOT)
    origin: Origin | None = target.names.get(first)
    if origin is None or origin[0] == target.name or first in target.shadowed:
        return None
    path: list[str] = [origin[0], *([origin[1]] if origin[1] else []), *(rest.split(_DOT) if rest else [])]
    return _DOT.join(path[:-1]), path[-1]


def called(
    modules: Mapping[str, Module],
    target: Module,
    has: Callable[[Module, str], bool],
) -> Iterator[tuple[str, tuple[Module, str]]]:
    """Find the calls `target` makes to what another module defines, as `has` says of a module's name.

    Through its imports, and the re-exports between the modules (`_HOPS` of them).

    Yields:
      Each call's name as written (`load`, `client.load`), and the module defining what it calls
      and its name there.

    """
    spelled: str
    for spelled in target.called:
        origin: Origin | None = named(target, spelled)
        defined: tuple[Module, str] | None = (
            None if origin is None else _followed(modules, origin, has, _HOPS)
        )
        if defined is not None:
            yield spelled, defined


def _followed(
    modules: Mapping[str, Module],
    origin: Origin,
    has: Callable[[Module, str], bool],
    hops: int,
) -> tuple[Module, str] | None:
    """Follow `origin` (through re-exports) to the module that `has` it.

    Returns:
      That module and the name, or `None`.

    """
    module: Module | None = modules.get(origin[0])
    name: str | None = origin[1]
    if module is None or name is None or not hops:
        return None
    if has(module, name):
        return module, name
    onward: Origin | None = module.names.get(name)
    return _followed(modules, onward, has, hops - 1) if onward and onward[0] != module.name else None
