"""Installed packages' declared types, for `--fix` to type calls into them as it does checked files'.

`with_installed` adds to the cross-file index the modules the checked files import from installed
packages that declare their types: a stub package (`numpy-stubs`), a `py.typed` package's stubs
(`.pyi`) or source, or a lone stub module; and, as guesses (`declared`, see `as_untyped`), those of
packages that declare none, read for their own annotations. Each is found on the search path (the
running interpreter's, and the active virtual environment's, `search_path`) as the import system
would, and read
as `modules.read` reads a checked file, but never checked or fixed; the modules they import from
their own package (re-exports) are read too, up to `LIMIT` modules in all. Each module read is
cached (`cached`) under the user's cache directory, by its file's path, size and modification time
and constricter's version and reading code: a package upgraded, or a changed constricter, reads it
again. Each version and reading code has its own part of the cache, swept as it's written to, a day
apart at most (`swept`): what's unread for a month goes, and what's over its cap.
"""

import contextlib
import hashlib
import os
import pickle  # the cache: written and read by constricter alone, in the user's own directory
import sys
import sysconfig
import tempfile
import time
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from typing import Final, cast

from constricter._version import __version__  # not the package's: it imports the rules
from constricter.empty import Empty
from constricter.fix.core.known import Returns
from constricter.fix.index.modules import DECLARED, PACKAGE, STUB, SUFFIX, Index, Memo, Module, read, settled
from constricter.fix.index.project import HOPS, STDLIB
from constricter.fix.index.stubs.declared import Class, Declarations

LIMIT: Final = 2000  # the most installed modules one run reads
_STUBS: Final = "-stubs"
_TYPED: Final = "py.typed"
# Modules whose classes are typing forms, typed by typeshed, installed with no `py.typed`: read as
# untyped, their `TypeVar` and `TypeVarTuple` would be constructed, and `_T: TypeVar = TypeVar("_T")`
# breaks every type named by `_T` (sqlalchemy's `util/typing.py`, the mega run of 2026-10-27).
_FORMS: Final = frozenset({"typing_extensions", "_typeshed"})
# Read for its classes alone (`u8`, `i64`, mypyc's native integers), its functions' returns not: its
# typing forms (`TypedDict`, `Arg`, `FlexibleAlias`) aren't classes, so only those name a type.
_CLASSES_ALONE: Final = frozenset({"mypy_extensions"})
_UNREAD: Final[Mapping[str, str]] = Empty()  # an untyped package's class's attributes: not offered
_PARTIAL: Final = "partial"  # in a stub package's `py.typed`: it types some of the package alone
_UNDERSCORE: Final = "_"
_VIRTUAL_ENV: Final = "VIRTUAL_ENV"
_CACHE_HOME: Final = "XDG_CACHE_HOME"
_LOCAL_APP_DATA: Final = "LOCALAPPDATA"  # Windows'
_CACHE: Final = "constricter"
_ENTRIES: Final = "*.pickle"
_SWEPT: Final = ".swept"  # in a build's part of the cache: touched when that build last swept it
_DAY: Final = 86400.0  # the seconds between a build's sweeps
_KEPT: Final = 30 * _DAY  # the seconds an entry is kept unread, and another build's part unswept
_CAP: Final = 256 << 20  # the bytes a build's entries may take: past it, the longest unread go


