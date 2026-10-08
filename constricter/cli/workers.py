# SPDX-License-Identifier: MIT
"""Worker processes for `--jobs`: each indexes its own share of the files, then checks it."""

import contextlib
import copy
import gc
import importlib
from collections.abc import Callable, Collection, Generator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self, TypeAlias, cast

from constricter.cli import collecting
from constricter.cli.paths import shares
from constricter.cli.runs import FileRun
from constricter.fix.core.known import Hints, Outside, Returns
from constricter.fix.index import project
from constricter.rules import parsed

if TYPE_CHECKING:  # slow to import, and only needed for many files
    from concurrent.futures import Future, ProcessPoolExecutor

# A worker's answers, one per file of its share: what it read (to index), and what it found.
_Reading: TypeAlias = "Future[list[project.Module | None]]"
_FIRST_COMPLETED: Final = "FIRST_COMPLETED"  # `concurrent.futures.FIRST_COMPLETED`
_Check: TypeAlias = Callable[[Path, Outside], FileRun]
# A worker's files to check: each with its hints; what checked modules' functions return since it
# was last told; and whether a file is checked only if what it imports returns something else now.
File: TypeAlias = tuple[Path, tuple[Hints, ...]]
Asked: TypeAlias = tuple[Sequence[File], Mapping[str, Returns], bool]
Answering: TypeAlias = "Future[list[FileRun | None]]"  # a worker's answer for the files it was asked
_Wait: TypeAlias = Callable[..., tuple[set[object], set[object]]]  # `concurrent.futures.wait`: done, and not


class Workers:
    """Worker processes, each with its own share of the files, which it indexes and then checks.

    The trees a worker parsed to index its files are still there to check (`parsed.keep`), within its
    part of the budget: sharing the files out anew for the check (a pool's way) would parse them again.
    """

    def __init__(self, paths: Sequence[Path], jobs: int) -> None:
        """Share `paths` out among up to `jobs` workers (see `paths.shares`)."""
        self.paths: Sequence[Path] = paths
        self.shares: list[list[int]] = shares(paths, jobs)
        self.stack: contextlib.ExitStack = contextlib.ExitStack()
        self.pools: list[ProcessPoolExecutor] = []  # started by `__enter__`

    def __enter__(self) -> Self:
        """Start the workers, one process each, each with its part of the budget.

        Returns:
          Them.

        """
        self.pools = [
            self.stack.enter_context(
                cast(
                    "type[ProcessPoolExecutor]",
                    importlib.import_module("concurrent.futures").ProcessPoolExecutor,
                )(
                    max_workers=1,
                    initializer=_started,
                    initargs=(len(self.shares),),
                ),
            )
            for _ in self.shares
        ]
        return self

    def __exit__(self, *_details: object) -> None:
        """Stop the workers."""
        self.stack.close()

    def over(self, paths: Sequence[Path]) -> "Workers":
        """Ask these workers about `paths` alone, some of their files: each has what it had of them.

        Returns:
          Them, each with its share of `paths`.

        """
        place: dict[Path, int] = {path: at for at, path in enumerate(paths)}
        some: Workers = copy.copy(self)
        some.paths = paths
        some.shares = [
            [place[self.paths[at]] for at in share if self.paths[at] in place] for share in self.shares
        ]
        return some

    def index(self) -> project.Index:
        """Index every file, each worker its share.

        Returns:
          The index, as one process would build it.

        """
        read: list[_Reading] = [
            pool.submit(_read_share, [self.paths[at] for at in share])
            for pool, share in zip(self.pools, self.shares, strict=True)
        ]
        found: dict[int, project.Module | None] = {}
        share: list[int]
        future: _Reading
        for share, future in zip(self.shares, read, strict=True):
            found.update(zip(share, future.result(), strict=True))
        return project.indexed(found[at] for at in range(len(self.paths)))  # in their order, as one at a time

    def tell(self, function: Callable[[bytes], None], told: bytes) -> None:
        """Run `function(told)` in every worker, and wait for them all: what each is to know from then on."""
        telling: list[Future[None]] = [pool.submit(function, told) for pool in self.pools]
        each: Future[None]
        for each in telling:
            each.result()

    def ask(
        self,
        worker: int,
        function: Callable[[_Check, Asked], list[FileRun | None]],
        check: _Check,
        asked: Asked,
    ) -> Answering:
        """Start `function(check, asked)` in one worker: its files to check, and what it's to know for them.

        Returns:
          The answer it will give.

        """
        return self.pools[worker].submit(function, check, asked)


@dataclass
class _Kept:
    """A run's workers, started for its first round and asked again in each later one."""

    stack: contextlib.ExitStack | None = None
    workers: Workers | None = None


_KEPT: Final = _Kept()


@contextlib.contextmanager
def kept() -> Generator[None]:
    """Keep the workers `started` starts until the block ends: a run's rounds share them.

    A file's second check is then by the process that has its tree and how its first check ended,
    where new processes would parse it and check it whole.
    """
    stack: contextlib.ExitStack
    with contextlib.ExitStack() as stack:
        _KEPT.stack = stack
        try:
            yield
        finally:
            _KEPT.stack = _KEPT.workers = None


def started(paths: Sequence[Path], jobs: int) -> Workers:
    """Start workers for `paths`, or ask the run's (see `kept`) about these of their files.

    Returns:
      The workers.

    """
    if _KEPT.workers is not None:
        return _KEPT.workers.over(paths)
    _KEPT.workers = (_KEPT.stack or contextlib.ExitStack()).enter_context(Workers(paths, jobs))
    return _KEPT.workers


def first_done(pending: Collection[Answering]) -> set[Answering]:
    """Wait for any of `pending` to finish.

    Returns:
      Those that have.

    """
    wait: _Wait = cast("_Wait", importlib.import_module("concurrent.futures").wait)
    return cast("set[Answering]", wait(pending, return_when=_FIRST_COMPLETED)[0])


def _started(processes: int) -> None:
    """Start a worker: its share of the kept trees' budget, and the collector off (see `collecting`)."""
    parsed.budget(processes)
    gc.disable()


def _read_share(paths: Sequence[Path]) -> list[project.Module | None]:
    """Index a worker's share of the files (see `project.read`).

    Returns:
      Each file's module, or `None`.

    """
    found: list[project.Module | None] = [project.read(path) for path in paths]
    collecting.indexed()
    return found


def check_share(
    check: Callable[[Path, Outside], FileRun],
    files: Sequence[tuple[Path, Outside]],
) -> list[FileRun]:
    """Check a share of the files (a worker's, or all of them in one process).

    Returns:
      What each found.

    """
    found: list[FileRun] = []
    path: Path
    outside: Outside
    for path, outside in files:
        found.append(check(path, outside))
        collecting.sweep()
    return found
