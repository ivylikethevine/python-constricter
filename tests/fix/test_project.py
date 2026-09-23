# SPDX-License-Identifier: MIT
"""Cross-module `--fix`: calls to functions, and uses of classes, other checked files define."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.fix import project
from constricter.fix.known import Classes

UTIL: Final = """
from pkg.types import Row
import pkg.types as t

class Local:
    pass

def helper() -> int:
    return 1

def row() -> Row:
    return Row()

def trow() -> t.Row:
    return t.Row()

def local() -> Local:
    return Local()

def text() -> "list[str]":
    return []

def length() -> len:
    return len
"""
MAIN: Final = """
from pkg import helper
from pkg.util import row, local, length
from pkg.types import Row
import pkg.util as u
import pkg.util

def run() -> None:
    a = helper()
    b = row()
    c = local()
    d = u.helper()
    e = pkg.util.text()
    f = u.trow()
    g = length()
"""
SERIAL: Final = "\n  require_serial: true\n"
DEEP: Final = "    x: int = helper()\n    y = far()\n"
FIXED: Final = """
from pkg import helper
from pkg.util import row, local, length
from pkg.types import Row
import pkg.util as u
import pkg.util

def run() -> None:
    a: int = helper()
    b: Row = row()
    c = local()
    d: int = u.helper()
    e: 'list[str]' = pkg.util.text()
    f = u.trow()
    g: len = length()
"""


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def _package(root: Path) -> None:
    """Write `pkg` (a re-export in `__init__`, a helper module, a deep relative import) under `root`."""
    _ = _write(root / "pkg" / "__init__.py", "from .util import helper\nfrom . import types\n")
    _ = _write(root / "pkg" / "types.py", "class Row:\n    pass\n")
    _ = _write(root / "pkg" / "util.py", UTIL)
    _ = _write(root / "pkg" / "sub" / "__init__.py", "")
    _ = _write(
        root / "pkg" / "sub" / "deep.py",
        "from ..util import helper\nfrom ...outside import far\n\ndef go() -> None:\n"
        + DEEP.replace(": int", ""),
    )


@pytest.mark.parametrize("jobs", ["1", "2"])
def test_fix_annotates_calls_to_other_modules(tmp_path: Path, jobs: str) -> None:
    """`--fix` types a call to another checked file's function, when the file can name its type."""
    _package(tmp_path)
    main: Path = _write(tmp_path / "main.py", MAIN)
    assert cli.main(["--fix", "-q", f"--jobs={jobs}", str(tmp_path)]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") == FIXED
    assert (tmp_path / "pkg" / "sub" / "deep.py").read_text(encoding="utf-8").endswith(DEEP)


def test_module_names_follow_packages(tmp_path: Path) -> None:
    """A file's module name starts at the outermost folder with an `__init__.py`."""
    _package(tmp_path)
    names: list[str] = [
        project.module_name(tmp_path / "pkg" / "sub" / "deep.py"),
        project.module_name(tmp_path / "pkg" / "__init__.py"),
        project.module_name(tmp_path / "main.py"),
    ]
    assert names == ["pkg.sub.deep", "pkg", "main"]


def test_index_reads_names_and_skips_what_it_cannot(tmp_path: Path) -> None:
    """The index records each top-level binding's origin, and skips unparsable and non-`.py` files."""
    source: Path = _write(
        tmp_path / "mod.py",
        "import os.path\nimport json as j\nx, (y, z) = 1, (2, 3)\nw: int = 1\nw += 1\nif w:\n    pass\n",
    )
    broken: Path = _write(tmp_path / "broken.py", "def (\n")
    sheet: Path = _write(tmp_path / "sheet.ipynb", "{}")
    index: project.Index = project.index([source, broken, sheet, tmp_path / "gone.py"])
    assert list(index.modules) == ["mod"]
    assert index.modules["mod"].names == {
        "os": ("os", None),
        "j": ("json", None),
        "x": ("mod", "x"),
        "y": ("mod", "y"),
        "z": ("mod", "z"),
        "w": ("mod", "w"),
    }


def test_calls_skip_what_they_cannot_resolve(tmp_path: Path) -> None:
    """Nothing for unindexed files, re-export loops, local names, or unknown modules."""
    loop: Path = _write(
        tmp_path / "loop.py",
        "from loop import f\nfrom other import g\ndef h() -> int:\n    return 1\n",
    )
    index: project.Index = project.index([loop])
    assert not project.calls(index, loop)
    assert not project.calls(index, tmp_path / "sheet.ipynb")
    assert not project.calls(index, tmp_path / "unknown.py")
    cycle: dict[str, project.Module] = {
        "a": project.Module("a", {}, {"f": ("b", "f")}),
        "b": project.Module("b", {}, {"f": ("a", "f")}),
    }
    assert not project.calls(project.Index(cycle, sorted(cycle)), Path("a.py"))


def test_split_run_misses_what_the_serial_hook_fixes(tmp_path: Path) -> None:
    """Split across processes (as pre-commit does by default), `main.py` can't see `pkg`'s types.

    So the `constricter-fix` hook asks pre-commit for one process (`require_serial`).
    """
    _package(tmp_path)
    main: Path = _write(tmp_path / "main.py", MAIN)
    assert cli.main(["--fix", "-q", str(main)]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") != FIXED
    assert cli.main(["--fix", "-q", str(main), str(tmp_path / "pkg")]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") == FIXED
    hooks: list[str] = (
        (Path(__file__).parents[2] / ".pre-commit-hooks.yaml").read_text(encoding="utf-8").split("- id: ")
    )
    fix: str = next(hook for hook in hooks if hook.startswith("constricter-fix\n"))
    assert SERIAL in fix


MODELS: Final = """
from typing import Self

from pkg.types import Tag


class Row:
    size: int
    tag: Tag
    local: "Hidden"

    @property
    def label(self) -> str:
        return ""

    def total(self) -> float:
        return 0.0

    def again(self) -> Self:
        return self


class Hidden:
    pass
"""
USES: Final = """
import pkg.models as m
from pkg import Row
from pkg.types import Tag


def f(row: Row, other: m.Row) -> None:
    a = row.size
    b = row.label
    c = row.total()
    d = row.again()
    e = other.again()
    g = row.tag
    h = other.tag
    i = row.local
    j = other.missing
"""


def test_imported_classes_type_their_members(tmp_path: Path) -> None:
    """An imported class's attributes, properties and methods type their uses, as in its own module.

    Through `from pkg import Row` (a re-export) and `import pkg.models as m`; a `Self` return is the
    class as the file spells it; a type the file can't name (`Hidden`) is left out.
    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "from .models import Row\n")
    _ = _write(tmp_path / "pkg" / "types.py", "class Tag:\n    pass\n")
    _ = _write(tmp_path / "pkg" / "models.py", MODELS)
    main: Path = _write(tmp_path / "main.py", USES)
    imported: project.Imported = project.imported(project.index(sorted(tmp_path.rglob("*.py"))), main)
    offences: list[Offence] = check_source(main.read_text(encoding="utf-8"), classes=imported.classes)
    assert {o.name: o.fix for o in offences} == {
        "a": "int",
        "b": "str",
        "c": "float",
        "d": "Row",
        "e": "m.Row",
        "g": "Tag",
        "h": "Tag",
        "i": None,
        "j": None,
    }
    assert project.imported(project.Index({}, []), main) == project.Imported({}, Classes({}, {}))
