# SPDX-License-Identifier: MIT
"""`--infer-with`: the language-server conversation, and the command's rounds of fixes with hints."""

import contextlib
import io
import json
import os
import runpy
import shutil
import signal
import subprocess
import sys
import textwrap
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

import pytest

from constricter.cli import command as cli
from constricter.cli import guard, hints
from constricter.cli.options import Options
from constricter.fix.known import Hints

_FAKE: Final = Path(__file__).with_name("fake_server.py")
_Found: TypeAlias = dict[Path, tuple[Hints, ...]]
_Asks: TypeAlias = Callable[[hints.Session, Mapping[Path, str]], _Found]
_CHECKER: Final = "basedpyright"
_STATUS: Final = 3  # a server's exit status, passed on
_WINDOWS: Final = "win32"
_READY: Final = b"ready\n"
_ZOMBIE: Final = "zombie"


def _runs(*argv: str) -> Callable[[str], list[str]]:
    """Make a stand-in for `hints.command` that runs `argv` for every checker.

    Returns:
      It.

    """

    def command(_checker: str) -> list[str]:
        return list(argv)

    return command


def _fake(monkeypatch: pytest.MonkeyPatch, *behaviours: str) -> None:
    """Make every checker the fake server, behaving as `behaviours` say."""
    monkeypatch.setattr(hints, "command", _runs(sys.executable, str(_FAKE), *behaviours))
    monkeypatch.setattr(hints, "_TIMEOUT", 5.0)
    monkeypatch.setattr(guard, "GRACE", 0.5)
    monkeypatch.setattr(hints, "_POLL", 0.05)


def _session_hints(tmp_path: Path, text: str) -> Hints:
    """Ask a session for one file's hints.

    Returns:
      Them.

    """
    path: Path = tmp_path / "hinted.py"
    session: hints.Session
    with hints.Session([_CHECKER], tmp_path) as session:
        return session.hints({path: text})[path][0]


