# SPDX-License-Identifier: MIT
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
from typing import Final, cast

from constricter.cli import collecting
from constricter.cli.runs import CoverageRun, FileRun
from constricter.cli.workers import Answering, Asked, File, Workers, check_share, first_done
from constricter.fix.core.known import Guarded, Hints, Outside, Passed, Returns
from constricter.fix.index import (
    awaits,
    beyond,
    callers,
    decorated,
    fixtures,
    linked,
    loose,
    offers,
    order,
    own_types,
    plain,
    project,
    sides,
    stubbed,
    tuples,
)
from constricter.fix.index.modules import Memo

CYCLE_ROUNDS: Final = 3  # how many times to check again files calling each other's functions


def outside(modules: project.Index, path: Path, hinted: Mapping[Path, tuple[Hints, ...]]) -> Outside:
    """Find what's known of a file from outside it: what it imports from the others, and its hints.

    Returns:
      It.

    """
    seeded: dict[str, Guarded] = {}
    seeds: dict[str, Passed] = fixtures.visible(modules, path, seeded)
    imported: project.Imported = project.imported(
        modules,
        path,
        (seeded, fixtures.attributes(seeds)),
    )
    side_calls: dict[str, str]
    guarded: dict[str, Guarded]
    side_calls, guarded = sides.calls(modules, path, imported.guarded)
    methods: stubbed.Methods = stubbed.methods(modules, path, guarded)
    hints: tuple[Hints, ...] = offers.vetted(modules, path, hinted.get(path, ()))
    # What only a hint can name: the classes the file imports for type checking alone.
    own: offers.Own = offers.own(modules, path) if hints else offers.Own()
    return Outside(
        calls={**imported.calls, **side_calls, **decorated.own(modules, path)},
        classes=imported.classes,
        hints=hints,
        type_vars=project.type_vars(modules, path),
        returned=loose.returned(modules, path, guarded, imported.returned),
        guarded=guarded,
        generics=imported.generics | own.generics,
        callees=callers.callees(modules, path),
        parameters=callers.own_parameters(modules, path),
        overloaded={**stubbed.overloaded(modules, path, guarded), **methods.signatures},
        installed_classes=stubbed.classes(modules, path),
        installed_parameters=methods.parameters,
        installed_lineage={**own_types.lineages(modules, path, guarded), **methods.lineage},
        installed_aliases=methods.aliases,
        checking=own.guarded,
        plain=plain.classes(modules, path),
        members=imported.members,
        same=linked.same(modules, path, guarded),
        partial=imported.partial,
        tuples=tuples.fields(modules, path, guarded),
        fixtures=seeds,
        beyond=beyond.library_bases(modules, path),
        awaits=awaits.calls(modules, path, guarded),
        values=linked.values(modules, path),
        untyped=linked.untyped(modules, path),
        unions=tuples.unions(modules, path, guarded),
    )


class _Planned:
    """What checking the files in order has found so far, and the index as it grows."""

    def __init__(
        self,
        paths: Sequence[Path],
        modules: project.Index,
        hinted: Mapping[Path, tuple[Hints, ...]],
        merge: Callable[[FileRun, FileRun], FileRun] | None,
    ) -> None:
        """Plan checking `paths` with `modules` and their hints; `merge` joins a file's two rounds' runs."""
        self.paths: Sequence[Path] = paths
        self.modules: project.Index = modules
        self.hinted: Mapping[Path, tuple[Hints, ...]] = hinted
        self.merge: Callable[[FileRun, FileRun], FileRun] | None = merge
        self.plan: order.Plan = order.plan(modules, paths)
        self.runs: dict[int, FileRun] = {}
        self.given: dict[int, Outside] = {}  # what each file was last checked knowing
        self.rounds: list[int] = [0] * len(self.plan.components)
        # Each file's component.
        self.of: dict[int, int] = {
            at: part for part, files in enumerate(self.plan.components) for at in files
        }

    def start(self, component: int) -> dict[int, Outside]:
        """Find what the component's files are to be checked knowing, now that it can start.

        Returns:
          Each file's.

        """
        given: dict[int, Outside] = {
            at: outside(self.modules, self.paths[at], self.hinted) for at in self.plan.components[component]
        }
        self.given.update(given)
        return given

    def record(self, component: int, found: Mapping[int, FileRun]) -> dict[str, Returns]:
        """Record what a round of the component's files found, and what its functions return.

        Returns:
          What each checked module's functions return now, by its name.

        """
        at: int
        run: FileRun
        for at, run in found.items():
            self.runs[at] = self.merge(self.runs[at], run) if self.merge and at in self.runs else run
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
            at: outside(self.modules, self.paths[at], self.hinted) for at in self.plan.components[component]
        }
        again = {at: known for at, known in again.items() if known.returned != self.given[at].returned}
        self.given.update(again)
        return again


