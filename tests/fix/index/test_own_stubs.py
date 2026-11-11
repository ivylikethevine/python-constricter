"""A checked package's own stub, `mod.pyi` beside `mod.py`: read before the source, as a checker does."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli

SOURCE: Final = """
class Axes:
    def legend(self):
        return Legend()


class Legend:
    pass


class Figure:
    def add_subplot(self):
        return Axes()


def subplots():
    return Figure(), Axes()


def gca():
    return current()


def local_use():
    ax = gca()
    return ax
"""
STUB: Final = """
from mpl.legend import Legend


class Axes:
    def legend(self) -> Legend: ...


class Figure:
    def add_subplot(self) -> Axes: ...


def subplots() -> tuple[Figure, Axes]: ...
def gca() -> Axes: ...
"""
USER: Final = """
from mpl.axes import gca, subplots


def draw():
    fig, ax = subplots()
    sub = fig.add_subplot()
    other = gca()
    legend = other.legend()
    return ax, sub, legend
"""
USER_FIXED: Final = (
    "    fig: Figure\n",
    "    ax: Axes\n",
    "    sub: Axes = fig.add_subplot()\n",
    "    other: Axes = gca()\n",
    "    legend: Legend = other.legend()\n",
)
LOCAL_FIXED: Final = "    ax: Axes = gca()\n"
UNSTUBBED: Final = "    other = gca()\n"  # with no stub, `gca` declares nothing


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def test_a_modules_own_stub_types_its_importers_calls_and_its_own(tmp_path: Path) -> None:
    """Its functions' and classes' methods' returns, which the source doesn't declare, by the stub.

    In the module itself, only a type it can write as it is: `Axes`, its own class; the stub's
    `Legend`, which the source doesn't import, is its importers' alone.
    """
    _ = _write(tmp_path / "mpl" / "__init__.py", "")
    _ = _write(tmp_path / "mpl" / "legend.py", "class Legend:\n    pass\n")
    axes: Path = _write(tmp_path / "mpl" / "axes.py", SOURCE)
    _ = _write(tmp_path / "mpl" / "axes.pyi", STUB)
    user: Path = _write(tmp_path / "user.py", USER)
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    fixed: str = user.read_text(encoding="utf-8")
    assert all(line in fixed for line in USER_FIXED), fixed
    assert LOCAL_FIXED in axes.read_text(encoding="utf-8")


def test_a_module_without_a_stub_is_read_from_its_source_alone(tmp_path: Path) -> None:
    """No `.pyi` beside it: its unannotated `gca()` gives its importers nothing."""
    _ = _write(tmp_path / "mpl" / "__init__.py", "")
    _ = _write(tmp_path / "mpl" / "axes.py", SOURCE)
    user: Path = _write(tmp_path / "user.py", USER)
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    assert UNSTUBBED in user.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "stub",
    [b"def gca( -> Axes: ...\n", b"\xff\xfe def gca() -> Axes: ...\n"],
    ids=["unparsed", "undecoded"],
)
def test_a_stub_that_cant_be_read_is_left_out(tmp_path: Path, stub: bytes) -> None:
    """One that doesn't parse, or decode: the module is read from its source alone."""
    _ = _write(tmp_path / "mpl" / "__init__.py", "")
    _ = _write(tmp_path / "mpl" / "axes.py", SOURCE)
    _ = (tmp_path / "mpl" / "axes.pyi").write_bytes(stub)
    user: Path = _write(tmp_path / "user.py", USER)
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    assert UNSTUBBED in user.read_text(encoding="utf-8")


LEGEND: Final = """
class Legend:
    pass


def make() -> Legend:
    return Legend()
"""
MAKING: Final = """
from mpl.legend import make


class Axes:
    def legend(self):
        return make()

    def own(self):
        mine = self.legend()
        return mine


def local_make():
    made = make()
    return made
"""
MADE: Final = """
from mpl.legend import make
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mpl.legend import Legend


class Axes:
    def legend(self):
        return make()

    def own(self):
        mine: Legend = self.legend()
        return mine


def local_make():
    made: Legend = make()
    return made
"""


def test_a_name_only_the_stub_imports_is_imported_where_the_source_writes_it(tmp_path: Path) -> None:
    """The stub's `Legend` isn't the source's: a fix there naming it adds its import for type checking.

    And the source is checked again in the same run: its own method the stub declares a `Legend`
    has that type once the name is imported, a second pass left nothing.
    """
    _ = _write(tmp_path / "mpl" / "__init__.py", "")
    _ = _write(tmp_path / "mpl" / "legend.py", LEGEND)
    axes: Path = _write(tmp_path / "mpl" / "axes.py", MAKING)
    _ = _write(tmp_path / "mpl" / "axes.pyi", STUB)
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    assert axes.read_text(encoding="utf-8") == textwrap.dedent(MADE)
