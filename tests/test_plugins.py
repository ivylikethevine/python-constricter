# SPDX-License-Identifier: MIT
"""The flake8 and pylint plugins, run through the real tools as a project would run them."""

import ast
import textwrap
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from typing import Final

import pytest
from astroid import nodes
from flake8.main.application import Application
from pylint.lint import PyLinter, Run
from pylint.reporters import CollectingReporter
from pylint.reporters.text import TextReporter

from constricter.checker import NESTING, Level
from constricter.flake8_plugin import ConstricterChecker
from constricter.pylint_plugin import ConstricterChecker as PylintChecker

SOURCE: Final = """
def broken(items: list[int]) -> None:
    plain = 1
    other = 2  # noqa: LVA001
    third = 3  # pylint: disable=unannotated-local-variable
    typed = 4  # type: int
    for loop in items:
        pass
    for commented in items:  # type: int
        pass
"""
MESSAGE: Final = "local variable {!r} is not annotated where it's first bound"
LOOP: Final = "for/match variable 'loop' is untyped; declare it before the statement"
COMMENTED: Final = "for variable 'commented' is typed only by a type comment; declare it before the loop"


def _write(tmp_path: Path) -> Path:
    path: Path = tmp_path / "broken.py"
    _ = path.write_text(textwrap.dedent(SOURCE), encoding="utf-8", newline="\n")
    return path


@pytest.fixture(name="flake8")
def _flake8_fixture(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> Callable[..., list[str]]:
    """Run flake8 in-process, undoing `parse_options` (which sets class state).

    Returns:
      Its output lines.

    """
    monkeypatch.setattr(ConstricterChecker, "level", Level.STRICT)
    monkeypatch.setattr(ConstricterChecker, "type_comments", False)
    monkeypatch.setattr(ConstricterChecker, "all_scopes", False)
    monkeypatch.setattr(ConstricterChecker, "nesting", NESTING)

    def _run(*args: str) -> list[str]:
        application: Application = Application()
        application.run(["--select=LVA", *args])
        return capsys.readouterr().out.splitlines()

    return _run


def test_flake8_reports_errors_only_and_honours_noqa(
    tmp_path: Path,
    flake8: Callable[..., list[str]],
) -> None:
    """The flake8 plugin reports the level's errors (LVA001 at strict), minus `# noqa` lines."""
    path: Path = _write(tmp_path)
    assert flake8(str(path)) == [
        f"{path}:3:5: LVA001 {MESSAGE.format('plain')}",
        f"{path}:5:5: LVA001 {MESSAGE.format('third')}",
        f"{path}:6:5: LVA001 {MESSAGE.format('typed')}",
    ]


def test_flake8_options(tmp_path: Path, flake8: Callable[..., list[str]]) -> None:
    """`--constricter-level` adds codes; `--constricter-type-comments` counts type comments."""
    path: Path = _write(tmp_path)
    lines: list[str] = flake8("--constricter-level=suffocate", "--constricter-type-comments", str(path))
    assert lines == [
        f"{path}:3:5: LVA001 {MESSAGE.format('plain')}",
        f"{path}:5:5: LVA001 {MESSAGE.format('third')}",
        f"{path}:7:9: LVA002 {LOOP}",
        f"{path}:9:9: LVA003 {COMMENTED}",
    ]


def test_flake8_lists_the_plugin(
    flake8: Callable[..., list[str]],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`flake8 --version` names the plugin."""
    with pytest.raises(SystemExit):
        _ = flake8("--version")
    assert ConstricterChecker.name in capsys.readouterr().out


def test_flake8_checker_uses_flake8s_tree_without_type_comments() -> None:
    """A file with no `# type:` comment is checked on the tree flake8 already parsed."""
    source: str = "def f() -> None:\n    x = 1\n"
    checker: ConstricterChecker = ConstricterChecker(ast.parse(source), source.splitlines(keepends=True))
    assert [(line, col) for line, col, _, _ in checker.run()] == [(2, 4)]


def _pylint(path: Path, *args: str) -> list[str]:
    output: StringIO = StringIO()
    _ = Run(
        [
            "--load-plugins=constricter.pylint_plugin",
            "--disable=all",
            "--enable=constricter",
            "--msg-template={line}:{column}: {msg_id} {symbol} {msg}",
            "--score=n",
            *args,
            str(path),
        ],
        reporter=TextReporter(output),
        exit=False,
    )
    return [line for line in output.getvalue().splitlines() if not line.startswith("*")]


def test_pylint_reports_errors_only_and_honours_disable(tmp_path: Path) -> None:
    """The pylint plugin reports the level's errors (C9101 at strict), minus disabled and `# noqa` lines."""
    prefix: str = "C9101 unannotated-local-variable"
    assert _pylint(_write(tmp_path)) == [
        f"3:4: {prefix} {MESSAGE.format('plain')}",
        f"6:4: {prefix} {MESSAGE.format('typed')}",
    ]


def test_pylint_options(tmp_path: Path) -> None:
    """`constricter-level` adds C9102/C9103; `constricter-type-comments` counts type comments."""
    lines: list[str] = _pylint(_write(tmp_path), "--constricter-level=3", "--constricter-type-comments=y")
    assert lines == [
        f"3:4: C9101 unannotated-local-variable {MESSAGE.format('plain')}",
        f"7:8: C9102 untyped-for-or-match-variable {LOOP}",
        f"9:8: C9103 comment-typed-for-variable {COMMENTED}",
    ]


def test_pylint_checker_skips_a_module_without_source() -> None:
    """A module astroid built without a file is skipped."""
    reporter: CollectingReporter = CollectingReporter()
    linter: PyLinter = PyLinter(reporter=reporter)
    PylintChecker(linter).process_module(nodes.Module("in_memory", file=None))
    assert not reporter.messages


def test_all_scopes_option(tmp_path: Path, flake8: Callable[..., list[str]]) -> None:
    """`all-scopes` makes both plugins report LVA004 / C9104 for module variables."""
    path: Path = tmp_path / "module.py"
    _ = path.write_text("LIMIT = 1\n", encoding="utf-8", newline="\n")
    member: str = "module or class variable 'LIMIT' is not annotated where it's first bound"
    assert not flake8(str(path))
    assert flake8("--constricter-all-scopes", str(path)) == [f"{path}:1:1: LVA004 {member}"]
    assert _pylint(path, "--constricter-all-scopes=y") == [
        f"1:0: C9104 unannotated-module-or-class-variable {member}",
    ]


def test_vague_and_nested_annotations_at_suffocate(tmp_path: Path, flake8: Callable[..., list[str]]) -> None:
    """At `suffocate`, both plugins report LVA005 / C9105 and, at the set nesting, LVA006 / C9106."""
    path: Path = tmp_path / "annotated.py"
    _ = path.write_text("def f() -> None:\n  x: list[list[Any]] = []\n", encoding="utf-8", newline="\n")
    vague: str = "the annotation of 'x' is vague: Any, object, or a generic without its parameters"
    nested: str = "the annotation of 'x' nests too deeply; name a part of it with a `type` alias"
    assert flake8("--constricter-level=suffocate", "--constricter-nesting=2", str(path)) == [
        f"{path}:2:6: LVA005 {vague}",
        f"{path}:2:6: LVA006 {nested}",
    ]
    assert _pylint(path, "--constricter-level=suffocate", "--constricter-nesting=2") == [
        f"2:5: C9105 vague-annotation {vague}",
        f"2:5: C9106 deeply-nested-annotation {nested}",
    ]
