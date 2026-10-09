# SPDX-License-Identifier: MIT
"""`--infer-from`: a traced run's types (`python -m constricter.trace`), as hints `--fix` guesses with."""

import ast
import hashlib
import json
import sys
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

import pytest

from constricter import recording, trace
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
    match typed:
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
    inner = param.inner
    stack = param.stack
    half = param.half
    if param:
        half = param.other
    varied = param.varied
    varied = param.more
    counted = param.count
    counted += 1
    for left, right in param.pairs:
        pass
    with param.open() as handle:
        handle = param.handle
    return once


def untraced(param):
    x = param.x
    return x


def checked(listed, sized=1, maybe=None, again=None, matched=None, sure=None, *, keyed=",", fine=None):
    if isinstance(listed, list):
        firstly = listed[0]
    width = sized.real
    innermost = maybe.inner
    again = again or []
    copied = again.copy()
    match matched:
        case _:
            pass
    subject = matched.name
    assert sure is None or known(kind=sure)
    surely = sure.name
    stripped = keyed.strip()
    okay = fine.name
    return okay


class Holder:
    kept = None

    def __init__(self, given, typed: int, *rest):
        self.given = given
        self.rest = rest
        self.typed = typed
        self.kept = given
        self.literal = 1
        self.added = given
        self.added += 1
        self.first, self.second = given
        self.dropped = given
        self.late: int = given

    def read(self, other):
        taken = self.given
        through = self.rest[0].child()
        for member in self.given:
            pass
        numbered = self.typed
        bodied = self.kept
        lettered = self.literal
        summed = self.added
        unpacked = self.first
        gone = self.dropped
        del self.dropped
        annotated = self.late
        called = self.read(other)
        absent = self.absent
        indexed = self[0]
        theirs = other.given
        return taken

    @staticmethod
    def apart(given):
        self = given
        loose = self.given
        return loose


class Based(Holder):
    def __init__(self, given):
        self.own = given

    def read(self, other):
        based = self.own
        return based


def free(self):
    outside = self.given
    return outside
