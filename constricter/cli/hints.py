# SPDX-License-Identifier: MIT
"""`--infer-with`: ask a type checker's language server what type each untyped name has.

Each checker's servers are started once, over standard input and output, with the project root as
their workspace, and work at once (see `Session`); each file is opened with the text constricter
read, and its inlay hints asked for over the whole file. A variable-type hint (`: int`) sits just
after the name it types: that end is its key, as the line (from 1) and the UTF-8 byte column `ast`
gives the name's end. What the hint says is `constricter.fix.hinted`'s to judge: here it's only
text.

A server that can't be started, exits, times out or answers an error stops the run: the option
asked for its types, and silently offering none would look like a checker that found nothing.
"""

import contextlib
import itertools
import json
import os
import queue
import re
import shutil
import subprocess  # starts the type checker's language server
import sys
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import IO, Final, NamedTuple, Self, TypeAlias, cast

from constricter.cli import guard, protocol
from constricter.cli.protocol import SERVERS, HintError, Server
from constricter.fix.known import Hints

_Json: TypeAlias = protocol.Json
_Object: TypeAlias = protocol.Object
_FileHints: TypeAlias = dict[tuple[int, int], str]  # a file's hints' texts, by where each name ends
_Found: TypeAlias = dict[Path, _FileHints]  # each file's
_Task: TypeAlias = Callable[[], _Found]  # one server's work: the hints of each file it's asked about


_BATCH: Final = 8  # files a free server takes at a time: few, so none is left with the slow ones
MEMORY: Final = 8 << 30  # the most a checker's servers use together, by default (`--infer-memory`)
_SERVER_MEMORY: Final = 600 << 20  # a server's memory, before the files (basedpyright's, measured)
_MEMORY_PER_BYTE: Final = 130  # and for each byte of them: 1.2 GB for SQLAlchemy's 8 MB, 3.4 for pandas' 21
_MEMINFO: Final = Path("/proc/meminfo")
_FILES_PER_SERVER: Final = 32  # fewer files than this each don't pay for another server's start
# Seconds without a word from a server before it's taken for hung. Not an answer's wait: pandas'
# first answer took basedpyright 410s, but it reports its progress (`$/progress`) all the while.
_TIMEOUT: Final = 120.0
_POLL: Final = 1.0  # seconds between looks at how long it's been silent, while waiting
# The guard's interpreter: the one a venv's is made from, if it's one. A Windows venv's `python.exe`
# is a launcher that starts that one as a child, which then outlives a kill of the launcher.
_GUARD_PYTHON: Final = str(getattr(sys, "_base_executable", "") or sys.executable)
_SILENCE: Final[_Object] = {}  # no message yet, while waiting for one (compared by identity)
_LINE_BREAK: Final = re.compile(r"\r\n|\r|\n")  # the lines positions count, as the protocol has them
_UTF16: Final = "utf-16"
_UTF8: Final = "utf-8"
_METHOD_NOT_FOUND: Final = -32601
_ID: Final = "id"
_METHOD: Final = "method"
_ERROR: Final = "error"
_CONFIGURATION: Final = "workspace/configuration"
_UTF16_UNITS: Final = "utf-16-le"  # UTF-16's code units, two bytes each, without a byte-order mark


@dataclass
class _Inbox:
    """What a server has said: its messages still to read, when it last said anything, and early answers.

    An early answer came while another request's were awaited (see `Connection._wanted`).
    """

    messages: queue.Queue[_Object | None] = field(default_factory=queue.Queue[_Object | None])
    heard: float = field(default_factory=time.monotonic)
    early: dict[int, _Object] = field(default_factory=dict[int, _Object])


@dataclass
class _Documents:
    """The files a server has open: each one's version and text, as the server has them, by URI."""

    versions: dict[str, int] = field(default_factory=dict[str, int])
    texts: dict[str, str] = field(default_factory=dict[str, str])


class _Asked(NamedTuple):
    """Hint requests sent, not yet answered: each request's file, and each file's lines."""

    numbers: dict[int, Path]
    lines: dict[Path, list[str]]


