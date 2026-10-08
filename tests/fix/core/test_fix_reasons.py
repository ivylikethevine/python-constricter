# SPDX-License-Identifier: MIT
"""`--show-fixes`: how each `--fix` annotation was decided (constricter.annotations.inference)."""

import json
from pathlib import Path
from typing import Final, TypeAlias, cast

import pytest

from constricter import check_source
from constricter.cli import command as cli
from constricter.cli.report import Result
from constricter.cli.runs import CheckRun, merged
from constricter.offences import Level, Offence

# One JSON result, and its `fix` object.
_Fix: TypeAlias = dict[str, str | bool | list[str]]
_Entry: TypeAlias = dict[str, str | int | _Fix | None]

SOURCE: str = """\
class Point:
    x: int

    def norm(self) -> float:
        return 0.0


def make() -> Point:
    return Point()


def f(s: str, nums: list[int], p: Point, pairs: dict[str, int]) -> None:
    a = 1
    b = s.strip()
    c = Box()
    d = nums.pop()
    e = len(s)
    g = [1, 2]
    h = not a
    i = f"{a}"
    j = a
    k = nums[0]
    m = p.x
    n = p.norm()
    o = make()
    q = -1
"""


def test_each_fix_says_how_its_value_decided_it() -> None:
    """Every inference mechanism names itself: the reason `--show-fixes` prints."""
    assert [(o.name, o.fix, o.reason) for o in check_source(SOURCE)] == [
        ("a", "int", "a literal"),
        ("b", "str", "`str.strip`'s fixed return type"),
        ("c", "Box", "a call to `Box`, taken to construct one"),
        ("d", "int", "`list[int].pop` on its element types"),
        ("e", "int", "`len`'s fixed return type"),
        ("g", "list[int]", "a list whose elements' types agree"),
        ("h", "bool", "`not`, always a `bool`"),
        ("i", "str", "an f-string"),
        ("j", "int", "a copy of `a`"),
        ("k", "int", "a subscript of `nums`, a `list[int]`"),
        ("m", "int", "the annotation of `Point.x`"),
        ("n", "float", "`Point.norm`'s declared return type"),
        ("o", "Point", "`make`'s declared return type"),
        ("q", "int", "a literal"),
    ]


