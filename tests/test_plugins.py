"""The flake8 and pylint plugins, run through the real tools as a project would run them."""

import ast
import subprocess
import sys
import textwrap
from pathlib import Path

from astroid import nodes
from pylint.lint import PyLinter, Run
from pylint.reporters import CollectingReporter

from constricter.flake8_plugin import ConstricterChecker
from constricter.pylint_plugin import ConstricterChecker as PylintChecker

SOURCE = """
def broken() -> None:
    plain = 1
    other = 2  # noqa: LVA001
    third = 3  # pylint: disable=unannotated-local-variable
"""


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, "-m", *args], capture_output=True, text=True, check=False)


def _write(tmp_path: Path) -> Path:
    path: Path = tmp_path / "broken.py"
    path.write_text(textwrap.dedent(SOURCE))
    return path


def test_flake8_reports_lva001_and_honours_noqa(tmp_path: Path) -> None:
    path: Path = _write(tmp_path)
    result: subprocess.CompletedProcess[str] = _run("flake8", "--select=LVA", str(path))
    assert result.returncode == 1, result.stderr
    assert result.stdout.splitlines() == [
        f"{path}:3:5: LVA001 local variable 'plain' is not annotated where it's first bound",
        f"{path}:5:5: LVA001 local variable 'third' is not annotated where it's first bound",
    ]


def test_flake8_lists_the_plugin() -> None:
    assert "constricter" in _run("flake8", "--version").stdout


def test_pylint_reports_c9101_and_honours_disable(tmp_path: Path) -> None:
    path: Path = _write(tmp_path)
    result: subprocess.CompletedProcess[str] = _run(
        "pylint",
        "--load-plugins=constricter.pylint_plugin",
        "--disable=all",
        "--enable=unannotated-local-variable",
        "--msg-template={line}:{column}: {msg_id} {symbol} {msg}",
        "--score=n",
        str(path),
    )
    assert result.returncode != 0, result.stderr
    lines: list[str] = [line for line in result.stdout.splitlines() if not line.startswith("*")]
    message: str = (
        "C9101 unannotated-local-variable local variable {!r} is not annotated where it's first bound"
    )
    assert lines == [f"3:4: {message.format('plain')}", f"4:4: {message.format('other')}"]


def test_flake8_checker_in_process() -> None:
    checker: ConstricterChecker = ConstricterChecker(ast.parse(textwrap.dedent(SOURCE)))
    assert [(line, col, message.split()[0]) for line, col, message, _ in checker.run()] == [
        (3, 4, "LVA001"),
        (4, 4, "LVA001"),
        (5, 4, "LVA001"),
    ]


def test_pylint_checker_in_process(tmp_path: Path) -> None:
    reporter: CollectingReporter = CollectingReporter()
    Run(
        [
            "--load-plugins=constricter.pylint_plugin",
            "--disable=all",
            "--enable=unannotated-local-variable",
            str(_write(tmp_path)),
        ],
        reporter=reporter,
        exit=False,
    )
    assert [(m.line, m.symbol) for m in reporter.messages] == [
        (3, "unannotated-local-variable"),
        (4, "unannotated-local-variable"),
    ]


def test_pylint_checker_skips_a_module_without_source() -> None:
    reporter: CollectingReporter = CollectingReporter()
    linter: PyLinter = PyLinter(reporter=reporter)
    PylintChecker(linter).process_module(nodes.Module("in_memory", file=None))
    assert reporter.messages == []