class Session:
    """The language servers of one or more type checkers, running for one command's files.

    Each checker's files are shared among its servers (see `Checker`), each sent all its files'
    requests at once, and every server works at the same time as the others. Raises `HintError`
    (as `hints` does) if a checker isn't installed.
    """

    def __init__(
        self,
        checkers: Sequence[str],
        root: Path,
        servers: int = 1,
        memory: int | None = None,
    ) -> None:
        """Get ready to start `checkers`' servers, with `root` as their workspace.

        Each checker gets up to `servers`, within `memory` bytes (see `Checker`).
        """
        self.checkers: list[Checker] = [Checker(checker, root, servers, memory) for checker in checkers]

    def __enter__(self) -> Self:
        """Use the servers.

        Returns:
          The session.

        """
        return self

    def __exit__(self, *_details: object) -> None:
        """Shut every server down, at once."""
        running: list[Connection]
        if running := [server for checker in self.checkers for server in checker.servers]:
            pool: ThreadPoolExecutor
            with ThreadPoolExecutor(len(running)) as pool:
                _ = list(pool.map(Connection.close, running))

    def hints(self, files: Mapping[Path, str]) -> dict[Path, tuple[Hints, ...]]:
        """Ask every checker for the variable-type hints in `files` (each path's current text).

        Raises `HintError` if a server can't be started, or fails.

        Returns:
          Each file's hints, one per checker, in the order the checkers were named.

        """
        self._start(files)
        work: list[tuple[Checker, _Task]] = [
            (checker, task) for checker in self.checkers for task in checker.tasks(files)
        ]
        found: dict[str, _Found] = {checker.name: {} for checker in self.checkers}
        pool: ThreadPoolExecutor
        with ThreadPoolExecutor(len(work)) as pool:
            futures: list[Future[_Found]] = [pool.submit(task) for _, task in work]
            checker: Checker
            future: Future[_Found]
            for (checker, _), future in zip(work, futures, strict=True):
                found[checker.name].update(future.result())
        return {
            path: tuple(Hints(checker.name, found[checker.name][path]) for checker in self.checkers)
            for path in files
        }

    def _start(self, files: Mapping[Path, str]) -> None:
        """Start the servers `files` need that aren't running yet, all at once.

        Raises `HintError` if one can't be started; those that could be are shut down with the session.
        """
        starting: list[Checker] = [
            checker for checker in self.checkers for _ in range(checker.wanted(files) - len(checker.servers))
        ]
        if not starting:
            return
        pool: ThreadPoolExecutor
        with ThreadPoolExecutor(len(starting)) as pool:
            futures: list[Future[Connection]] = [
                pool.submit(Connection, checker.command, checker.root) for checker in starting
            ]
        failures: list[HintError] = []
        checker: Checker
        future: Future[Connection]
        for checker, future in zip(starting, futures, strict=True):
            try:
                checker.servers.append(future.result())
            except HintError as failure:
                failures.append(failure)
        if failures:
            raise failures[0]


