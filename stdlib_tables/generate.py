"""Generate `constricter/fix/tables/`, the standard-library tables `--fix` types calls from.

  local/.venv/bin/python -m stdlib_tables             # rewrite them
  local/.venv/bin/python -m stdlib_tables --if-stale  # only if they're missing or stale

They aren't tracked: a build (`hatch_build.py`) generates them where they're missing or stale
(`current`), and an sdist carries them. They're stale when `source.json`'s stamp differs: the
basedpyright version `uv.lock` pins, and a digest of the code that generates them (`INPUTS`).

It reads the typeshed stubs basedpyright bundles (that pinned version, installed), as each platform
(Linux, macOS, Windows) and each Python version constricter supports (3.11 to 3.14) sees them (each
of the twelve in a worker process, where there are cores and processes to have), and keeps what
comes out the same for all twelve:

- `returns`: functions (and classes' own classmethods and staticmethods) returning a builtin type
  (`int`, `list[str]`, `str | None`), by every public path they're reached through;
- `any_str`: functions returning their arguments' `str` or `bytes` (an `AnyStr`, or overloads);
- `classes`: non-generic classes, and functions returning one, by the class's public path: the
  shortest (`unittest.TestLoader`, not `unittest.loader.TestLoader`), then its own module's;
- `methods` and `attributes`: what each such class's public methods (and `__enter__`, for `with`)
  return, and its attributes and properties hold, inherited ones included (in their method
  resolution order), by that path; a generic class's `__enter__` too, where it returns `Self`;
- `aliases`: the class's other public paths;
- `overloads`: functions whose arguments decide their return, and generic classes' constructors,
  each signature as `stdlib_tables/overloads.py` reads it;
- `type_parameters` and `subscriptable`: each generic class's type parameters, and whether every
  Python can subscript it at run time; `generic_attributes`: its own attributes and properties, as
  templates its instance's type arguments bind, and a non-generic class's own that `attributes`
  can't hold (a `list[ast.stmt]`); `elements`: what iterating each class's instance
  gives (`io.TextIOWrapper`'s `str`, `itertools.chain`'s `_T`), as such a template;
- `functions`: capitalised functions no other table types (`xml.etree.ElementTree.Comment`), and
  capitalised variables bound to one (`multiprocessing.Value`), so a call to one isn't taken to
  construct a class;
- `platform`: the modules some platform's stubs have nothing public in (`winreg`, `fcntl`), each
  to the platforms that have it;
- `awaited`: what awaiting a call of each `async def` with one declared return gives, a function's
  by its path and a method's by its class's path and its name (a class's own path: its instance);
  `awaited_overloads`: those its arguments decide (`asyncio.wait_for`), as `overloads` holds a
  function's;
- `variables`: module-level variables' types (`sys.path`, `os.sep`), as `returns` and `classes` hold
  a function's;
- `scalars`: which builtin scalar types (`accepting.SCALARS`), then containers (`CONTAINERS`),
  each class or alias takes, by every path an installed package's stub may import it from
  (`typing.SupportsIndex`, `_typeshed.StrPath`), and `scalar_members`: each of those types'
  members, for its protocols; installed packages' overloads are matched with them
  (`constricter.fix.index.stubs.stubbed`).

A return that names a `TypeVar` (but `AnyStr`), or anything vague but `Any` alone (`json.loads`'s,
under `returns`, for `vague` to judge), differs between overloads, or is spelled with a class inside
a generic (`list[Path]`), is left out; so is `typing` (its factories), `enum`'s classes (their
functional API makes a class), and what `_RUNTIME` lists.
"""

import argparse
import contextlib
import hashlib
import importlib.metadata
import json
import os
import tomllib
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures.process import BrokenProcessPool
from functools import lru_cache
from pathlib import Path
from typing import Final, TypeAlias, TypeVar, cast

from stdlib_tables.configured import YES, Signatures, Tables, tables_for
from stdlib_tables.reading import (
    Table,
)
from stdlib_tables.stubs import (
    CONFIGS,
    Config,
    Stubs,
)
from stdlib_tables.written import inherited, platform_only

