# SPDX-License-Identifier: MIT
"""`--fix` for what's read off calls and written names: a method's return's attribute, a module's members."""

import ast
import textwrap
from pathlib import Path
from typing import Final

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.cli import schedule
from constricter.fix.index import chained, modules, project
from constricter.fix.index.declared import Class, declarations

_STUB: Final = """
from typing import TYPE_CHECKING, AnyStr, Generic, NamedTuple, overload


if TYPE_CHECKING:

    class Result(NamedTuple, Generic[AnyStr]):
        out: AnyStr
        code: int

else:

    class Result: ...


class Fixture(Generic[AnyStr]):
    def read(self) -> Result[AnyStr]: ...

    @overload
    def both(self, flag: bool) -> Result[AnyStr]: ...
    @overload
    def both(self) -> Result[AnyStr]: ...

    def other(self) -> Missing[AnyStr]: ...

    def bare(self) -> Result: ...
"""
_BOTH: Final = "    both = capsys.readouterr()\n"
_TEST: Final = f"import pytest\n\n\ndef test_out(capsys):\n    out = capsys.readouterr().out\n{_BOTH}"
_OUT: Final = "    out: str = capsys.readouterr().out\n"
_UTIL: Final = """
class Row:
    name: str


def load() -> int:
    return 1
"""
_MAIN: Final = """
import pkg.util as u
import pkg


def f(row: "u.Row") -> None:
    name = row.name
    count = u.load()
    other = pkg.util.load()
"""


def test_a_methods_returns_attribute_is_a_signature_of_the_methods() -> None:
    """A class under `if TYPE_CHECKING:` is read; one signature, a class of its module, as many arguments."""
    tree: ast.Module = ast.parse(textwrap.dedent(_STUB))
    module: modules.Module = modules.Module(name="stub", returns={}, names={}, declared=declarations(tree))
    assert module.declared is not None
    klass: Class = module.declared.classes["Fixture"]
    assert module.declared.classes["Result"].attributes == {"out": "AnyStr", "code": "int"}
    found: dict[str, str | None] = {
        name: each[0].returns
        for name, each in chained.attributes(module, klass, "read", frozenset({"out", "code", "err"})).items()
    }
    assert found == {"out": "AnyStr", "code": "int"}
    method: str
    for method in ("both", "other", "bare", "missing"):
        assert not chained.attributes(module, klass, method, frozenset({"out"}))
    assert [chained.key("read", "out")] == ["read().out"]


def test_capsys_readouterr_out_is_a_str(tmp_path: Path) -> None:
    """Off the call: pytest's `CaptureResult` is private, so the call itself has no type to write."""
    test: Path = tmp_path / "test_out.py"
    _ = test.write_text(_TEST, encoding="utf-8", newline="\n")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    fixed: str = test.read_text(encoding="utf-8")
    assert _OUT in fixed
    assert _BOTH in fixed


def test_a_modules_members_are_found_by_the_names_the_file_writes(tmp_path: Path) -> None:
    """Each dotted name, its beginnings and a string's too; of all a module has, only those are spelled."""
    (tmp_path / "pkg").mkdir()
    name: str
    source: str
    for name, source in (("__init__", ""), ("util", _UTIL)):
        _ = (tmp_path / "pkg" / f"{name}.py").write_text(textwrap.dedent(source), encoding="utf-8")
    main: Path = tmp_path / "main.py"
    _ = main.write_text(textwrap.dedent(_MAIN), encoding="utf-8", newline="\n")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    target: modules.Module = catalog.modules["main"]
    assert target.written == {
        "u": ("u.Row", "u.load"),
        "pkg": ("pkg.util", "pkg.util.load"),
        "row": ("row.name",),
    }
    assert list(modules.written_under(target, "u")) == [("u.Row", "", "Row"), ("u.load", "", "load")]
    assert list(modules.written_under(target, "pkg.util")) == [("pkg.util.load", "", "load")]
    assert list(modules.written_under(target, "pkg")) == [
        ("pkg.util", "", "util"),
        ("pkg.util.load", ".util", "load"),
    ]
    assert dict(project.spellings(catalog, target, "function")) == {
        "u.load": ("pkg.util", "load"),
        "pkg.util.load": ("pkg.util", "load"),
    }
    assert dict(modules.classes_under(catalog, "u", "pkg.util", project.CLASS)) == {
        "u.Row": ("pkg.util", "Row"),
    }
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, main, {}),
    )
    assert {o.name: o.fix for o in found} == {"name": "str", "count": "int", "other": "int"}
