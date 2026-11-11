"""A checked tree's stub with no source beside it, a compiled module's (`_path.pyi`, with `_path.so`).

A type checker reads it for the module; `within` finds it for `installed.with_installed`, which
reads it as it reads an installed package's stub, for the calls the checked files make into it. It's
never checked or fixed. A stub beside its source is that module's own (`own_stubs`).
"""

import contextlib
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Final

from constricter.fix.index.modules import PACKAGE, STUB, SUFFIX, Module, module_name

_DOT: Final = "."


def roots(modules: Mapping[str, Module]) -> tuple[Path, ...]:
    """Find the directories the checked files' top-level packages and modules are in.

    Returns:
      Them, sorted: where a top-level module with a stub alone would be.

    """
    found: set[Path] = set()
    module: Module
    for module in modules.values():
        if module.folder and _DOT not in module.name:
            folder: Path = Path(module.folder)
            found.add(folder.parent if _is_package(module) else folder)
    return tuple(sorted(found))


def within(modules: Mapping[str, Module], tops: Sequence[Path], name: str) -> Path | None:
    """Find the stub the checked tree has alone for the module `name`.

    Under the nearest module above it that's checked, where that's a package (`pkg/_path.pyi` for
    `pkg._path`, a stub-only subpackage's `pkg/ext/__init__.pyi` for `pkg.ext`); with none above
    it, under the first of `tops` (see `roots`) that has one.

    Returns:
      The stub, or `None`: there's none, a source is beside it, or the module above is no package.

    """
    parts: list[str] = name.split(_DOT)
    end: int
    for end in range(len(parts) - 1, 0, -1):
        above: Module | None
        if (above := modules.get(_DOT.join(parts[:end]))) is not None:
            if not above.folder or not _is_package(above):
                return None
            return _alone(Path(above.folder).joinpath(*parts[end:]))
    top: Path
    for top in tops:
        stub: Path | None
        if (stub := _alone(top.joinpath(*parts))) is not None:
            return stub
    return None


def _is_package(module: Module) -> bool:
    """Check whether a checked module is a package: its folder's `__init__.py` is the module.

    Returns:
      Whether it is.

    """
    return module_name(Path(module.folder) / f"{PACKAGE}{SUFFIX}") == module.name


def _alone(base: Path) -> Path | None:
    """Find a module's stub under `base`, its path without a suffix, where no source is beside it.

    Returns:
      A package's `__init__.pyi`, or `base.pyi`; `None` with an `__init__.py` or a `base.py` there.

    """
    inside: frozenset[str] = _entries(base)
    if f"{PACKAGE}{SUFFIX}" in inside:
        return None
    if f"{PACKAGE}{STUB}" in inside:
        return base / f"{PACKAGE}{STUB}"
    beside: frozenset[str] = _entries(base.parent)
    if f"{base.name}{STUB}" in beside and f"{base.name}{SUFFIX}" not in beside:
        return base.with_name(f"{base.name}{STUB}")
    return None


@lru_cache(maxsize=4096)  # asked for each module the checked files import that isn't checked
def _entries(directory: Path) -> frozenset[str]:
    """List a directory's entries by name.

    Returns:
      Them; none for what isn't a directory, or can't be read.

    """
    with contextlib.suppress(OSError):
        return frozenset(entry.name for entry in directory.iterdir())
    return frozenset()
