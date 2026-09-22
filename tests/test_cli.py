# SPDX-License-Identifier: MIT
"""The `constricter` command: file discovery, `# noqa`, output and exit status."""

import json
import runpy
import sys
import textwrap
from pathlib import Path
from typing import Final, TypeAlias, cast

import pytest

from constricter import cli

BROKEN: Final = """
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
ONE_CLEAN_FILE: Final = "Found 0 error(s) and 0 warning(s) in 1 file(s).\n"
PLAIN: Final = "local variable 'plain' is not annotated where it's first bound"
FOURTH: Final = "local variable 'fourth' is not annotated where it's first bound"
LOOP: Final = "for/match variable 'loop' is untyped; declare it before the statement"
_Json: TypeAlias = "str | int | float | bool | list[_Json] | dict[str, _Json] | None"
_Sarif: TypeAlias = dict[str, list[dict[str, list[dict[str, _Json]]]]]
CLEAN: Final = """
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
  results: list[dict[str, _Json]] = cast("list[dict[str, _Json]]", json.loads(capsys.readouterr().out))
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
  results: list[dict[str, _Json]] = sarif["runs"][0]["results"]
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


def _pyproject(directory: Path, text: str) -> None:
  _ = (directory / "pyproject.toml").write_text(text, encoding="utf-8")


def test_pyproject_sets_the_defaults(
  tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
  """The nearest `pyproject.toml`'s `[tool.constricter]` sets the defaults; flags still win."""
  _pyproject(
    tmp_path,
    """
[tool.constricter]
level = "constrict"
exclude = ["skipped.py"]
type-comments = true
all-scopes = true
""",
  )
  source: str = (
    "LIMIT = 1\ndef f(items: list[int]) -> None:\n  x = 1  # type: int\n  for y in items:\n    pass\n"
  )
  _ = _write(tmp_path / "pkg" / "checked.py", source)
  _ = _write(tmp_path / "pkg" / "skipped.py", "def f() -> None:\n  z = 1\n")
  monkeypatch.chdir(tmp_path / "pkg")
  assert cli.main(["."]) == cli.EXIT_FOUND
  out: str = capsys.readouterr().out
  assert [(line.split(": ")[1], line.split(": ")[2][:6]) for line in out.splitlines()[:-1]] == [
    ("error", "LVA004"),
    ("error", "LVA002"),
  ]
  assert out.endswith("Found 2 error(s) and 0 warning(s) in 1 file(s).\n")
  assert cli.main(["--level=0", "."]) == cli.EXIT_CLEAN


def test_pyproject_level_can_be_a_number(tmp_path: Path) -> None:
  """`level` takes a number too."""
  _pyproject(tmp_path, "[tool.constricter]\nlevel = 3\n")
  assert cli.config_defaults(tmp_path) == {"level": "3"}


def test_no_table_or_no_pyproject_sets_nothing(tmp_path: Path) -> None:
  """A `pyproject.toml` without the table, or none at all, sets no defaults."""
  _pyproject(tmp_path, '[project]\nname = "x"\n')
  assert not cli.config_defaults(tmp_path)
  assert not cli.config_defaults(Path(tmp_path.anchor))


@pytest.mark.parametrize(
  "text",
  [
    '[tool.constricter]\nlevel = "tight"\n',
    "[tool.constricter]\nlevel = true\n",
    '[tool.constricter]\nexclude = "x"\n',
    "[tool.constricter]\nexclude = [1]\n",
    "[tool.constricter]\nall-scopes = 1\n",
    "[tool.constricter]\ncolour = 1\n",
    "[tool.constricter]\nnesting = 0\n",
    "[tool.constricter]\nnesting = true\n",
    '[tool.constricter]\nselect = "LVA001"\n',
    "[tool]\nconstricter = 1\n",
    "not toml [",
  ],
)
def test_a_bad_pyproject_exits_2(
  tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], text: str
) -> None:
  """An unreadable `pyproject.toml`, or a bad key or value in the table, exits 2."""
  _pyproject(tmp_path, text)
  monkeypatch.chdir(tmp_path)
  exit_info: pytest.ExceptionInfo[SystemExit]
  with pytest.raises(SystemExit) as exit_info:
    _ = cli.main([])
  assert exit_info.value.code == cli.EXIT_ERROR
  assert f"{tmp_path / 'pyproject.toml'}: " in capsys.readouterr().err


