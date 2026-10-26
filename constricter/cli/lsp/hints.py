"""`--infer-with`: ask a type checker's language server what type each untyped name has.

Each checker's servers are started once (each round, asked in turn: see `Asking`), over standard
input and output, with the project root as their workspace, and work at once (see `Session`); each
file is opened with the text constricter read, and its inlay hints asked for over the whole file. A
variable-type hint (`: int`) sits just after the name it types: that end is its key, as the line
(from 1) and the UTF-8 byte column `ast` gives the name's end. What the hint says is
`constricter.fix.values.hinted`'s to judge: here it's only text.

A server that can't be started, exits or answers an error stops the run: the option asked for its
types, and silently offering none would look like a checker that found nothing. One that hangs is
restarted and asked about each of its unanswered files alone; a file it hangs on again gets no hints
(`Session.abandoned`, which the command reports), and a checker that hangs on more than
`_MOST_ABANDONED` files stops the run. A Node server whose heap is capped (`Checker.share`) and
exits is taken for one past its cap, as one that hung. A round of files whose hints are kept from an
earlier run, nothing they rest on changed since, is read from the store instead (see `stored`).
"""

import contextlib
import itertools
import os
import queue
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Final, NamedTuple, Self, TypeAlias

from constricter.cli.lsp import protocol, remembered, stored
from constricter.cli.lsp.connection import Connection, FileHints, Found, Sent
from constricter.cli.lsp.protocol import SERVERS, ExitedError, HintError, HungError, Server
from constricter.fix.core.known import Hints

_Task: TypeAlias = Callable[[], Found]  # one server's work: the hints of each file it's asked about


_BATCH: Final = 8  # files a free server takes at a time: few, so none is left with the slow ones
MEMORY: Final = 8 << 30  # the most a checker's servers use together, by default (`--infer-memory`)
_MEMINFO: Final = Path("/proc/meminfo")
_FILES_PER_SERVER: Final = 32  # fewer files than this each don't pay for another server's start
_MOST_ABANDONED: Final = 3  # files a checker may hang on twice before the run stops
_NODE_OPTIONS: Final = "NODE_OPTIONS"  # where a Node server's heap is capped (`Checker.share`)
_HEAP: Final = 9  # tenths of a Node server's share of the memory its heap may take
_WHOLE: Final = 10