def test_show_fixes_lists_each_fix_after_the_report(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """One line per fixable offence, after the report; a guess says it needs `--unsafe-fixes`."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    a = 1\n    b = Box()\n    c = g()\n", encoding="utf-8")
    assert cli.main(["-q", "--show-fixes", str(path)]) == cli.EXIT_FOUND
    out: list[str] = capsys.readouterr().out.splitlines()
    assert out[-2:] == [
        f"{path}:2:5: fix 'a': `int`, from a literal [literal]",
        (
            f"{path}:3:5: fix 'b': `Box`, from a call to `Box`, taken to construct one [constructor]"
            " (a guess: --unsafe-fixes)"
        ),
    ]


def test_json_carries_each_fix_and_its_reason(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=json` always has a `fix` object (or `null`): annotation, reason, and whether a guess."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    a = 1\n    c = g()\n", encoding="utf-8")
    assert cli.main(["--format=json", str(path)]) == cli.EXIT_FOUND
    report: list[_Entry] = cast("list[_Entry]", json.loads(capsys.readouterr().out))
    assert [entry["fix"] for entry in report] == [
        {"annotation": "int", "reason": "a literal", "unsafe": False, "kinds": ["literal"]},
        None,
    ]


_MADE: Final = """\
def f(rows: list[str]) -> None:
    a = 1
    for b in rows:
        pass
    c = open("x", "rb")
    d = Box()
"""
_GUESS: Final = (
    "fix 'd': `Box`, from a call to `Box`, taken to construct one [constructor] (a guess: --unsafe-fixes)"
)


def test_show_fixes_lists_the_fixes_fix_made(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """After what's left, each as `fixed`, on the line it was on before a declaration or an import."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text(_MADE, encoding="utf-8")
    assert cli.main(["--fix", "-q", "--show-fixes", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines()[1:] == [
        f"{path}:6:5: {_GUESS}",  # left: where it was too
        f"{path}:2:5: fixed 'a': `int`, from a literal [literal]",
        f"{path}:3:9: fixed 'b': `str`, from the elements of a copy of `rows` [copy, loop]",
        f"{path}:5:5: fixed 'c': `BufferedReader`, from `open`'s mode `rb` [open]",
    ]
    assert cli.main(["--fix", "-q", "--unsafe-fixes", "--show-fixes", str(path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.endswith(
        ":8:5: fixed 'd': `Box`, from a call to `Box`, taken to construct one [constructor]\n",
    )


def test_json_lists_the_fixes_fix_made_with_show_fixes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each entry says whether it's `fixed`; without `--show-fixes`, only what's left is listed."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text(_MADE, encoding="utf-8")
    assert cli.main(["--fix", "--show-fixes", "--format=json", str(path)]) == cli.EXIT_FOUND
    report: list[_Entry] = cast("list[_Entry]", json.loads(capsys.readouterr().out))
    assert [
        (entry["line"], entry["fixed"], cast("_Fix", entry["fix"])["annotation"]) for entry in report
    ] == [
        (6, False, "Box"),
        (2, True, "int"),
        (3, True, "str"),
        (5, True, "BufferedReader"),
    ]
    _ = path.write_text(_MADE, encoding="utf-8")
    assert cli.main(["--fix", "--format=json", str(path)]) == cli.EXIT_FOUND
    report = cast("list[_Entry]", json.loads(capsys.readouterr().out))
    assert [(entry["line"], entry["fixed"]) for entry in report] == [(6, False)]


def test_a_notebooks_fixes_are_listed_in_their_cells(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A cell's lines, as they were."""
    cell: dict[str, str | list[str]] = {
        "cell_type": "code",
        "source": ["def f(rows: list[str]) -> None:\n", "    for b in rows:\n", "        c = 1\n"],
    }
    path: Path = tmp_path / "demo.ipynb"
    _ = path.write_text(json.dumps({"cells": [cell], "nbformat": 4}), encoding="utf-8")
    assert cli.main(["--fix", "-q", "--show-fixes", str(path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.splitlines() == [
        f"{path}:cell 1:2:9: fixed 'b': `str`, from the elements of a copy of `rows` [copy, loop]",
        f"{path}:cell 1:3:9: fixed 'c': `int`, from a literal [literal]",
    ]


def _made(line: int, cell: int | None = None) -> Result:
    return Result(Path("demo.py"), Offence(line, 0, "x", cell=cell), Level.STRICT, fixed=True)


def test_a_later_rounds_fixes_are_placed_where_they_were_before_the_first() -> None:
    """Past each line an earlier round added; one on an added line, where that line went."""
    # An import before line 1 and two declarations before line 3: lines 1, 4 and 5 are new.
    first: CheckRun = CheckRun(fixed=1, made=[_made(3)], rounds=(((None, 1), (None, 3), (None, 3)),))
    later: CheckRun = CheckRun(fixed=7, made=[_made(line) for line in range(1, 8)], rounds=(((None, 2),),))
    joined: CheckRun = cast("CheckRun", merged(first, later))
    assert joined.fixed == first.fixed + later.fixed
    assert [made.offence.line for made in joined.made] == [3, 1, 1, 2, 3, 3, 3, 4]
    third: CheckRun = cast("CheckRun", merged(joined, CheckRun(made=[_made(8)], rounds=((),))))
    assert third.made[-1].offence.line == 1 + 3  # through both rounds: line 7, then line 4
    cells: CheckRun = CheckRun(rounds=(((1, 2),),))
    in_cells: CheckRun = cast("CheckRun", merged(cells, CheckRun(made=[_made(3, 1), _made(3, 2)])))
    assert [made.offence.line for made in in_cells.made] == [2, 3]