def search_path() -> tuple[Path, ...]:
    """List the directories installed packages are found in: the active environment's, then the interpreter's.

    The environment in `VIRTUAL_ENV`, where the checked code runs, even when constricter runs in
    another (pre-commit's, pipx's), whose own packages mustn't shadow the code's.

    Returns:
      Them, the standard library's own left out.

    """
    stdlib: set[Path] = {Path(sysconfig.get_paths()[key]).resolve() for key in ("stdlib", "platstdlib")}
    active: str | None = os.environ.get(_VIRTUAL_ENV)
    extra: list[str] = []
    if active is not None:
        extra = [str(p) for p in sorted(Path(active).glob("lib/python3*/site-packages"))]
        extra.append(str(Path(active) / "Lib" / "site-packages"))  # Windows
    found: dict[Path, None] = {}
    entry: str
    for entry in (*extra, *sys.path):
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
        if name in seen:
            continue
        seen.add(name)
        path: Path | None
        module: Module | None
        if (path := locate(name, tuple(search))) is not None:
            module = cached(path, name)
        elif name.partition(".")[0] in _FORMS:  # typeshed's: its classes are special forms
            module = None
        else:  # installed with no types declared, or not at all
            module = _unseen(name, tuple(search))
            module = None if module is None else as_untyped(module)
            if module is not None and name.partition(".")[0] in _CLASSES_ALONE:
                module = replace(module, returned=Returns(), loose=frozenset())
        if module is None:
            continue
        found[name] = module
        top: str = name.partition(".")[0].lstrip(_UNDERSCORE)
        # Walked as it grows: the modules this one re-exports from, its package's private twin's
        # too (`pytest`'s, from `_pytest`).
        wanted.extend(  # ruff: ignore[loop-iterator-mutation]
            other for other in _imported([module]) if other.partition(".")[0].lstrip(_UNDERSCORE) == top
        )
    if not found:
        return catalog
    every: dict[str, Module] = {**catalog.modules, **found}
    every.update((name, _generics(every, settled(every, module))) for name, module in found.items())
    # The checked files' repeated names kept; what was worked out of the modules there were, not.
    return catalog._replace(modules=every, names=sorted(every), memo=Memo())


def _generics(modules: Mapping[str, Module], module: Module) -> Module:
    """Drop the classes a subscripted base made look generic whose bases pass no type variable.

    `class float64(floating[_64Bit])` binds every parameter it inherits: it's written bare.

    Returns:
      The module, its `generics` corrected.

    """
    bases: Mapping[str, frozenset[str]] = {} if module.declared is None else module.declared.bases
    bound: frozenset[str] = frozenset(
        name
        for name, names in bases.items()
        if name in module.generics and not any(_is_type_var(modules, module, found) for found in names)
    )
    return replace(module, generics=module.generics - bound) if bound else module


def _is_type_var(modules: Mapping[str, Module], module: Module, name: str, hops: int = HOPS) -> bool:
    """Check whether `name` is a type variable in `module`: its own, or one it imports from an indexed module.

    Returns:
      Whether it is (unknown: no).

    """
    if name in module.type_vars or (module.declared is not None and name in module.declared.variables):
        return True
    origin: tuple[str, str | None] | None = module.names.get(name) or module.guarded.get(name)
    onward: Module | None = None if origin is None or origin[1] is None else modules.get(origin[0])
    return (
        hops > 0
        and onward is not None
        and onward is not module
        and origin is not None
        and _is_type_var(modules, onward, origin[1] or "", hops - 1)
    )


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
    key: str = f"{name}\0{path.resolve()}\0{stat.st_size}\0{stat.st_mtime_ns}"
    entry: Path = _own() / f"{hashlib.sha256(key.encode()).hexdigest()}.pickle"
    loaded: Module | None
    if (loaded := _load(entry)) is not None:
        return loaded
    module: Module | None
    if (module := read(path, name)) is not None:
        _store(entry, module)
    return module


@lru_cache(maxsize=1)
def _code() -> str:
    """Fingerprint the code that reads a module and shapes what's cached (`constricter.fix`'s).

    A development build keeps its version as its modules' fields change: an entry pickled by another
    unpickles with them shifted.

    Returns:
      Its sources' digest.

    """
    sources: list[Path] = sorted(Path(__file__).parents[1].rglob(f"*{SUFFIX}"))
    return hashlib.sha256(b"\0".join(source.read_bytes() for source in sources)).hexdigest()


def _own() -> Path:
    """Find this build's part of the cache: another version's or build's entries unpickle wrong.

    Returns:
      Its directory, named by the version and `_code` (not made yet).

    """
    return cache_directory() / hashlib.sha256(f"{__version__}\0{_code()}".encode()).hexdigest()[:16]


def _load(entry: Path) -> Module | None:
    """Read a cache entry, and mark one read after half its keep as read now.

    Returns:
      Its module, or `None` if there's none, or it can't be read.

    """
    with contextlib.suppress(OSError, pickle.UnpicklingError, EOFError, AttributeError, TypeError):
        module: Module | None = _module(cast("object", pickle.loads(entry.read_bytes())))
        if _age(entry, time.time()) > _KEPT / 2:
            os.utime(entry)
        return module
    return None