ROOT: Final = Path(__file__).parents[1]
OUTPUT: Final = ROOT / "constricter" / "fix" / "tables"  # one JSON file per table
# Where each function or class only some platforms and Python versions have is (the tests' alone).
PARTIAL: Final = Path(__file__).with_name("partial.json")
STUBS: Final = "basedpyright"  # the package whose bundled typeshed stubs the tables are read from
READER: Final = "typeshed-client"  # and the one that reads them (`stdlib_tables.shed`)
# The code that decides the tables: the generator's, and the modules of constricter it imports (a
# test checks that's all of them).
INPUTS: Final = (
    *sorted(path.relative_to(ROOT).as_posix() for path in Path(__file__).parent.glob("*.py")),
    "constricter/fix/__init__.py",
    "constricter/fix/core/__init__.py",
    "constricter/fix/core/signatures.py",
    "constricter/offences.py",
    "constricter/source/__init__.py",
    "constricter/source/annotations.py",
    "constricter/source/decorators.py",
    "constricter/source/flow.py",
    "constricter/source/keys.py",
    "constricter/source/quoted.py",
    "constricter/source/syntax.py",
    "constricter/source/walked.py",
)
_SOURCE: Final = OUTPUT / "source.json"  # what the tables were generated from: `stamp`, and more
_LOCK: Final = ROOT / "uv.lock"
_TABLES_KEY: Final = "tables"  # `source.json`'s list of the tables


_Locked: TypeAlias = dict[str, str]  # a package `uv.lock` pins: its name, its version, and more

_V = TypeVar("_V")
# One of the tables (or `source`, where they're from).
_Json: TypeAlias = (
    Table
    | dict[str, Table]
    | dict[str, dict[str, str | None]]
    | dict[str, list[Signatures]]
    | dict[str, list[str]]
)


def readings(root: Path) -> list[Tables]:
    """Read the stubs under `root` as each of `CONFIGS` sees them: in worker processes, if it can.

    In this process where there's one core, or no process can be started (a sandbox).

    Returns:
      Each configuration's tables, in `CONFIGS`' order.

    """
    workers: int = min(len(CONFIGS), os.cpu_count() or 1)
    pool: ProcessPoolExecutor
    if workers > 1:
        with contextlib.suppress(OSError, BrokenProcessPool), ProcessPoolExecutor(workers) as pool:
            return list(pool.map(read_config, CONFIGS, [root] * len(CONFIGS)))
    return [read_config(config, root) for config in CONFIGS]


def read_config(config: Config, root: Path) -> Tables:
    """Build every table as `config` sees the stubs under `root`, parsed once a process.

    Returns:
      Them.

    """
    return tables_for(_parsed(root), config)


@lru_cache(maxsize=1)
def _parsed(root: Path) -> Stubs:
    return Stubs(root)


def _common(each: list[Table]) -> Table:
    """Keep the entries every table that has them has the same.

    One only some platforms or Python versions have is kept: code calling it runs where it's there.

    Returns:
      Them.

    """
    found: dict[str, set[str]] = {}
    one: Table
    for one in each:
        key: str
        value: str
        for key, value in one.items():
            found.setdefault(key, set()).add(value)
    return {key: values.pop() for key, values in found.items() if len(values) == 1}


def _variants(each: list[dict[str, list[Signatures]]]) -> dict[str, list[Signatures]]:
    """Keep each function's signatures as each configuration that has it reads them, each once.

    `--fix` types a call only when every variant gives it the same type.

    Returns:
      Each function's variants.

    """
    found: dict[str, list[Signatures]] = {}
    one: dict[str, list[Signatures]]
    for one in each:
        path: str
        read: list[Signatures]
        for path, read in one.items():
            variants: list[Signatures] = found.setdefault(path, [])
            variants.extend(signatures for signatures in read if signatures not in variants)
    return found


