# SPDX-License-Identifier: MIT
"""`--show-fixes`: how each `--fix` annotation was decided (constricter.annotations.inference)."""

import json
from pathlib import Path
from typing import TypeAlias, cast

import pytest

from constricter import check_source
from constricter.cli import command as cli

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