def _age(path: Path, now: float) -> float:
    """Find how long ago `path` was written or marked read.

    Returns:
      The seconds; none for one that can't be read, which is then kept.

    """
    try:
        return now - path.stat().st_mtime
    except OSError:
        return 0.0


def _dropped(part: Path) -> None:
    """Remove a build's part of the cache: its entries, what a stopped write left, and its directory."""
    with contextlib.suppress(OSError):
        each: Path
        for each in (*part.glob(_ENTRIES), *part.glob("*.tmp"), part / _SWEPT):
            each.unlink(missing_ok=True)
        part.rmdir()


@lru_cache(maxsize=4)  # once a process for a cache, as it first writes there
def swept(own: Path) -> None:
    """Sweep the cache, a day or more after this build last did.

    The entries no build's part holds (the cache's, before each had one) go, and another build's
    part unswept for `_KEPT`: one still used sweeps, and marks its own. Of this build's entries,
    those unread for `_KEPT`, then the longest unread until the rest fit `_CAP`.
    """
    now: float = time.time()
    if (own / _SWEPT).exists() and _age(own / _SWEPT, now) < _DAY:
        return
    with contextlib.suppress(OSError):
        (own / _SWEPT).touch()
        other: Path
        for other in own.parent.iterdir():
            if other.match(_ENTRIES):
                other.unlink(missing_ok=True)
            elif other != own and len(other.name) == len(own.name) and _age(other / _SWEPT, now) > _KEPT:
                _dropped(other)
        held: list[tuple[float, int, Path]] = sorted(
            (stat.st_mtime, stat.st_size, entry) for entry in own.glob(_ENTRIES) for stat in (entry.stat(),)
        )
        size: int = sum(taken for _, taken, _ in held)
        written: float
        taken: int
        entry: Path
        for written, taken, entry in held:
            if now - written <= _KEPT and size <= _CAP:
                break
            entry.unlink(missing_ok=True)
            size -= taken


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
        swept(entry.parent)


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
            if origin[0].partition(".")[0] not in STDLIB and origin[0] != module.name:
                names[origin[0]] = None
                if origin[1] is not None:
                    names[f"{origin[0]}.{origin[1]}"] = None
        callee: str
        for callee in module.called:
            head: str
            parts: list[str]
            head, *parts = callee.split(".")
            through: tuple[str, str | None] = module.names[head]
            if through[1] is None and through[0].partition(".")[0] not in STDLIB:
                names.update(
                    dict.fromkeys(".".join([through[0], *parts[:end]]) for end in range(1, len(parts))),
                )
    return list(names)


@lru_cache(maxsize=4096)
def locate(name: str, search: tuple[Path, ...]) -> Path | None:
    """Find the file an installed module `name` declares its types in, as PEP 561 orders them.

    Its stub package (`pkg-stubs`) first, in any directory of `search`; one that's partial (its
    `py.typed` says so) leaves a module it lacks to the package. Then, in the first directory that
    has the package, as the import system would: the package itself if it's typed (`py.typed`, or a
    namespace package's subpackage's), a stub (`.pyi`) before its source; or a lone stub module
    (`mod.pyi`).

    Returns:
      The file, or `None` if it isn't installed, or doesn't declare its types.

    """
    top: str
    rest: list[str]
    top, *rest = name.split(".")
    directory: Path
    for directory in search:
        stubs: Path = directory / f"{top}{_STUBS}"
        found: Path | None
        if stubs.is_dir() and (
            (found := _module_file(stubs.joinpath(*rest))) is not None or not _partial(stubs)
        ):
            return found
    for directory in search:
        root: Path | None
        stub: bool
        here: bool
        root, stub, here = _package(directory, top, tuple(rest))
        if root is not None:
            return _module_file(root.joinpath(*rest))
        if not rest and stub:
            return directory / f"{top}{STUB}"
        if here:
            return None  # installed here, untyped: an earlier directory shadows any later one
    return None


@lru_cache(maxsize=256)
def _partial(stubs: Path) -> bool:
    """Check whether a stub package is partial: its `py.typed` says `partial` (PEP 561).

    Returns:
      Whether it is.

    """
    marker: Path = stubs / _TYPED
    return marker.is_file() and _PARTIAL in marker.read_text(encoding="utf-8", errors="replace").split()