def _common_by_class(each: list[dict[str, Table]]) -> dict[str, Table]:
    """Keep each class's members every configuration that has them has the same (see `_common`).

    Returns:
      Them, by class (a class with none left out).

    """
    found: dict[str, Table] = {}
    klass: str
    kept: Table
    for klass in dict.fromkeys(key for one in each for key in one):
        if kept := _common([one[klass] for one in each if klass in one]):
            found[klass] = kept
    return found


def _agreed(tables: list[Tables]) -> Tables:
    """Keep what every configuration's tables that have an entry agree on.

    Returns:
      The entries that are the same in each that has them, less those they hold in different tables
      (see `_split`).

    """
    split: frozenset[str] = _split(tables)
    tables = [_unsplit(one, split) for one in tables]
    return Tables(
        _common([one.returns for one in tables]),
        _variants([one.overloads for one in tables]),
        _common([one.classes for one in tables]),
        _common([one.aliases for one in tables]),
        _common_by_class([one.methods for one in tables]),
        _common_by_class([one.attributes for one in tables]),
        _common_by_class([one.method_overloads for one in tables]),
        _variants([one.method_signatures for one in tables]),
        _common([one.type_parameters for one in tables]),
        _common([one.bases for one in tables]),
        _common([one.subscriptable for one in tables]),
        _common_by_class([one.generic_attributes for one in tables]),
        _common([one.variables for one in tables]),
        _common([one.scalars for one in tables]),
        _common_lists([one.scalar_members for one in tables]),
        _common([one.functions for one in tables]),
        _common([one.awaited for one in tables]),
        _variants([one.awaited_overloads for one in tables]),
        _common([one.elements for one in tables]),
    )


def _split(each: list[Tables]) -> frozenset[str]:
    """Find the functions and members the configurations hold in different tables.

    `importlib.metadata.entry_points` is overloaded before Python 3.12 (`overloads`) and one `def`
    since (`classes`): each table alone would answer for the Pythons it wasn't read from too.

    Returns:
      Each one's path, a member's after its class's.

    """
    first: dict[str, frozenset[int]] = {}
    split: set[str] = set()
    one: Tables
    for one in each:
        members: list[dict[str, Table]] = [one.methods, one.attributes, one.method_overloads]
        members += [one.generic_attributes]
        held: list[Iterable[str]] = [one.returns, one.overloads, one.classes, one.functions, one.awaited]
        held += [one.awaited_overloads]
        held += ([f"{klass}.{name}" for klass, own in table.items() for name in own] for table in members)
        tables: dict[str, set[int]] = {}
        at: int
        paths: Iterable[str]
        for at, paths in enumerate(held):
            path: str
            for path in paths:
                tables.setdefault(path, set()).add(at)
        found: set[int]
        for path, found in tables.items():
            if first.setdefault(path, frozenset(found)) != frozenset(found):
                split.add(path)
    return frozenset(split)


def _unsplit(one: Tables, split: frozenset[str]) -> Tables:
    """Leave `split`'s functions and members out of a configuration's tables (see `_split`).

    Returns:
      The tables without them.

    """
    return one._replace(
        returns=_without(one.returns, split),
        overloads=_without(one.overloads, split),
        classes=_without(one.classes, split),
        functions=_without(one.functions, split),
        awaited=_without(one.awaited, split),
        awaited_overloads=_without(one.awaited_overloads, split),
        methods=_without_members(one.methods, split),
        attributes=_without_members(one.attributes, split),
        method_overloads=_without_members(one.method_overloads, split),
        generic_attributes=_without_members(one.generic_attributes, split),
    )


def _without(table: dict[str, _V], split: frozenset[str]) -> dict[str, _V]:
    """Leave `split`'s paths out of a table.

    Returns:
      The table without them.

    """
    return {path: value for path, value in table.items() if path not in split}


