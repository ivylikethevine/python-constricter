# SPDX-License-Identifier: MIT
"""Jupyter notebooks: code cells checked as one module, offences placed in their cells."""

import json
from pathlib import Path
from typing import Final, TypeAlias, cast

import pytest

from constricter import cli

_Json: TypeAlias = "str | int | list[_Json] | dict[str, _Json] | None"
_Run: TypeAlias = dict[str, list[dict[str, _Json]]]
_Sarif: TypeAlias = dict[str, list[_Run]]
CELLS: Final = [
  {"cell_type": "markdown", "source": ["# A notebook"]},
  {"cell_type": "code", "source": ["%matplotlib inline\n", "!pip list\n", "import os\n", "os?\n"]},
  {"cell_type": "code", "source": "%%bash\necho $HOME\n"},
  {"cell_type": "code", "source": ["def f() -> None:\n", "  count = 0\n", "  quiet = 1  # noqa: LVA001\n"]},
]
MESSAGE: Final = "local variable 'count' is not annotated where it's first bound"


def _notebook(tmp_path: Path) -> Path:
  path: Path = tmp_path / "analysis.ipynb"
  _ = path.write_text(json.dumps({"cells": CELLS, "nbformat": 4}), encoding="utf-8", newline="\n")
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
    {"physicalLocation": {"artifactLocation": {"uri": path.as_posix()}}}
  ]


def test_notebooks_are_found_and_never_fixed(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """Directory walks include notebooks; `--fix` and `--diff` leave them alone."""
  path: Path = _notebook(tmp_path)
  before: bytes = path.read_bytes()
  assert cli.main(["-q", "--fix", str(tmp_path)]) == cli.EXIT_FOUND
  assert path.read_bytes() == before
  assert cli.main(["--diff", str(tmp_path)]) == cli.EXIT_CLEAN
  assert capsys.readouterr().out.startswith(f"{path}:cell 4:")


@pytest.mark.parametrize("text", ['{"cells": 1}', "[]", "{not json"])
def test_a_bad_notebook_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str], text: str) -> None:
  """A `.ipynb` that isn't a notebook is reported as an error."""
  path: Path = tmp_path / "bad.ipynb"
  _ = path.write_text(text, encoding="utf-8")
  assert cli.main([str(path)]) == cli.EXIT_ERROR
  assert capsys.readouterr().err.startswith(f"{path}: error: ")
