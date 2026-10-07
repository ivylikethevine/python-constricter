# SPDX-License-Identifier: MIT
"""One class or alias a file spells two ways (`Schema`, `core.Schema`) is one type to `--fix`."""

import ast
import textwrap
from pathlib import Path
from typing import Final

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.fix.core.known import Guarded, Outside
from constricter.fix.index import project
from constricter.rules.flow import Hierarchy

CORE: Final = """
from typing import Union


class Row: ...


class Other: ...


class Late: ...


Schema = Union[int, str]


def row(q) -> Row: ...
"""
USING: Final = """
from typing import TYPE_CHECKING

from pkg import Schema, core
from pkg.core import Row

if TYPE_CHECKING:
    from pkg.core import Other


def first(q) -> Schema: ...


def second(q) -> core.Schema: ...


def f(q) -> None:
    schema = first(q)
    schema = second(q)
"""
_SCHEMAS: Final = frozenset({"Schema", "core.Schema"})
_ROWS: Final = frozenset({"Row", "core.Row"})


def _package(root: Path) -> list[Path]:
    """Write `pkg` (a class and an alias, the alias re-exported) and a file spelling both two ways.

    Returns:
      Their paths, the using file last.

    """
    (root / "pkg").mkdir()
    sources: dict[str, str] = {"pkg/__init__.py": "from pkg.core import Schema\n", "pkg/core.py": CORE}
    paths: list[Path] = [root / name for name in (*sources, "using.py")]
    path: Path
    for path in paths:
        _ = path.write_text(sources.get(path.relative_to(root).as_posix(), USING), encoding="utf-8")
    return paths


def test_the_index_groups_the_ways_a_file_spells_one_type(tmp_path: Path) -> None:
    """By its name and through its module; the name imported to run, or for type checking alone."""
    paths: list[Path] = _package(tmp_path)
    catalog: project.Index = project.index(paths)
    late: dict[str, Guarded] = {"Late": Guarded(("pkg.core", "Late"), "from pkg.core import Late")}
    assert set(project.same(catalog, paths[-1], late)) == {
        _SCHEMAS,  # through the package's re-export
        _ROWS,
        frozenset({"Other", "core.Other"}),  # imported under `if TYPE_CHECKING:`
        frozenset({"Late", "core.Late"}),  # one a fix imports there
    }
    assert set(project.same(catalog, paths[-1], {})) == {_SCHEMAS, _ROWS, frozenset({"Other", "core.Other"})}
    assert not project.same(catalog, paths[1], {})  # a file that spells each its one way
    assert not project.same(catalog, tmp_path / "missing.py", {})


def test_a_later_binding_spelled_otherwise_fits_the_fix() -> None:
    """`Schema`, then `core.Schema`: no other type, so the first binding's fix stands."""
    source: str = textwrap.dedent(
        """\
        def f(q) -> None:
            schema = first(q)
            schema = second(q)
        """,
    )
    calls: dict[str, str] = {"first": "Schema", "second": "core.Schema"}
    found: list[Offence] = check_source(source, outside=Outside(calls, same=(_SCHEMAS,)))
    assert [(o.name, o.fix, o.unsafe) for o in found] == [("schema", "Schema", False)]
    assert [o.fix for o in check_source(source, outside=Outside(calls))] == [None]
    clashing: Outside = Outside(
        calls,
        guarded={"Schema": Guarded(("pkg.core", "Schema"), "from pkg.core import Schema")},
        same=(_SCHEMAS,),
    )
    assert clashing.usable(frozenset({"Schema"}), frozenset()).same == (_SCHEMAS,)


def test_spellings_of_one_type_fit_each_other() -> None:
    """Each way, and nothing else."""
    hierarchy: Hierarchy = Hierarchy.for_module(ast.parse("class Sub(Row): ...\n"), None, [_ROWS])
    assert hierarchy.fits("Row", "core.Row")
    assert hierarchy.fits("core.Row", "Row")
    assert hierarchy.fits("Sub", "core.Row")
    assert not hierarchy.fits("Row", "core.Schema")


def test_one_run_fixes_a_name_bound_to_both_spellings(tmp_path: Path) -> None:
    """With the CLI, whose index says which spellings are one type; a second pass changes nothing."""
    paths: list[Path] = _package(tmp_path)
    for _ in range(2):
        _ = cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)])
        assert paths[-1].read_text(encoding="utf-8") == USING.replace(
            "schema = first",
            "schema: Schema = first",
        )
