# SPDX-License-Identifier: MIT
"""A fake language server for `--infer-with`'s tests: it hints what a file's comments say.

  python tests/cli/fake_server.py [BEHAVIOUR ...]

A line `name = value  # hint: T` gets a variable-type hint `: T` after `name` (the last on the line,
after a `; `), as long as `name` is unannotated (so fixing it ends its hint, as a real checker's
does); `# parts: T` gives the label as parts; `# kinds: T` adds a parameter-name hint and a
return-type one, which `--infer-with` ignores; `# round N: T` hints only from the file's Nth version
(as a checker's view changes, as a file is annotated). Positions count UTF-16 code units, or UTF-8
bytes with the `utf-8` behaviour.

Behaviours: `utf-8` (it negotiates UTF-8 positions), `ask` (before answering `initialize`, it asks
for its settings, registers a capability and asks something the client can't answer, and logs a
message), `past-end` (it also hints a line past the file's end), `crash` (it exits when asked to
initialize), `deaf` (asked to initialize, it stops reading, asks for its settings and exits),
`fail` (it answers the hint request with an error), `exit` (it exits when asked for hints),
`silent` (it never answers the hint request), `stubborn` (it ignores `shutdown` and `exit`),
`clingy` (it stays, whatever it's told, even once its input ends), `truncate` (asked for hints, it
writes half an answer and exits), `swap` (it answers each pair of hint requests second first),
`slow` (it reports its progress for a second before each answer), `modified` (it drops each file's
first hint request as ty does, "content modified"), `always-modified` (it drops every one). With
`FAKE_SERVER_PID` set, it writes its process id to that file first.
"""

import json
import os
import re
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

_Json: TypeAlias = dict[str, "_Json"] | list["_Json"] | str | int | float | bool | None
_Object: TypeAlias = dict[str, _Json]

# The name bound last on the line: at its start, or after a `; `.
_HINTED: Final = re.compile(r"^((?:.*; )?\s*)(\w+) = .*#\s*(hint|parts|kinds|round \d+): (.+)$")
_BEHAVIOURS: Final = frozenset(sys.argv[1:])
_UTF8: Final = "utf-8"
_PARTS: Final = "parts"
_KINDS: Final = "kinds"
_ROUND: Final = "round "
_HEADERS_END: Final = b"\r\n"
_PAST_END: Final = "past-end"
_CRASH: Final = "crash"
_DEAF: Final = "deaf"
_CLINGY: Final = "clingy"
_TRUNCATE: Final = "truncate"
_SWAP: Final = "swap"
_SLOW: Final = "slow"
_LINGER: Final = 60.0  # seconds a clingy server stays: far longer than any test waits
_ASK: Final = "ask"
_EXIT: Final = "exit"
_FAIL: Final = "fail"
_SILENT: Final = "silent"
_STUBBORN: Final = "stubborn"
_MODIFIED: Final = "modified"
_ALWAYS_MODIFIED: Final = "always-modified"
_CONTENT_MODIFIED: Final = -32801


@dataclass
class _Documents:
    """What the client has opened: each file's text and version, by its URI."""

    texts: dict[str, str] = field(default_factory=dict[str, str])
    versions: dict[str, int] = field(default_factory=dict[str, int])
    held: _Object | None = None  # `swap`'s answer, held for the next
    dropped: set[str] = field(default_factory=set[str])  # the files a `modified` server dropped a request for


def _receive(stream: IO[bytes]) -> _Object | None:
    """Read one message.

    Returns:
      It, or `None` at the end of the stream.

    """
    length: int = 0
    line: bytes
    for line in iter(stream.readline, b""):
        if line == _HEADERS_END:
            break
        if line.lower().startswith(b"content-length:"):
            length = int(line.split(b":")[1])
    return cast("_Object", json.loads(stream.read(length))) if length else None


def _send(message: _Object) -> None:
    """Write one message."""
    body: bytes = json.dumps(message).encode()
    _ = sys.stdout.buffer.write(f"Content-Length: {len(body)}\r\n\r\n".encode() + body)
    _ = sys.stdout.buffer.flush()


def _column(text: str) -> int:
    """Count `text` as the negotiated positions do.

    Returns:
      Its length in UTF-8 bytes, or UTF-16 code units.

    """
    return len(text.encode()) if _UTF8 in _BEHAVIOURS else len(text.encode("utf-16-le")) // 2


def _hints(text: str, version: int) -> list[_Json]:
    """Hint what `text`'s comments say, as of its `version`.

    Returns:
      The hints.

    """
    found: list[_Json] = []
    number: int
    line: str
    for number, line in enumerate(text.splitlines()):
        match: re.Match[str] | None = _HINTED.match(line)
        if match is None or (match[3].startswith(_ROUND) and version < int(match[3].removeprefix(_ROUND))):
            continue
        indent: str
        name: str
        how: str
        annotation: str
        indent, name, how, annotation = match.groups()
        position: _Object = {"line": number, "character": _column(indent + name)}
        label: _Json = [{"value": ": "}, {"value": annotation}] if how == _PARTS else f": {annotation}"
        found.append({"position": position, "label": label, "kind": 1})
        if how == _KINDS:
            found.extend(
                [
                    {"position": position, "label": "file=", "kind": 2},
                    {"position": position, "label": "-> None", "kind": 1},
                ],
            )
    if _PAST_END in _BEHAVIOURS:
        found.append({"position": {"line": len(text.splitlines()) + 5, "character": 0}, "label": ": int"})
    return found


