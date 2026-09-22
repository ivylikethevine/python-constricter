# SPDX-License-Identifier: MIT
"""The `constricter` command: file discovery, `# noqa`, output and exit status."""

import json
import runpy
import sys
import textwrap
from pathlib import Path
from typing import cast

import pytest

from constricter import cli

BROKEN = """
def broken(items: list[int]) -> None:
    plain = 1
    other = 2  # noqa: LVA001
    third = 3  # noqa
    fourth = 4  # noqa: E501
    for loop in items:
        pass
    for hushed in items:  # noqa: LVA002
        pass
"""
ONE_CLEAN_FILE = "Found 0 error(s) and 0 warning(s) in 1 file(s).\n"
PLAIN = "local variable 'plain' is not annotated where it's first bound"
FOURTH = "local variable 'fourth' is not annotated where it's first bound"
LOOP = "for/match variable 'loop' is untyped; declare it before the statement"
_Sarif = dict[str, list[dict[str, list[dict[str, object]]]]]
CLEAN = """
def clean() -> None:
    fine: int = 1
"""


def _write(path: Path, source: str) -> Path:
  path.parent.mkdir(parents=True, exist_ok=True)
  _ = path.write_text(textwrap.dedent(source), encoding="utf-8")
  return path


def test_reports_unsuppressed_offences_and_exits_1(
  tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
  """Unsuppressed offences print with their severity; an error exits 1."""
  broken: Path = _write(tmp_path / "broken.py", BROKEN)
  assert cli.main([str(broken)]) == cli.EXIT_FOUND
  assert capsys.readouterr().out == (
    f"{broken}:3:5: error: LVA001 {PLAIN}\n"
    f"{broken}:6:5: error: LVA001 {FOURTH}\n"
    f"{broken}:7:9: warning: LVA002 {LOOP}\n"
    "Found 2 error(s) and 1 warning(s) in 1 file(s).\n"
  )


@pytest.mark.parametrize(
  ("level", "status", "summary"),
  [
    ("relaxed", cli.EXIT_CLEAN, "Found 0 error(s) and 3 warning(s)"),
    ("0", cli.EXIT_CLEAN, "Found 0 error(s) and 3 warning(s)"),
    ("constrict", cli.EXIT_FOUND, "Found 3 error(s) and 0 warning(s)"),
  ],
)
def test_level_sets_what_is_an_error(
  tmp_path: Path, capsys: pytest.CaptureFixture[str], level: str, status: int, summary: str
) -> None:
  """`--level` decides which codes are errors; warnings alone exit 0."""
  broken: Path = _write(tmp_path / "broken.py", BROKEN)
  assert cli.main([f"--level={level}", str(broken)]) == status
  assert capsys.readouterr().out.splitlines()[-1].startswith(summary)


def test_clean_files_exit_0_and_quiet_drops_the_summary(
  tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
  """A clean file exits 0; `-q` drops the summary."""
  clean: Path = _write(tmp_path / "clean.py", CLEAN)
  assert cli.main([str(clean)]) == cli.EXIT_CLEAN
  assert capsys.readouterr().out == ONE_CLEAN_FILE
  assert cli.main(["-q", str(clean)]) == cli.EXIT_CLEAN
  assert not capsys.readouterr().out


def test_directories_skip_hidden_and_tool_dirs_and_honour_exclude(tmp_path: Path) -> None:
  """Directory walks skip hidden and tool directories and `--exclude` globs."""
  name: str
  for name in ("a.py", "pkg/b.py", "pkg/fixtures/c.py", ".venv/d.py", "pkg/__pycache__/e.py", "venv/f.py"):
    _ = _write(tmp_path / name, CLEAN)
  _ = _write(tmp_path / "notes.txt", "")
  found: list[Path] = list(cli.python_files([tmp_path], ["*/fixtures/*"]))
  assert found == [tmp_path / "a.py", tmp_path / "pkg" / "b.py"]
  # A file named explicitly is checked even where a directory walk would skip it.
  assert list(cli.python_files([tmp_path / ".venv" / "d.py"])) == [tmp_path / ".venv" / "d.py"]
  assert not list(cli.python_files([tmp_path / "a.py"], ["a.py"]))


def test_defaults_to_the_current_directory(
  tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
  """With no paths it checks the current directory."""
  _ = _write(tmp_path / "clean.py", CLEAN)
  monkeypatch.chdir(tmp_path)
  assert cli.main([]) == cli.EXIT_CLEAN
  assert capsys.readouterr().out == ONE_CLEAN_FILE


def test_unparsable_files_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """An unparsable file is reported on stderr and exits 2; the rest are still checked."""
  bad: Path = _write(tmp_path / "bad.py", "def (:\n")
  broken: Path = _write(tmp_path / "broken.py", BROKEN)
  assert cli.main([str(bad), str(broken)]) == cli.EXIT_ERROR
  out: str
  err: str
  out, err = capsys.readouterr()
  assert err.startswith(f"{bad}: error: ")
  assert out.endswith("Found 2 error(s) and 1 warning(s) in 2 file(s).\n")


def test_runs_as_a_module(
  tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
  """`python -m constricter` runs the command."""
  monkeypatch.setattr(sys, "argv", ["constricter", str(_write(tmp_path / "clean.py", CLEAN))])
  exit_info: pytest.ExceptionInfo[SystemExit]
  with pytest.raises(SystemExit) as exit_info:
    _ = runpy.run_module("constricter", run_name="__main__")
  assert exit_info.value.code == cli.EXIT_CLEAN
  assert capsys.readouterr().out.startswith("Found 0")


def test_type_comments_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """`--type-comments` counts `x = 1  # type: int` as annotated."""
  typed: Path = _write(tmp_path / "typed.py", "def f() -> None:\n    x = 1  # type: int\n")
  assert cli.main(["-q", str(typed)]) == cli.EXIT_FOUND
  assert cli.main(["-q", "--type-comments", str(typed)]) == cli.EXIT_CLEAN
  assert capsys.readouterr().out.count("LVA001") == 1


def test_json_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """`--format=json` prints one object per offence."""
  broken: Path = _write(tmp_path / "broken.py", BROKEN)
  assert cli.main(["--format=json", str(broken)]) == cli.EXIT_FOUND
  results: list[dict[str, object]] = cast("list[dict[str, object]]", json.loads(capsys.readouterr().out))
  assert results[0] == {
    "path": str(broken),
    "line": 3,
    "column": 5,
    "code": "LVA001",
    "severity": "error",
    "message": PLAIN,
  }
  assert [(r["code"], r["severity"]) for r in results] == [
    ("LVA001", "error"),
    ("LVA001", "error"),
    ("LVA002", "warning"),
  ]


def test_github_format_escapes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """`--format=github` prints escaped workflow commands, one per offence."""
  odd: Path = _write(
    tmp_path / "a,b%c.py",
    "def f(items: list[int]) -> None:\n    x = 1\n    for y in items:\n        pass\n",
  )
  assert cli.main(["--format=github", str(odd)]) == cli.EXIT_FOUND
  escaped: str = str(odd).replace("%", "%25").replace(":", "%3A").replace(",", "%2C")
  assert capsys.readouterr().out == (
    f"::error file={escaped},line=2,col=5,title=LVA001::"
    "local variable 'x' is not annotated where it's first bound\n"
    f"::warning file={escaped},line=3,col=9,title=LVA002::"
    "for/match variable 'y' is untyped; declare it before the statement\n"
  )


def test_sarif_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """`--format=sarif` prints a SARIF log with each result's level."""
  broken: Path = _write(tmp_path / "broken.py", BROKEN)
  assert cli.main(["--format=sarif", str(broken)]) == cli.EXIT_FOUND
  sarif: _Sarif = cast("_Sarif", json.loads(capsys.readouterr().out))
  results: list[dict[str, object]] = sarif["runs"][0]["results"]
  assert [(r["ruleId"], r["level"]) for r in results] == [
    ("LVA001", "error"),
    ("LVA001", "error"),
    ("LVA002", "warning"),
  ]
  assert results[0]["locations"] == [
    {
      "physicalLocation": {
        "artifactLocation": {"uri": broken.as_posix()},
        "region": {"startLine": 3, "startColumn": 5},
      }
    }
  ]
