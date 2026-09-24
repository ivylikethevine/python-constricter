# SPDX-License-Identifier: MIT
"""Worker processes for `--jobs`: each indexes its own share of the files, then checks it."""

import contextlib
import gc
import importlib
from collections.abc import Callable, Collection, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final, Self, TypeAlias, cast

from constricter.cli import collecting
from constricter.cli.paths import shares
from constricter.cli.runs import FileRun
from constricter.fix import project
from constricter.fix.known import Outside
from constricter.rules import parsed

if TYPE_CHECKING:  # slow to import, and only needed for many files
    from concurrent.futures import Future, ProcessPoolExecutor

# A worker's answers, one per file of its share: what it read (to index), and what it found.
_Reading: TypeAlias = "Future[list[project.Module | None]]"
Checking: TypeAlias = "Future[list[FileRun]]"
_FIRST_COMPLETED: Final = "FIRST_COMPLETED"  # `concurrent.futures.FIRST_COMPLETED`
_Waited: TypeAlias = tuple[set[Checking], set[Checking]]  # `concurrent.futures.wait`'s: done, and not
_Share: TypeAlias = tuple[list[int], Checking]  # a worker's files to check, by index, and its answer


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

    def submit(
        self,
        check: Callable[[Path, Outside], FileRun],
        outside: Mapping[int, Outside],
    ) -> list[_Share]:
        """Start checking the files `outside` has (by index), each by the worker that indexed it.

        Returns:
          Each worker's files given, by index, and the answer it will give for them, in their order.

        """
        mine: list[list[int]] = [[at for at in share if at in outside] for share in self.shares]
        return [
            (files, pool.submit(check_share, check, [(self.paths[at], outside[at]) for at in files]))
            for pool, files in zip(self.pools, mine, strict=True)
            if files
        ]


def first_done(pending: Collection[Checking]) -> set[Checking]:
    """Wait for any of `pending` to finish.

    Returns:
      Those that have.

    """
    wait: Callable[..., _Waited] = cast(
        "Callable[..., _Waited]",
        importlib.import_module("concurrent.futures").wait,
    )
    return wait(pending, return_when=_FIRST_COMPLETED)[0]


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
