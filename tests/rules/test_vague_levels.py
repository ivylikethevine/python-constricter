# SPDX-License-Identifier: MIT
"""`vague`: how vague an annotation may be before it's LVA005, as `nesting` is LVA006's depth."""

import ast
from pathlib import Path

import pytest

from constricter import VAGUE_TYPE, Checks, check_source
from constricter.cli import command as cli
from constricter.cli import config
from constricter.rules.annotations import vague_fits, vague_parts

_SOURCE: str = """
from typing import Any, Optional


def f() -> None:
    a: Any = g()
    b: tuple[str, Any] = g()
    c: tuple[Any, Any] = g()
    d: Optional[Any] = g()
    e: list = g()
    h: tuple[Any, Any, Any] = g()
"""


@pytest.mark.parametrize(
    ("annotation", "parts"),
    [
        ("int", (0, False)),
        ("Any", (1, True)),
        ("typing.Any", (1, True)),
        ("tuple[str, Any]", (1, False)),
        ("tuple[Any, object]", (2, False)),
        ("list", (1, False)),  # a generic without its parameters says the rest: a list
        ("Any | None", (1, True)),
        ("Optional[object]", (1, True)),
        ("Union[int, Any]", (1, True)),
        ("dict[str, Any] | None", (1, False)),
        ("'Any'", (1, True)),
    ],
)
def test_vague_parts_are_counted_and_one_alone_is_seen(annotation: str, parts: tuple[int, bool]) -> None:
    """Alone: the annotation, or a member of its outermost union; anywhere else, inside a type."""
    assert vague_parts(ast.parse(annotation, mode="eval").body) == parts


@pytest.mark.parametrize(
    ("annotation", "levels"),
    [
        ("int", (True, True, True, True)),
        ("Any", (False, False, True, True)),
        ("tuple[str, Any]", (False, True, True, True)),
        ("tuple[Any, Any]", (False, False, True, True)),
        ("tuple[Any, Any, Any]", (False, False, False, True)),
        ("list", (False, True, True, True)),
        ("Any | None", (False, False, True, True)),
    ],
)
def test_each_level_lets_more_through(annotation: str, levels: tuple[bool, bool, bool, bool]) -> None:
    """-1: none; 0: one inside a type; N from 1: N + 1, or one alone."""
    node: ast.expr = ast.parse(annotation, mode="eval").body
    assert tuple(vague_fits(node, level) for level in (-1, 0, 1, 2)) == levels


def test_lva005_is_reported_past_the_level() -> None:
    """None vague by default; what the level lets through isn't reported."""
    reported: list[list[str]] = [
        [o.name for o in check_source(_SOURCE, checks=Checks(vague=level)) if o.code == VAGUE_TYPE]
        for level in (-1, 0, 1, 2)
    ]
    assert reported == [["a", "b", "c", "d", "e", "h"], ["a", "c", "d", "h"], ["h"], []]


def test_vague_on_the_cli_and_in_pyproject(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`--vague` and `vague` in `[tool.constricter]` set it; below -1, or not a number, it's refused."""
    _ = (tmp_path / "m.py").write_text(
        "from typing import Any\n\n\ndef f() -> None:\n    a: tuple[str, Any] = g()\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    arguments: list[str] = ["-q", "--select", "LVA005", "--level=suffocate", "m.py"]
    assert cli.main(arguments) == cli.EXIT_FOUND
    assert cli.main([*arguments, "--vague=0"]) == cli.EXIT_CLEAN
    assert cli.main([*arguments, "--vague", "-1"]) == cli.EXIT_FOUND
    wrong: str
    for wrong in ("-2", "x"):
        with pytest.raises(SystemExit):
            _ = cli.main([*arguments, f"--vague={wrong}"])
    _ = (tmp_path / "pyproject.toml").write_text("[tool.constricter]\nvague = 0\n", encoding="utf-8")
    assert config.config_defaults(tmp_path) == {"vague": 0}
    assert cli.main(arguments) == cli.EXIT_CLEAN
