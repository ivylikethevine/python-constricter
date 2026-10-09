# SPDX-License-Identifier: MIT
"""`--fix` for `with` on another checked file's context manager: a `@contextmanager` function, a class."""

import textwrap
from pathlib import Path
from typing import TYPE_CHECKING, Final

from constricter.cli import command as cli
from constricter.fix.index import managed, order, project

if TYPE_CHECKING:
    from constricter.fix.core.known import Passed

_HELPER: Final = """
import contextlib
import os
from collections.abc import Iterator


class Frame:
    pass


@contextlib.contextmanager
def declared(path: str) -> Iterator[Frame]:
    yield Frame()


@contextlib.contextmanager
def cwd(path):
    yield os.getcwd()


@contextlib.contextmanager
def made(path):
    yield Frame()


@contextlib.contextmanager
def unknown(path):
    yield path


def plain(path: str) -> int:
    return 1


class Guard:
    def __enter__(self):
        return self

    def __exit__(self, *exc: object) -> None:
        pass
"""
_INIT: Final = "from pkg.helper import cwd as moved\nfrom pkg.missing import gone\n"
_USE: Final = """
import pkg
from pkg import helper
from pkg.helper import Guard, declared, made


def run(cwd) -> None:
    with declared("p") as a, helper.declared("p") as b:
        pass
    with helper.cwd("p") as c, pkg.moved("p") as d:
        pass
    with made("p") as e, helper.unknown("p") as f:
        pass
    with Guard() as g, helper.Guard() as h:
        pass
    with cwd("p") as i, helper.plain("p") as j, pkg.gone("p") as k:
        pass
"""
_FIXED: Final = (
    "    a: helper.Frame\n",
    "    b: helper.Frame\n",
    "    c: str\n",
    "    d: str\n",  # through a re-export
    "    e: helper.Frame\n",
    "    g: Guard\n",  # an `__enter__` returning `self`
    "    h: helper.Guard\n",
)
_UNFIXED: Final = ("    f: ", "    i: ", "    j: ", "    k: ")


def _project(root: Path) -> Path:
    name: str
    source: str
    for name, source in (("__init__", _INIT), ("helper", _HELPER), ("use", _USE)):
        path: Path = root / "pkg" / f"{name}.py"
        path.parent.mkdir(exist_ok=True)
        _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return root / "pkg" / "use.py"


def test_another_files_manager_types_a_with_target(tmp_path: Path) -> None:
    """By what it declares it yields, or its `yield`s once its file is checked; a guess's is a guess."""
    use: Path = _project(tmp_path)
    _ = cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)])
    fixed: str = use.read_text(encoding="utf-8")
    assert all(line in fixed for line in _FIXED[:4]), fixed
    assert not any(line in fixed for line in _FIXED[4:])
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    fixed = use.read_text(encoding="utf-8")
    assert all(line in fixed for line in _FIXED), fixed
    assert not any(line in fixed for line in _UNFIXED), fixed


def test_a_file_is_checked_after_the_managers_whose_yields_type_it(tmp_path: Path) -> None:
    """Those declaring nothing; a file the index doesn't have calls none."""
    use: Path = _project(tmp_path)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert managed.needs(catalog, catalog.modules["pkg.use"]) == {"pkg.helper"}
    assert not managed.needs(catalog, catalog.modules["pkg.helper"])
    assert not managed.calls(catalog, tmp_path / "other.py", {})
    assert not managed.calls(catalog, use.with_suffix(".txt"), {})
    found: dict[str, Passed] = managed.calls(catalog, use, {})
    declared: Passed = ("helper.Frame", frozenset())
    assert found == {"declared": declared, "helper.declared": declared}
    paths: list[Path] = sorted(tmp_path.rglob("*.py"))
    plan: order.Plan = order.plan(catalog, paths)
    helper: int = plan.components.index([paths.index(use.with_name("helper.py"))])
    assert plan.components.index([paths.index(use)]) > helper
