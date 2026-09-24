# SPDX-License-Identifier: MIT
"""Installed packages' declared types, for `--fix` to type calls into them as it does checked files'.

`with_installed` adds to the cross-file index the modules the checked files import from installed
packages that declare their types: a stub package (`numpy-stubs`), a `py.typed` package's stubs
(`.pyi`) or source, or a lone stub module. Each is found on the search path (`search_path`: the
running interpreter's, and the active virtual environment's) as the import system would, and read
as `modules.read` reads a checked file, but never checked or fixed; the modules they import from
their own package (re-exports) are read too, up to `LIMIT` modules in all. Each module read is
cached (`cached`) under the user's cache directory, by its file's path, size and modification time
and constricter's version: a package upgraded, or a new constricter, reads it again.
"""

import contextlib
import hashlib
import os
import pickle  # the cache: written and read by constricter alone, in the user's own directory
import sys
import sysconfig
import tempfile
from collections.abc import Iterable, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Final, cast

from constricter import __version__
from constricter.fix.modules import STUB, SUFFIX, Index, Module, indexed, read

LIMIT: Final = 2000  # the most installed modules one run reads
_STUBS: Final = "-stubs"
_TYPED: Final = "py.typed"
_PACKAGE: Final = "__init__"
_VIRTUAL_ENV: Final = "VIRTUAL_ENV"
_STDLIB: Final = sys.stdlib_module_names
_CACHE_HOME: Final = "XDG_CACHE_HOME"
_LOCAL_APP_DATA: Final = "LOCALAPPDATA"  # Windows'
_CACHE: Final = "constricter"


def search_path() -> tuple[Path, ...]:
    """List the directories installed packages are found in: the interpreter's, then the active environment's.

    The environment in `VIRTUAL_ENV`, where the checked code runs, even when constricter runs in
    another (pre-commit's, pipx's).

    Returns:
      Them, the standard library's own left out.

    """
    stdlib: set[Path] = {Path(sysconfig.get_paths()[key]).resolve() for key in ("stdlib", "platstdlib")}
    active: str | None = os.environ.get(_VIRTUAL_ENV)
    extra: list[str] = (
        [] if active is None else [str(p) for p in sorted(Path(active).glob("lib/python3*/site-packages"))]
    )
    extra += [] if active is None else [str(Path(active) / "Lib" / "site-packages")]  # Windows
    found: dict[Path, None] = {}
    entry: str
    for entry in (*sys.path, *extra):
        path: Path = Path(entry or ".").resolve()
        if path.is_dir() and path not in stdlib:
            found[path] = None
    return tuple(found)


def with_installed(catalog: Index, search: Sequence[Path]) -> Index:
    """Add the installed modules the checked files import to `catalog` (see the module docstring).

    Returns:
      The index, with them.

    """
    wanted: list[str] = _imported(catalog.modules.values())  # grows as it's walked
    found: dict[str, Module] = {}
    seen: set[str] = set(catalog.modules)
    name: str
    for name in wanted:
        if len(found) >= LIMIT:
            break
        path: Path | None
        module: Module | None
        if (
            name in seen
            or (path := locate(name, tuple(search))) is None
            or (module := cached(path, name)) is None
        ):
            seen.add(name)
            continue
        seen.add(name)
        found[name] = module
        top: str = name.partition(".")[0]
        # Walked as it grows: the modules this one re-exports from.
        wanted.extend(  # ruff: ignore[loop-iterator-mutation]
            other for other in _imported([module]) if other.partition(".")[0] == top
        )
    return indexed([*catalog.modules.values(), *found.values()]) if found else catalog


def cache_directory() -> Path:
    """Find where installed modules' reads are cached: `$XDG_CACHE_HOME`, `%LOCALAPPDATA%`, or `~/.cache`.

    Returns:
      Its `constricter` directory (not made yet).

    """
    base: str | None = os.environ.get(_CACHE_HOME) or os.environ.get(_LOCAL_APP_DATA)
    return (Path(base) if base else Path.home() / ".cache") / _CACHE / "installed"


