# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for unannotated functions: their `return`s type their calls in other files."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.fix import order, project
from constricter.fix.known import Returns

DEEP: Final = "def base():\n    return 41\n"
UTIL: Final = """
from pkg.deep import base
from pkg.types import Row

def helper():
    return "x"

def chained():
    return base() + 1

def row(flag):
    return Row()

def hidden():
    return Local()

class Local:
    pass
"""
MAIN: Final = """
from pkg import util
from pkg.deep import base
from pkg.util import chained, helper, row, hidden
from pkg.types import Row
import pkg.util as u

def run():
    a = helper()
    b = util.helper()
    c = chained()
    d = u.chained()
    e = row(1)
    f = hidden()
    g = base()
    return a, b, c, d, e, f, g
"""
FIXED: Final = """
from pkg import util
from pkg.deep import base
from pkg.util import chained, helper, row, hidden
from pkg.types import Row
import pkg.util as u

def run():
    a: str = helper()
    b: str = util.helper()
    c: int = chained()
    d: int = u.chained()
    e = row(1)
    f = hidden()
    g: int = base()
    return a, b, c, d, e, f, g
"""
GUESSED: Final = "    e: Row = row(1)\n    f: Local = hidden()\n"
SHOWN: Final = (
    "fix 'e': `Row`, from `row`'s `return`s [returned] (a guess: --unsafe-fixes)\n",
    "fix 'b': `str`, from `util.helper`'s `return`s [returned]\n",
)
CYCLE_A: Final = """
from b import f

def g():
    return 1

def run():
    x = f()
    return x
"""
CYCLE_B: Final = """
import a

def f():
    return a.g()
"""
CYCLE_FIXED: Final = "    x: int = f()\n"
CYCLE_LEFT: Final = "    return a.g()\n"
PACKAGE_FUNCTION: Final = "    a: int = util()\n"


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def _package(root: Path) -> Path:
    """Write `pkg` (a chain of unannotated functions over three modules) and `main.py` under `root`.

    Returns:
      `main.py`.

    """
    _ = _write(root / "pkg" / "__init__.py", "")
    _ = _write(root / "pkg" / "types.py", "class Row:\n    pass\n")
    _ = _write(root / "pkg" / "deep.py", DEEP)
    _ = _write(root / "pkg" / "util.py", UTIL)
    return _write(root / "main.py", MAIN)


@pytest.mark.parametrize("jobs", ["1", "2"])
def test_calls_to_other_files_unannotated_functions_are_typed(tmp_path: Path, jobs: str) -> None:
    """A chain over three files types in one run; a guess stays one, its type imported if it must be.

    `main` calls both `pkg.util` and `pkg.deep`: it waits for both.
    """
    main: Path = _package(tmp_path)
    assert cli.main(["--fix", "-q", f"--jobs={jobs}", str(tmp_path)]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") == FIXED
    main = _package(tmp_path)
    assert cli.main(["--fix", "--unsafe-fixes", "-q", f"--jobs={jobs}", str(tmp_path)]) == cli.EXIT_CLEAN
    assert GUESSED in main.read_text(encoding="utf-8")


def test_a_guess_is_shown_as_one(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A call typed by another file's guessed `return`s is a guess too."""
    _ = _package(tmp_path)
    arguments: list[str] = [
        "--show-fixes",
        "--unsafe-fixes",
        "-q",
        str(tmp_path / "main.py"),
        str(tmp_path / "pkg"),
    ]
    assert cli.main(arguments) == cli.EXIT_FOUND
    shown: str = capsys.readouterr().out
    assert all(line in shown for line in SHOWN)


@pytest.mark.parametrize("jobs", ["1", "2"])
def test_files_calling_each_other_are_checked_again(tmp_path: Path, jobs: str) -> None:
    """In a cycle, each file is checked again while the other's `return`s type more of its calls."""
    first: Path = _write(tmp_path / "a.py", CYCLE_A)
    second: Path = _write(tmp_path / "b.py", CYCLE_B)
    assert cli.main(["--fix", f"--jobs={jobs}", str(tmp_path)]) == cli.EXIT_CLEAN
    assert CYCLE_FIXED in first.read_text(encoding="utf-8")
    assert CYCLE_LEFT in second.read_text(encoding="utf-8")


def test_a_diff_is_the_last_rounds(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Checked again, a file's diff is the later round's, whole."""
    _ = _write(tmp_path / "a.py", CYCLE_A)
    _ = _write(tmp_path / "b.py", CYCLE_B)
    assert cli.main(["--diff", "--jobs=1", str(tmp_path)]) == cli.EXIT_FOUND
    assert f"+{CYCLE_FIXED}" in capsys.readouterr().out


def test_the_plan_orders_callees_first(tmp_path: Path) -> None:
    """Each file comes after those whose unannotated functions it calls; the rest stand alone."""
    _ = _package(tmp_path)
    twin: Path = _write(tmp_path / "other" / "main.py", "def f():\n    return 1\n")
    paths: list[Path] = [
        tmp_path / "main.py",
        tmp_path / "pkg" / "util.py",
        tmp_path / "pkg" / "deep.py",
        tmp_path / "pkg" / "types.py",
        twin,
        tmp_path / "sheet.ipynb",
    ]
    plan: order.Plan = order.plan(project.index(paths), paths)
    checked: list[int] = [at for component in plan.components for at in component]
    assert checked.index(2) < checked.index(1)
    assert plan.components[-3:] == [[0], [4], [5]]  # `main` twice, and a notebook: each alone
    assert not any(plan.after[-3:])
    assert plan.names == {1: "pkg.util", 2: "pkg.deep", 3: "pkg.types"}
    assert plan.after[plan.components.index([1])] == {plan.components.index([2])}


def test_a_package_function_is_not_taken_for_a_submodule(tmp_path: Path) -> None:
    """`from pkg import util` is the package's own `util` if it defines one, not `pkg.util`."""
    _ = _write(tmp_path / "pkg" / "__init__.py", "def util():\n    return 1\n")
    _ = _write(tmp_path / "pkg" / "util.py", "def helper():\n    return 'x'\n")
    main: Path = _write(
        tmp_path / "main.py",
        "from pkg import util\n\ndef run():\n    a = util()\n    return a\n",
    )
    assert cli.main(["--fix", "-q", str(tmp_path)]) == cli.EXIT_CLEAN
    assert PACKAGE_FUNCTION in main.read_text(encoding="utf-8")


def test_returns_are_recorded_only_for_indexed_modules() -> None:
    """A module the index doesn't have gets nothing."""
    catalog: project.Index = project.Index({"m": project.Module("m", {}, {})}, ["m"])
    found: project.Index = project.with_returned(
        catalog,
        {"m": Returns({"f": "int"}), "gone": Returns({"g": "str"})},
    )
    assert list(found.modules) == ["m"]
    assert found.modules["m"].returned.calls == {"f": "int"}