def _without_members(table: dict[str, Table], split: frozenset[str]) -> dict[str, Table]:
    """Leave `split`'s members out of each class's (a class with none left out).

    Returns:
      The table without them.

    """
    kept: dict[str, Table] = {
        klass: {name: value for name, value in own.items() if f"{klass}.{name}" not in split}
        for klass, own in table.items()
    }
    return {klass: own for klass, own in kept.items() if own}


def _common_lists(each: list[dict[str, list[str]]]) -> dict[str, list[str]]:
    """Keep each entry's names every configuration that has it has (see `_common`).

    Returns:
      Them.

    """
    found: dict[str, list[str]] = {}
    key: str
    for key in dict.fromkeys(key for one in each for key in one):
        lists: list[list[str]] = [one[key] for one in each if key in one]
        found[key] = [name for name in lists[0] if all(name in other for other in lists[1:])]
    return found


def pinned(package: str = STUBS) -> str:
    """Find the version of `package` the tables are read from or with: `uv.lock`'s, else the one they were.

    An sdist has no `uv.lock`, but carries the tables and their stamp.

    Returns:
      It; nothing for a package the lock doesn't have yet (`uv lock` builds the project to write it).

    """
    if not _LOCK.exists():
        return _written()[package]
    lock: dict[str, list[_Locked]] = cast(
        "dict[str, list[_Locked]]",
        tomllib.loads(_LOCK.read_text(encoding="utf-8")),
    )
    return next((locked["version"] for locked in lock["package"] if locked["name"] == package), "")


def digest() -> str:
    """Hash `INPUTS`, each by its path and its text (line endings as a checkout on Linux has them).

    Returns:
      The digest, in hex.

    """
    parts: list[bytes] = [
        part
        for path in INPUTS
        for part in (path.encode(), (ROOT / path).read_bytes().replace(b"\r\n", b"\n"))
    ]
    return hashlib.sha256(b"\0".join(parts)).hexdigest()


def stamp() -> dict[str, str]:
    """Say what the tables would be generated from now: the stubs' and their reader's versions, and `digest`.

    Returns:
      Each, by `source.json`'s key.

    """
    return {STUBS: pinned(), READER: pinned(READER), "digest": digest()}


def requirements() -> list[str]:
    """Name what generating the tables needs installed: the pinned stubs, and their pinned reader.

    Returns:
      Each requirement: by name alone where the lock has no version of it yet.

    """
    versions: dict[str, str] = {package: pinned(package) for package in (STUBS, READER)}
    return [f"{package}=={version}" if version else package for package, version in versions.items()]


def current() -> bool:
    """Check the tables and `PARTIAL` are all there, and generated from what `stamp` says.

    Returns:
      Whether they are.

    """
    if not (_SOURCE.exists() and PARTIAL.exists()):
        return False
    written: dict[str, str] = _written()
    tables: list[str] = cast("list[str]", json.loads(_SOURCE.read_bytes())[_TABLES_KEY])
    return all(written.get(key) == value for key, value in stamp().items()) and all(
        (OUTPUT / f"{name}.json").exists() for name in tables
    )


def _written() -> dict[str, str]:
    """Read `source.json`'s stamp.

    Returns:
      Its entries that are strings.

    """
    entries: dict[str, str | list[str]] = cast("dict[str, str | list[str]]", json.loads(_SOURCE.read_bytes()))
    return {key: value for key, value in entries.items() if isinstance(value, str)}


def typeshed() -> Path:
    """Find the typeshed stubs the installed basedpyright bundles: it and the reader at their pinned versions.

    Returns:
      Their directory.

    Raises:
      RuntimeError: if another version is installed.

    """
    package: str
    for package in (READER, STUBS):
        installed: str
        if (installed := importlib.metadata.version(package)) != pinned(package):
            message: str = f"{package} {installed} is installed, but the tables need {pinned(package)}"
            raise RuntimeError(message)
    stubs: importlib.metadata.Distribution = importlib.metadata.distribution(STUBS)
    return Path(str(stubs.locate_file(f"{STUBS}/dist/typeshed-fallback")))


