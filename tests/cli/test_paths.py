# SPDX-License-Identifier: MIT
"""A directory in a git checkout: only what git tracks there or would is checked (`paths.python_files`)."""

import shutil
import subprocess  # makes a checkout for the walk to ask git about
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.cli import paths

_UNTYPED: Final = "def f() -> None:\n    a = 1\n"
_MADE: Final = "made.py"  # what the checkout's `.gitignore` names, with `made/`
_FILES: Final = ("a.py", "pkg/b.py", "pkg/gone.py", "build/c.py", "made/d.py", "made.py", "notes.txt")


def _git(root: Path, *words: str) -> None:
    _ = subprocess.run(["git", "-C", str(root), *words], check=True, capture_output=True)


@pytest.fixture(name="checkout")
def _checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Make a checkout that ignores `made.py` and `made/`, with a file tracked and since deleted.

    Returns:
      Its root.

    """
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))  # no checkout above it is asked
    root: Path = tmp_path / "checkout"
    name: str
    for name in _FILES:
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        _ = (root / name).write_text(_UNTYPED, encoding="utf-8")
    _ = (root / ".gitignore").write_text("made*\n", encoding="utf-8")
    _git(root, "init", "--quiet")
    _git(root, "add", "pkg/gone.py")
    (root / "pkg" / "gone.py").unlink()
    return root


def test_a_checkouts_ignored_files_are_skipped(checkout: Path) -> None:
    """What git ignores isn't walked, nor what the walk skips anyway; a path named is checked regardless."""
    tracked: list[Path] = list(paths.python_files([checkout], tracked=True))
    assert tracked == [checkout / "a.py", checkout / "pkg" / "b.py"]
    whole: list[Path] = [
        checkout / "a.py",
        checkout / "made" / "d.py",
        checkout / "made.py",
        checkout / "pkg" / "b.py",
    ]
    assert list(paths.python_files([checkout])) == whole
    assert list(paths.python_files([checkout / "made.py"], tracked=True)) == [checkout / "made.py"]
    # A directory git ignores, named: it lists nothing there, and the directory is walked whole.
    assert list(paths.python_files([checkout / "made"], tracked=True)) == [checkout / "made" / "d.py"]
    assert not list(paths.python_files([checkout], ["pkg"], tracked=True))[1:]


def test_the_command_skips_them_unless_told_not_to(
    checkout: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--no-gitignore` walks the directory whole."""
    assert cli.main([str(checkout)]) == cli.EXIT_FOUND
    assert _MADE not in capsys.readouterr().out
    assert cli.main(["--no-gitignore", str(checkout)]) == cli.EXIT_FOUND
    assert _MADE in capsys.readouterr().out


def test_a_directory_is_walked_where_git_has_no_say(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """In no checkout, without git, or where git can't be started."""
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))
    _ = (tmp_path / "a.py").write_text(_UNTYPED, encoding="utf-8")
    assert list(paths.python_files([tmp_path], tracked=True)) == [tmp_path / "a.py"]

    def missing(_name: str) -> str:
        return str(tmp_path / "missing")

    def none(_name: str) -> None:
        return None

    monkeypatch.setattr(shutil, "which", missing)
    assert list(paths.python_files([tmp_path], tracked=True)) == [tmp_path / "a.py"]
    monkeypatch.setattr(shutil, "which", none)
    assert list(paths.python_files([tmp_path], tracked=True)) == [tmp_path / "a.py"]
