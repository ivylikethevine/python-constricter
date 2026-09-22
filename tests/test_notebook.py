# SPDX-License-Identifier: MIT
"""Jupyter notebooks: code cells checked as one module, offences placed in their cells."""

import json
from pathlib import Path
from typing import Final, TypeAlias, cast

import pytest

from constricter import cli, notebook
from constricter.checker import Offence

_Json: TypeAlias = "str | int | list[_Json] | dict[str, _Json] | None"
_Cell: TypeAlias = dict[str, str | list[str]]
_Run: TypeAlias = dict[str, list[dict[str, _Json]]]
_Sarif: TypeAlias = dict[str, list[_Run]]
CELLS: Final[list[_Cell]] = [
    {"cell_type": "markdown", "source": ["# A notebook"]},
    {"cell_type": "code", "source": ["%matplotlib inline\n", "!pip list\n", "import os\n", "os?\n"]},
    {"cell_type": "code", "source": "%%bash\necho $HOME\n"},
    {"cell_type": "code", "source": ["def f() -> None:\n", "  count = 0\n", "  quiet = 1  # noqa: LVA001\n"]},
]
MESSAGE: Final = "local variable 'count' is not annotated where it's first bound"


def _nbformat(cells: list[_Cell]) -> str:
    """Write a notebook's JSON as nbformat does: indent 1, and a final newline.

    Returns:
      The JSON.

    """
    return json.dumps({"cells": cells, "nbformat": 4}, indent=1) + "\n"


def _notebook(tmp_path: Path) -> Path:
    path: Path = tmp_path / "analysis.ipynb"
    _ = path.write_text(_nbformat(CELLS), encoding="utf-8", newline="\n")
    return path


def test_offences_are_placed_in_their_cells(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """IPython syntax is skipped; an offence is reported at its cell and line in it; `# noqa` works."""
    path: Path = _notebook(tmp_path)
    assert cli.main(["-q", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out == f"{path}:cell 4:2:3: error: LVA001 {MESSAGE}\n"


def test_every_format_names_the_cell(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """JSON has the cell; GitHub and SARIF point at the file, with the cell and line in the message."""
    path: Path = _notebook(tmp_path)
    _ = cli.main(["--format=json", str(path)])
    results: list[dict[str, _Json]] = cast("list[dict[str, _Json]]", json.loads(capsys.readouterr().out))
    assert [(r["cell"], r["line"], r["column"]) for r in results] == [(4, 2, 3)]
    _ = cli.main(["--format=github", str(path)])
    escaped: str = str(path).replace("%", "%25").replace(":", "%3A").replace(",", "%2C")
    assert capsys.readouterr().out == f"::error file={escaped},title=LVA001::cell 4, line 2: {MESSAGE}\n"
    _ = cli.main(["--format=sarif", str(path)])
    sarif: _Sarif = cast("_Sarif", json.loads(capsys.readouterr().out))
    assert sarif["runs"][0]["results"][0]["locations"] == [
        {"physicalLocation": {"artifactLocation": {"uri": path.as_posix()}}},
    ]


def test_fix_and_diff_edit_the_cells(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--diff` shows each changed cell; `--fix` edits it and keeps the rest of the file as it was."""
    path: Path = _notebook(tmp_path)
    before: str = path.read_text(encoding="utf-8")
    assert cli.main(["--diff", str(tmp_path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out == (
        f"--- {path}:cell 4\n+++ {path}:cell 4\n@@ -1,3 +1,3 @@\n def f() -> None:\n-  count = 0\n"
        "+  count: int = 0\n   quiet = 1  # noqa: LVA001\n"
    )
    assert path.read_text(encoding="utf-8") == before
    assert cli.main(["-q", "--fix", str(tmp_path)]) == cli.EXIT_CLEAN
    fixed: list[_Cell] = [
        *CELLS[:3],
        {**CELLS[3], "source": ["def f() -> None:\n", "  count: int = 0\n", "  quiet = 1  # noqa: LVA001\n"]},
    ]
    assert path.read_text(encoding="utf-8") == _nbformat(fixed)


def test_fix_applies_every_offence_in_a_cell(tmp_path: Path) -> None:
    """`--fix` applies every fixable offence in a cell, not just its first."""
    cells: list[_Cell] = [
        {"cell_type": "code", "source": ["def f() -> None:\n", "  a = 0\n", "  b = 1\n"]},
    ]
    path: Path = tmp_path / "two.ipynb"
    _ = path.write_text(_nbformat(cells), encoding="utf-8", newline="\n")
    assert cli.main(["-q", "--fix", str(path)]) == cli.EXIT_CLEAN
    fixed: list[_Cell] = [
        {**cells[0], "source": ["def f() -> None:\n", "  a: int = 0\n", "  b: int = 1\n"]},
    ]
    assert path.read_text(encoding="utf-8") == _nbformat(fixed)


def test_fix_ignores_an_offence_without_a_fix_or_a_cell() -> None:
    """`notebook.fix` skips an offence that has no fix or no cell, not just the ones that do."""
    cells: list[_Cell] = [{"cell_type": "code", "source": ["a = 0\n"]}]
    raw: str = _nbformat(cells)
    offences: list[Offence] = [
        Offence(1, 0, "unfixable", fix=None, cell=1),
        Offence(1, 0, "cellless", fix="int", cell=None),
        Offence(1, 0, "a", fix="int", cell=1),
    ]
    text: str
    changed: list[notebook.Cell]
    text, changed = notebook.fix(raw, offences)
    assert [c.number for c in changed] == [1]
    assert cast("_Cell", json.loads(text)["cells"][0])["source"] == ["a: int = 0\n"]


@pytest.mark.parametrize("text", ['{"cells": 1}', "[]", "{not json"])
def test_a_bad_notebook_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str], text: str) -> None:
    """A `.ipynb` that isn't a notebook is reported as an error."""
    path: Path = tmp_path / "bad.ipynb"
    _ = path.write_text(text, encoding="utf-8")
    assert cli.main([str(path)]) == cli.EXIT_ERROR
    assert capsys.readouterr().err.startswith(f"{path}: error: ")


def test_coverage_counts_a_notebooks_cells(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--coverage` counts a notebook's code cells: `count` and `quiet` untyped (`# noqa` types nothing)."""
    path: Path = _notebook(tmp_path)
    assert cli.main(["--coverage", str(path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.startswith(f"{path}: 0/2 typed (0.0%)\n")
