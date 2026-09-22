"""The `constricter` command: file discovery, `# noqa`, output and exit status."""

import runpy
import sys
import textwrap
from pathlib import Path

import pytest

from constricter import cli

BROKEN = """
def broken() -> None:
    plain = 1
    other = 2  # noqa: LVA001
    third = 3  # noqa
    fourth = 4  # noqa: E501
"""
CLEAN = """
def clean() -> None:
    fine: int = 1
"""


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source))
    return path


def test_reports_unsuppressed_offences_and_exits_1(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    broken: Path = _write(tmp_path / "broken.py", BROKEN)
    assert cli.main([str(broken)]) == 1
    assert capsys.readouterr().out == (
        f"{broken}:3:5: LVA001 local variable 'plain' is not annotated where it's first bound\n"
        f"{broken}:6:5: LVA001 local variable 'fourth' is not annotated where it's first bound\n"
        "Found 2 unannotated local(s) in 1 file(s).\n"
    )


def test_clean_files_exit_0_and_quiet_drops_the_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    clean: Path = _write(tmp_path / "clean.py", CLEAN)
    assert cli.main([str(clean)]) == 0
    assert capsys.readouterr().out == "Found 0 unannotated local(s) in 1 file(s).\n"
    assert cli.main(["-q", str(clean)]) == 0
    assert capsys.readouterr().out == ""


def test_directories_skip_hidden_and_tool_dirs_and_honour_exclude(tmp_path: Path) -> None:
    for name in ("a.py", "pkg/b.py", "pkg/fixtures/c.py", ".venv/d.py", "pkg/__pycache__/e.py", "venv/f.py"):
        _ = _write(tmp_path / name, CLEAN)
    _ = _write(tmp_path / "notes.txt", "")
    found: list[Path] = list(cli.python_files([tmp_path], ["*/fixtures/*"]))
    assert found == [tmp_path / "a.py", tmp_path / "pkg" / "b.py"]
    # A file named explicitly is checked even where a directory walk would skip it.
    assert list(cli.python_files([tmp_path / ".venv" / "d.py"])) == [tmp_path / ".venv" / "d.py"]
    assert list(cli.python_files([tmp_path / "a.py"], ["a.py"])) == []


def test_defaults_to_the_current_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _ = _write(tmp_path / "clean.py", CLEAN)
    monkeypatch.chdir(tmp_path)
    assert cli.main([]) == 0
    assert capsys.readouterr().out == "Found 0 unannotated local(s) in 1 file(s).\n"


def test_unparseable_files_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    bad: Path = _write(tmp_path / "bad.py", "def (:\n")
    broken: Path = _write(tmp_path / "broken.py", BROKEN)
    assert cli.main([str(bad), str(broken)]) == 2
    out: str
    err: str
    out, err = capsys.readouterr()
    assert err.startswith(f"{bad}: error: ")
    assert "Found 2 unannotated local(s) in 2 file(s)." in out


def test_runs_as_a_module(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["constricter", str(_write(tmp_path / "clean.py", CLEAN))])
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = runpy.run_module("constricter", run_name="__main__")
    assert exit_info.value.code == 0
    assert capsys.readouterr().out.startswith("Found 0")
