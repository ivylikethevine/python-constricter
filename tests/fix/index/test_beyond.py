# SPDX-License-Identifier: MIT
"""A library base out of sight: what a class under another checked file's class takes from the library."""

import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.fix.index import beyond, installed, project

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
    "short": "int",  # by its `return`s, in the file defining it
}
_UNTYPED: Final = ("mixed", "lost", "deep")
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


_LOUD: Final = "loud: int = self.id()"
_TANGLED: Final = "tangled = self.id()"
_MIXINS: Final = """
import threading
import unittest


class Base:
    def name(self) -> str:
        return ""


class Named(Base):
    def id(self) -> int:
        return 1


class Plain(Base):
    def __init__(self) -> None:
        self.level: int = 1


class Mixed(Base, unittest.TestCase):
    pass


class Both(unittest.TestCase, dict):
    pass


class Threaded(threading.Thread, unittest.TestCase):
    pass


class Shared(unittest.TestCase, unittest.IsolatedAsyncioTestCase):
    pass
"""
_MIXED: Final = """
import unittest

from pkg.mixins import Both, Mixed, Named, Plain, Shared, Threaded


class Quiet(Plain, unittest.TestCase):
    def test(self) -> None:
        quiet = self.id()
        name = self.name()
        level = self.level


class Loud(Named, unittest.TestCase):
    def test(self) -> None:
        loud = self.id()


class Under(Mixed):
    def test(self) -> None:
        under = self.id()
        helped = self.name()


class Twice(Both):
    def test(self) -> None:
        twice = self.id()


class Runner(Threaded):
    def test(self) -> None:
        ident = self.id()
        alive = self.is_alive()
        neither = self.missing()


class Tangled(Shared):
    def test(self) -> None:
        tangled = self.id()
"""


def test_another_files_mixin_doesnt_end_a_class_order(tmp_path: Path) -> None:
    """What its line of bases doesn't bind is the next base's: the library class's, behind it."""
    (tmp_path / "pkg").mkdir()
    _ = (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    _ = (tmp_path / "pkg" / "mixins.py").write_text(textwrap.dedent(_MIXINS), encoding="utf-8", newline="\n")
    tests: Path = tmp_path / "test_mixed.py"
    _ = tests.write_text(textwrap.dedent(_MIXED), encoding="utf-8", newline="\n")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert beyond.library_bases(catalog, tests) == {
        "Named": ("", frozenset({"Named", "id", "Base", "name"})),
        "Plain": ("", frozenset({"Plain", "__init__", "Base", "name"})),
        # Behind a class of two bases: the one line that reaches a library class, with the other's names.
        "Mixed": ("unittest.TestCase", frozenset({"Mixed", "Base", "name"})),
        # Behind two library classes: both, the first's members before the second's.
        "Threaded": ("threading.Thread,unittest.TestCase", frozenset({"Threaded"})),
    }
    _ = cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)])
    fixed: str = tests.read_text(encoding="utf-8")
    line: str
    # `loud`: the mixin's own `id`.
    for line in ("quiet: str = self.id()", "name: str = self.name()", "level: int = self.level", _LOUD):
        assert f"        {line}\n" in fixed
    for line in ("under: str = self.id()", "helped: str = self.name()", "twice = self.id()"):
        assert f"        {line}\n" in fixed  # not behind a class out of sight
    # `tangled`: behind two lines sharing an ancestor, which have no order.
    for line in (
        "ident: str = self.id()",
        "alive: bool = self.is_alive()",
        "neither = self.missing()",
        _TANGLED,
    ):
        assert f"        {line}\n" in fixed


_UNTYPED_PACKAGE: Final = {
    "__init__.py": "from web.testing import Case as Case\n",
    "testing.py": """
        import unittest


        class Simple(unittest.TestCase):
            def helper(self) -> int:
                return 1

            def shortDescription(self):
                return 1


        class Case(Simple):
            pass
    """,
}
_UNDER_UNTYPED: Final = """
import web.testing
from web import Case


class Tests(Case):
    def test(self):
        name = self.id()
        short = self.shortDescription()
        helped = self.helper()


class Missing(web.testing.Gone):
    def test(self):
        gone = self.id()
"""


def test_a_package_declaring_no_types_is_followed_for_its_bases(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """To the library class its classes end at; nothing they declare types a call, as no checker reads it."""
    site: Path = tmp_path / "site" / "web"
    site.mkdir(parents=True)
    name: str
    text: str
    for name, text in _UNTYPED_PACKAGE.items():
        _ = (site / name).write_text(textwrap.dedent(text), encoding="utf-8", newline="\n")
    monkeypatch.setattr(sys, "path", [str(site.parent), *sys.path])
    tests: Path = tmp_path / "project" / "test_it.py"
    tests.parent.mkdir()
    _ = tests.write_text(textwrap.dedent(_UNDER_UNTYPED), encoding="utf-8", newline="\n")
    catalog: project.Index = project.index([tests])
    assert beyond.library_bases(catalog, tests) == {
        "Case": ("unittest.TestCase", frozenset({"Case", "Simple", "helper", "shortDescription"})),
    }
    assert installed.unseen("unittest.case") is None
    assert installed.unseen("web.missing") is None
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tests)])
    fixed: list[str] = tests.read_text(encoding="utf-8").splitlines()
    assert [line.strip() for line in fixed if _CALL in line] == [
        "name: str = self.id()",
        "short = self.shortDescription()",
        "helped = self.helper()",
        "gone = self.id()",
    ]
