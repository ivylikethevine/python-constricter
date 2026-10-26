"""Checking files in `order.plan`'s order: each after the modules whose unannotated functions it calls.

A component (files calling each other's functions) is checked once all it comes after have settled,
knowing what their functions return; then, while their `return`s change what its files import, its
files are checked again, up to `CYCLE_ROUNDS` times, before it settles. With worker processes, a
component starts as soon as it can, rather than in lockstep with the others.
"""

import pickle
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NamedTuple, cast

from constricter.cli import collecting
from constricter.cli.runs import CheckRun, CoverageRun, FileRun, shifted
from constricter.cli.workers import Again, Answering, Asked, File, Told, Workers, first_done
from constricter.empty import Empty
from constricter.fix.core.known import Hints, Outside, Returns
from constricter.fix.index import (
    linked,
    order,
    project,
)
from constricter.fix.index.across import outside
from constricter.fix.index.modules import Memo

CYCLE_ROUNDS: Final = 3  # how many times to check again files calling each other's functions


class Rounds(NamedTuple):
    """How a check stands to the files' earlier ones.

    `merge` joins a file's two rounds' runs (`None`: the later one's stands). `kept`: the last runs
    of those whose text is as it was then, by index: each is checked only if it knows anything else
    from outside now, else that run is its own.
    """

    merge: Callable[[FileRun, FileRun], FileRun] | None = None
    kept: Mapping[int, FileRun] = Empty()


class _Planned:
    """What checking the files in order has found so far, and the index as it grows."""

    def __init__(
        self,
        paths: Sequence[Path],
        modules: project.Index,
        hinted: Mapping[Path, tuple[Hints, ...]],
        rounds: Rounds,
    ) -> None:
        """Plan checking `paths` with `modules` and their hints, after `rounds`."""
        self.paths: Sequence[Path] = paths
        self.modules: project.Index = modules
        self.hinted: Mapping[Path, tuple[Hints, ...]] = hinted
        self.plan: order.Plan = order.plan(modules, paths)
        self.runs: dict[int, FileRun] = {}
        self.earlier: Rounds = rounds
        self.given: dict[int, Outside] = {}  # what each file was last checked knowing
        self.rounds: list[int] = [0] * len(self.plan.components)
        # Each file's component.
        self.of: dict[int, int] = {
            at: part for part, files in enumerate(self.plan.components) for at in files
        }

    def start(self, component: int) -> dict[int, Outside]:
        """Find what the component's files are to be checked knowing, now that it can start.

        Returns:
          Each file's; not a kept one's (see `checked`) that knows what it was last checked knowing.

        """
        given: dict[int, Outside] = self._known(component)
        self.given.update(given)
        return {
            at: known
            for at, known in given.items()
            if at not in self.earlier.kept or _WORKER.given.get(self.paths[at]) != known
        }

    def _known(self, component: int) -> dict[int, Outside]:
        """Find what each of the component's files knows from outside it now (see `outside`).

        Returns:
          Each one's.

        """
        return {
            at: outside(self.modules, self.paths[at], self.hints_of(at))
            for at in self.plan.components[component]
        }

    def hints_of(self, at: int) -> Mapping[Path, tuple[Hints, ...]]:
        """Find file `at`'s hints, at their places in its text as this round's fixes have left it.

        A file in a cycle is checked again within the round, its earlier checks' fixes written: the
        hints were asked on the text before them (see `runs.shifted`).

        Returns:
          What `outside` reads: the round's hints, the file's moved past the lines its checks added.

        """
        run: FileRun | None = self.runs.get(at)  # this round's checks of it, joined (see `runs.merged`)
        path: Path = self.paths[at]
        if not isinstance(run, CheckRun) or not run.rounds or path not in self.hinted:
            return self.hinted
        return {path: tuple(shifted(found, run.rounds) for found in self.hinted[path])}

    def record(self, component: int, found: Mapping[int, FileRun]) -> dict[str, Returns]:
        """Record what a round of the component's files found, and what its functions return.

        Returns:
          What each checked module's functions return now, by its name.

        """
        merge: Callable[[FileRun, FileRun], FileRun] | None = self.earlier.merge
        at: int
        run: FileRun
        for at, run in found.items():
            self.runs[at] = merge(self.runs[at], run) if merge and at in self.runs else run
        returned: dict[str, Returns] = {
            self.plan.names[at]: run.returned
            for at, run in found.items()
            if at in self.plan.names and not isinstance(run, CoverageRun)
        }
        self.modules = linked.with_returned(self.modules, returned)
        self.rounds[component] += 1
        return returned

    def settled(self, component: int) -> bool:
        """Check whether the component has no more rounds to run: one file, or `CYCLE_ROUNDS` done.

        Returns:
          Whether it is.

        """
        return len(self.plan.components[component]) == 1 or self.rounds[component] > CYCLE_ROUNDS

    def settle(self, component: int, found: Mapping[int, FileRun]) -> dict[int, Outside]:
        """Record a round (see `record`), and find what to check again, in this process.

        Returns:
          Those of its files to check again, each with what it's to know now; none once it's settled.

        """
        _ = self.record(component, found)
        if self.settled(component):
            return {}
        again: dict[int, Outside] = {
            at: known
            for at, known in self._known(component).items()
            if known.returned != self.given[at].returned
        }
        self.given.update(again)
        return again