class Checker:
    """One checker's servers, and which of them has each file.

    It has as many as its files need (one per `_FILES_PER_SERVER`), up to the command's `--jobs`, the
    checker's own most (`Server.most`: one for a checker that works in parallel itself), and as many
    as fit in its memory: `--infer-memory` (never more than is available), or by default `MEMORY`
    (never more than half what's available). Each server loads the whole program it checks, which
    takes (as measured) about `_SERVER_MEMORY` plus `_MEMORY_PER_BYTE` for each byte of the files.
    One server it always has, whatever the memory.

    The files are handed out a few at a time (`_BATCH`), the biggest first, to whichever server is
    free: one file's analysis can take far longer than another's, and none waits on a busy one. A
    file stays with the server that took it, which has it open, however many times it's asked about.
    """

    def __init__(self, name: str, root: Path, servers: int, memory: int | None = None) -> None:
        """Get ready to start checker `name`'s servers, with `root` as their workspace, in `memory` bytes."""
        self.name: str = name
        self.root: Path = root
        self.command: list[str] = command(name)
        self.most: int = max(1, min(servers, SERVERS[name].most))
        self.memory: int = budget(memory, available_memory())
        self.servers: list[Connection] = []
        self.assigned: dict[Path, int] = {}  # each file's server, by its place in `servers`

    def wanted(self, files: Mapping[Path, str]) -> int:
        """Count the servers `files` want, as many as fit in memory (never fewer than it has).

        Returns:
          It.

        """
        size: int = sum(len(text) for text in files.values())
        fit: int = max(1, self.memory // (_SERVER_MEMORY + _MEMORY_PER_BYTE * size))
        return max(len(self.servers), min(self.most, -(-len(files) // _FILES_PER_SERVER), fit))

    def tasks(self, files: Mapping[Path, str]) -> list[_Task]:
        """Make each server's work on `files`: its own files first, then new ones as it's free for them.

        Returns:
          A task per server, giving the hints of every file it was sent.

        """
        own: dict[int, dict[Path, str]] = {}
        path: Path
        for path in files.keys() & self.assigned.keys():
            own.setdefault(self.assigned[path], {})[path] = files[path]
        fresh: list[Path] = sorted(
            files.keys() - self.assigned.keys(),
            key=lambda new: (-len(files[new]), new),
        )
        batches: queue.SimpleQueue[dict[Path, str]] = queue.SimpleQueue()
        start: int
        for start in range(0, len(fresh), _BATCH):
            batch: list[Path] = fresh[start:][:_BATCH]
            batches.put({path: files[path] for path in batch})
        return [partial(self._work, index, own.get(index, {}), batches) for index in range(len(self.servers))]

    def _work(
        self,
        index: int,
        own: dict[Path, str],
        batches: "queue.SimpleQueue[dict[Path, str]]",
    ) -> _Found:
        """Ask server `index` about its own files, then take batches of new ones until there are none.

        Returns:
          Each file's hints.

        """
        server: Connection = self.servers[index]
        found: _Found = {}
        waiting: _Asked | None = None
        batch: dict[Path, str]
        # Two batches in flight: the next is asked before the last's answers are read, so the server
        # always has work while they're read and the next batch is taken.
        for batch in itertools.chain([own] if own else [], iter(partial(_taken, batches), None)):
            asked: _Asked = server.ask(batch)
            self.assigned.update(dict.fromkeys(batch, index))  # each file's taken once: no two write one
            if waiting is not None:
                found.update(server.answers(waiting))
            waiting = asked
        if waiting is not None:
            found.update(server.answers(waiting))
        return found


def _taken(batches: "queue.SimpleQueue[dict[Path, str]]") -> dict[Path, str] | None:
    """Take the next batch of files, if there's one left.

    Returns:
      It, or `None`.

    """
    try:
        return batches.get_nowait()
    except queue.Empty:
        return None


def budget(asked: int | None, available: int | None) -> int:
    """Settle the memory a checker's servers may use: what's `asked`, or `MEMORY`, within what's `available`.

    Returns:
      It, in bytes: asked for, no more than is available; by default, no more than half of it
      (none, where that can't be read: one server).

    """
    if asked is not None:
        return asked if available is None else min(asked, available)
    return min(MEMORY, (available or 0) // 2)


def available_memory() -> int | None:
    """Find how much memory is free for more servers.

    What the system says is available (Linux's `MemAvailable`), or else half of all it has.

    Returns:
      It, in bytes, or `None` where neither can be read (Windows): one server, then.

    """
    with contextlib.suppress(OSError, ValueError, StopIteration):
        lines: list[str] = _MEMINFO.read_text(encoding="ascii").splitlines()
        return 1024 * int(next(line for line in lines if line.startswith("MemAvailable:")).split()[1])
    with contextlib.suppress(OSError, ValueError, AttributeError):
        return os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE") // 2
    return None


def command(checker: str) -> list[str]:
    """Find `checker`'s language server: on `PATH`, or beside this Python (an unactivated venv).

    Returns:
      Its command line.

    Raises:
      HintError: It isn't installed.

    """
    server: Server = SERVERS[checker]
    name: str = server.executable
    executable: str | None = shutil.which(name) or shutil.which(name, path=str(Path(sys.executable).parent))
    if executable is None:
        message: str = (
            f"--infer-with={checker} needs `{name}`, which isn't installed (`pip install {checker}`)"
        )
        raise HintError(message)
    return [executable, *server.args]


class Connection:
    """A running language server, and the JSON-RPC conversation with it."""

    def __init__(self, argv: Sequence[str], root: Path) -> None:
        """Start the server (`argv`) and initialize it, with `root` as its one workspace folder.

        Raises:
          HintError: It can't be started, or fails to initialize.

        """
        self.name: str = Path(argv[0]).name
        if shutil.which(argv[0]) is None:
            message: str = f"{self.name} couldn't be started: {argv[0]} isn't a program"
            raise HintError(message)
        # Closing it closes its pipes and waits for it, as leaving a `with` would.
        self.stack: contextlib.ExitStack = contextlib.ExitStack()
        # Through `guard`, which stops the server when constricter stops, however it does. Run by
        # its path, not as a module: it needs only the standard library, and this Python needn't be
        # able to import constricter from the server's working directory.
        self.process: subprocess.Popen[bytes] = self.stack.enter_context(
            subprocess.Popen(
                [_GUARD_PYTHON, guard.__file__, str(guard.GRACE), *argv],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=root,
            ),
        )
        self.inbox: _Inbox = _Inbox()
        self.writing: threading.Lock = threading.Lock()  # the reader answers the server as it asks
        self.last: int = 0
        self.documents: _Documents = _Documents()
        self.reader: threading.Thread = threading.Thread(
            target=self._listen,
            daemon=True,
        )
        self.reader.start()
        self.encoding: str = _UTF16
        try:
            self._initialize(root)
        except HintError:
            self.close(graceful=False)
            raise

    def _initialize(self, root: Path) -> None:
        """Initialize the server, with `root` as its workspace folder, and learn how it counts positions."""
        uri: str = root.resolve().as_uri()
        result: _Json = self.request(
            "initialize",
            {
                "processId": os.getpid(),
                "rootUri": uri,
                "workspaceFolders": [{"uri": uri, "name": root.resolve().name}],
                "capabilities": {
                    "general": {"positionEncodings": [_UTF8, _UTF16]},
                    "textDocument": {"inlayHint": {"dynamicRegistration": False}},
                    "workspace": {"configuration": True, "workspaceFolders": True},
                    # Its progress, as it works: a server busy for minutes isn't taken for hung.
                    "window": {"workDoneProgress": True},
                },
            },
        )
        capabilities: _Object = cast("_Object", cast("_Object", result)["capabilities"])
        self.encoding = str(capabilities.get("positionEncoding") or _UTF16)
        self.notify("initialized", {})

    def close(self, *, graceful: bool = True) -> None:
        """Shut the server down (or, not `graceful`, stop it); stop it anyway if it won't shut down.

        Stopping it ends its input: its guard kills it if it doesn't exit then, and exits itself.
        """
        if not (graceful and self._stopped()):
            with self.writing, contextlib.suppress(OSError):  # it may have gone: then so has its input
                cast("IO[bytes]", self.process.stdin).close()
            try:
                _ = self.process.wait(timeout=2 * guard.GRACE)
            except subprocess.TimeoutExpired:  # the guard itself is stuck: the server goes with its input
                self.process.kill()
                _ = self.process.wait()
        self.reader.join()  # its output has ended with it, and so has reading it
        with contextlib.suppress(OSError):  # what's left to write can't be: it has gone
            self.stack.close()

    def _stopped(self) -> bool:
        """Ask the server to shut down and exit, and wait for it to.

        Returns:
          Whether it did.

        """
        with contextlib.suppress(HintError):  # it's gone, or won't answer: waiting says which
            _ = self.request("shutdown", None)
            self.notify("exit", None)
        try:
            _ = self.process.wait(timeout=guard.GRACE)
        except subprocess.TimeoutExpired:
            return False
        return True

    def ask(self, files: Mapping[Path, str]) -> "_Asked":
        """Open each file (or send its new text), and ask for its hints over the whole of it.

        It doesn't wait for them. Each file is left open: basedpyright (1.40) fails the next file's
        hints when that file imports one just closed, and the server is shut down after the last
        file anyway.

        Returns:
          The requests, to collect their answers with `answers`.

        """
        lines: dict[Path, list[str]] = {path: _LINE_BREAK.split(text) for path, text in files.items()}
        path: Path
        text: str
        for path, text in files.items():
            self._opened(path.resolve().as_uri(), text)
        asked: dict[int, Path] = {
            self._ask(
                "textDocument/inlayHint",
                {
                    "textDocument": {"uri": path.resolve().as_uri()},
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": len(lines[path]), "character": 0},
                    },
                },
            ): path
            for path in files
        }
        return _Asked(asked, lines)

    def answers(self, asked: "_Asked") -> _Found:
        """Wait for the answers to hint requests `ask` sent.

        Returns:
          Each file's variable-type hints' texts, by where the name each types ends.

        """
        answers: dict[int, _Json] = self._collect(set(asked.numbers), "textDocument/inlayHint")
        return {
            path: self._found(answers[number], asked.lines[path]) for number, path in asked.numbers.items()
        }

    def _opened(self, uri: str, text: str) -> None:
        """Send a file's text: opening it, or (open already) replacing its whole text, if it's changed."""
        if self.documents.texts.get(uri) == text:
            return
        self.documents.texts[uri] = text
        version: int
        if (version := self.documents.versions.get(uri, 0) + 1) == 1:
            self.notify(
                "textDocument/didOpen",
                {"textDocument": {"uri": uri, "languageId": "python", "version": version, "text": text}},
            )
        else:
            self.notify(
                "textDocument/didChange",
                {"textDocument": {"uri": uri, "version": version}, "contentChanges": [{"text": text}]},
            )
        self.documents.versions[uri] = version

    def _found(self, answer: _Json, lines: Sequence[str]) -> _FileHints:
        """Read one file's hints.

        Returns:
          Each variable-type hint's text, by where the name it types ends.

        """
        found: _FileHints = {}
        hint: _Json
        for hint in cast("list[_Json]", answer or []):
            where: tuple[int, int] | None
            label: str | None
            if (label := protocol.label(cast("_Object", hint))) is not None and (
                where := self._where(cast("_Object", cast("_Object", hint)["position"]), lines)
            ) is not None:
                _ = found.setdefault(where, label)
        return found

    def _where(self, position: _Object, lines: Sequence[str]) -> tuple[int, int] | None:
        """Turn a position into a line (from 1) and a UTF-8 byte column, as `ast` counts.

        Returns:
          It, or `None` for a position past the file's end.

        """
        line: int = int(cast("int", position["line"]))
        character: int = int(cast("int", position["character"]))
        if line >= len(lines):
            return None
        text: str = lines[line]
        if self.encoding == _UTF8:
            return line + 1, character
        # The first `character` UTF-16 code units, two bytes each.
        before: str = text.encode(_UTF16_UNITS)[: 2 * character].decode(_UTF16_UNITS, errors="ignore")
        return line + 1, len(before.encode())

    def request(self, method: str, params: _Json) -> _Json:
        """Send a request and wait for its answer.

        Returns:
          Its result.

        """
        number: int = self._ask(method, params)
        return self._collect({number}, method)[number]

    def _ask(self, method: str, params: _Json) -> int:
        """Send a request, without waiting for its answer.

        Returns:
          Its number, which its answer carries.

        """
        self.last += 1
        self._send({"jsonrpc": "2.0", _ID: self.last, _METHOD: method, "params": params})
        return self.last

    def _collect(self, numbers: set[int], method: str) -> dict[int, _Json]:
        """Wait for the answers to requests `numbers` (to `method`), in whatever order they come.

        Raises `HintError` if the server exits, takes too long, or answers one with an error.

        Returns:
          Each request's result.

        """
        return dict(self._answer_to(numbers, method) for _ in numbers)

    def _answer_to(self, numbers: set[int], method: str) -> tuple[int, _Json]:
        """Wait for the next answer to one of requests `numbers`, passing over any other message.

        Returns:
          Its request's number, and its result.

        Raises:
          HintError: The server exited, took too long, or answered with an error.

        """
        early: set[int] = numbers & self.inbox.early.keys()
        # `_next` raises rather than end: there is always a next message, or an error.
        answer: _Object = (
            self.inbox.early.pop(early.pop())
            if early
            else next(
                message
                for message in iter(partial(self._next, method), None)
                if self._wanted(message, numbers)
            )
        )
        if _ERROR in answer:
            failure: _Object = cast("_Object", answer[_ERROR])
            error: str = f"{self.name} failed `{method}`: {failure.get('message')}"
            raise HintError(error)
        return cast("int", answer[_ID]), answer.get("result")

    def _wanted(self, message: _Object, numbers: set[int]) -> bool:
        """Check whether `message` answers one of requests `numbers`, keeping it if it answers another.

        With a second batch asked before the first's answers are in, the second's can come first.

        Returns:
          Whether it answers one of `numbers`.

        """
        number: _Json = message.get(_ID)
        if isinstance(number, int) and number not in numbers and number <= self.last:
            self.inbox.early[number] = message
        return number in numbers

    def _next(self, method: str) -> _Object:
        """Wait for the server's next message, while waiting for its answer to `method`.

        Returns:
          It.

        Raises:
          HintError: The server exited, or took too long.

        """
        # `_waited` raises rather than end: there is always a next message, or an error.
        message: _Object | None = next(
            waited for waited in (self._waited(method) for _ in itertools.count()) if waited is not _SILENCE
        )
        if message is None:
            error: str = f"{self.name} exited while answering `{method}`"
            raise HintError(error)
        return message

    def _waited(self, method: str) -> _Object | None:
        """Wait a moment for the server's next message.

        Returns:
          It (`None` at the end of its output), or `_SILENCE` if none came yet.

        Raises:
          HintError: It has said nothing at all for `_TIMEOUT` seconds: it's hung.

        """
        try:
            return self.inbox.messages.get(timeout=_POLL)
        except queue.Empty:
            if time.monotonic() - self.inbox.heard >= _TIMEOUT:
                error: str = f"{self.name} said nothing for {_TIMEOUT:.0f}s while answering `{method}`"
                raise HintError(error) from None
            return _SILENCE

    def _listen(self) -> None:
        """Read the server's messages until it closes its output (then queue `None`).

        Its own requests are answered at once, here: a server may wait for the answer before it
        reads anything more, while a batch of requests is still being written to it. The rest are
        queued for the requests waiting on them.
        """
        stdout: IO[bytes] = cast("IO[bytes]", self.process.stdout)
        message: _Object
        for message in iter(partial(protocol.message, stdout), None):
            self.inbox.heard = time.monotonic()  # a word, of any kind: it's working
            if _METHOD in message and _ID in message:
                with contextlib.suppress(HintError):  # it has gone: its output ends next
                    self._answer(message)
            else:
                self.inbox.messages.put(message)
        self.inbox.messages.put(None)

    def _answer(self, message: _Object) -> None:
        """Answer one of the server's own requests: its settings, and nothing else it asks for."""
        method: str = str(message[_METHOD])
        reply: _Object = {"jsonrpc": "2.0", _ID: message[_ID]}
        if method == _CONFIGURATION:
            items: list[_Json] = cast("list[_Json]", cast("_Object", message["params"])["items"])
            reply["result"] = [protocol.settings(cast("_Object", item).get("section")) for item in items]
        elif method in {"client/registerCapability", "window/workDoneProgress/create"}:
            reply["result"] = None
        else:
            reply[_ERROR] = {"code": _METHOD_NOT_FOUND, "message": f"not supported: {method}"}
        self._send(reply)

    def notify(self, method: str, params: _Json) -> None:
        """Send a notification: no answer comes."""
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def _send(self, message: _Object) -> None:
        """Frame and send one message.

        Raises:
          HintError: The server has exited.

        """
        body: bytes = json.dumps(message).encode()
        with self.writing:  # one message at a time: the reader answers the server's own meanwhile
            try:
                protocol.write(
                    cast("IO[bytes]", self.process.stdin),
                    f"Content-Length: {len(body)}\r\n\r\n".encode() + body,
                )
            except OSError as error:
                failure: str = f"{self.name} exited: {error}"
                raise HintError(failure) from error
