# SPDX-License-Identifier: MIT
"""`--infer-from`: a traced run's types (`python -m constricter.trace`), as hints `--fix` guesses with."""

import ast
import hashlib
import json
import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import trace
from constricter.cli import command as cli
from constricter.cli import config, traced
from constricter.fix.core.known import Hints, Offered

_SOURCE: Final = """
import os


class Local:
    pass


@decorated
def f(self, param, typed: int, *rest, **named):
    global shared
    once = param.make()
    twice = param.first
    twice = param.second
    for looped in param.rows:
        inside = looped.row
    while param.more:
        spun = param.next
    shared = param.shared
    import late
    try:
        pass
    except ValueError as caught:
        pass
    match param:
        case [_, *starred]:
            pass
        case {"k": 1, **mapped}:
            pass
        case captured:
            pass
    late = param.late
    caught = param.caught
    starred = param.starred
    mapped = param.mapped
    captured = param.captured
    param = param.parent

    def inner(deep):
        nested = deep.count
        return nested

    total = [each for each in rest]
    made = make(param)
    declared = typed.real
    mine = self.count
    self.count = param.count
    both = also = param.both
    own = param.local()
    other = rest[0]
    maybe = named["k"]
    again = other.child
    unknown = param.unknown
    many = param.many
    private = param.private
    clash = param.clash
    unseen = param.unseen
    return once


def untraced(param):
    x = param.x
    return x
"""
_F: Final = _SOURCE.splitlines().index("@decorated") + 1  # `f`'s first line: its decorator's
_INNER: Final = _SOURCE.splitlines().index("    def inner(deep):") + 1
_ONE: Final = ["int"]
_HELD: Final = {
    **dict.fromkeys(
        (
            *("once", "twice", "looped", "inside", "spun", "shared", "late", "caught", "starred"),
            *("mapped", "captured", "param", "rest", "nested", "each", "made", "declared", "mine"),
            *("both", "also", "again"),
        ),
        _ONE,
    ),
    "total": ["list[int]"],
    "own": ["m:Local"],
    "other": ["pkg.things:Thing"],
    "maybe": ["None", "pkg.things:Thing"],
    "unknown": ["int", trace.UNKNOWN],
    "many": ["bytes", "float", "int", "str"],
    "private": ["_thread:lock"],
    "clash": ["a:Thing", "b:Thing"],
}
_IMPORT: Final = ("from pkg.things import Thing",)
_USER: Final = "def f(q):\n    x = q.make()\n    return x\n"
_USER_FIXED: Final = "def f(q):\n    x: int = q.make()\n    return x\n"
_TRACE: Final = "trace.json"
_REFUSED: Final = f"{_TRACE}: "  # how a refusal names the file
_SHOWN: Final = "fix 'x': `int`, from what a traced run bound it to [traced] (a guess: --unsafe-fixes)"


def _digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def _trace(source: str, functions: dict[int, dict[str, list[str]]], *, local: str = "m") -> traced.Trace:
    """Make the trace of a file holding `source`, the module `local` to those who name its classes.

    Returns:
      It.

    """
    return traced.Trace(
        {
            _digest(source): {
                line: {name: tuple(types) for name, types in held.items()} for line, held in functions.items()
            },
        },
        {local: _digest(source)},
    )


def _written(path: Path, source: str, functions: dict[int, dict[str, list[str]]]) -> Path:
    """Write the trace file of a file holding `source` to `path`.

    Returns:
      `path`.

    """
    _ = path.write_text(
        json.dumps(
            {
                "version": trace.VERSION,
                "files": {
                    _digest(source): {
                        "path": "user.py",
                        "functions": {str(line): held for line, held in functions.items()},
                    },
                },
                "modules": {},
            },
        ),
        encoding="utf-8",
    )
    return path


def _named(source: str, found: Hints | None) -> dict[str, tuple[str, tuple[str, ...]]]:
    """Name each of a file's hints by the name it types.

    Returns:
      Each hint's text and its imports.

    """
    assert found is not None
    names: dict[tuple[int, int], str] = {
        (node.lineno, node.end_col_offset or 0): node.id
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Name)
    }
    return {
        names[where]: (text, found.offered.get(where, Offered(text)).imports)
        for where, text in found.types.items()
    }


def test_a_local_bound_once_has_what_it_held() -> None:
    """One taken from an unannotated parameter, bound once, outside any loop."""
    found: Hints | None = traced.hints(
        _trace(_SOURCE, {_F: _HELD, _INNER: {"nested": _ONE}}),
        _SOURCE.encode(),
    )
    assert found is not None
    assert (found.checker, found.kind) == ("a traced run", "traced")
    assert _named(_SOURCE, found) == {
        "once": ("int", ()),
        "nested": ("int", ()),
        "own": ("Local", ()),  # the file's own class: no import
        "other": ("Thing", _IMPORT),
        "maybe": ("Thing | None", _IMPORT),
    }


