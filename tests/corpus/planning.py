"""The order a run's steps start in, planned by a solver from what each took in the last runs.

A run's steps on its corpora are a resource-constrained project: each holds CPUs and memory for so
long, the machine has so many of both, a suite's tests hold its port and each of its checkouts holds
one step at a time, and a step waits for those whose records it reads (`suite_steps.needs`). OR-Tools'
CP-SAT schedules that, each step's seconds as the last runs measured them (`sizing.before`), and
the CPUs and memory the runner will hold for it (`sizing.Plan.wanted`), so the plan is one it can
keep; each step's planned start is its rank, and of the steps that could start, the
one ranked first does (`sizing.Slots.take`). A step no run has measured has no rank: the runner's
rules order it (`sizing`). Where OR-Tools isn't installed, nothing is planned.
"""

import importlib
import importlib.util
import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final, cast

from tests.corpus import catalog, pipeline, sizing, suite_steps
from tests.corpus.pipeline import Job, Store
from tests.corpus.run_config import DEV, Run
from tests.corpus.trees import Tree

if TYPE_CHECKING:
    import types

    from ortools.sat.python import cp_model

_SECONDS: Final = 20.0  # the most the solver takes before the run starts
_WORKERS: Final = 2  # its threads: the run's steps are what the machine is for
_TENTHS: Final = 10  # memory in tenths of a gigabyte: the solver's demands are whole numbers
_RELEASED: Final = pipeline.part(pipeline.TESTS, pipeline.RELEASED)


class _Step:  # pylint: disable=too-few-public-methods
    """One step to plan: its corpus and name, what it takes, and the steps it waits for."""

    def __init__(self, corpus: str, name: str, wanted: sizing.Wanted, after: frozenset[str]) -> None:
        """Keep what's planned of it: what the runner holds for it (`wanted`), for its last run's seconds."""
        self.corpus: str = corpus
        self.name: str = name
        self.seconds: int = max(1, math.ceil(wanted.seconds))
        self.cpus: int = max(1, wanted.cpus)
        self.memory: int = math.ceil(wanted.memory / sizing.GIB * _TENTHS)
        self.after: frozenset[str] = after


def ranks(run: Run, entries: Sequence[catalog.Entry], plan: sizing.Plan) -> dict[tuple[str, str], float]:
    """Plan the order the run's steps start in, where OR-Tools is installed.

    Only the steps the last runs measured are planned; the timed steps, which run alone at the end,
    are not.

    Returns:
      Each planned step's start, in seconds, by its corpus's name and its own; none where nothing is
      planned.

    """
    if importlib.util.find_spec("ortools") is None:
        return {}
    steps: list[_Step] = _measured(run, entries, plan)
    return _solved(steps, plan.cpus, plan.memory, {entry.name: entry.port for entry in entries if entry.port})


def _measured(
    run: Run,
    entries: Sequence[catalog.Entry],
    plan: sizing.Plan,
) -> list[_Step]:
    """List the run's steps on `entries` that an earlier run measured, each with those it waits for.

    Each as `plan` sizes it: the CPUs and the memory the runner will hold for it, not what it used.

    Returns:
      Them.

    """
    found: list[_Step] = []
    entry: catalog.Entry
    for entry in entries:
        job: Job = Job(run, Store(Path()), Tree(entry.name, entry.version, Path(), suite=entry.suite), DEV)
        names: list[str] = [name for name in pipeline.steps(run) if name not in sizing.TIMED]
        names += list(suite_steps.waiting(job)) if entry.suite is not None else []
        needs: dict[str, frozenset[str]] = suite_steps.needs(job) if entry.suite is not None else {}
        name: str
        for name in names:
            if name == _RELEASED and not run.steps.tests_released:
                continue  # an earlier run's, most likely: not run
            if (entry.name.replace(" ", "-"), name) in plan.before:
                wanted: sizing.Wanted = plan.wanted(job.tree, name, heavy=entry.heavy)
                found.append(_Step(entry.name, name, wanted, needs.get(name, frozenset())))
    return found


def _solved(
    steps: Sequence[_Step],
    cpus: int,
    memory: int,
    ports: Mapping[str, str],
) -> dict[tuple[str, str], float]:
    """Schedule `steps` on `cpus` CPUs and `memory` bytes with CP-SAT, the shortest it finds in `_SECONDS`.

    Returns:
      Each step's start in that schedule; none where it found none.

    """
    sat: types.ModuleType = importlib.import_module("ortools.sat.python.cp_model")
    model: cp_model.CpModel = cast("type[cp_model.CpModel]", sat.CpModel)()
    starts: dict[tuple[str, str], cp_model.IntVar] = _modelled(model, steps, (cpus, memory), ports)
    solver: cp_model.CpSolver = cast("type[cp_model.CpSolver]", sat.CpSolver)()
    solver.parameters.max_time_in_seconds = _SECONDS
    solver.parameters.num_workers = _WORKERS
    solved: frozenset[int] = frozenset({cast("int", sat.OPTIMAL), cast("int", sat.FEASIBLE)})
    if solver.solve(model) not in solved:
        return {}
    return {key: float(solver.value(start)) for key, start in starts.items()}


def _modelled(
    model: "cp_model.CpModel",
    steps: Sequence[_Step],
    machine: tuple[int, int],
    ports: Mapping[str, str],
) -> dict[tuple[str, str], "cp_model.IntVar"]:
    """Lay `steps` out in `model` on the `machine`'s CPUs and bytes, the shortest end its objective.

    Returns:
      Each step's start, by its corpus's name and its own.

    """
    horizon: int = sum(step.seconds for step in steps) + 1
    starts: dict[tuple[str, str], cp_model.IntVar] = {}
    intervals: dict[tuple[str, str], cp_model.IntervalVar] = {}
    step: _Step
    for step in steps:
        key: tuple[str, str] = (step.corpus, step.name)
        starts[key] = model.new_int_var(0, horizon, f"{key}")
        intervals[key] = model.new_fixed_size_interval_var(starts[key], step.seconds, f"{key}")
    seconds: dict[tuple[str, str], int] = {(step.corpus, step.name): step.seconds for step in steps}
    end: cp_model.IntVar = model.new_int_var(0, horizon, "end")
    for step in steps:
        _ = model.add(end >= starts[step.corpus, step.name] + step.seconds)
        name: str
        for name in step.after & {other for corpus, other in starts if corpus == step.corpus}:
            _ = model.add(
                starts[step.corpus, step.name] >= starts[step.corpus, name] + seconds[step.corpus, name],
            )
    held: int = machine[1] * _TENTHS // sizing.GIB
    _ = model.add_cumulative(
        list(intervals.values()),
        [min(step.cpus, machine[0]) for step in steps],
        machine[0],
    )
    _ = model.add_cumulative(list(intervals.values()), [min(step.memory, held) for step in steps], held)
    bound: dict[str, list[cp_model.IntervalVar]] = {}
    for step in steps:
        if suite_steps.binds(step.name) and step.corpus in ports:
            bound.setdefault(ports[step.corpus], []).append(intervals[step.corpus, step.name])
    each: list[cp_model.IntervalVar]
    for each in bound.values():
        _ = model.add_no_overlap(each)
    model.minimize(end)
    return starts
