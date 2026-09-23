# SPDX-License-Identifier: MIT
"""Run a type checker's language server for `--infer-with`, so it can't outlive constricter.

  python .../constricter/cli/guard.py GRACE EXECUTABLE [ARGUMENT ...]

It imports only the standard library, so it runs by its path whatever the Python can import.

The server's input and output both come through here, so that only this holds constricter's end of
them: if this is killed, constricter's reading ends at once, and the server's input and output are
gone. When constricter's input ends, constricter has closed it or is gone (however it went: killed
outright too, when it can't shut anything down itself), and the server is given GRACE seconds to
exit as it's been asked to, then killed. A server doesn't always notice on its own: one waiting for
an answer from constricter reads nothing more, and would wait forever. This exits with the
server's status.
"""

import contextlib
import os
import signal
import subprocess  # the language server
import sys
import threading
from collections.abc import Callable, Sequence
from typing import IO, Final, cast

GRACE: Final = 5.0  # seconds a server has to exit once its input ends, by default
_CHUNK: Final = 1 << 16


def main(argv: Sequence[str], stdin: IO[bytes] | None = None, stdout: IO[bytes] | None = None) -> int:
    """Run the server (`argv`: the grace, then its command), between `stdin` and `stdout` (this process's).

    Returns:
      The server's exit status, once all its output is passed on.

    """
    grace: float = float(argv[0])
    server: subprocess.Popen[bytes]
    # Its own process group (POSIX), so it's killed with whatever it starts: a venv's
    # `basedpyright-langserver` is a Python script that starts `node`.
    with subprocess.Popen(
        list(argv[1:]),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        start_new_session=True,
    ) as server:
        relay: threading.Thread = threading.Thread(
            target=relay_to,
            args=(stdin or sys.stdin.buffer, server, grace),
            daemon=True,  # blocked reading a constricter that's still there: it goes when this does
        )
        relay.start()
        output: threading.Thread = threading.Thread(
            target=_pass_on,
            args=(cast("IO[bytes]", server.stdout), stdout or sys.stdout.buffer),
        )
        output.start()
        status: int = server.wait()
        output.join()
        return status


def _pass_on(source: IO[bytes], target: IO[bytes]) -> None:
    """Pass the server's output on until it ends (or constricter's end of it has gone)."""
    chunk: bytes
    with contextlib.suppress(OSError):
        for chunk in iter(lambda: _read(source), b""):
            _write(target, chunk)


def relay_to(source: IO[bytes], server: "subprocess.Popen[bytes]", grace: float) -> None:
    """Pass `source` on to the server's input; when it ends, end the server's, and give it `grace` seconds."""
    target: IO[bytes] = cast("IO[bytes]", server.stdin)
    chunk: bytes
    # The server has gone (or this is exiting, its input closed): nothing more to pass on.
    with contextlib.suppress(OSError, ValueError):
        for chunk in iter(lambda: _read(source), b""):
            _write(target, chunk)
    with contextlib.suppress(OSError):  # what's left for a server that has gone is dropped
        target.close()
    try:
        _ = server.wait(timeout=grace)
    except subprocess.TimeoutExpired:
        kill(server)


def kill(server: "subprocess.Popen[bytes]") -> None:
    """Kill the server and everything it started: its process group (POSIX), else the server itself."""
    killpg: Callable[[int, int], None] | None
    if (killpg := getattr(os, "killpg", None)) is None:  # Windows: only what's started directly
        server.kill()
        return
    with contextlib.suppress(ProcessLookupError):  # it has gone, with all it started
        killpg(server.pid, signal.SIGKILL)


def _write(target: IO[bytes], chunk: bytes) -> None:
    """Write `chunk`, now."""
    _ = target.write(chunk)
    target.flush()


def _read(source: IO[bytes]) -> bytes:
    """Read what's there of `source`, as soon as there's any.

    Returns:
      It, or nothing at its end.

    """
    return cast("IO[bytes]", getattr(source, "raw", source)).read(_CHUNK) or b""


if __name__ == "__main__":
    # Interrupted at a terminal, the whole group is: constricter shuts the server down itself.
    _ = signal.signal(signal.SIGINT, signal.SIG_IGN)
    sys.exit(main(sys.argv[1:]))