def checked(
    paths: Sequence[Path],
    check: Callable[[Path, Outside], FileRun],
    pool: Workers | None,
    known: tuple[project.Index, Mapping[Path, tuple[Hints, ...]]],
    merge: Callable[[FileRun, FileRun], FileRun] | None = None,
) -> tuple[list[FileRun], project.Index]:
    """Check `paths` in order (see `order.plan`), in `pool`'s workers or this process.

    `known`: the index and each file's hints; `merge` joins a file's two rounds' runs (`None`: the
    later one's stands).

    Returns:
      What each file found, and the index, with what their functions return.

    """
    planned: _Planned = _Planned(paths, known[0], known[1], merge)
    if pool is None:
        component: int
        for component in range(len(planned.plan.components)):
            _in_process(planned, check, component, planned.start(component))
    else:
        _Pooled(planned, check, pool).run()
    return [planned.runs[at] for at in range(len(paths))], planned.modules


def _in_process(
    planned: _Planned,
    check: Callable[[Path, Outside], FileRun],
    component: int,
    todo: Mapping[int, Outside],
) -> None:
    """Check a component's files here (`todo`: each with what it's to know), round by round."""
    if todo:
        runs: list[FileRun] = check_share(check, [(planned.paths[at], given) for at, given in todo.items()])
        _in_process(planned, check, component, planned.settle(component, dict(zip(todo, runs, strict=True))))


@dataclass
class _Worker:
    """What a worker process knows: the index it was sent, and what each of its files last knew."""

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


def know(index: bytes) -> None:
    """Take the index (see `sent`), in a worker process: what it works its files' `Outside` out from."""
    _WORKER.modules = cast("project.Index", pickle.loads(index))._replace(memo=Memo())
    _WORKER.given.clear()


def check_asked(check: Callable[[Path, Outside], FileRun], asked: Asked) -> list[FileRun | None]:
    """Check a worker's files, each knowing what the worker's index says of it now.

    Returns:
      What each found; `None` for one left unchecked, what it imports returning what it did.

    """
    files: Sequence[File]
    returned: Mapping[str, Returns]
    again: bool
    files, returned, again = asked
    _WORKER.modules = linked.with_returned(_WORKER.modules, returned)
    found: list[FileRun | None] = []
    path: Path
    hints: tuple[Hints, ...]
    for path, hints in files:
        known: Outside = outside(_WORKER.modules, path, {path: hints} if hints else {})
        if again and path in _WORKER.given and known.returned == _WORKER.given[path].returned:
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

        `again`: only those whose imports return something else now.
        """
        if not files:
            return
        hinted: Mapping[Path, tuple[Hints, ...]] = self.planned.hinted
        paths: Sequence[Path] = self.planned.paths
        wanted: frozenset[int] = frozenset(files)
        worker: int
        share: list[int]
        for worker, share in enumerate(self.pool.shares):
            mine: list[int]
            if not (mine := [at for at in share if at in wanted]):
                continue
            given: list[File] = [(paths[at], hinted.get(paths[at], ())) for at in mine]
            asked: Asked = (given, self.news.since(worker), again)
            self.active[self.pool.ask(worker, check_asked, self.check, asked)] = mine
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
