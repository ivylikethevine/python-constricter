# SPDX-License-Identifier: MIT
"""`min-python`: the oldest Python a project runs on, from `--min-python` or its `requires-python`."""

from pathlib import Path

import pytest

from constricter.cli import config
from constricter.cli.options import Options


def _pyproject(directory: Path, text: str) -> None:
    _ = (directory / "pyproject.toml").write_text(text, encoding="utf-8", newline="\n")


@pytest.mark.parametrize(
    ("required", "oldest"),
    [
        ('">=3.11"', "3.11"),
        ('">=3.9,<4"', "3.9"),
        ('"~=3.10.2"', "3.10"),
        ('"==3.12.*"', "3.12"),
        ('"> 3.8, >=3.10, !=3.13.*, <=3.14"', "3.10"),  # the highest lower bound
        ('">=3"', "3.0"),
        ('"<4"', None),  # no lower bound
        ("3", None),  # not a specifier
    ],
)
def test_requires_python_says_the_oldest_python(tmp_path: Path, required: str, oldest: str | None) -> None:
    """Its highest lower bound, where `[tool.constricter]` doesn't set `min-python`."""
    _pyproject(tmp_path, f"[project]\nrequires-python = {required}\n")
    assert config.config_defaults(tmp_path) == ({} if oldest is None else {"min_python": oldest})


def test_min_python_is_set_over_requires_python(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """By `[tool.constricter]`'s `min-python`, and over both by `--min-python`."""
    monkeypatch.chdir(tmp_path)
    assert Options.parse([]).checks.min_python is None  # no `pyproject.toml`
    _pyproject(tmp_path, '[project]\nrequires-python = ">=3.9"\n')
    assert Options.parse([]).checks.min_python == (3, 9)
    _pyproject(tmp_path, '[project]\nrequires-python = ">=3.9"\n[tool.constricter]\nmin-python = "3.12"\n')
    assert config.config_defaults(tmp_path) == {"min_python": "3.12"}
    assert Options.parse([]).checks.min_python == (3, 12)
    assert Options.parse(["--min-python=3.10"]).checks.min_python == (3, 10)


@pytest.mark.parametrize("version", ["3", "py311", "3.x", ""])
def test_a_bad_min_python_exits_2(version: str, capsys: pytest.CaptureFixture[str]) -> None:
    """`--min-python` takes a version: a major and a minor number."""
    with pytest.raises(SystemExit):
        _ = Options.parse([f"--min-python={version}"])
    assert capsys.readouterr().err.endswith(f"expected a Python version like 3.11, got {version!r}\n")


@pytest.mark.parametrize("value", ["3.11", '"py311"', '"3"', '["3.11"]'])
def test_a_bad_min_python_in_pyproject_is_refused(tmp_path: Path, value: str) -> None:
    """`min-python` takes a version, as text."""
    _pyproject(tmp_path, f"[tool.constricter]\nmin-python = {value}\n")
    with pytest.raises(ValueError, match=r"\[tool.constricter\] has an invalid min-python = "):
        _ = config.config_defaults(tmp_path)
