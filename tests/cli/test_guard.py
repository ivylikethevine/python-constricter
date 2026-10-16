# SPDX-License-Identifier: MIT
"""`constricter.cli.guard`: a type checker's server, and what it started, stopped when constricter goes."""

import io
import os
import runpy
import signal
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import IO, Final, cast

import pytest

from constricter.cli import guard
from tests.cli.sources import FAKE_SERVER

_STATUS: Final = 3  # a server's exit status, passed on


_WINDOWS: Final = "win32"
_READY: Final = b"ready\n"
_ZOMBIE: Final = "zombie"


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
        hints.command = lambda _checker: [sys.executable, {str(FAKE_SERVER)!r}, "clingy"]
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


def test_a_process_group_is_killed_where_there_are_groups(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where there are process groups (POSIX), the server's is killed; one already gone is fine."""
    killed: list[tuple[int, int]] = []

    def killpg(group: int, number: int) -> None:
        killed.append((group, number))
        raise ProcessLookupError

    monkeypatch.setattr(os, "killpg", killpg, raising=False)
    monkeypatch.setattr(signal, "SIGKILL", 9, raising=False)
    server: subprocess.Popen[bytes]
    with subprocess.Popen([sys.executable, "-c", "pass"]) as server:
        _ = server.wait()
        guard.kill(server)
    assert killed == [(server.pid, 9)]