def test_fix_adds_the_annotations_values_decide(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """`--fix` annotates what it can in place, keeps line endings, and reports the rest."""
  source: bytes = (
    b"def f() -> None:\r\n  a = 1; b = 'x'\r\n  c = [1]\r\n  d = 2  # noqa: LVA001\r\n  e = Path()\r\n"
  )
  path: Path = tmp_path / "fixable.py"
  _ = path.write_bytes(source)
  assert cli.main(["--fix", str(path)]) == cli.EXIT_FOUND
  fixed: bytes = (
    b"def f() -> None:\r\n"
    b"  a: int = 1; b: str = 'x'\r\n"
    b"  c = [1]\r\n"
    b"  d = 2  # noqa: LVA001\r\n"
    b"  e: Path = Path()\r\n"
  )
  assert path.read_bytes() == fixed
  out: str = capsys.readouterr().out
  assert out.startswith(f"{path}:3:3: error: LVA001 local variable 'c'")
  assert out.endswith("Found 1 error(s) and 0 warning(s) in 1 file(s); fixed 3.\n")
  assert cli.main(["--fix", "-q", str(path)]) == cli.EXIT_FOUND
  assert cli.fix_file(path, []) == 0


def test_relaxed_hides_vague_and_nested_annotations(
  tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
  """LVA005 and LVA006 aren't reported at `relaxed`; `--nesting` sets LVA006's depth."""
  path: Path = _write(tmp_path / "vague.py", "def f() -> None:\n  x: list[list[Any]] = []\n")
  assert cli.main(["-q", "--level=relaxed", str(path)]) == cli.EXIT_CLEAN
  assert not capsys.readouterr().out
  assert cli.main(["-q", "--nesting=2", str(path)]) == cli.EXIT_CLEAN
  assert [line.split(": ")[2][:6] for line in capsys.readouterr().out.splitlines()] == ["LVA005", "LVA006"]


@pytest.mark.parametrize("nesting", ["0", "x", "-1"])
def test_a_bad_nesting_exits_2(nesting: str, capsys: pytest.CaptureFixture[str]) -> None:
  """`--nesting` takes a whole number of at least 1."""
  exit_info: pytest.ExceptionInfo[SystemExit]
  with pytest.raises(SystemExit) as exit_info:
    _ = cli.main([f"--nesting={nesting}"])
  assert exit_info.value.code == cli.EXIT_ERROR
  assert capsys.readouterr().err.endswith(f"expected a whole number of at least 1, not {nesting!r}\n")


def test_pyproject_nesting(tmp_path: Path) -> None:
  """`nesting` in `[tool.constricter]` takes a whole number of at least 1."""
  _pyproject(tmp_path, "[tool.constricter]\nnesting = 3\n")
  assert cli.config_defaults(tmp_path) == {"nesting": 3}


DEMO: Final = "def f(items: list[int]) -> None:\n  a = 1\n  b = [1]\n  for c in items:\n    pass\n"


@pytest.mark.parametrize("code", ["LVA001", "LVA002", "LVA003", "LVA004", "LVA005", "LVA006"])
def test_explain_prints_each_code(code: str, capsys: pytest.CaptureFixture[str]) -> None:
  """`--explain` prints a code's message, rationale and levels, then exits 0."""
  exit_info: pytest.ExceptionInfo[SystemExit]
  with pytest.raises(SystemExit) as exit_info:
    _ = cli.main(["--explain", code])
  assert exit_info.value.code == cli.EXIT_CLEAN
  out: str = capsys.readouterr().out
  assert out.startswith(f"{code}: ")
  assert out.rstrip().endswith("suffocate: error")


def test_statistics_counts_each_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """`--statistics` prints a count per code instead of each offence."""
  path: Path = _write(tmp_path / "demo.py", DEMO)
  assert cli.main(["--statistics", str(path)]) == cli.EXIT_FOUND
  assert capsys.readouterr().out.splitlines() == [
    "    2  LVA001  error",
    "    1  LVA002  warning",
    "Found 2 error(s) and 1 warning(s) in 1 file(s).",
  ]


def test_select_and_ignore(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
  """`--select` keeps only matching codes or prefixes; `--ignore` drops them."""
  path: Path = _write(tmp_path / "demo.py", DEMO)
  assert cli.main(["-q", "--select", "lva002", str(path)]) == cli.EXIT_CLEAN
  assert [line.split(": ")[2][:6] for line in capsys.readouterr().out.splitlines()] == ["LVA002"]
  assert cli.main(["-q", "--select", "LVA00", "--ignore", "LVA001,LVA002", str(path)]) == cli.EXIT_CLEAN
  assert not capsys.readouterr().out


def test_pyproject_select_and_ignore(tmp_path: Path) -> None:
  """`select` and `ignore` in `[tool.constricter]` take lists of codes."""
  _pyproject(tmp_path, '[tool.constricter]\nselect = ["LVA001"]\nignore = ["LVA002"]\n')
  assert cli.config_defaults(tmp_path) == {"select": ["LVA001"], "ignore": ["LVA002"]}


def test_a_select_matching_no_code_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
  """A code or prefix that matches no code is an error."""
  exit_info: pytest.ExceptionInfo[SystemExit]
  with pytest.raises(SystemExit) as exit_info:
    _ = cli.main(["--select", "LVA001,XYZ"])
  assert exit_info.value.code == cli.EXIT_ERROR
  assert capsys.readouterr().err.endswith("no code starts with XYZ\n")


def test_diff_prints_the_fixes_and_changes_nothing(
  tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
  """`--diff` prints what `--fix` would change, exits 1 if anything would, and writes nothing."""
  path: Path = _write(tmp_path / "demo.py", DEMO)
  assert cli.main(["--diff", str(path)]) == cli.EXIT_FOUND
  assert capsys.readouterr().out == (
    f"--- {path}\n+++ {path}\n@@ -1,5 +1,5 @@\n def f(items: list[int]) -> None:\n-  a = 1\n+  a: int = 1\n"
    "   b = [1]\n   for c in items:\n     pass\n"
  )
  assert path.read_text(encoding="utf-8") == DEMO
  clean: Path = _write(tmp_path / "clean.py", CLEAN)
  assert cli.main(["--diff", str(clean)]) == cli.EXIT_CLEAN
  assert not capsys.readouterr().out
  bad: Path = _write(tmp_path / "bad.py", "def (:\n")
  assert cli.main(["--diff", str(bad)]) == cli.EXIT_ERROR


def test_fix_and_diff_cant_be_combined(capsys: pytest.CaptureFixture[str]) -> None:
  """`--fix --diff` is an error."""
  exit_info: pytest.ExceptionInfo[SystemExit]
  with pytest.raises(SystemExit) as exit_info:
    _ = cli.main(["--fix", "--diff"])
  assert exit_info.value.code == cli.EXIT_ERROR
  assert capsys.readouterr().err.endswith("--fix and --diff can't be combined\n")