def checked(
    paths: Sequence[Path],
    check: Callable[[Path, Outside], FileRun],
    pool: Workers | None,
    known: tuple[project.Index, Mapping[Path, tuple[Hints, ...]]],
    rounds: Rounds,
) -> tuple[list[FileRun], project.Index]:
    """Check `paths` in order (see `order.plan`), in `pool`'s workers or this process.

    `known`: the index and each file's hints; `rounds`: how this check stands to earlier ones.

    Returns:
      What each file found, and the index, with what their functions return.

    """
    planned: _Planned = _Planned(paths, known[0], known[1], rounds)
    if pool is None:
        component: int
        for component in range(len(planned.plan.components)):
            _in_process(planned, check, component, planned.start(component))
    else:
        _Pooled(planned, check, pool).run()
    runs: list[FileRun] = [planned.runs.get(at) or planned.earlier.kept[at] for at in range(len(paths))]
    return runs, planned.modules


def _in_process(
    planned: _Planned,
    check: Callable[[Path, Outside], FileRun],
    component: int,
    todo: Mapping[int, Outside],
) -> None:
    """Check a component's files here (`todo`: each with what it's to know), round by round."""
    runs: dict[int, FileRun] = {}
    at: int
    given: Outside
    for at, given in todo.items():
        runs[at] = check(planned.paths[at], given)
        collecting.sweep()
    _WORKER.given.update((planned.paths[at], given) for at, given in todo.items())
    if todo:
        _in_process(planned, check, component, planned.settle(component, runs))


@dataclass
class _Worker:
    """What a worker process knows: the index it was sent, and what each of its files last knew.

    A run checking alone keeps the latter here too: its files' checks, round after round.
    """

    modules: project.Index = field(default_factory=lambda: project.Index({}, []))
    given: dict[Path, Outside] = field(default_factory=dict[Path, Outside])


@dataclass
class _News:
    """What each recorded round's modules return, and how much of it each worker has been told."""

    returned: list[dict[str, Returns]]
    told: list[int]

    def since(self, worker: int) -> dict[str, Returns]:
        """Gather what a worker hasn't been told yet, which it's told now.

        Returns:
          Each such module's returns, the latest of each.

        """
        news: dict[str, Returns] = {}
        last: int = self.told[worker]
        each: dict[str, Returns]
        for each in self.returned[last:]:
            news.update(each)
        self.told[worker] = len(self.returned)
        return news


_WORKER: Final = _Worker()


def sent(modules: project.Index) -> bytes:
    """Pickle the index for the workers: once, for them all, each then reading it at the same time.

    Returns:
      It, without what it keeps worked out, which each worker works out for itself.

    """
    return pickle.dumps(modules._replace(memo=None), pickle.HIGHEST_PROTOCOL)


def know(index: Told) -> None:
    """Take the index (see `sent`), in a worker process: what it works its files' `Outside` out from."""
    _WORKER.modules = cast("project.Index", pickle.loads(index))._replace(memo=Memo())


def forget() -> None:
    """Forget what each file was last checked knowing, as a run starts: its workers are new."""
    _WORKER.given.clear()


def check_asked(check: Callable[[Path, Outside], FileRun], asked: Asked) -> list[FileRun | None]:
    """Check a worker's files, each knowing what the worker's index says of it now.

    Returns:
      What each found; `None` for one left unchecked, knowing what it last did (see `Again`).

    """
    files: Sequence[File]
    returned: Mapping[str, Returns]
    again: Again
    files, returned, again = asked
    _WORKER.modules = linked.with_returned(_WORKER.modules, returned)
    found: list[FileRun | None] = []
    path: Path
    hints: tuple[Hints, ...]
    for path, hints in files:
        known: Outside = outside(_WORKER.modules, path, {path: hints} if hints else {})
        last: Outside | None = _WORKER.given.get(path)
        if last is not None and (
            (again is Again.RETURNED and known.returned == last.returned)
            or (again is Again.OUTSIDE and known == last)
        ):
            found.append(None)
            continue
        _WORKER.given[path] = known
        found.append(check(path, known))
        collecting.sweep()
    return found


