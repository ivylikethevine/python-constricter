# SPDX-License-Identifier: MIT
"""`--format=full`: each offence with its source line and a caret under the name."""

import json
from pathlib import Path

import pytest

from constricter.cli import command as cli


def test_full_shows_the_line_and_a_caret_under_the_name(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The caret sits under the name, counted in characters (`col` counts UTF-8 bytes)."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    café = 1\n", encoding="utf-8")
    assert cli.main(["-q", "--format=full", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines() == [
        f"{path}:2:5: error: LVA001 local variable 'café' is not annotated where it's first bound",
        "  |",
        "2 |     café = 1",
        "  |     ^^^^",
        "",
    ]


def test_full_marks_an_annotations_start_with_one_caret(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An offence about an annotation (LVA011) sits at the annotation, not the name: one caret."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    r: tuple[int, int, int, int, int] = t()\n", encoding="utf-8")
    assert cli.main(["-q", "--format=full", "--select=LVA011", str(path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.splitlines()[1:4] == [
        "  |",
        "2 |     r: tuple[int, int, int, int, int] = t()",
        "  |        ^",
    ]


def test_full_places_a_notebooks_offence_in_its_cell(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A notebook's offence shows its cell's line, numbered within the cell."""
    cell: dict[str, str | list[str] | dict[str, str]] = {
        "cell_type": "code",
        "metadata": {},
        "source": ["def f() -> None:\n", "    x = 1\n"],
    }
    path: Path = tmp_path / "demo.ipynb"
    notebook: str = json.dumps({"cells": [cell], "metadata": {}, "nbformat": 4, "nbformat_minor": 5})
    _ = path.write_text(notebook, encoding="utf-8")
    assert cli.main(["-q", "--format=full", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines()[:4] == [
        f"{path}:cell 1:2:5: error: LVA001 local variable 'x' is not annotated where it's first bound",
        "  |",
        "2 |     x = 1",
        "  |     ^",
    ]


def test_full_counts_as_text_for_the_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The summary line (and `--statistics`, `--show-fixes`) treat `full` as text."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    x = 1\n", encoding="utf-8")
    assert cli.main(["--format=full", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines()[-1].startswith("Found 1 error(s)")