def as_untyped(module: Module) -> Module:
    """Take an installed module that declares no types as the guesses its own annotations are.

    What pyright reads with `useLibraryCodeForTypes`, held to the source's own annotations: its
    functions' declared returns become its `returned.calls`, and its classes' methods' its
    `returned.methods`, each resting on `declared`, so a call to one is a guess (`--unsafe-fixes`,
    or `--likely` where the set passes the bars) as an unannotated function's `return`s are; its
    classes' attributes, its classmethods' returns and its overloads aren't offered, having no way
    to be a guess.

    Returns:
      The module, so taken.

    """
    guesses: dict[str, frozenset[str]] = dict.fromkeys(module.returns, DECLARED)
    methods: dict[str, dict[str, str]] = {owner: dict(each) for owner, each in module.methods.items()}
    guesses.update({f"{owner}.{name}": DECLARED for owner, each in methods.items() for name in each})
    return replace(
        module,
        untyped=True,
        returns={},
        methods={},
        classes=dict.fromkeys(module.classes, _UNREAD),  # its classes by name, their attributes unread
        sides={},
        held_sides={},
        # Its signatures would type a call as certain: not offered. Its classes' bases stay, for
        # the library class a line of bases ends at (see `constricter.fix.index.beyond`).
        declared=None
        if module.declared is None
        else Declarations(
            {},
            {},
            {},
            {},
            module.declared.exports,
            module.declared.bases,
            {name: Class((), each.bases, {}, {}) for name, each in module.declared.classes.items()},
        ),
        returned=Returns(
            {**module.returned.calls, **module.returns},
            {**module.returned.guesses, **guesses},
            module.returned.names,
            {**module.returned.methods, **methods},
        ),
        loose=module.loose | frozenset(name for each in methods.values() for name in each),
    )


def unseen(name: str) -> Module | None:
    """Read an installed module that declares no types, for its classes' bases alone.

    Never part of the index: nothing it declares types a call, as no type checker reads it. What
    its classes inherit from still says where a class under one ends (see `constricter.fix.index.beyond`).

    Returns:
      Its module, read from its source as `cached` reads one; `None` for the standard library's, or
      one that isn't installed.

    """
    if not name or name.partition(".")[0] in STDLIB:
        return None
    return _unseen(name, _searched(tuple(sys.path), os.environ.get(_VIRTUAL_ENV)))


@lru_cache(maxsize=4)
def _searched(_path: tuple[str, ...], _active: str | None) -> tuple[Path, ...]:  # `search_path`, for both
    return search_path()


@lru_cache(maxsize=1024)  # asked for each class under one of its classes
def _unseen(name: str, search: tuple[Path, ...]) -> Module | None:
    paths: Iterable[Path | None] = (
        _module_file(directory.joinpath(*name.split("."))) for directory in search
    )
    path: Path | None = next((path for path in paths if path is not None), None)
    return None if path is None else cached(path, name)


@lru_cache(maxsize=4096)  # asked for each of a package's modules
def _package(directory: Path, top: str, rest: tuple[str, ...]) -> tuple[Path | None, bool, bool]:
    """Find what `directory` has of the top-level package or module `top`, for its module `rest`.

    Returns:
      The package, where it declares its types: a `py.typed` in it, or in the subpackage of a
      namespace package (no `__init__`) on the way to `rest`; else `None`. Whether it has a lone stub
      module for it. And whether it's installed there, shadowing a later directory's: not a namespace
      package's portion, which another directory may add to.

    """
    package: Path = directory / top
    namespace: bool = package.is_dir() and _module_file(package) is None
    typed: bool = (package / _TYPED).is_file() or (
        namespace
        and any((package.joinpath(*rest[:end]) / _TYPED).is_file() for end in range(1, len(rest) + 1))
    )
    return (
        package if typed and package.is_dir() else None,
        (directory / f"{top}{STUB}").is_file(),
        (package.is_dir() and not namespace) or (directory / f"{top}{SUFFIX}").is_file(),
    )


def _module_file(base: Path) -> Path | None:
    """Find a module's file under a package's root: a package's `__init__`, or a module, stub first.

    Returns:
      It, or `None`.

    """
    candidates: tuple[Path, ...] = (
        base / f"{PACKAGE}{STUB}",
        base / f"{PACKAGE}{SUFFIX}",
        base.with_name(f"{base.name}{STUB}"),
        base.with_name(f"{base.name}{SUFFIX}"),
    )
    return next((path for path in candidates if path.is_file()), None)