def test_a_hint_is_keyed_by_where_its_name_ends(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A position in UTF-16 code units becomes `ast`'s UTF-8 byte column, past any wide character."""
    _fake(monkeypatch, "ask", "past-end")
    text: str = 's = "😀é"; x = 1  # hint: int\ny = 2  # parts: list[str]\nz = 3  # kinds: bytes\n'
    found: Hints = _session_hints(tmp_path, text)
    assert found.checker == _CHECKER
    assert found.types == {
        (1, len('s = "😀é"; x'.encode())): "int",
        (2, 1): "list[str]",
        (3, 1): "bytes",
    }


def test_utf8_positions_are_taken_as_they_are(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A server that negotiates UTF-8 positions counts bytes already."""
    _fake(monkeypatch, "utf-8")
    text: str = 's = "😀"; x = 1  # hint: int\n'
    assert _session_hints(tmp_path, text).types == {(1, len('s = "😀"; x'.encode())): "int"}


def test_a_file_asked_about_again_is_changed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """The second time a file is asked about, its new text replaces the old: its hints follow it."""
    _fake(monkeypatch)
    path: Path = tmp_path / "again.py"
    session: hints.Session
    with hints.Session([_CHECKER], tmp_path) as session:
        assert session.hints({path: "x = 1  # hint: int\n"})[path][0].types == {(1, 1): "int"}
        assert session.hints({path: "x: int = 1  # hint: int\n"})[path][0].types == {}


@pytest.mark.parametrize(
    ("behaviour", "message"),
    [
        ("fail", "failed `textDocument/inlayHint`: it broke"),
        ("exit", "exited while answering `textDocument/inlayHint`"),
        ("silent", "said nothing for 0s while answering `textDocument/inlayHint`"),
        ("truncate", "exited while answering `textDocument/inlayHint`"),
    ],
)
def test_a_failing_server_stops_the_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    behaviour: str,
    message: str,
) -> None:
    """An error, an exit or no answer at all is an error: silently hinting nothing would mislead."""
    _fake(monkeypatch, behaviour)
    monkeypatch.setattr(hints, "_TIMEOUT", 0.5)
    with pytest.raises(hints.HintError, match=message):
        _ = _session_hints(tmp_path, "x = 1  # hint: int\n")


def test_a_server_that_wont_stop_is_killed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A server ignoring `shutdown` is killed once it's had time to answer."""
    _fake(monkeypatch, "stubborn")
    monkeypatch.setattr(hints, "_TIMEOUT", 0.5)
    assert _session_hints(tmp_path, "x = 1  # hint: int\n").types == {(1, 1): "int"}


def test_a_server_that_cant_start_is_an_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A missing executable, or one that can't be run, is an error naming what's needed."""

    def nowhere(*_args: object, **_kwargs: object) -> None:
        return None

    patched: pytest.MonkeyPatch
    with monkeypatch.context() as patched:
        patched.setattr(shutil, "which", nowhere)
        with pytest.raises(hints.HintError, match="needs `basedpyright-langserver`, which isn't installed"):
            _ = hints.Session([_CHECKER], tmp_path)
    monkeypatch.setattr(hints, "command", _runs(str(tmp_path / "missing")))
    with pytest.raises(hints.HintError, match="couldn't be started"):
        _ = _session_hints(tmp_path, "x = 1\n")
    _fake(monkeypatch, "crash")
    with pytest.raises(hints.HintError, match="exited while answering `initialize`"):
        _ = _session_hints(tmp_path, "x = 1\n")
    _fake(monkeypatch, "deaf")
    with pytest.raises(hints.HintError, match="exited while answering `initialize`"):
        _ = _session_hints(tmp_path, "x = 1\n")


def test_a_server_that_closes_its_input_is_an_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Writing to a server that has gone is an error, not a crash."""
    _fake(monkeypatch)
    session: hints.Session
    with hints.Session([_CHECKER], tmp_path) as session:
        _ = session.hints({tmp_path / "one.py": "x = 1\n"})
        running: hints.Connection = session.checkers[0].servers[0]
        running.process.kill()
        _ = running.process.wait()
        with pytest.raises(hints.HintError, match="exited"):
            running.notify("exit", None)


def test_every_checker_is_asked_in_the_order_named(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Each file gets one set of hints per checker, in the order they were named."""
    _fake(monkeypatch)
    path: Path = tmp_path / "both.py"
    session: hints.Session
    with hints.Session(["ty", _CHECKER], tmp_path) as session:
        found: tuple[Hints, ...] = session.hints({path: "x = 1  # hint: int\n"})[path]
    assert [(each.checker, each.types) for each in found] == [
        ("ty", {(1, 1): "int"}),
        (_CHECKER, {(1, 1): "int"}),
    ]


def test_files_are_shared_among_servers_and_stay_with_theirs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Many files are shared among a checker's servers, a file staying with its own the next time.

    `ty` works in parallel itself: it gets one server, whatever `--jobs` says.
    """
    _fake(monkeypatch)
    files: dict[Path, str] = {tmp_path / f"m{n}.py": f"x{n} = 1  # hint: int\n" * (n + 1) for n in range(40)}
    session: hints.Session
    with hints.Session([_CHECKER, "ty"], tmp_path, servers=8) as session:
        found: dict[Path, tuple[Hints, ...]] = session.hints(files)
        pyright: hints.Checker = session.checkers[0]
        first: dict[Path, int] = dict(pyright.assigned)
        some: dict[Path, str] = dict(list(files.items())[:3])
        again: dict[Path, tuple[Hints, ...]] = session.hints(some)
        assert [len(checker.servers) for checker in session.checkers] == [2, 1]
        assert set(first.values()) <= {0, 1}  # whichever was free took each batch
        assert pyright.assigned == first
    assert [len(found[path][0].types) for path in files] == [text.count("\n") for text in files.values()]
    assert again.keys() == some.keys()


def test_the_checker_is_found_beside_this_python(monkeypatch: pytest.MonkeyPatch) -> None:
    """Off `PATH`, the server is looked for beside the interpreter (an unactivated venv's)."""
    seen: list[str | None] = []

    def which(name: str, path: str | None = None) -> str | None:
        seen.append(path)
        return None if path is None else f"{path}/{name}"

    monkeypatch.setattr(shutil, "which", which)
    assert hints.command("ty") == [f"{Path(sys.executable).parent}/ty", "server"]
    assert seen == [None, str(Path(sys.executable).parent)]


def _fixed(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    source: str,
    *options: str,
) -> tuple[int, str, str]:
    """Run the command over one file, with the fake checker's hints.

    Returns:
      Its exit status, its output, and the file's text afterwards.

    """
    path: Path = tmp_path / "module.py"
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    status: int = cli.main(["--infer-with", _CHECKER, "--level=suffocate", *options, str(path)])
    return status, capsys.readouterr().out, path.read_text(encoding="utf-8")


def test_fix_repeats_while_the_hints_change(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Fixing changes what a checker infers: a file a round changed is asked about and fixed again.

    `b`'s hint comes only once the file has changed, as a checker's can once `a` is annotated: the
    second round fixes it, the third changes nothing, and the rounds stop.
    """
    _fake(monkeypatch)
    source: str = """
    def f(q) -> None:
        a = q.make()  # hint: int
        b = a.thing()  # round 2: str
        c = q.other()  # hint: Box
    """
    status: int
    output: str
    text: str
    status, output, text = _fixed(tmp_path, capsys, source, "--fix", "--unsafe-fixes", "-q")
    assert status == cli.EXIT_FOUND
    left: str = "LVA001 local variable 'c'"  # `Box` means nothing in this file: never used
    assert left in output
    fixed: list[str] = ["    a: int = q.make()  # hint: int", "    b: str = a.thing()  # round 2: str"]
    assert text.splitlines()[2:4] == fixed


def test_fix_stops_after_its_last_round(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """However long the hints keep changing, a file is fixed at most four times; checked together.

    Every round's hints bring another fix here: the fifth's is left, reported.
    """
    _fake(monkeypatch)
    source: str = "".join(f"def f{n}(q) -> None:\n    x = q()  # round {n}: int\n" for n in range(1, 6))
    paths: list[Path] = [tmp_path / "one.py", tmp_path / "two.py"]
    path: Path
    for path in paths:
        _ = path.write_text(source, encoding="utf-8")
    options: list[str] = ["--infer-with", _CHECKER, "--fix", "--unsafe-fixes", "--jobs=2", "-q"]
    assert cli.main([*options, *[str(path) for path in paths]]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.count("LVA001") == len(paths)
    for path in paths:
        assert path.read_text(encoding="utf-8").count("x: int = q()") == cli.HINT_ROUNDS


def test_hints_are_guesses_only_unsafe_fixes_apply(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A hint's fix is a guess: `--show-fixes` names the checker, and plain `--fix` leaves it."""
    _fake(monkeypatch)
    source: str = "def f(q) -> None:\n    a = q.make()  # hint: int\n"
    output: str
    text: str
    shown: str = "fix 'a': `int`, from basedpyright's inferred type [checker] (a guess: --unsafe-fixes)"
    _, output, text = _fixed(tmp_path, capsys, source, "--show-fixes")
    assert shown in output
    _, _, text = _fixed(tmp_path, capsys, source, "--fix", "-q")
    assert text == source
    added: str = "+    a: int = q.make()  # hint: int"
    _, output, _ = _fixed(tmp_path, capsys, source, "--diff", "--unsafe-fixes")
    assert added in output


def test_a_failing_checker_is_the_commands_error(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The checker's failure is reported, and the run exits 2."""
    _fake(monkeypatch, "fail")
    path: Path = tmp_path / "module.py"
    _ = path.write_text("x = 1\n", encoding="utf-8")
    assert cli.main(["--infer-with", _CHECKER, str(path)]) == cli.EXIT_ERROR
    expected: str = (
        f"constricter: error: {Path(sys.executable).name} failed `textDocument/inlayHint`: it broke\n"
    )
    assert capsys.readouterr().err == expected


def test_only_files_it_can_read_are_asked_about(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A notebook, standard input, or a file that can't be decoded isn't sent to the checker."""
    asked: list[Path] = []
    monkeypatch.setattr(hints, "command", _runs(sys.executable, str(_FAKE)))
    original: _Asks = hints.Session.hints

    def recorded(self: hints.Session, files: Mapping[Path, str]) -> dict[Path, tuple[Hints, ...]]:
        asked.extend(files)
        return original(self, files)

    monkeypatch.setattr(hints.Session, "hints", recorded)
    notebook: Path = tmp_path / "book.ipynb"
    _ = notebook.write_text(json.dumps({"cells": [], "metadata": {}, "nbformat": 4}), encoding="utf-8")
    broken: Path = tmp_path / "broken.py"
    _ = broken.write_bytes(b"x = '\xff'\n")
    plain: Path = tmp_path / "plain.py"
    _ = plain.write_text("x = 1\n", encoding="utf-8")
    _ = cli.main(["--infer-with", _CHECKER, "-q", str(tmp_path)])
    assert asked == [plain]
    _ = capsys.readouterr()


def test_baseline_and_coverage_dont_ask(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Hints change what `--fix` offers, never what's reported or counted: no checker is started."""
    monkeypatch.setattr(hints, "command", _runs(str(tmp_path / "missing")))
    path: Path = tmp_path / "module.py"
    _ = path.write_text("def f() -> None:\n    x = 1\n", encoding="utf-8")
    assert cli.main(["--infer-with", _CHECKER, "--coverage", str(path)]) == cli.EXIT_CLEAN
    baseline: Path = tmp_path / "baseline.json"
    assert (
        cli.main(["--infer-with", _CHECKER, "--write-baseline", "--baseline", str(baseline), str(path)]) == 0
    )
    _ = capsys.readouterr()


def test_infer_with_is_a_setting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`infer-with` in `[tool.constricter]` names a checker; anything else is an error."""
    monkeypatch.chdir(tmp_path)
    pyproject: Path = tmp_path / "pyproject.toml"
    checker: str = "ty"
    _ = pyproject.write_text(f'[tool.constricter]\ninfer-with = "{checker}"\n', encoding="utf-8")
    assert Options.parse([]).infer_with == (checker,)
    _ = pyproject.write_text('[tool.constricter]\ninfer-with = ["ty", "basedpyright"]\n', encoding="utf-8")
    assert Options.parse([]).infer_with == (checker, _CHECKER)
    assert Options.parse(["--infer-with", "basedpyright, ty,basedpyright"]).infer_with == (_CHECKER, checker)
    wrong: str
    for wrong in ('"mypy"', '["ty", "mypy"]', "[]", "1"):
        _ = pyproject.write_text(f"[tool.constricter]\ninfer-with = {wrong}\n", encoding="utf-8")
        with pytest.raises(SystemExit):
            _ = Options.parse([])
    pyproject.unlink()
    with pytest.raises(SystemExit):
        _ = Options.parse(["--infer-with", "ty,mypy"])


@pytest.mark.skipif(shutil.which("basedpyright-langserver") is None, reason="basedpyright isn't installed")
def test_basedpyright_types_what_constricter_cant(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The real thing: basedpyright's hints type a stat result, and a literal union, widened."""
    monkeypatch.chdir(tmp_path)
    source: str = """
    import os


    def f(p: str, n: int) -> None:
        u = os.stat(p)
        m = None if n else 1
    """
    output: str
    text: str
    _, output, text = _fixed(tmp_path, capsys, source, "--fix", "--unsafe-fixes", "-q")
    assert not output
    fixed: list[str] = ["    u: os.stat_result = os.stat(p)", "    m: int | None = None if n else 1"]
    assert text.splitlines()[-2:] == fixed


@pytest.mark.skipif(sys.platform == _WINDOWS, reason="a process is looked for by its id, with a POSIX signal")
def test_a_server_goes_when_constricter_is_killed(tmp_path: Path) -> None:
    """Killed outright, constricter can shut nothing down: the guard kills a server that would stay."""
    pid_file: Path = tmp_path / "server.pid"
    program: str = textwrap.dedent(
        f"""
        import sys, time
        from pathlib import Path
        from constricter.cli import guard, hints
        guard.GRACE = 0.5
        hints.command = lambda _checker: [sys.executable, {str(_FAKE)!r}, "clingy"]
        with hints.Session(["ty"], Path({str(tmp_path)!r})) as session:
            session.hints({{Path({str(tmp_path / "x.py")!r}): "x = 1\\n"}})
            print("ready", flush=True)
            time.sleep(60)
        """,
    )
    environment: dict[str, str] = {**os.environ, "FAKE_SERVER_PID": str(pid_file)}
    running: subprocess.Popen[bytes]
    with subprocess.Popen(
        [sys.executable, "-c", program],
        stdout=subprocess.PIPE,
        env=environment,
    ) as running:
        output: IO[bytes] = cast("IO[bytes]", running.stdout)
        assert output.readline() == _READY
        server: int = int(pid_file.read_text(encoding="utf-8"))
        running.kill()
    assert _gone(server)


def _gone(pid: int) -> bool:
    """Wait (twenty seconds at most) for process `pid` to go.

    Returns:
      Whether it went.

    """
    _: int
    for _ in range(200):
        if not _alive(pid):
            return True
        time.sleep(0.1)
    return False


def _alive(pid: int) -> bool:
    """Check whether process `pid` is running (not merely a zombie waiting for its parent).

    Returns:
      Whether it is.

    """
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    status: Path = Path(f"/proc/{pid}/status")
    try:
        return _ZOMBIE not in status.read_text(encoding="utf-8")
    except ProcessLookupError:  # gone while it was read
        return False
    except FileNotFoundError:  # gone just now (Linux), or there's no `/proc` (macOS): it's running
        return not status.parent.parent.is_dir()


def test_the_guard_passes_input_on_and_returns_the_servers_status() -> None:
    """A server that exits when its input ends does, with its own status."""
    output: io.BytesIO = io.BytesIO()
    echo: str = (
        "import sys; data = sys.stdin.buffer.read(); sys.stdout.buffer.write(data); sys.exit(len(data))"
    )
    sent: bytes = b"abc"
    assert guard.main(["5", sys.executable, "-c", echo], io.BytesIO(sent), output) == len(sent)
    assert output.getvalue() == sent


def test_the_guard_kills_a_server_that_stays() -> None:
    """A server still running a grace period after its input ends is killed."""
    script: str = "import sys, time; sys.stdin.read(); time.sleep(60)"
    assert guard.main(["0.2", sys.executable, "-c", script], io.BytesIO(b"")) != 0


def test_the_guard_stops_passing_input_to_a_server_that_has_gone() -> None:
    """Input for a server that has exited is dropped, not an error."""
    server: subprocess.Popen[bytes]
    with subprocess.Popen([sys.executable, "-c", "pass"], stdin=subprocess.PIPE) as server:
        _ = server.wait()
        guard.relay_to(io.BytesIO(b"x" * (1 << 20)), server, 1.0)
        given: IO[bytes] = cast("IO[bytes]", server.stdin)
        assert given.closed


def test_the_guard_runs_as_a_module(monkeypatch: pytest.MonkeyPatch) -> None:
    """`python -m constricter.cli.guard` exits with the server's status, ignoring interrupts."""
    monkeypatch.setattr(sys, "argv", ["guard", "5", sys.executable, "-c", f"raise SystemExit({_STATUS})"])
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b""), encoding="utf-8"))
    monkeypatch.delitem(sys.modules, guard.__name__)  # run afresh, as `-m` does
    ignored: list[int] = []

    def handle(number: int, handler: object) -> None:
        if handler is signal.SIG_IGN:
            ignored.append(number)

    monkeypatch.setattr(signal, "signal", handle)
    exited: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exited:
        _ = runpy.run_module(guard.__name__, run_name="__main__")
    assert exited.value.code == _STATUS
    assert ignored == [signal.SIGINT]


def test_a_guard_that_wont_exit_is_killed(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A server that ignores every request, and a guard still giving it its grace: the guard is killed.

    That leaves the server (its input ended): the last resort, when shutting down takes too long.
    """
    _fake(monkeypatch, "stubborn", "clingy")
    monkeypatch.setattr(guard, "GRACE", 30.0)  # the guard's, as it's started
    pid_file: Path = tmp_path / "server.pid"
    monkeypatch.setenv("FAKE_SERVER_PID", str(pid_file))
    session: hints.Session
    with hints.Session(["ty"], tmp_path) as session:
        _ = session.hints({tmp_path / "x.py": "x = 1\n"})
        running: hints.Connection = session.checkers[0].servers[0]
        monkeypatch.setattr(guard, "GRACE", 0.1)  # constricter's wait for it, as it's shut down
        monkeypatch.setattr(hints, "_TIMEOUT", 0.2)
    assert running.process.returncode != 0
    with contextlib.suppress(ProcessLookupError):  # it may have gone already, its output broken
        os.kill(int(pid_file.read_text(encoding="utf-8")), signal.SIGTERM)


def test_answers_that_come_out_of_order_are_kept(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A server may answer a later request first: that answer waits for its turn."""
    _fake(monkeypatch, "swap")
    monkeypatch.setattr(hints, "_BATCH", 1)  # a batch each: the second's asked before the first's answered
    files: dict[Path, str] = {
        tmp_path / "a.py": "a = 1  # hint: int\n",
        tmp_path / "b.py": "b = 1  # hint: str\n",
    }
    session: hints.Session
    with hints.Session([_CHECKER], tmp_path) as session:
        found: dict[Path, tuple[Hints, ...]] = session.hints(files)
    assert [found[path][0].types for path in files] == [{(1, 1): "int"}, {(1, 1): "str"}]


@pytest.mark.parametrize(
    ("asked", "available", "budget"),
    [
        (None, 64 << 30, hints.MEMORY),  # the default, where there's plenty
        (None, 6 << 30, 3 << 30),  # half what's available, where that's less
        (None, None, 0),  # nothing known: one server
        (32 << 30, 64 << 30, 32 << 30),  # asked for, and there
        (32 << 30, 16 << 30, 16 << 30),  # asked for, but only what's there
        (32 << 30, None, 32 << 30),
    ],
)
def test_a_checkers_memory_is_asked_for_or_a_sensible_share(
    asked: int | None,
    available: int | None,
    budget: int,
) -> None:
    """`--infer-memory`, within what's available; by default 8 GB, within half of it."""
    assert hints.budget(asked, available) == budget


def test_servers_are_as_many_as_fit_in_memory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Big files take more memory a server: fewer of them fit, but one always does."""
    monkeypatch.setattr(hints, "available_memory", lambda: 64 << 30)
    small: dict[Path, str] = {tmp_path / f"m{n}.py": "x = 1\n" for n in range(200)}
    big: dict[Path, str] = {tmp_path / f"m{n}.py": "x" * (1 << 20) for n in range(200)}  # 200 MB of files
    checker: hints.Checker = hints.Checker(_CHECKER, tmp_path, 8, 8 << 30)
    assert [checker.wanted(small), checker.wanted(big)] == [4, 1]
    assert hints.Checker(_CHECKER, tmp_path, 8, 1 << 20).wanted(small) == 1


def test_available_memory_is_what_the_system_says(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Linux's `MemAvailable`; elsewhere half of all the memory there is; or nothing known."""
    meminfo: Path = tmp_path / "meminfo"
    _ = meminfo.write_text("MemTotal: 4000 kB\nMemAvailable: 3000 kB\n", encoding="ascii")
    monkeypatch.setattr(hints, "_MEMINFO", meminfo)
    assert hints.available_memory() == 3000 * 1024
    monkeypatch.setattr(hints, "_MEMINFO", tmp_path / "missing")
    sizes: dict[str, int] = {"SC_PHYS_PAGES": 1000, "SC_PAGE_SIZE": 4096}
    monkeypatch.setattr(os, "sysconf", sizes.__getitem__, raising=False)
    assert hints.available_memory() == 1000 * 4096 // 2
    monkeypatch.delattr(os, "sysconf", raising=False)
    assert hints.available_memory() is None


@pytest.mark.skipif(sys.platform == _WINDOWS, reason="a process group is POSIX's")
def test_the_guard_kills_what_the_server_started_too() -> None:
    """What a server started goes with it (a venv's `basedpyright-langserver` starts `node`)."""
    script: str = textwrap.dedent(
        """
        import subprocess, sys, time
        child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
        sys.stdout.write(f"{child.pid}\\n")
        sys.stdout.flush()
        sys.stdin.read()
        time.sleep(60)
        """,
    )
    output: io.BytesIO = io.BytesIO()
    assert guard.main(["0.2", sys.executable, "-c", script], io.BytesIO(b""), output) != 0
    assert _gone(int(output.getvalue()))


def test_without_process_groups_the_guard_kills_the_server(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where there are no process groups to kill (Windows), the server itself is killed."""
    monkeypatch.delattr(os, "killpg", raising=False)
    script: str = "import sys, time; sys.stdin.read(); time.sleep(60)"
    assert guard.main(["0.2", sys.executable, "-c", script], io.BytesIO(b"")) != 0


def test_a_server_already_gone_is_not_an_error() -> None:
    """Killing a server whose process group has gone already does nothing."""
    server: subprocess.Popen[bytes]
    with subprocess.Popen([sys.executable, "-c", "pass"], start_new_session=True) as server:
        _ = server.wait()
        guard.kill(server)


def test_a_server_reporting_progress_is_waited_for(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """A server that takes longer than the timeout to answer, but reports its progress, isn't hung."""
    _fake(monkeypatch, "slow")
    monkeypatch.setattr(hints, "_TIMEOUT", 0.3)
    assert _session_hints(tmp_path, "x = 1  # hint: int\n").types == {(1, 1): "int"}


def test_infer_memory_is_an_option_and_a_setting(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`--infer-memory GB` (`infer-memory`): what each checker's servers may use; a positive number."""
    monkeypatch.chdir(tmp_path)
    assert Options.parse([]).infer_memory is None
    assert Options.parse(["--infer-memory", "1.5"]).infer_memory == 3 << 29
    pyproject: Path = tmp_path / "pyproject.toml"
    _ = pyproject.write_text("[tool.constricter]\ninfer-memory = 32\n", encoding="utf-8")
    assert Options.parse([]).infer_memory == 32 << 30
    wrong: str
    for wrong in ("0", "-2", "lots"):
        with pytest.raises(SystemExit):
            _ = Options.parse(["--infer-memory", wrong])
    for wrong in ("0", "true", '"32"'):
        _ = pyproject.write_text(f"[tool.constricter]\ninfer-memory = {wrong}\n", encoding="utf-8")
        with pytest.raises(SystemExit):
            _ = Options.parse([])
