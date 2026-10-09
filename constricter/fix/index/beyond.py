# SPDX-License-Identifier: MIT
"""The standard-library class another checked file's class inherits from, out of a file's sight.

A file's class under another file's (`django.test.TestCase`) can't see what that one inherits from:
the index can. `library_bases` follows each of a file's classes' bases through the checked files
and the installed packages, to the standard-library class its lines of bases end at
(`unittest.TestCase`), with the names the classes on the way bind: any other member is the
library class's, as `constricter.fix.core.inherited.Lineage.definer` then says. A package that
declares no types is read for its classes' bases alone (`installed.unseen`). Two lines each ending
at a library class give both, in order, where they share no ancestor.
"""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final

from constricter.fix.core.inherited import SEVERAL, Beyond
from constricter.fix.index import installed, plain
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name, takes
from constricter.fix.libraries import stdlib
from constricter.fix.values import classvars

if TYPE_CHECKING:
    from constricter.fix.index.declared import Class

_DOT: Final = "."
_OBJECT: Final = "object"
_DEPTH: Final = 8  # how many classes a line of bases is followed through


def library_bases(catalog: Index, path: Path) -> dict[str, Beyond]:
    """Find where the line of each base of the file at `path`'s classes ends, for one another module defines.

    Returns:
      Each such base, as the file writes it, with the standard-library class its line of single
      bases ends at (one the tables hold whole; `""` for a line that ends at none, a mixin's) and
      the names bound on the way; none for a base whose line has a class of several bases or one
      out of sight, nor for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return {}
    written: set[str] = {base for bases in target.bases.values() for base in bases} - {classvars.SPECIAL}
    ends: dict[str, Beyond | None] = {
        base: _end(catalog.modules, plain.resolved(catalog.modules, target, base))
        for base in sorted(written)
        if base not in target.bases
    }
    return {base: end for base, end in ends.items() if end is not None}


def _end(modules: Mapping[str, Module], defined: str) -> Beyond | None:
    """Follow a class another module defines (`defined`: its dotted path) up its bases.

    Returns:
      The standard-library class it ends at (`""`: none, a class with no base), and the names the
      classes on the way bind; `None` if `defined` is no indexed module's class, or its line
      doesn't end.

    """
    found: Beyond | None = _line(modules, defined, _DEPTH)
    return None if found is None or (found[0] and not found[1]) else found


def _line(modules: Mapping[str, Module], defined: str, depth: int) -> Beyond | None:
    """Follow a class's bases to where they end: at a library class, any mixins beside it.

    A class of several bases ends where those that reach a library class do, the others (each
    ending at none) binding what they bind before them. An installed package that declares no
    types is read for its classes' bases (see `installed.unseen`).

    Returns:
      The standard-library class (the tables hold whole; `""`: none; several, `SEVERAL` between
      them) and the names bound on the way; `None` for a base out of sight, two lines reaching
      library classes that share an ancestor, or one too deep.

    """
    name: str = defined.rpartition(_DOT)[2]
    module: Module | None = modules.get(defined.rpartition(_DOT)[0])
    library: str | None = stdlib.held_whole(defined)
    if module is None and library is None:
        module = installed.unseen(defined.rpartition(_DOT)[0])
    bases: list[str] | None = None if module is None else _bases(module, name)
    if module is not None and bases is None and depth and takes(module, name):  # a re-export: followed
        onward: tuple[str, str | None] = module.names[name]
        return _line(modules, _DOT.join(part for part in onward if part), depth - 1)
    if module is None or bases is None:
        return None if library is None else (library, frozenset())
    hidden: frozenset[str] = module.bound[name] | {name}
    ends: list[Beyond | None] = [
        _line(
            modules,
            f"{module.name}{_DOT}{base}" if base in module.bound else plain.resolved(modules, module, base),
            depth - 1,
        )
        if depth
        else None
        for base in bases
    ]
    reached: list[str] = [end[0] for end in ends if end is not None and end[0]]
    lines: list[frozenset[str]] = [stdlib.lines(path) for each in reached for path in each.split(SEVERAL)]
    if None in ends or len(frozenset[str]().union(*lines)) != sum(len(line) for line in lines):
        return None
    return (SEVERAL.join(reached), hidden.union(*(end[1] for end in ends if end is not None)))


def _bases(module: Module, name: str) -> list[str] | None:
    """List the bases of a class `module` (a checked file's, or an installed package's) defines once.

    Returns:
      Them as written, `object` left out; `None` if it defines no such class.

    """
    if name not in module.bound:
        return None
    declared: Class | None = None if module.declared is None else module.declared.classes.get(name)
    written: Sequence[str] = module.bases.get(name, ()) if declared is None else declared.bases
    return [base for base in written if base not in {classvars.SPECIAL, _OBJECT}]


def emptied(catalog: Index, path: Path) -> dict[str, Mapping[str, str]]:
    """Find the attributes the file at `path`'s classes take bound to an empty container from another file's.

    A base another checked file defines, which binds one so and does no more with it (see
    `Module.emptied`): what the file's own classes' methods add to it types it for them.

    Returns:
      Each such class's attributes' kinds, by its name; none for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return {}
    found: dict[str, Mapping[str, str]] = {}
    name: str
    bases: tuple[str, ...]
    for name, bases in target.bases.items():
        kinds: dict[str, str] = {}
        base: str
        for base in bases:
            defined: str = "" if base in target.bases else plain.resolved(catalog.modules, target, base)
            module: Module | None = catalog.modules.get(defined.rpartition(_DOT)[0])
            if module is not None and not module.installed:
                kinds.update(module.emptied.get(defined.rpartition(_DOT)[2], {}))
        if kinds:
            found[name] = kinds
    return found
