# SPDX-License-Identifier: MIT
"""`--fix` for calls into installed packages that declare their types: stubs, `py.typed`, a lone stub."""

import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.fix import installed, project

# Each installed file, under the site directory: a typed package (its source and a stub), a stub
# package for an untyped one, a lone stub module, an untyped package, and a broken stub.
SITE: Final = {
    "typed/py.typed": "",
    "typed/__init__.py": "from typed._impl import make, thing\nfrom typed._types import Thing\n",
    "typed/_impl.pyi": "from typed._types import Thing\ndef make() -> int: ...\ndef thing() -> Thing: ...\n",
    "typed/_types.pyi": "class Thing: ...\n",
    "typed/sub.py": "def sub() -> float:\n    return 1.0\n",
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


def run():
    a = make()
    b2 = g()
    c = lone.k()
    d = h()
    e = typed.sub.sub()
    f = thing()
    return a, b2, c, d, e, f
"""
FIXED: Final = (
    "    a: int = make()\n",
    "    b2: str = g()\n",
    "    c: bytes = lone.k()\n",
    "    d = h()\n",  # untyped: no `py.typed`
    "    e: float = typed.sub.sub()\n",
    "    f: Thing = thing()\n",
    "    from typed import Thing\n",  # the public re-export, not `typed._types`
)


def _site(root: Path, files: dict[str, str]) -> Path:
    site: Path = root / "site"
    name: str
    text: str
    for name, text in files.items():
        path: Path = site / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(textwrap.dedent(text), encoding="utf-8")
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
    _ = main.write_text(textwrap.dedent(MAIN), encoding="utf-8")
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
        [project.Module("main", {}, {"typed": ("typed", None), "lone": ("lone", None)})],
    )
    monkeypatch.setattr(installed, "LIMIT", 1)
    assert sorted(installed.with_installed(catalog, (site,)).modules) == ["main", "typed"]
    assert installed.with_installed(catalog, ()) is catalog
