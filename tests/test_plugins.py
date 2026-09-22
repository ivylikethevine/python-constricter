# SPDX-License-Identifier: MIT
"""The flake8 and pylint plugins, run through the real tools as a project would run them."""

import ast
import textwrap
from collections.abc import Callable
from io import StringIO
from pathlib import Path

import pytest
from astroid import nodes
from flake8.main.application import Application
from pylint.lint import PyLinter, Run
from pylint.reporters import CollectingReporter
from pylint.reporters.text import TextReporter

from constricter.flake8_plugin import ConstricterChecker
from constricter.pylint_plugin import ConstricterChecker as PylintChecker

SOURCE = """
def broken() -> None:
    plain = 1
    other = 2  # noqa: LVA001
    third = 3  # pylint: disable=unannotated-local-variable
    typed = 4  # type: int
"""
MESSAGE = "local variable {!r} is not annotated where it's first bound"


def _write(tmp_path: Path) -> Path:
    path: Path = tmp_path / "broken.py"
    _ = path.write_text(textwrap.dedent(SOURCE), encoding="utf-8")
    return path


@pytest.fixture(name="flake8")
def _flake8_fixture(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> Callable[..., list[str]]:
    """Run flake8 in-process; its output lines. Undoes `parse_options`, which sets class state."""
    monkeypatch.setattr(ConstricterChecker, "type_comments", False)

    def _run(*args: str) -> list[str]:
        application: Application = Application()
        application.run(["--select=LVA", *args])
        return capsys.readouterr().out.splitlines()

    return _run


def test_flake8_reports_lva001_and_honours_noqa(tmp_path: Path, flake8: Callable[..., list[str]]) -> None:
    path: Path = _write(tmp_path)
    assert flake8(str(path)) == [
        f"{path}:3:5: LVA001 {MESSAGE.format('plain')}",
        f"{path}:5:5: LVA001 {MESSAGE.format('third')}",
        f"{path}:6:5: LVA001 {MESSAGE.format('typed')}",
    ]


def test_flake8_type_comments_option(tmp_path: Path, flake8: Callable[..., list[str]]) -> None:
    path: Path = _write(tmp_path)
    lines: list[str] = flake8("--constricter-type-comments", str(path))
    assert [line.split(": ", 1)[0] for line in lines] == [f"{path}:3:5", f"{path}:5:5"]


def test_flake8_lists_the_plugin(
    flake8: Callable[..., list[str]], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        _ = flake8("--version")
    assert ConstricterChecker.name in capsys.readouterr().out


def test_flake8_checker_in_process() -> None:
    source: str = textwrap.dedent(SOURCE)
    checker: ConstricterChecker = ConstricterChecker(ast.parse(source), source.splitlines(keepends=True))
    assert [(line, col) for line, col, _, _ in checker.run()] == [(3, 4), (4, 4), (5, 4), (6, 4)]


def _pylint(path: Path, *args: str) -> list[str]:
    output: StringIO = StringIO()
    _ = Run(
        [
            "--load-plugins=constricter.pylint_plugin",
            "--disable=all",
            "--enable=unannotated-local-variable",
            "--msg-template={line}:{column}: {msg_id} {symbol} {msg}",
            "--score=n",
            *args,
            str(path),
        ],
        reporter=TextReporter(output),
        exit=False,
    )
    return [line for line in output.getvalue().splitlines() if not line.startswith("*")]


def test_pylint_reports_c9101_and_honours_disable(tmp_path: Path) -> None:
    prefix: str = "C9101 unannotated-local-variable"
    assert _pylint(_write(tmp_path)) == [
        f"3:4: {prefix} {MESSAGE.format('plain')}",
        f"4:4: {prefix} {MESSAGE.format('other')}",
        f"6:4: {prefix} {MESSAGE.format('typed')}",
    ]


def test_pylint_type_comments_option(tmp_path: Path) -> None:
    lines: list[str] = _pylint(_write(tmp_path), "--constricter-type-comments=y")
    assert [line.split(": ", 1)[0] for line in lines] == ["3:4", "4:4"]


def test_pylint_checker_skips_a_module_without_source() -> None:
    reporter: CollectingReporter = CollectingReporter()
    linter: PyLinter = PyLinter(reporter=reporter)
    PylintChecker(linter).process_module(nodes.Module("in_memory", file=None))
    assert not reporter.messages