def generate(stubs_root: Path | None = None) -> dict[Path, str]:
    """Generate the tables from the stubs under `stubs_root` (`typeshed()`), one file each (see `write`).

    And `PARTIAL`, for the tests alone.

    Returns:
      Each file's text, by path.

    """
    root: Path = typeshed() if stubs_root is None else stubs_root
    each: list[Tables] = readings(root)
    tables: Tables = _agreed(each)
    document: dict[str, _Json] = {
        "returns": tables.returns,
        "overloads": tables.overloads,
        "classes": tables.classes,
        "aliases": tables.aliases,
        "methods": inherited(tables.methods, tables.bases),
        "attributes": inherited(tables.attributes, tables.bases),
        "bases": tables.bases,
        "method_overloads": inherited(tables.method_overloads, tables.bases),
        "method_signatures": tables.method_signatures,
        "type_parameters": tables.type_parameters,
        # Where Pythons differ (`array.array`, 3.12+), the entry is left out: not subscriptable.
        "subscriptable": {path: value for path, value in tables.subscriptable.items() if value == YES},
        "generic_attributes": tables.generic_attributes,
        "variables": tables.variables,
        "scalars": tables.scalars,
        "scalar_members": tables.scalar_members,
        "functions": tables.functions,
        "awaited": tables.awaited,
        "awaited_overloads": tables.awaited_overloads,
        "elements": tables.elements,
        "platform": platform_only(_parsed(root)),
    }
    source: dict[str, str | list[str]] = {
        **stamp(),
        _TABLES_KEY: sorted(document),
        "typeshed": (root / "commit.txt").read_text(encoding="utf-8").strip(),
    }
    files: dict[Path, str] = {OUTPUT / f"{name}.json": write(table) for name, table in document.items()}
    files[_SOURCE] = json.dumps(source, indent=0, sort_keys=True) + "\n"
    files[PARTIAL] = write(_partial(each))
    return files


def write(table: _Json) -> str:
    """Write a table as JSON, one entry a line, sorted: a change to one entry is a change to its line.

    Returns:
      The text.

    """
    entries: list[str] = [
        f"{json.dumps(key)}: {json.dumps(value, separators=(',', ':'), sort_keys=True)}"
        for key, value in sorted(table.items())
    ]
    return "{\n" + ",\n".join(entries) + "\n}\n"


def _partial(each: list[Tables]) -> dict[str, list[str]]:
    """Find the functions and classes only some configurations have, for the tests to look for there alone.

    Returns:
      Each one's configurations (`linux-3.12`), by path.

    """
    found: dict[str, list[str]] = {}
    config: Config
    tables: Tables
    for config, tables in zip(CONFIGS, each, strict=True):
        path: str
        for path in {*tables.returns, *tables.overloads, *tables.classes, *tables.functions}:
            found.setdefault(path, []).append(f"{config[0]}-3.{config[1]}")
    return {path: configs for path, configs in sorted(found.items()) if len(configs) < len(CONFIGS)}


def ensure() -> bool:
    """Generate the tables if they're missing or stale (see `current`).

    Returns:
      Whether it did.

    """
    if current():
        return False
    _write(generate())
    return True


def _write(files: dict[Path, str]) -> None:
    """Write the tables, and remove any other there."""
    OUTPUT.mkdir(exist_ok=True)
    stale: Path
    for stale in OUTPUT.glob("*.json"):
        if stale not in files:
            stale.unlink()
    path: Path
    text: str
    for path, text in files.items():
        _ = path.write_text(text, encoding="utf-8", newline="\n")


def main(argv: Sequence[str]) -> int:
    """Write the tables; with `--if-stale`, only if they're missing or stale.

    Returns:
      The exit status.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="python -m stdlib_tables")
    _ = parser.add_argument("--if-stale", action="store_true", help="only if they're missing or stale")
    options: argparse.Namespace = parser.parse_args(argv)
    if not cast("bool", options.if_stale):
        _write(generate())
    else:
        _ = ensure()
    return 0
