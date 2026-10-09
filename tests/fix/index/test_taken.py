# SPDX-License-Identifier: MIT
"""`--fix` for an empty container another checked file types: by its function's parameter, or its class."""

import textwrap
from pathlib import Path
from typing import Final

from constricter.cli import command as cli
from constricter.fix.index import beyond, project, taken

_LIBRARY: Final = """
class Row:
    pass


def add(names: list[str], extra: str) -> None:
    names.append(extra)


def keep(*, rows: list[Row]) -> None:
    pass


def plain(count: int) -> None:
    pass


def hide(rows: list[Row]) -> None:
    pass


class Holder:
    def __init__(self) -> None:
        self.rows = []
        self.seen = set()
        self.read = []
        self.filled = []
        self.under = []
        self.twice = []
        self.twice = {}
        self.typed: list[int] = []

    def size(self) -> int:
        return len(self.read)

    def fill(self) -> None:
        self.filled.append(1)


class Under(Holder):
    def fill(self) -> None:
        self.under.append(1)


class Twice:
    pass


class Twice:
    def __init__(self) -> None:
        self.rows = []
"""
_INIT: Final = "from lib.library import add as moved\nfrom lib.missing import gone\n"
_USE: Final = """
import lib
from lib import library
from lib.library import Holder, Row, add


def run() -> None:
    names = []
    add(names, "a")
    rows = []
    library.keep(rows=rows)
    moved = []
    lib.moved(moved, "a")
    plain = []
    library.plain(plain)
    gone = []
    lib.gone(gone)


class Sub(Holder):
    def push(self, row: str, flag: bool) -> None:
        self.rows.append(row)
        self.seen.add(flag)
        self.read.append(row)
        self.filled.append(row)
        self.under.append(row)
        self.twice.append(row)


class Reader(Sub):
    def first(self) -> None:
        one = self.rows[0]
        flags = self.seen
        read = self.read
        filled = self.filled
        under = self.under
        twice = self.twice


class Bound(Holder):
    rows = ()

    def push(self) -> None:
        self.rows.append(1)


class Stored(Holder):
    def push(self) -> None:
        self.rows = [1]
        self.seen.add(1)


def read(sub: Sub, holder: Holder, bound: Bound, stored: Stored) -> None:
    mine = sub.rows
    theirs = holder.rows
    kept = bound.rows
    reset = stored.rows
    added = stored.seen
"""
_FIXED: Final = (
    "    names: list[str] = []\n",
    "    rows: list[Row] = []\n",
    "    moved: list[str] = []\n",  # through a re-export
    "        one: str = self.rows[0]\n",  # filled under another file's class, which only binds it
    "        flags: set[bool] = self.seen\n",
    "    mine: list[str] = sub.rows\n",
    "    added: set[int] = stored.seen\n",
    "    reset: list[int] = stored.rows\n",  # stored again: by its class's own assignment
)
_UNFIXED: Final = (
    "    plain = []\n",
    "    gone = []\n",
    "        read = self.read\n",  # its own class reads it
    "        filled = self.filled\n",  # or fills it,
    "        under = self.under\n",  # or a class of its file's under it does,
    "        twice = self.twice\n",  # or binds it two kinds
    "    theirs = holder.rows\n",
    "    kept = bound.rows\n",  # bound in the class's body
)


_SHADOWING: Final = (
    "from lib.library import hide\n\nRow = 1\n\n\ndef run() -> None:\n    rows = []\n    hide(rows)\n"
)


def _project(root: Path) -> Path:
    name: str
    source: str
    for name, source in (
        ("__init__", _INIT),
        ("library", _LIBRARY),
        ("use", _USE),
        ("shadowing", _SHADOWING),
    ):
        path: Path = root / "lib" / f"{name}.py"
        path.parent.mkdir(exist_ok=True)
        _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return root / "lib" / "use.py"


def test_another_files_parameter_or_class_types_an_empty_container(tmp_path: Path) -> None:
    """Guesses, as what a function's own fills type is."""
    use: Path = _project(tmp_path)
    _ = cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)])
    assert not any(line in use.read_text(encoding="utf-8") for line in _FIXED)
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    fixed: str = use.read_text(encoding="utf-8")
    assert all(line in fixed for line in (*_FIXED, *_UNFIXED)), fixed


def test_the_index_has_each_files_takers_and_untouched_containers(tmp_path: Path) -> None:
    """A function's container parameters, as the calling file writes them; a class's, bound empty alone."""
    use: Path = _project(tmp_path)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert catalog.modules["lib.library"].emptied == {"Holder": {"rows": "list", "seen": "set"}}
    assert taken.calls(catalog, use, {}) == {
        "add": {"names": (0, True, "list[str]")},
        "library.keep": {"rows": (None, True, "list[Row]")},
        "lib.moved": {"names": (0, True, "list[str]")},
    }
    assert not taken.calls(catalog, tmp_path / "missing.py", {})
    assert not taken.calls(catalog, use.with_name("shadowing.py"), {})  # no way to name its `Row`
    assert beyond.emptied(catalog, use) == {
        name: {"rows": "list", "seen": "set"} for name in ("Sub", "Bound", "Stored")
    }
    assert not beyond.emptied(catalog, tmp_path / "missing.py")