def cached(path: Path, name: str) -> Module | None:
    """Read an installed module (see `modules.read`), from the cache if it's there and still current.

    A cache that can't be read or written (a read-only home, a corrupt entry) is passed over: the
    module is read from its file.

    Returns:
      Its module, or `None` if it can't be read or parsed.

    """
    try:
        stat: os.stat_result = path.stat()
    except OSError:
        return None
    key: str = f"{__version__}\0{name}\0{path.resolve()}\0{stat.st_size}\0{stat.st_mtime_ns}"
    entry: Path = cache_directory() / f"{hashlib.sha256(key.encode()).hexdigest()}.pickle"
    module: Module | None
    if (module := _load(entry)) is not None:
        return module
    if (module := read(path, name)) is not None:
        _store(entry, module)
    return module


def _load(entry: Path) -> Module | None:
    """Read a cache entry.

    Returns:
      Its module, or `None` if there's none, or it can't be read.

    """
    with contextlib.suppress(OSError, pickle.UnpicklingError, EOFError, AttributeError, TypeError):
        return _module(cast("object", pickle.loads(entry.read_bytes())))
    return None


def _module(found: object) -> Module | None:
    return found if isinstance(found, Module) else None


def _store(entry: Path, module: Module) -> None:
    """Write a module's read to its cache entry, whole or not at all (another run may be reading it)."""
    with contextlib.suppress(OSError):
        entry.parent.mkdir(parents=True, exist_ok=True)
        handle: int
        temporary: str
        handle, temporary = tempfile.mkstemp(dir=entry.parent, suffix=".tmp")
        os.close(handle)
        _ = Path(temporary).write_bytes(pickle.dumps(module))
        _ = Path(temporary).replace(entry)


def _imported(found: Iterable[Module]) -> list[str]:
    """List the modules `found` import from outside the standard library, and those they may name.

    `from pkg import util` may name the module `pkg.util` as well as something `pkg` defines; a call
    through an imported module (`pkg.util.f()` after `import pkg.util`) names each module on its way.

    Returns:
      Their names, in order, each once.

    """
    names: dict[str, None] = {}
    module: Module
    for module in found:
        origin: tuple[str, str | None]
        for origin in (*module.names.values(), *module.guarded.values()):
            if origin[0].partition(".")[0] not in _STDLIB and origin[0] != module.name:
                names[origin[0]] = None
                if origin[1] is not None:
                    names[f"{origin[0]}.{origin[1]}"] = None
        callee: str
        for callee in module.called:
            head: str
            parts: list[str]
            head, *parts = callee.split(".")
            through: tuple[str, str | None] = module.names[head]
            if through[1] is None and through[0].partition(".")[0] not in _STDLIB:
                names.update(
                    dict.fromkeys(".".join([through[0], *parts[:end]]) for end in range(1, len(parts))),
                )
    return list(names)


@lru_cache(maxsize=4096)
def locate(name: str, search: tuple[Path, ...]) -> Path | None:
    """Find the file an installed module `name` declares its types in, as the import system would.

    In the first directory of `search` that has its package: its stub package (`pkg-stubs`) first,
    then the package itself if it's typed (`py.typed`), a stub (`.pyi`) before its source; or a lone
    stub module (`mod.pyi`).

    Returns:
      The file, or `None` if it isn't installed, or doesn't declare its types.

    """
    top: str
    rest: list[str]
    top, *rest = name.split(".")
    directory: Path
    for directory in search:
        roots: list[Path] = [directory / f"{top}{_STUBS}"]
        if (directory / top / _TYPED).is_file():
            roots.append(directory / top)
        root: Path
        for root in roots:
            if root.is_dir():
                return _module_file(root.joinpath(*rest))
        if not rest and (directory / f"{top}{STUB}").is_file():
            return directory / f"{top}{STUB}"
        if (directory / top).is_dir() or (directory / f"{top}{SUFFIX}").is_file():
            return None  # installed here, untyped: an earlier directory shadows any later one
    return None


def _module_file(base: Path) -> Path | None:
    """Find a module's file under a package's root: a package's `__init__`, or a module, stub first.

    Returns:
      It, or `None`.

    """
    candidates: tuple[Path, ...] = (
        base / f"{_PACKAGE}{STUB}",
        base / f"{_PACKAGE}{SUFFIX}",
        base.with_name(f"{base.name}{STUB}"),
        base.with_name(f"{base.name}{SUFFIX}"),
    )
    return next((path for path in candidates if path.is_file()), None)
