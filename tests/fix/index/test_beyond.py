# SPDX-License-Identifier: MIT
"""A library base out of sight: what a class under another checked file's class takes from the library."""

import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.fix.index import beyond, project

_TESTING: Final = """
import unittest
from unknown import Elsewhere


class SimpleCase(unittest.TestCase):
    def shortDescription(self):
        return 1

    def client(self) -> int:
        return 1


class Case(SimpleCase):
    databases = {"default"}


class Mixed(SimpleCase, dict):
    pass


class Lost(Elsewhere):
    pass
"""
_TESTS: Final = """
from pkg.testing import Case, Lost, Mixed
from pkg.deep import C9


class Tests(Case):
    def test(self):
        name = self.id()
        short = self.shortDescription()
        made = self.client()
        with self.assertRaises(ValueError) as raised:
            pass
        error = raised.exception


class Other(Mixed):
    def test(self):
        mixed = self.id()


class Gone(Lost):
    def test(self):
        lost = self.id()


class Deep(C9):
    def test(self):
        deep = self.id()


def f(case: Case):
    count = case.countTestCases()
"""
_DIRECT: Final = """
import unittest


class Direct(unittest.TestCase):
    def test(self):
        direct = self.id()
"""
_SHADOWED: Final = """
from pkg.testing import Case


class Tests(Case):
    def test(self, unittest):
        name = self.id()
"""
_FIXED: Final = {
    "name": "str",
    "made": "int",
    "error": "ValueError",
    "count": "int",
}
_UNTYPED: Final = ("short", "mixed", "lost", "deep")
_CALL: Final = " = self."  # a binding to a method call on `self`
_INSTALLED: Final = """
import unittest


class Base(unittest.TestCase, object):
    def helper(self) -> int: ...
    def shortDescription(self): ...


class Case(Base): ...


class Twice(Base): ...


class Twice(Base): ...
"""
_USING: Final = """
from typed.testing import Case, Twice


class Tests(Case):
    def test(self):
        name = self.id()
        short = self.shortDescription()
        count = self.helper()


class Other(Twice):
    def test(self):
        twice = self.id()
"""
_RAISED: Final = "        raised: _AssertRaisesContext[ValueError]\n"
_UNFIXED: Final = "        name = self.id()\n"
_BASES: Final = frozenset({"shortDescription", "client", "SimpleCase", "databases", "Case"})


def _package(root: Path) -> Path:
    """Write a package whose test cases inherit from `unittest.TestCase`, and the tests under them.

    Returns:
      The tests' file.

    """
    deep: str = "import unittest\n\n\nclass C0(unittest.TestCase):\n    pass\n" + "".join(
        f"\n\nclass C{at}(C{at - 1}):\n    pass\n" for at in range(1, 10)
    )
    name: str
    source: str
    for name, source in (("__init__", ""), ("testing", _TESTING), ("deep", deep)):
        (root / "pkg").mkdir(exist_ok=True)
        _ = (root / "pkg" / f"{name}.py").write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    _ = (root / "test_direct.py").write_text(textwrap.dedent(_DIRECT), encoding="utf-8", newline="\n")
    tests: Path = root / "test_it.py"
    _ = tests.write_text(textwrap.dedent(_TESTS), encoding="utf-8", newline="\n")
    return tests


def test_a_class_takes_a_library_bases_members_through_another_files(tmp_path: Path) -> None:
    """What no class on the way binds: not behind a class of two bases, one out of sight, or eight deep."""
    tests: Path = _package(tmp_path)
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    fixed: str = tests.read_text(encoding="utf-8")
    name: str
    typed: str
    for name, typed in _FIXED.items():
        assert f" {name}: {typed} = " in fixed
    assert _RAISED in fixed
    for name in _UNTYPED:
        assert f" {name} = " in fixed


def test_each_base_another_file_defines_has_its_lines_end(tmp_path: Path) -> None:
    """The standard-library class, and the names bound on the way; nothing for a file not indexed."""
    tests: Path = _package(tmp_path)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert beyond.library_bases(catalog, tests) == {"Case": ("unittest.TestCase", _BASES)}
    assert not beyond.library_bases(catalog, tmp_path / "test_direct.py")  # in the file's own sight
    assert not beyond.library_bases(catalog, tmp_path / "notebook.ipynb")
    assert not beyond.library_bases(catalog, tmp_path / "missing.py")


def test_a_name_the_module_binds_isnt_the_library_class(tmp_path: Path) -> None:
    """A module with its own `unittest` can't mean the library's by it."""
    tests: Path = _package(tmp_path)
    _ = tests.write_text(textwrap.dedent(_SHADOWED), encoding="utf-8", newline="\n")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    assert _UNFIXED in tests.read_text(encoding="utf-8")


def test_an_installed_packages_class_is_followed_too(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """One that declares its types: through its own bases, to the library's; not a class it defines twice."""
    site: Path = tmp_path / "site" / "typed"
    site.mkdir(parents=True)
    name: str
    text: str
    for name, text in (("py.typed", ""), ("__init__.py", ""), ("testing.py", _INSTALLED)):
        _ = (site / name).write_text(textwrap.dedent(text), encoding="utf-8", newline="\n")
    monkeypatch.setattr(sys, "path", [str(site.parent), *sys.path])
    tests: Path = tmp_path / "project" / "test_it.py"
    tests.parent.mkdir()
    _ = tests.write_text(textwrap.dedent(_USING), encoding="utf-8", newline="\n")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tests)])
    fixed: list[str] = tests.read_text(encoding="utf-8").splitlines()
    assert [line.strip() for line in fixed if _CALL in line] == [
        "name: str = self.id()",
        "short = self.shortDescription()",
        "count: int = self.helper()",
        "twice = self.id()",
    ]