class Asking(NamedTuple):
    """How a session asks its checkers.

    With `kept`, a round's hints are read from the store where it has them, and kept there where it
    doesn't. With `in_turn`, a round asks one checker after another, each one's servers shut down
    before the next one's start: the most memory held is the largest checker's, not their sum, for
    their starts every round.
    """

    kept: bool = True
    in_turn: bool = False


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
        how: Asking | None = None,
    ) -> None:
        """Get ready to start `checkers`' servers, with `root` as their workspace.

        Each checker gets up to `servers`, within `memory` bytes (see `Checker`), and is asked `how`
        says (by default, every round's hints kept, all checkers at once).
        """
        self.checkers: list[Checker] = [Checker(checker, root, servers, memory) for checker in checkers]
        self.how: Asking = how or Asking()
        # Each checker's rounds, by its name: whether the store had each one's hints.
        self.rounds: dict[str, list[bool]] = {checker.name: [] for checker in self.checkers}

    def __enter__(self) -> Self:
        """Use the servers.

        Returns:
          The session.

        """
        return self

    def __exit__(self, *_details: object) -> None:
        """Shut every server down, at once."""
        _closed([server for checker in self.checkers for server in checker.servers])

    def hints(self, files: Mapping[Path, str]) -> dict[Path, tuple[Hints, ...]]:
        """Ask every checker for the variable-type hints in `files` (each path's current text).

        Raises `HintError` if a server can't be started, or fails.

        Returns:
          Each file's hints, one per checker, in the order the checkers were named.

        """
        names: dict[str, str] = {}
        found: dict[str, Found] = {}
        checker: Checker
        for checker in self.checkers if self.how.kept else ():
            names[checker.name] = stored.key(checker.name, checker.command, checker.root, files)
            read: tuple[Found, frozenset[Path]] | None
            if (read := stored.load(names[checker.name], checker.root, files)) is not None:
                found[checker.name] = read[0]
                checker.abandoned |= read[1]
        asking: list[Checker] = [checker for checker in self.checkers if checker.name not in found]
        for checker in self.checkers:
            self.rounds[checker.name].append(checker.name in found)
        found |= {checker.name: {} for checker in asking}
        turns: list[list[Checker]] = [[checker] for checker in asking] if self.how.in_turn else [asking]
        turn: list[Checker]
        for turn in turns:
            _asked(files, turn, found)
            for checker in turn if self.how.in_turn else ():
                checker.stop()
        # An abandoned file has no hints: one abandoned before, or as it was asked (an earlier run's hang).
        for checker in asking:
            found[checker.name] = {path: {} for path in checker.abandoned & files.keys()} | found[
                checker.name
            ]
        for checker in asking if self.how.kept else ():
            stored.store(
                names[checker.name],
                checker.root,
                found[checker.name],
                frozenset(checker.abandoned & files.keys()),
            )
        return {
            path: tuple(_hints(checker.name, found[checker.name][path]) for checker in self.checkers)
            for path in files
        }

    @property
    def abandoned(self) -> list[tuple[str, Path]]:
        """List the files a checker's server hung on twice, which it has no hints for.

        Returns:
          Each checker's name and file, in the order the checkers were named.

        """
        return [(checker.name, path) for checker in self.checkers for path in sorted(checker.abandoned)]

    @property
    def reused(self) -> list[tuple[str, int, int]]:
        """List the checkers some of whose rounds' hints were read from the store, not asked for.

        Returns:
          Each one's name, the rounds read from the store and all its rounds, in the order the
          checkers were named.

        """
        return [(name, sum(rounds), len(rounds)) for name, rounds in self.rounds.items() if any(rounds)]


def _asked(files: Mapping[Path, str], checkers: Sequence["Checker"], found: dict[str, Found]) -> None:
    """Ask `checkers` about `files` at once, each over its servers (started as needed), into `found`."""
    _start(files, checkers)
    work: list[tuple[Checker, _Task]] = [
        (checker, task) for checker in checkers for task in checker.tasks(files)
    ]
    if work:
        pool: ThreadPoolExecutor
        with ThreadPoolExecutor(len(work)) as pool:
            futures: list[Future[Found]] = [pool.submit(task) for _, task in work]
            checker: Checker
            future: Future[Found]
            for (checker, _), future in zip(work, futures, strict=True):
                found[checker.name].update(future.result())


def _start(files: Mapping[Path, str], checkers: Sequence["Checker"]) -> None:
    """Start the servers `checkers` need for `files` that aren't running yet, all at once.

    Raises `HintError` if one can't be started; those that could be are shut down with the session.
    """
    starting: list[Checker] = []
    checker: Checker
    wanted: int
    for checker in checkers:
        # None for no files: its heap is set as its first server starts.
        if wanted := checker.wanted(files):
            checker.share(wanted)
        starting += [checker] * (wanted - len(checker.servers))
    if not starting:
        return
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(len(starting)) as pool:
        futures: list[Future[Connection]] = [
            pool.submit(Connection, checker.command, checker.root, checker.environment)
            for checker in starting
        ]
    failures: list[HintError] = []
    future: Future[Connection]
    for checker, future in zip(starting, futures, strict=True):
        try:
            checker.servers.append(future.result())
        except HintError as failure:
            failures.append(failure)
    if failures:
        raise failures[0]


def _hints(checker: str, found: FileHints) -> Hints:
    """Gather one file's hints from `checker` as `--fix` reads them.

    Returns:
      Them.

    """
    return Hints(
        checker,
        {where: text for where, (text, _) in found.items()},
        {where: offered for where, (_, offered) in found.items() if offered is not None},
    )