class _Pooled:
    """Checking files in the workers, in `order.plan`'s order: each component once all it follows settle.

    Each worker has the index, and works out what its files know from outside as it reaches them:
    it's told what the checked modules' functions return since it was last asked (`told`).
    """

    def __init__(self, planned: _Planned, check: Callable[[Path, Outside], FileRun], pool: Workers) -> None:
        """Plan the order: what each component waits for, and what follows it."""
        self.planned: _Planned = planned
        self.check: Callable[[Path, Outside], FileRun] = check
        self.pool: Workers = pool
        self.waiting: list[int] = [len(after) for after in planned.plan.after]  # components still to settle
        self.followers: list[list[int]] = [[] for _ in planned.plan.components]
        component: int
        after: frozenset[int]
        for component, after in enumerate(planned.plan.after):
            callee: int
            for callee in after:
                self.followers[callee].append(component)
        self.left: list[int] = [0] * len(planned.plan.components)  # each component's files being checked
        self.found: dict[int, dict[int, FileRun]] = {}  # what they've found so far
        self.active: dict[Answering, list[int]] = {}  # what each worker is checking
        self.news: _News = _News([], [0] * len(pool.shares))

    def run(self) -> None:
        """Check every file: start what waits for nothing, then whatever each answer lets start."""
        self.pool.tell(know, sent(self.planned.modules))
        self.submit(
            [
                at
                for component, count in enumerate(self.waiting)
                if not count
                for at in self.planned.plan.components[component]
            ],
            again=False,
        )
        done: set[Answering]
        for done in iter(self._done, None):
            first: list[int] = []
            again: list[int] = []
            future: Answering
            for future in done:
                at: int
                run: FileRun | None
                for at, run in zip(self.active.pop(future), future.result(), strict=True):
                    todo: tuple[list[int], bool] = self._answered(at, run)
                    (again if todo[1] else first).extend(todo[0])
            self.submit(first, again=False)
            self.submit(again, again=True)

    def _done(self) -> set[Answering] | None:
        """Wait for a worker's answer.

        Returns:
          Those that have answered; `None` once none is checking anything.

        """
        return first_done(self.active) if self.active else None

    def submit(self, files: Sequence[int], *, again: bool) -> None:
        """Start checking `files` (by index), each by its worker.

        `again`: only those whose imports return something else now. Otherwise a kept file (see
        `checked`) only if it knows anything else from outside now.
        """
        if not files:
            return
        paths: Sequence[Path] = self.planned.paths
        kept: Mapping[int, FileRun] = self.planned.earlier.kept
        wanted: frozenset[int] = frozenset(files)
        worker: int
        share: list[int]
        for worker, share in enumerate(self.pool.shares):
            mine: list[int] = [at for at in share if at in wanted]
            each: list[int]
            how: Again
            for each, how in (
                [(mine, Again.RETURNED)]
                if again
                else [
                    ([at for at in mine if at not in kept], Again.NO),
                    ([at for at in mine if at in kept], Again.OUTSIDE),
                ]
            ):
                if each:
                    given: list[File] = [
                        (paths[at], self.planned.hints_of(at).get(paths[at], ())) for at in each
                    ]
                    asked: Asked = (given, self.news.since(worker), how)
                    self.active[self.pool.ask(worker, check_asked, self.check, asked)] = each
        at: int
        for at in files:
            self.left[self.planned.of[at]] += 1

    def _answered(self, at: int, run: FileRun | None) -> tuple[list[int], bool]:
        """Record what file `at` found (`None`: left unchecked); its component's round done, settle it.

        Returns:
          The files to check next, and whether again (the component's, where their imports return
          anew) or for the first time (those of the components it let start).

        """
        component: int = self.planned.of[at]
        if run is not None:
            self.found.setdefault(component, {})[at] = run
        self.left[component] -= 1
        if self.left[component]:
            return [], False
        found: dict[int, FileRun]
        # None found: every file's imports return what they did, and the component's settled.
        if found := self.found.pop(component, {}):
            self.news.returned.append(self.planned.record(component, found))
            if not self.planned.settled(component):
                return list(self.planned.plan.components[component]), True
        started: list[int] = []
        follower: int
        for follower in self.followers[component]:
            self.waiting[follower] -= 1
            if not self.waiting[follower]:
                started.extend(self.planned.plan.components[follower])
        return started, False
