# SPDX-License-Identifier: MIT
"""Checking files in `order.plan`'s order: each after the modules whose unannotated functions it calls.

A component (files calling each other's functions) is checked once all it comes after have settled,
knowing what their functions return; then, while their `return`s change what its files import, its
files are checked again, up to `CYCLE_ROUNDS` times, before it settles. With worker processes, a
component starts as soon as it can, rather than in lockstep with the others.
"""

from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Final

from constricter.cli.runs import CoverageRun, FileRun
from constricter.cli.workers import Checking, Workers, check_share, first_done
from constricter.fix import callers, order, project, stubbed
from constricter.fix.known import Hints, Outside

CYCLE_ROUNDS: Final = 3  # how many times to check again files calling each other's functions


def outside(modules: project.Index, path: Path, hinted: Mapping[Path, tuple[Hints, ...]]) -> Outside:
    """Find what's known of a file from outside it: what it imports from the others, and its hints.

    Returns:
      It.

    """
    imported: project.Imported = project.imported(modules, path)
    methods: stubbed.Methods = stubbed.methods(modules, path)
    return Outside(
        imported.calls,
        imported.classes,
        hinted.get(path, ()),
        project.type_vars(modules, path),
        imported.returned,
        imported.guarded,
        imported.generics,
        callers.callees(modules, path),
        callers.own_parameters(modules, path),
        {**stubbed.overloaded(modules, path), **methods.signatures},
        stubbed.classes(modules, path),
        methods.parameters,
        methods.lineage,
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

    def settle(self, component: int, found: Mapping[int, FileRun]) -> dict[int, Outside]:
        """Record what a round of the component's files found, and what its functions return.

        Returns:
          Those of its files to check again, each with what it's to know now; none once it's settled.

        """
        at: int
        run: FileRun
        for at, run in found.items():
            self.runs[at] = self.merge(self.runs[at], run) if self.merge and at in self.runs else run
        self.modules = project.with_returned(
            self.modules,
            {
                self.plan.names[at]: run.returned
                for at, run in found.items()
                if at in self.plan.names and not isinstance(run, CoverageRun)
            },
        )
        self.rounds[component] += 1
        if len(self.plan.components[component]) == 1 or self.rounds[component] > CYCLE_ROUNDS:
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


class _Pooled:
    """Checking files in the workers, in `order.plan`'s order: each component once all it follows settle."""

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
        self.of: dict[int, int] = {
            at: part for part, files in enumerate(planned.plan.components) for at in files
        }
        self.left: list[int] = [0] * len(planned.plan.components)  # each component's files being checked
        self.found: dict[int, dict[int, FileRun]] = {}  # what they've found so far
        self.active: dict[Checking, list[int]] = {}  # what each worker is checking

    def run(self) -> None:
        """Check every file: start what waits for nothing, then whatever each answer lets start."""
        self.submit(
            {
                at: given
                for component, count in enumerate(self.waiting)
                if not count
                for at, given in self.planned.start(component).items()
            },
        )
        done: set[Checking]
        for done in iter(self._done, None):
            todo: dict[int, Outside] = {}
            future: Checking
            for future in done:
                at: int
                run: FileRun
                for at, run in zip(self.active.pop(future), future.result(), strict=True):
                    todo.update(self._answered(at, run))
            self.submit(todo)

    def _done(self) -> set[Checking] | None:
        """Wait for a worker's answer.

        Returns:
          Those that have answered; `None` once none is checking anything.

        """
        return first_done(self.active) if self.active else None

    def submit(self, todo: Mapping[int, Outside]) -> None:
        """Start checking `todo`'s files, each with what it's to know."""
        self.active.update((future, files) for files, future in self.pool.submit(self.check, todo))
        at: int
        for at in todo:
            self.left[self.of[at]] += 1

    def _answered(self, at: int, run: FileRun) -> dict[int, Outside]:
        """Record what file `at` found; once its component's round is done, settle it.

        Returns:
          The files to check next: the component's again, or those of the components it let start.

        """
        component: int = self.of[at]
        self.found.setdefault(component, {})[at] = run
        self.left[component] -= 1
        if self.left[component]:
            return {}
        again: dict[int, Outside]
        if again := self.planned.settle(component, self.found.pop(component)):
            return again
        follower: int
        for follower in self.followers[component]:
            self.waiting[follower] -= 1
            if not self.waiting[follower]:
                again.update(self.planned.start(follower))
        return again