class Checker:  # pylint: disable=too-many-instance-attributes
    """One checker's servers, and which of them has each file.

    It has as many as its files need (one per `_FILES_PER_SERVER`), up to the command's `--jobs`, the
    checker's own most (`Server.most`), and as many as fit in its memory: `--infer-memory` (never
    more than is available), or by default `MEMORY` (never more than half what's available). Each
    server loads the whole program it checks, or its share of it, by its checker's own measure (see
    `Server.fitting`). One server it always has, whatever the memory.

    The files are handed out a few at a time (`_BATCH`), the biggest first, to whichever server is
    free: one file's analysis can take far longer than another's, and none waits on a busy one. A
    file stays with the server that took it, which has it open, however many times it's asked about.
    """

    def __init__(self, name: str, root: Path, servers: int, memory: int | None = None) -> None:
        """Get ready to start checker `name`'s servers, with `root` as their workspace, in `memory` bytes."""
        self.name: str = name
        self.root: Path = root
        self.command: list[str] = command(name)
        self.server: Server = SERVERS[name]
        self.most: int = max(1, min(servers, self.server.most))
        self.memory: int = budget(memory, available_memory())
        self.servers: list[Connection] = []
        self.assigned: dict[Path, int] = {}  # each file's server, by its place in `servers`
        self.abandoned: set[Path] = set()  # the files a server hung on twice: never asked about again
        self.environment: dict[str, str] | None = None  # its servers', where their heap is capped (`share`)

    def share(self, servers: int) -> None:
        """Cap each server's heap at its share of the memory, as the first starts, where they run on Node.

        Of `servers`' share, a tenth is left for what isn't the heap; never under a server's own
        (`Server.memory`). Past the cap, basedpyright empties its caches, and else exits: restarted
        then, its files asked about alone (`_alone`).
        """
        if self.server.node and self.environment is None:
            heap: int = max(self.server.memory, self.memory // servers * _HEAP // _WHOLE) >> 20
            given: str = os.environ.get(_NODE_OPTIONS, "")
            self.environment = {**os.environ, _NODE_OPTIONS: f"{given} --max-old-space-size={heap}".strip()}

    def wanted(self, files: Mapping[Path, str]) -> int:
        """Count the servers `files` want, as many as fit in memory (never fewer than it has).

        Returns:
          It.

        """
        size: int = sum(len(text) for text in files.values())
        fit: int = max(1, self.server.fitting(self.memory, size))
        return max(len(self.servers), min(self.most, -(-len(files) // _FILES_PER_SERVER), fit))

    def tasks(self, files: Mapping[Path, str]) -> list[_Task]:
        """Make each server's work on `files`: its own files first, then new ones as it's free for them.

        A file abandoned (see `_alone`), in this run or an earlier one (see `remembered`), isn't
        asked about again.

        Returns:
          A task per server, giving the hints of every file it was sent.

        """
        own: dict[int, dict[Path, str]] = {}
        path: Path
        for path in files.keys() & self.assigned.keys() - self.abandoned:
            own.setdefault(self.assigned[path], {})[path] = files[path]
        # One it hung on in an earlier run, unchanged since: left without hints from the start.
        self.abandoned.update(
            path
            for path in files.keys() - self.assigned.keys() - self.abandoned
            if remembered.hung(self.name, self.command, files[path], path)
        )
        fresh: list[Path] = sorted(
            files.keys() - self.assigned.keys() - self.abandoned,
            key=lambda new: (-len(files[new]), new),
        )
        batches: queue.SimpleQueue[dict[Path, str]] = queue.SimpleQueue()
        start: int
        for start in range(0, len(fresh), _BATCH):
            batch: list[Path] = fresh[start : start + _BATCH]
            batches.put({path: files[path] for path in batch})
        return [partial(self._work, index, own.get(index, {}), batches) for index in range(len(self.servers))]

    def _work(
        self,
        index: int,
        own: dict[Path, str],
        batches: "queue.SimpleQueue[dict[Path, str]]",
    ) -> Found:
        """Ask server `index` about its own files, then take batches of new ones until there are none.

        Returns:
          Each file's hints.

        Raises:
          HintError: The server failed as no restart gets past (see `_restartable`).

        """
        found: Found = {}
        pending: list[Sent] = []
        batch: dict[Path, str]
        # Two batches in flight: the next is asked before the last's answers are read, so the server
        # always has work while they're read and the next batch is taken.
        for batch in itertools.chain([own] if own else [], iter(partial(_taken, batches), None)):
            self.assigned.update(dict.fromkeys(batch, index))  # each file's taken once: no two write one
            try:
                pending.append((batch, self.servers[index].ask(batch)))
            except HintError as failure:  # it has gone since its last answers: past its cap, say
                if not self._restartable(failure):
                    raise
                found.update(self._requeued(index, pending, batch))
                continue
            if len(pending) > 1:
                found.update(self._answers(index, pending))
        if pending:
            found.update(self._answers(index, pending))
        return found

    def _answers(self, index: int, pending: list[Sent]) -> Found:
        """Collect the answers to the first of `pending`'s batches from server `index`, and take it off.

        If the server hangs, or exits past its heap's cap, every pending file is asked about again
        alone (see `_alone`).

        Returns:
          Each file's hints: the batch's, or every pending file's.

        Raises:
          HintError: The server failed as no restart gets past (see `_restartable`).

        """
        try:
            found: Found = self.servers[index].answers(pending[0][1])
        except HintError as failure:
            if not self._restartable(failure):
                raise
            return self._requeued(index, pending, {})
        del pending[0]
        return found

    def _requeued(self, index: int, pending: list[Sent], more: Mapping[Path, str]) -> Found:
        """Ask server `index`, which failed, about each pending file and each of `more` alone (see `_alone`).

        Returns:
          Their hints.

        """
        unanswered: dict[Path, str] = {path: text for batch, _ in pending for path, text in batch.items()}
        pending.clear()
        return self._alone(index, unanswered | dict(more))

    def _alone(self, index: int, files: Mapping[Path, str]) -> Found:
        """Restart server `index`, which hung or exited past its cap, and ask it about each of `files` alone.

        A file it hangs on again is abandoned, with no hints, and the server restarted for the rest:
        one file's analysis needn't cost every other file's hints. As is one it exits on again past
        its cap, though not remembered (see `remembered`): a larger share may fit it.

        Returns:
          Each file's hints.

        Raises:
          HintError: It hung on more than `_MOST_ABANDONED` files, or can't be restarted.

        """
        self._restart(index)
        found: Found = {}
        path: Path
        text: str
        for path, text in files.items():
            server: Connection = self.servers[index]
            try:
                found.update(server.answers(server.ask({path: text})))
            except HintError as hung:
                if not self._restartable(hung):
                    raise
                self.abandoned.add(path)
                if isinstance(hung, HungError):
                    remembered.remember(self.name, self.command, text, path)
                if len(self.abandoned) > _MOST_ABANDONED:
                    error: str = f"{self.name} hung on {len(self.abandoned)} file(s), each asked about alone"
                    raise HintError(error) from hung
                found[path] = {}
                self._restart(index)
        return found

    def stop(self) -> None:
        """Shut its servers down, at once: the next round starts others, which open each file anew."""
        _closed(self.servers)
        self.servers.clear()
        self.assigned.clear()

    def _restartable(self, failure: HintError) -> bool:
        """Decide whether a server's `failure` is one a restart may get past: a hang, or an exit past its cap.

        Returns:
          Whether it is; any other failure stops the run.

        """
        return isinstance(failure, HungError) or (
            isinstance(failure, ExitedError) and self.environment is not None
        )

    def _restart(self, index: int) -> None:
        """Stop server `index` and start another in its place, which opens each file it's asked about."""
        self.servers[index].close(graceful=False)
        self.servers[index] = Connection(self.command, self.root, self.environment)


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
    found: str | None
    if (found := protocol.executable(checker)) is None:
        install: str = f"`pip install {checker}`"
        message: str = (
            f"--infer-with={checker} needs `{server.executable}`, which isn't installed ({install})"
        )
        raise HintError(message)
    return [found, *server.args]


def _closed(servers: Sequence[Connection]) -> None:
    """Shut `servers` down, at once: none where a turn had no file to ask about."""
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, len(servers))) as pool:
        _ = list(pool.map(Connection.close, servers))
