# SPDX-License-Identifier: MIT
"""`--fix` for calls into installed packages that declare their types: stubs, `py.typed`, a lone stub."""

import os
import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.fix.index import installed, project

# Each installed file, under the site directory: a typed package (its source and a stub), a stub
# package for an untyped one, a lone stub module, an untyped package, and a broken stub.
SITE: Final = {
    "typed/py.typed": "",
    "typed/__init__.py": "from typed._impl import make, thing\nfrom typed._types import Thing as Thing\n",
    "typed/_impl.pyi": "from typed._types import Thing\ndef make() -> int: ...\ndef thing() -> Thing: ...\n",
    "typed/_types.pyi": "class Thing: ...\n",
    "typed/sub.py": "def sub() -> float:\n    return 1.0\n",
    "twin/py.typed": "",
    "twin/__init__.py": "from _twin.impl import Kept as Kept, keep as keep\n",
    "_twin/py.typed": "",
    "_twin/__init__.py": "",
    "_twin/impl.py": "class Kept:\n    pass\n\n\ndef keep() -> Kept:\n    return Kept()\n",
    "stubbed/__init__.py": "def g():\n    return 'x'\n",
    "stubbed-stubs/__init__.pyi": "def g() -> str: ...\n",
    "lone.pyi": "def k() -> bytes: ...\n",
    "plain/__init__.py": "def h() -> int:\n    return 1\n",
    "broken/py.typed": "",
    "broken/__init__.pyi": "def (:\n",
}
MAIN: Final = """
import lone
import typed.sub
from typed import make, thing
from stubbed import g
from plain import h
from broken import b
from . import sibling
import os
from twin import keep


def run():
    k = keep()
    a = make()
    b2 = g()
    c = lone.k()
    d = h()
    e = typed.sub.sub()
    f = thing()
    return a, b2, c, d, e, f
"""
FIXED: Final = (
    "    k: Kept = keep()\n",  # a package's private twin's, read through it
    "    from twin import Kept\n",  # named by the public package
    "    a: int = make()\n",
    "    b2: str = g()\n",
    "    c: bytes = lone.k()\n",
    "    d = h()\n",  # untyped: no `py.typed`
    "    e: float = typed.sub.sub()\n",
    "    f: typed.Thing = thing()\n",  # through the public module it imports, not `typed._types`
)


def _site(root: Path, files: dict[str, str]) -> Path:
    site: Path = root / "site"
    name: str
    text: str
    for name, text in files.items():
        path: Path = site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(textwrap.dedent(text), encoding="utf-8", newline="\n")
    return site


def test_calls_into_typed_installed_packages_are_typed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """As a checked file's are, by their declared returns; an untyped package's aren't."""
    site: Path = _site(tmp_path, SITE)
    monkeypatch.setattr(sys, "path", [str(site), *sys.path])
    main: Path = tmp_path / "project" / "main.py"
    main.parent.mkdir()
    _ = main.write_text(textwrap.dedent(MAIN), encoding="utf-8", newline="\n")
    assert cli.main(["--fix", "-q", str(main)]) == cli.EXIT_FOUND
    fixed: str = main.read_text(encoding="utf-8")
    assert all(line in fixed for line in FIXED), fixed


