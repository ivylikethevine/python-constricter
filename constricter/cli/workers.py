# SPDX-License-Identifier: MIT
"""Worker processes for `--jobs`: each indexes its own share of the files, then checks it."""

import contextlib
import gc
import importlib
from collections.abc import Callable, Collection, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self, TypeAlias, TypeVar, cast

from constricter.cli import collecting
from constricter.cli.paths import shares
from constricter.cli.runs import FileRun
from constricter.fix.core.known import Outside
from constricter.fix.index import project
from constricter.rules import parsed

if TYPE_CHECKING:  # slow to import, and only needed for many files
    from concurrent.futures import Future, ProcessPoolExecutor

# A worker's answers, one per file of its share: what it read (to index), and what it found.
_Reading: TypeAlias = "Future[list[project.Module | None]]"
Checking: TypeAlias = "Future[list[FileRun]]"
_FIRST_COMPLETED: Final = "FIRST_COMPLETED"  # `concurrent.futures.FIRST_COMPLETED`
_Check: TypeAlias = Callable[[Path, Outside], FileRun]
_Told = TypeVar("_Told")  # what every worker is told
_Asking = TypeVar("_Asking")  # what one worker is asked
_Pending = TypeVar("_Pending")  # a worker's answer to come
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

    def tell(self, function: Callable[[_Told], None], told: _Told) -> None:
        """Run `function(told)` in every worker, and wait for them all: what each is to know from then on."""
        telling: list[Future[None]] = [pool.submit(function, told) for pool in self.pools]
        each: Future[None]
        for each in telling:
            each.result()

    def ask(
        self,
        worker: int,
        function: Callable[[_Check, _Asking], list[FileRun | None]],
        check: _Check,
        asked: _Asking,
    ) -> "Future[list[FileRun | None]]":
        """Start `function(check, asked)` in one worker: its files to check, and what it's to know for them.

        Returns:
          The answer it will give.

        """
        return self.pools[worker].submit(function, check, asked)


def first_done(pending: Collection[_Pending]) -> set[_Pending]:
    """Wait for any of `pending` to finish.

    Returns:
      Those that have.

    """
    wait: _Wait = cast("_Wait", importlib.import_module("concurrent.futures").wait)
    return cast("set[_Pending]", wait(pending, return_when=_FIRST_COMPLETED)[0])


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
