# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for a name typed by another checked file's alias of a union."""

import textwrap
from pathlib import Path
from typing import Final

from constricter.cli import command as cli
from constricter.fix.index import project, tuples

SHAPES: Final = """
from typing import Union

Key = Union[int, str]
Maybe = int | None
Pair = tuple[int, str]


class Plain:
    pass
"""

USER: Final = """
from typing import TYPE_CHECKING

import pkg.shapes as shapes
from pkg.shapes import Plain

if TYPE_CHECKING:
    from pkg.shapes import Key


def f(key: Key, maybe: shapes.Maybe, plain: Plain, tested: Key) -> None:
    a = key
    b = maybe
    c = plain
    if tested:
        d = tested
"""

# `maybe` is nearly always checked for `None` first, and `tested` is narrowed under its test.
_FIXED: Final = "    a: Key = key\n    b = maybe\n    c: Plain = plain\n    if tested:\n        d = tested\n"


def test_another_files_alias_of_a_union_is_read_as_the_union(tmp_path: Path) -> None:
    """Imported by name, for type checking alone too, or named through its module."""
    (tmp_path / "pkg").mkdir()
    _ = (tmp_path / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    _ = (tmp_path / "pkg" / "shapes.py").write_text(textwrap.dedent(SHAPES), encoding="utf-8")
    user: Path = tmp_path / "user.py"
    _ = user.write_text(textwrap.dedent(USER), encoding="utf-8")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert tuples.unions(catalog, user, {}) == {
        "Key": "Union[int, str]",
        "shapes.Key": "Union[int, str]",
        "shapes.Maybe": "int | None",
    }
    assert tuples.unions(catalog, tmp_path / "missing.py", {}) == {}
    assert cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)]) == cli.EXIT_FOUND
    assert _FIXED in user.read_text(encoding="utf-8")