def test_the_virtual_environment_is_searched(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`VIRTUAL_ENV`'s site-packages (POSIX or Windows), after the interpreter's own directories."""
    posix: Path = tmp_path / "venv" / "lib" / "python3.99" / "site-packages"
    windows: Path = tmp_path / "venv" / "Lib" / "site-packages"
    posix.mkdir(parents=True)
    windows.mkdir(parents=True)
    monkeypatch.setenv("VIRTUAL_ENV", str(tmp_path / "venv"))
    found: tuple[Path, ...] = installed.search_path()
    assert found[-2:] == (posix.resolve(), windows.resolve())
    monkeypatch.delenv("VIRTUAL_ENV")
    assert posix.resolve() not in installed.search_path()


def test_an_untyped_package_shadows_a_later_one(tmp_path: Path) -> None:
    """The import system takes the first directory that has it: a typed copy after it isn't read."""
    first: Path = _site(tmp_path / "a", {"pkg/__init__.py": "", "mod.py": ""})
    second: Path = _site(tmp_path / "b", {"pkg/py.typed": "", "pkg/__init__.py": "", "mod.pyi": ""})
    assert installed.locate("pkg", (first, second)) is None
    assert installed.locate("mod", (first, second)) is None
    assert installed.locate("pkg.missing", (second,)) is None
    assert installed.locate("nowhere", (first,)) is None


def test_at_most_the_limit_is_read(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Past `LIMIT` modules, the rest are left out; with none found, the index is as it was."""
    site: Path = _site(tmp_path, SITE)
    catalog: project.Index = project.indexed(
        [project.Module(name="main", returns={}, names={"typed": ("typed", None), "lone": ("lone", None)})],
    )
    monkeypatch.setattr(installed, "LIMIT", 1)
    assert sorted(installed.with_installed(catalog, (site,)).modules) == ["main", "typed"]
    assert installed.with_installed(catalog, ()) is catalog


def test_a_read_is_cached_until_its_file_changes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The second read comes from the cache; a changed file, or an unreadable entry, is read again."""
    site: Path = _site(tmp_path, {"lone.pyi": "def k() -> bytes: ...\n"})
    stub: Path = site / "lone.pyi"
    reads: list[Path] = []

    def counted(path: Path, name: str | None = None) -> project.Module | None:
        reads.append(path)
        return project.read(path, name)

    monkeypatch.setattr("constricter.fix.index.installed.read", counted)
    first: project.Module | None = installed.cached(stub, "lone")
    assert installed.cached(stub, "lone") == first
    assert len(reads) == 1
    _ = stub.write_text("def k() -> str: ...\n", encoding="utf-8", newline="\n")
    assert installed.cached(stub, "lone") != first
    entry: Path = next(installed.cache_directory().glob("*/*.pickle"))
    _ = entry.write_bytes(b"not a pickle")
    assert installed.cached(site / "missing.pyi", "missing") is None
    monkeypatch.setenv("XDG_CACHE_HOME", str(stub))  # a file: nothing can be made under it
    assert installed.cached(stub, "lone") is not None


def test_a_read_is_cached_until_constricter_changes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A changed `constricter.fix`, at the same version, reads the module again."""
    site: Path = _site(tmp_path, {"lone.pyi": "def k() -> bytes: ...\n"})
    reads: list[Path] = []

    def counted(path: Path, name: str | None = None) -> project.Module | None:
        reads.append(path)
        return project.read(path, name)

    monkeypatch.setattr("constricter.fix.index.installed.read", counted)
    _ = installed.cached(site / "lone.pyi", "lone")
    monkeypatch.setattr("constricter.fix.index.installed._code", lambda: "changed")
    _ = installed.cached(site / "lone.pyi", "lone")
    assert reads == [site / "lone.pyi"] * 2


def test_the_cache_is_swept_as_its_written_to(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A day apart: no build's entries and builds long unswept go, its own long unread or over the cap."""
    site: Path = _site(tmp_path, {"lone.pyi": "def k() -> bytes: ...\n", "more.pyi": "def m() -> int: ...\n"})
    root: Path = installed.cache_directory()
    long_ago: tuple[float, float] = (0.0, 0.0)
    gone: Path = root / ("0" * 16)
    kept: tuple[Path, ...] = (root / ("1" * 16), root / ("2" * 16), root / "hung", root / ("3" * 16))
    part: Path
    for part in (gone, *kept):
        part.mkdir(parents=True)
        _ = (part / "old.pickle").write_bytes(b"")
    for part in (gone, kept[0], kept[1]):
        (part / ".swept").touch()
    _ = (gone / "left.tmp").write_bytes(b"")
    os.utime(gone / ".swept", long_ago)
    os.utime(kept[1] / ".swept", long_ago)
    _ = (kept[1] / "another").write_bytes(b"")  # not the cache's: its directory can't be removed
    _ = (root / "flat.pickle").write_bytes(b"")
    assert installed.cached(site / "lone.pyi", "lone") is not None
    assert not gone.exists()
    own: Path = next(each for each in root.iterdir() if each.is_dir() and each not in kept)
    assert not (root / "flat.pickle").exists()
    assert [each.exists() for each in kept] == [True] * len(kept)
    assert not (kept[1] / "old.pickle").exists()
    # Within a day of its last sweep, nothing is looked at; after it, what's unread for a month goes.
    entry: Path = next(own.glob("*.pickle"))
    os.utime(entry, long_ago)
    installed.swept.cache_clear()
    assert installed.cached(site / "more.pyi", "more") is not None
    assert entry.exists()
    assert installed.cached(site / "lone.pyi", "lone") is not None  # read: marked read now
    assert entry.stat().st_mtime > 0
    os.utime(entry, long_ago)
    os.utime(own / ".swept", long_ago)
    installed.swept.cache_clear()
    _ = (site / "more.pyi").write_text("def m() -> str: ...\n", encoding="utf-8", newline="\n")
    assert installed.cached(site / "more.pyi", "more") is not None
    assert not entry.exists()
    # And of the rest, the longest unread until what's left fits the cap.
    assert len(list(own.glob("*.pickle"))) > 1
    monkeypatch.setattr(installed, "_CAP", 0)
    os.utime(own / ".swept", long_ago)
    installed.swept.cache_clear()
    _ = (site / "more.pyi").write_text("def m() -> bytes: ...\n", encoding="utf-8", newline="\n")
    assert installed.cached(site / "more.pyi", "more") is not None
    assert not list(own.glob("*.pickle"))


def test_the_cache_is_the_platforms(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """`$XDG_CACHE_HOME`, else Windows' `%LOCALAPPDATA%`, else `~/.cache`."""
    monkeypatch.delenv("XDG_CACHE_HOME")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert installed.cache_directory() == tmp_path / "constricter" / "installed"
    monkeypatch.delenv("LOCALAPPDATA")
    assert installed.cache_directory() == Path.home() / ".cache" / "constricter" / "installed"


# A package that imports its names only when asked for one, and for type checking: pydantic's layout.
_LAZY: Final = {
    "lazy/py.typed": "",
    "lazy/__init__.py": """
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from lazy.boxes import Box, Plain


        def __getattr__(name: str) -> object:
            raise AttributeError(name)
    """,
    "lazy/boxes.py": """
        from typing import Generic, TypeVar

        T = TypeVar("T")


        class Box(Generic[T]):
            def __init__(self, held: T) -> None:
                self.held = held


        class Plain:
            pass
    """,
}
_BOXED: Final = """
import lazy
from lazy import Box, Plain


def run() -> None:
    a = Box(1)
    b = lazy.Box(1)
    c = Plain()
"""
_BOXED_FIXED: Final = """
import lazy
from lazy import Box, Plain


def run() -> None:
    a = Box(1)
    b = lazy.Box(1)
    c: Plain = Plain()
"""


def test_a_generic_class_reexported_for_type_checking_isnt_written_bare(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A call taken to construct one has no fix, by either name: its class's arguments aren't known."""
    monkeypatch.setattr(sys, "path", [str(_site(tmp_path, _LAZY)), *sys.path])
    main: Path = tmp_path / "project" / "main.py"
    main.parent.mkdir()
    _ = main.write_text(textwrap.dedent(_BOXED), encoding="utf-8", newline="\n")
    assert cli.main(["--fix", "--unsafe-fixes", "-q", str(main)]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") == textwrap.dedent(_BOXED_FIXED)
