# SPDX-License-Identifier: MIT
"""The standard-library class another checked file's class inherits from, out of a file's sight.

A file's class under another file's (`django.test.TestCase`) can't see what that one inherits from:
the index can. `library_bases` follows each of a file's classes' bases through the checked files
and the installed packages that declare their types, to the one standard-library class its
lines of bases end at (`unittest.TestCase`), with the names the classes on the way bind: any
other member is the library class's, as `constricter.fix.core.inherited.Lineage.definer` then
says.
"""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final

from constricter.fix.core.inherited import Beyond
from constricter.fix.index import plain
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name
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
    """Follow a class's bases to where they end: one library class at most, any mixins beside it.

    A class of several bases ends where the one that reaches a library class does, the others
    (each ending at none) binding what they bind before it.

    Returns:
      The standard-library class (the tables hold whole; `""`: none) and the names bound on the
      way; `None` for a base out of sight, two lines reaching a library class, or one too deep.

    """
    module: Module | None = modules.get(defined.rpartition(_DOT)[0])
    name: str = defined.rpartition(_DOT)[2]
    bases: list[str] | None = None if module is None else _bases(module, name)
    if module is None or bases is None:
        library: str | None = stdlib.held_whole(defined)
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
    if None in ends or len(reached) > 1:
        return None
    return (reached[0] if reached else "", hidden.union(*(end[1] for end in ends if end is not None)))


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
