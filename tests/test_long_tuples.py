# SPDX-License-Identifier: MIT
"""LVA011: a fixed-length tuple annotation listing more than `max-length` types."""

import ast
from pathlib import Path

import pytest

from constricter import LONG_TUPLE, Checks, Level, Offence, check_source
from constricter.cli import command as cli
from constricter.cli import config
from constricter.rules.annotations import length


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        ("int", 0),
        ("tuple[int, str]", 2),
        ("Tuple[int]", 1),
        ("tuple[int, ...]", 0),
        ("typing.Tuple[int, int, int]", 3),
        ("dict[str, tuple[int, int, int, int, int]]", 5),
        ("'tuple[int, int, int]'", 3),
    ],
)
def test_length_is_the_longest_fixed_length_tuple(annotation: str, expected: int) -> None:
    """One type per element counts; `tuple[T, ...]` (any length) doesn't."""
    assert length(ast.parse(annotation, mode="eval").body) == expected


def test_a_tuple_longer_than_max_length_is_lva011() -> None:
    """Reported at the annotation, with the length; 4 by default, `max_length` otherwise."""
    source: str = (
        "def f() -> None:\n"
        "    a: tuple[int, int, int, int] = t()\n"
        "    b: tuple[int, int, int, int, int] = t()\n"
    )
    assert [(o.name, o.code, o.detail) for o in check_source(source)] == [("b", LONG_TUPLE, "5")]
    assert [o.name for o in check_source(source, checks=Checks(max_length=3))] == ["a", "b"]
    expected: str = "the annotation of 'b' lists a tuple of 5 elements; name them (a NamedTuple)"
    assert check_source(source)[0].message == expected


def test_lva011_is_reported_from_strict_and_errors_at_suffocate() -> None:
    """Like LVA005 and LVA006: a warning from `strict`, an error at `suffocate`."""
    offence: Offence = Offence(1, 0, "x", LONG_TUPLE)
    assert [offence.is_reported(level) for level in Level] == [False, True, True, True]
    assert [offence.is_error(level) for level in Level] == [False, False, False, True]


def test_max_length_on_the_cli_and_in_pyproject(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`--max-length` and `max-length` in `[tool.constricter]` set it."""
    _ = (tmp_path / "m.py").write_text(
        "def f() -> None:\n    a: tuple[int, int, int] = t()\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    assert cli.main(["-q", "--select", "LVA011", "m.py"]) == cli.EXIT_CLEAN
    assert (
        cli.main(["-q", "--select", "LVA011", "--level=suffocate", "--max-length=2", "m.py"])
        == cli.EXIT_FOUND
    )
    _ = (tmp_path / "pyproject.toml").write_text("[tool.constricter]\nmax-length = 2\n", encoding="utf-8")
    assert config.config_defaults(tmp_path) == {"max_length": 2}
