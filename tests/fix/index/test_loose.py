# SPDX-License-Identifier: MIT
"""`--fix` for a call of another checked file's unannotated method: its `return`s' type, a guess."""

import textwrap
from pathlib import Path
from typing import Final

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.cli import schedule
from constricter.fix.core.known import Returns
from constricter.fix.index import loose, order, project
from constricter.rules.checker import Checked, checked_source

_BASE: Final = """
class Case:
    def mktemp(self):
        return "tmp"

    def count(self):
        return 3

    def made(self):
        return Tool()

    def declared(self) -> bytes:
        return b""


class Tool:
    def name(self):
        return self.label()

    def label(self):
        return "tool"

    def me(self):
        return self


class Hammer(Tool):
    def label(self):
        return b"hammer"
"""
_USE: Final = """
import pkg.base as b
from pkg.base import Case, Tool


class Sub(Case):
    def test(self) -> None:
        path = self.mktemp()
        made = self.made()
        declared = self.declared()


def use(tool: Tool, other: b.Tool, case: Case) -> None:
    name = tool.name()
    again = other.name()
    missing = case.missing()
"""
_UNFIXED: Final = "        path = self.mktemp()\n"
_GUESSED: Final = "        path: str = self.mktemp()\n"
_CASE: Final = {"mktemp": "str", "made": "Tool"}  # what the file calls of `Case`
_METHODS: Final = {"Case": _CASE, "b.Case": _CASE, "Tool": {"name": "str"}, "b.Tool": {"name": "str"}}


def _package(root: Path) -> tuple[project.Index, Path, Path]:
    """Write a package with a module of classes and one using them.

    Returns:
      Their index, and the two files.

    """
    (root / "pkg").mkdir()
    name: str
    source: str
    for name, source in (("__init__", ""), ("base", _BASE), ("use", _USE)):
        _ = (root / "pkg" / f"{name}.py").write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return project.index(sorted(root.rglob("*.py"))), root / "pkg" / "base.py", root / "pkg" / "use.py"


def test_a_file_is_checked_after_the_classes_whose_methods_it_calls(tmp_path: Path) -> None:
    """A module with a method only `return`s could type, of a class the file names, comes first."""
    catalog: project.Index
    base: Path
    use: Path
    catalog, base, use = _package(tmp_path)
    assert catalog.modules["pkg.base"].loose == {"mktemp", "count", "made", "name", "label", "me"}
    assert loose.needs(catalog, catalog.modules["pkg.use"]) == {"pkg.base"}
    assert not loose.needs(catalog, catalog.modules["pkg.base"])
    planned: order.Plan = order.plan(catalog, [use, base])
    assert [planned.names[at] for group in planned.components for at in group] == ["pkg.base", "pkg.use"]


def test_another_files_methods_returns_type_their_calls(tmp_path: Path) -> None:
    """Those the file calls, by each class as it spells it; a guess, with what a guessed one rests on."""
    catalog: project.Index
    base: Path
    use: Path
    catalog, base, use = _package(tmp_path)
    assert loose.returned(catalog, use, {}) == Returns()  # nothing checked yet
    checked: Checked = checked_source(base.read_text(encoding="utf-8"))
    assert checked.returned.methods == {
        "Case": {"mktemp": "str", "count": "int", "made": "Tool"},
        "Tool": {"name": "str", "label": "str", "me": "Tool"},
        "Hammer": {"label": "bytes", "name": "str"},  # not `me`: a `Hammer`, by `return self`
    }
    assert checked.returned.guesses == {
        "Case.made": {"constructor"},
        "Tool.name": {"returned"},
        "Hammer.name": {"returned"},
    }
    catalog = project.with_returned(catalog, {"pkg.base": checked.returned})
    found: Returns = loose.returned(catalog, use, {})
    assert found.methods == {**_METHODS, "b.Hammer": {"name": "str"}}
    assert found.guesses == {
        "Case.made": {"constructor"},
        "b.Case.made": {"constructor"},
        "b.Hammer.name": {"returned"},
        "Tool.name": {"returned"},
        "b.Tool.name": {"returned"},
    }
    assert loose.returned(catalog, tmp_path / "missing.py") == Returns()
    offences: list[Offence] = check_source(
        use.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, use, {}),
    )
    assert {o.name: (o.fix, o.unsafe) for o in offences} == {
        "path": ("str", True),
        "made": ("Tool", True),
        "declared": ("bytes", False),
        "name": ("str", True),
        "again": ("str", True),
        "missing": (None, False),
    }


def test_the_cli_types_a_method_of_another_files_base(tmp_path: Path) -> None:
    """Only with `--unsafe-fixes`: a subclass may override it."""
    use: Path = _package(tmp_path)[2]
    _ = cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)])
    assert _UNFIXED in use.read_text(encoding="utf-8")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    assert _GUESSED in use.read_text(encoding="utf-8")


_LIBRARY: Final = """
class BaseConfigurator:
    def __init__(self, config):
        self.config = config

    def depth(self):
        return len(self.config)
"""
_LIBRARY_USE: Final = """
import logging.config


def f() -> None:
    made = logging.config.BaseConfigurator({})
    size = made.depth()
"""
_LIBRARY_FIXED: Final = (
    "    made: BaseConfigurator = logging.config.BaseConfigurator({})\n    size: int = made.depth()\n"
)


def test_a_checked_library_class_named_by_an_added_import_has_its_methods(tmp_path: Path) -> None:
    """The standard library, checked: its class, named by an import a fix adds, is the one the file spells."""
    (tmp_path / "logging").mkdir()
    use: Path = tmp_path / "use.py"
    path: Path
    source: str
    for path, source in (
        (tmp_path / "logging" / "__init__.py", ""),
        (tmp_path / "logging" / "config.py", _LIBRARY),
        (use, _LIBRARY_USE),
    ):
        _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    assert _LIBRARY_FIXED in use.read_text(encoding="utf-8")
