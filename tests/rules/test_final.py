# SPDX-License-Identifier: MIT
"""LVA012 (opt-in): a local bound once and never rebound could be `Final`."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import Checks, Offence, check_source
from constricter.cli import command as cli

CAN_BE_FINAL: Final = "LVA012"
SOURCE: Final = """
from typing import Final


def f(param: int, items: list[int]) -> None:
    once = 1
    typed: int = 2
    already: Final = 3
    also: Final[int] = 4
    twice = 5
    twice = 6
    grown = 7
    grown += 1
    declared: int
    declared = 8
    _ = 9
    param = 10
    for item in items:
        inside = item
    else:
        after = 11
    while items:
        looping = items.pop()
    with open("x") as handle:
        pass
    shared = 12

    def inner() -> None:
        nonlocal shared
        shared = 13
        kept = 14
"""


def _finals(source: str) -> list[str]:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=Checks(final=True))
    return [o.name for o in found if o.code == CAN_BE_FINAL]


def test_bound_once_outside_a_loop() -> None:
    """Only a single plain assignment outside any loop, not declared apart or already `Final`."""
    assert _finals(SOURCE) == ["once", "typed", "after", "kept"]


def test_off_unless_selected() -> None:
    """Without `Checks(final=True)` there's no LVA012 at all."""
    assert all(o.code != CAN_BE_FINAL for o in check_source(textwrap.dedent(SOURCE)))


def test_module_and_class_bodies_are_left_out() -> None:
    """A module or class variable is state other code may rebind."""
    source: str = "LIMIT = 3\n\nclass C:\n    size = 1\n"
    found: list[Offence] = check_source(source, checks=Checks(all_scopes=True, final=True))
    assert all(o.code != CAN_BE_FINAL for o in found)


@pytest.mark.parametrize(
    ("args", "reported"),
    [
        ([], False),
        (["--select=LVA0"], False),  # a prefix never selects an opt-in code
        (["--select=LVA012"], True),
        (["--extend-select=LVA012"], True),
        (["--select=LVA001", "--extend-select=LVA012"], True),
    ],
)
def test_the_command_reports_it_only_when_named(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    args: list[str],
    reported: bool,  # ruff: ignore[boolean-type-hint-positional-argument]  # a parameter pytest fills in
) -> None:
    """`--select` or `--extend-select` must name LVA012 in full; it's an error only at `suffocate`."""
    path: Path = tmp_path / "once.py"
    _ = path.write_text("def f() -> None:\n    limit: int = 3\n", encoding="utf-8")
    assert cli.main(["-q", *args, str(path)]) == cli.EXIT_CLEAN
    assert (CAN_BE_FINAL in capsys.readouterr().out) == reported
    if reported:
        assert cli.main(["-q", "--level=suffocate", *args, str(path)]) == cli.EXIT_FOUND
        assert f"error: {CAN_BE_FINAL}" in capsys.readouterr().out


def test_explain_says_it_is_opt_in(capsys: pytest.CaptureFixture[str]) -> None:
    """`--explain LVA012` says it's only reported when selected."""
    with pytest.raises(SystemExit):
        _ = cli.main(["--explain", CAN_BE_FINAL])
    assert capsys.readouterr().out.endswith("suffocate: error (only when selected)\n")