def test_a_file_the_trace_doesnt_have_has_no_hints() -> None:
    """One edited since, one that doesn't parse, and one whose functions bind nothing it saw."""
    found: traced.Trace = _trace(_SOURCE, {_F: _HELD})
    assert traced.hints(found, _SOURCE.encode() + b"\n") is None
    assert traced.hints(_trace("def (", {1: {"x": _ONE}}), b"def (") is None
    assert traced.hints(_trace(_SOURCE, {_F: {"param": _ONE}}), _SOURCE.encode()) is None


def test_a_trace_file_is_read_leniently(tmp_path: Path) -> None:
    """What isn't as the recorder writes it is skipped."""
    path: Path = tmp_path / _TRACE
    _ = path.write_text(
        json.dumps(
            {
                "version": trace.VERSION,
                "files": {"d": {"functions": {"3": {"x": _ONE, "y": "int"}, "three": {"z": _ONE}}}, "e": []},
                "modules": {"m": "d", "n": 1},
            },
        ),
        encoding="utf-8",
    )
    assert traced.load(path) == traced.Trace({"d": {3: {"x": ("int",)}}, "e": {}}, {"m": "d"})


@pytest.mark.parametrize("text", [None, "{", "[]", '{"version": 0}'])
def test_what_isnt_a_trace_is_refused(
    tmp_path: Path,
    text: str | None,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A file that's missing, isn't JSON, or isn't this version's: the command exits 2."""
    path: Path = tmp_path / _TRACE
    if text is not None:
        _ = path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match=r"trace\.json: "):
        _ = traced.load(path)
    with pytest.raises(SystemExit):
        _ = cli.main([f"--infer-from={path}", str(tmp_path)])
    assert _REFUSED in capsys.readouterr().err


def test_a_traces_hints_follow_the_checkers(tmp_path: Path) -> None:
    """Each file's, where the trace has it: not a notebook's, nor an unreadable file's."""
    user: Path = tmp_path / "user.py"
    _ = user.write_text(_USER, encoding="utf-8", newline="\n")
    other: Path = tmp_path / "other.py"
    _ = other.write_text("x = 1\n", encoding="utf-8", newline="\n")
    checker: Hints = Hints("ty")
    found: dict[Path, tuple[Hints, ...]] = traced.merged(
        {user: (checker,)},
        _trace(_USER, {1: {"x": _ONE}}),
        [user, other, tmp_path / "notebook.ipynb", tmp_path / "missing.py"],
    )
    assert list(found) == [user]
    assert found[user][0] is checker
    assert found[user][1].types == {(2, 5): "int"}


def test_fix_guesses_with_a_trace(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """With `--unsafe-fixes`, as kind `traced`, which `fix-ignore` leaves out."""
    user: Path = tmp_path / "user.py"
    _ = user.write_text(_USER, encoding="utf-8", newline="\n")
    found: str = f"--infer-from={_written(tmp_path / _TRACE, _USER, {1: {'x': _ONE, 'q': [trace.UNKNOWN]}})}"
    assert cli.main(["--show-fixes", "--jobs=1", found, str(user)]) == cli.EXIT_FOUND
    assert _SHOWN in capsys.readouterr().out
    assert cli.main(["--fix", "-q", "--jobs=1", found, str(user)]) == cli.EXIT_FOUND
    assert (
        cli.main(["--fix", "-q", "--unsafe-fixes", "--fix-ignore=traced", found, str(user)]) == cli.EXIT_FOUND
    )
    assert user.read_text(encoding="utf-8") == _USER
    assert cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", found, str(user)]) == cli.EXIT_CLEAN
    assert user.read_text(encoding="utf-8") == _USER_FIXED
    # The file's no longer the one traced: a second run has nothing from it, and nothing to do.
    assert cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", found, str(user)]) == cli.EXIT_CLEAN


def test_pyproject_names_the_trace(tmp_path: Path) -> None:
    """`infer-from`, a path relative to the `pyproject.toml`."""
    _ = (tmp_path / "pyproject.toml").write_text(
        '[tool.constricter]\ninfer-from = "local/trace.json"\n',
        encoding="utf-8",
        newline="\n",
    )
    assert config.config_defaults(tmp_path) == {"infer_from": str(tmp_path / "local" / "trace.json")}


def test_a_traced_run_types_what_it_ran(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The recorder's file, read back: a script's own class needs no import."""
    script: Path = tmp_path / "script.py"
    source: str = """
        class Row:
            pass


        def f(make):
            row = make()
            rows = [row]
            return rows


        f(Row)
    """
    _ = script.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", [*sys.argv])
    monkeypatch.setattr(sys, "path", [*sys.path])
    assert trace.main([script.name]) == 0
    assert cli.main(
        ["--fix", "-q", "--unsafe-fixes", "--jobs=1", f"--infer-from={trace.DEFAULT}", script.name],
    ) == (cli.EXIT_CLEAN)
    fixed: list[str] = script.read_text(encoding="utf-8").splitlines()
    assert [line for line in fixed if line.startswith("    row")] == [
        "    row: Row = make()",
        "    rows: list[Row] = [row]",
    ]