"""
_ONE: Final = ["int"]
# What each name's bindings held, but those of `_LINES`.
_HELD: Final = {
    **dict.fromkeys(
        (
            *("once", "twice", "looped", "inside", "spun", "shared", "late", "caught", "starred"),
            *("mapped", "captured", "nested", "each", "made", "declared", "mine"),
            *("firstly", "width", "innermost", "again", "copied", "subject", "surely", "stripped", "okay"),
            *("both", "also", "again", "half", "varied", "counted", "left", "right", "handle"),
            *("taken", "through", "member", "numbered", "bodied", "lettered", "summed", "unpacked"),
            *("gone", "annotated", "called", "absent", "indexed", "theirs", "loose", "based", "outside"),
        ),
        _ONE,
    ),
    "total": ["list[int]"],
    "own": ["m:Local"],
    "other": ["pkg.things:Thing"],
    "maybe": ["None", "pkg.things:Thing"],
    "unknown": ["int", recording.UNKNOWN],
    "many": ["bytes", "float", "int", "str"],
    "private": ["_thread:lock"],
    "clash": ["a:Thing", "b:Thing"],
    "inner": ["pkg.things:Outer.Inner"],
    "stack": ["pkg.things:Stack[int]"],
}
# What the bindings on these lines held: one never reached, and one of another type.
_LINES: Final = {"        half = param.other": [], "    varied = param.more": ["str"]}
_IMPORT: Final = ("from pkg.things import Thing",)
_USER: Final = "def f(q):\n    x = q.make()\n    return x\n"
_USER_FIXED: Final = "def f(q):\n    x: int = q.make()\n    return x\n"
_TRACE: Final = "trace.json"
_REFUSED: Final = f"{_TRACE}: "  # how a refusal names the file
_Bindings: TypeAlias = dict[int, dict[str, list[str]]]  # each binding's spellings, by its line and name
_ANNOTATED: Final = ": "  # in a line that declares a name
_SHOWN: Final = "fix 'x': `int`, from what a traced run bound it to [traced] (a guess: --unsafe-fixes)"


def _digest(source: str) -> str:
    return hashlib.sha256(source.encode()).hexdigest()


def _trace(source: str, bindings: _Bindings, *, local: str = "m") -> traced.Trace:
    """Make the trace of a file holding `source`, the module `local` to those who name its classes.

    Returns:
      It.

    """
    return traced.Trace(
        {
            _digest(source): {
                line: {name: tuple(types) for name, types in held.items()} for line, held in bindings.items()
            },
        },
        {local: _digest(source)},
    )


def _seen(source: str, held: dict[str, list[str]], lines: dict[str, list[str]]) -> _Bindings:
    """Make the bindings a run of `source` would note: each by what its name `held`, or its line of `lines`.

    Returns:
      Them, by line and name.

    """
    texts: list[str] = source.splitlines()
    found: _Bindings = {}
    node: ast.AST
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            types: list[str]
            if types := lines.get(texts[node.lineno - 1], held.get(node.id, [])):
                found.setdefault(node.lineno, {})[node.id] = types
    return found


def _written(path: Path, source: str, bindings: _Bindings) -> Path:
    """Write the trace file of a file holding `source` to `path`.

    Returns:
      `path`.

    """
    _ = path.write_text(
        json.dumps(
            {
                "version": recording.VERSION,
                "files": {
                    _digest(source): {
                        "path": "user.py",
                        "bindings": {str(line): held for line, held in bindings.items()},
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


def test_a_local_has_what_its_bindings_held() -> None:
    """One an assignment or a loop takes from an unannotated parameter, wherever the run reached each.

    Or from an attribute of `self` no checker types.
    """
    found: Hints | None = traced.hints(_trace(_SOURCE, _seen(_SOURCE, _HELD, _LINES)), _SOURCE.encode())
    assert found is not None
    assert (found.checker, found.kind) == ("a traced run", "traced")
    assert _named(_SOURCE, found) == {
        "once": ("int", ()),
        "twice": ("int", ()),
        "looped": ("int", ()),
        "spun": ("int", ()),
        "nested": ("int", ()),
        "varied": ("int | str", ()),
        "inner": ("Outer.Inner", ("from pkg.things import Outer",)),  # by the class it's defined in
        "stack": ("Stack[int]", ("from pkg.things import Stack",)),
        # What's taken from an attribute its class, of no base, stores only unannotated parameters in.
        "taken": ("int", ()),
        "through": ("int", ()),
        "member": ("int", ()),
        "theirs": ("int", ()),  # from a parameter, as ever
        # Not from a parameter a checker types: by its default, a test of it, or what it's bound to again.
        "innermost": ("int", ()),
        "okay": ("int", ()),
        "own": ("Local", ()),  # the file's own class: no import
        "other": ("Thing", _IMPORT),
        "maybe": ("Thing | None", _IMPORT),
    }


def test_a_file_the_trace_doesnt_have_has_no_hints() -> None:
    """One edited since, one that doesn't parse, and one whose functions bind nothing it saw."""
    found: traced.Trace = _trace(_SOURCE, _seen(_SOURCE, _HELD, _LINES))
    assert traced.hints(found, _SOURCE.encode() + b"\n") is None
    assert traced.hints(_trace("def (", {1: {"x": _ONE}}), b"def (") is None
    assert traced.hints(_trace(_SOURCE, _seen(_SOURCE, {"listed": _ONE}, {})), _SOURCE.encode()) is None


def test_a_trace_file_is_read_leniently(tmp_path: Path) -> None:
    """What isn't as the recorder writes it is skipped."""
    path: Path = tmp_path / _TRACE
    _ = path.write_text(
        json.dumps(
            {
                "version": recording.VERSION,
                "files": {"d": {"bindings": {"3": {"x": _ONE, "y": "int"}, "three": {"z": _ONE}}}, "e": []},
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
        _trace(_USER, {2: {"x": _ONE}}),
        [user, other, tmp_path / "notebook.ipynb", tmp_path / "missing.py"],
    )
    assert list(found) == [user]
    assert found[user][0] is checker
    assert found[user][1].types == {(2, 5): "int"}


def test_fix_guesses_with_a_trace(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """With `--unsafe-fixes`, as kind `traced`, which `fix-ignore` leaves out."""
    user: Path = tmp_path / "user.py"
    _ = user.write_text(_USER, encoding="utf-8", newline="\n")
    found: str = f"--infer-from={_written(tmp_path / _TRACE, _USER, {2: {'x': _ONE}})}"
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
    """The recorder's file, read back: a script's own class needs no import, and a loop's target is typed."""
    script: Path = tmp_path / "script.py"
    source: str = """
        class Row:
            pass


        def f(make, items):
            row = make()
            rows = [row]
            for item in items:
                last = item
            return rows, last


        f(Row, [Row()])
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
    assert [line.strip() for line in fixed if _ANNOTATED in line] == [
        "row: Row = make()",
        "rows: list[Row] = [row]",
        "item: Row",
        "last: Row = item",
    ]