def _initialize(message: _Object, _documents: _Documents) -> bool:
    """Answer `initialize`, first asking the client the questions `ask` asks.

    Returns:
      Whether to go on serving: not after a `crash`.

    """
    if _CRASH in _BEHAVIOURS:
        return False
    if _DEAF in _BEHAVIOURS:
        os.close(0)  # the client's answer can't be written: it finds the pipe closed
        _send({"jsonrpc": "2.0", "id": "c", "method": "workspace/configuration", "params": {"items": []}})
        time.sleep(0.5)
        return False
    if _ASK in _BEHAVIOURS:
        items: list[_Json] = [{"section": "basedpyright.analysis"}, {"section": "python"}]
        _send({"jsonrpc": "2.0", "id": "c", "method": "workspace/configuration", "params": {"items": items}})
        _send({"jsonrpc": "2.0", "id": "r", "method": "client/registerCapability", "params": {}})
        _send({"jsonrpc": "2.0", "id": "u", "method": "custom/unknown", "params": {}})
        _send({"jsonrpc": "2.0", "method": "window/logMessage", "params": {"type": 3, "message": "hello"}})
        answers: list[_Object | None] = [_receive(sys.stdin.buffer) for _ in range(3)]
        _ = sys.stderr.write(json.dumps(answers))
    capabilities: _Object = {"inlayHintProvider": True}
    if _UTF8 in _BEHAVIOURS:
        capabilities["positionEncoding"] = _UTF8
    _send({"jsonrpc": "2.0", "id": message["id"], "result": {"capabilities": capabilities}})
    return True


def _opened(message: _Object, documents: _Documents) -> bool:
    """Take a file's first text, or its new one.

    Returns:
      Whether to go on serving: always.

    """
    params: _Object = cast("_Object", message["params"])
    document: _Object = cast("_Object", params["textDocument"])
    uri: str = str(document["uri"])
    changes: list[_Json] = cast("list[_Json]", params.get("contentChanges") or [document])
    documents.texts[uri] = str(cast("_Object", changes[-1])["text"])
    documents.versions[uri] = int(cast("int", document["version"]))
    return True


def _hinted(message: _Object, documents: _Documents) -> bool:
    """Answer a hint request, as the behaviours say.

    Returns:
      Whether to go on serving: not after an `exit`.

    """
    if _EXIT in _BEHAVIOURS:
        return False
    if _TRUNCATE in _BEHAVIOURS:  # half a message, then gone
        _ = sys.stdout.buffer.write(b'Content-Length: 100\r\n\r\n{"jsonrpc": "2.0", "id": ')
        _ = sys.stdout.buffer.flush()
        return False
    if _SLOW in _BEHAVIOURS:  # a second's work, reporting its progress, before answering
        for _ in range(10):
            _send(
                {
                    "jsonrpc": "2.0",
                    "method": "$/progress",
                    "params": {"token": 1, "value": {"kind": "report"}},
                },
            )
            time.sleep(0.1)
    uri: str = str(cast("_Object", cast("_Object", message["params"])["textDocument"])["uri"])
    reply: _Object = {"jsonrpc": "2.0", "id": message["id"]}
    modified: bool = _ALWAYS_MODIFIED in _BEHAVIOURS or (
        _MODIFIED in _BEHAVIOURS and uri not in documents.dropped
    )
    documents.dropped.add(uri)
    if _FAIL in _BEHAVIOURS:
        reply["error"] = {"code": -32603, "message": "it broke"}
    elif modified:
        reply["error"] = {"code": _CONTENT_MODIFIED, "message": "content modified"}
    else:
        reply["result"] = _hints(documents.texts[uri], documents.versions[uri])
    if _SWAP in _BEHAVIOURS and documents.held is None:
        documents.held = reply
    elif _SILENT not in _BEHAVIOURS:
        _send(reply)
        if documents.held is not None:
            _send(documents.held)
            documents.held = None
    return True


def _shutdown(message: _Object, _documents: _Documents) -> bool:
    """Answer `shutdown` (a `stubborn` server doesn't).

    Returns:
      Whether to go on serving: always.

    """
    if _STUBBORN not in _BEHAVIOURS:
        _send({"jsonrpc": "2.0", "id": message["id"], "result": None})
    return True


def _exit(_message: _Object, _documents: _Documents) -> bool:
    """Exit (a `stubborn` server doesn't).

    Returns:
      Whether to go on serving.

    """
    return _STUBBORN in _BEHAVIOURS


_Handler: TypeAlias = Callable[[_Object, _Documents], bool]
_HANDLERS: Final[dict[str, _Handler]] = {
    "initialize": _initialize,
    "textDocument/didOpen": _opened,
    "textDocument/didChange": _opened,
    "textDocument/inlayHint": _hinted,
    "shutdown": _shutdown,
    "exit": _exit,
}


def main() -> None:
    """Serve until the client says `exit`, or the behaviours stop it (a `clingy` server stays on)."""
    pid_file: str | None
    if pid_file := os.environ.get("FAKE_SERVER_PID"):
        _ = Path(pid_file).write_text(str(os.getpid()), encoding="utf-8")
    _serve()
    if _CLINGY in _BEHAVIOURS:
        time.sleep(_LINGER)


def _serve() -> None:
    """Serve until the client says `exit`, its input ends, or the behaviours stop it."""
    documents: _Documents = _Documents()
    message: _Object
    for message in iter(partial(_receive, sys.stdin.buffer), None):
        handler: _Handler | None = _HANDLERS.get(str(message.get("method")))
        if handler is not None and not handler(message, documents):
            return


if __name__ == "__main__":
    main()
