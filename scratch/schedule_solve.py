"""Find the shortest schedule of finished corpus runs' steps with a solver, beside how long each took.

The runs' steps as `schedule_sim.read` has them (each's seconds, CPUs and memory as measured, or as
the runner gave them with `--given`), scheduled by OR-Tools' CP-SAT as a resource-constrained
project under what the runner itself keeps: the steps' CPUs and memory each held within the
machine's at every moment (`AddCumulative`), a suite's tests one at a time per port, a suite's
checkouts one step at a time each (`suite_checkouts.checkouts`, as the runner locks them), and each
step after those it waits for, by `suite_steps.needs` of the run's own file, read as the run read
it: of the runs before it alone. The tests as released an earlier run's record stood for are a step
of no seconds, so what waits for them still waits for the traced tests that confirmed it. The
timed steps follow, one at a time, alone, unless the run file's `timing-beside` runs them as any
other. Prints, for each run, how long it took, the shortest schedule found and the bound the solver
proved, the order its first steps start in, and what of that model the run itself broke (`broken`):
with `--given` nothing, where the model is the runner's.

Needs OR-Tools, which the dev group installs:

    local/.venv/bin/python scratch/schedule_solve.py FOLDER... [--cpus 16] [--memory 36]
        [--given [--only cpus|memory]] [--seconds 60] [--staged [--pauses SECONDS]]

`--staged` holds each of the runner's built-in stages to start once the one before it has ended, as
a run in stages does; `--pauses` leaves the seconds between them out of the recorded time. About
the `--seconds` given for each run, 2 workers on 16CPU/60GB.
"""

import argparse
import functools
import math
import sys
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(1, str(Path(__file__).parent.parent))
import schedule_sim  # noqa: E402  # the sibling script that reads a run's steps

from tests.corpus import archive, catalog, run_config, sizing, stages, suite_checkouts, suite_steps  # noqa: E402
from tests.corpus.pipeline import Job, Store  # noqa: E402
from tests.corpus.trees import Tree  # noqa: E402

_TENTHS = 10  # memory in tenths of a gigabyte: the solver's demands are whole numbers
_SLACK = 1.0  # seconds a recorded start may come before what it waits for ends: both are rounded


def staged(steps: list[schedule_sim.Step]) -> dict[tuple[str, str], int]:
    """Find the stage each step runs in, by the built-in stages' order: its own, or a later one it waits for.

    Returns:
      Each step's stage, as its index in `stages.BUILT_IN`.

    """
    order: dict[str, int] = {name: index for index, (name, _) in enumerate(stages.BUILT_IN)}
    found: dict[tuple[str, str], int] = {
        (step.corpus, step.name): order[stages.stage_of(step.name, stages.BUILT_IN)] for step in steps
    }
    changed: bool = True
    while changed:  # a step needing another stage's record runs in that one (`stages.runnable`)
        changed = False
        for step in steps:
            key: tuple[str, str] = (step.corpus, step.name)
            needed: list[int] = [
                found[step.corpus, name] for name in step.after if (step.corpus, name) in found
            ]
            if needed and max(needed) > found[key]:
                found[key], changed = max(needed), True
    return found


class Kept:
    """What the runner keeps of a run's steps beside the machine's CPUs and memory: its file's."""

    def __init__(self, folder: Path) -> None:
        """Read the run file in `folder`, and each of its suites' jobs as the run made them."""
        self.run: run_config.Run = run_config.read(folder / "run.toml")
        known: catalog.Catalog = catalog.load()
        names: list[str] = known.names(list(self.run.include), list(self.run.minus))
        self.entries: dict[str, catalog.Entry] = {
            run_config.directory(name): known.entry(name) for name in names
        }
        self.jobs: dict[str, Job] = {
            corpus: Job(
                self.run,
                Store(folder),
                Tree(entry.name, entry.version, Path(), suite=entry.suite),
                run_config.DEV,
            )
            for corpus, entry in self.entries.items()
            if entry.suite is not None
        }
        # The runs a step's wait may hang on (`suite_steps.earlier`) are those before this one.
        # Each of their reports is read once, not once a suite.
        before = run_config.started(folder)
        every, read = archive.runs, archive.kept
        archive.runs = lambda output: [each for each in every(output) if run_config.started(each) < before]
        archive.kept = functools.cache(read)
        try:
            self.needs: dict[str, dict[str, frozenset[str]]] = {
                corpus: suite_steps.needs(job) for corpus, job in self.jobs.items()
            }
        finally:
            archive.runs, archive.kept = every, read
        self.last: frozenset[str] = sizing.held_last(self.run)

    def waits(self, steps: list[schedule_sim.Step]) -> None:
        """Give each step the steps of its corpus the runner starts it after (`Runner._versioned`)."""
        for step in steps:
            step.after = set(self.needs.get(step.corpus, {}).get(step.name, frozenset()))

    def locks(self, step: schedule_sim.Step) -> tuple[tuple[str, str], ...]:
        """Name the locks a step holds as it runs (`Runner.locks`): its checkouts', and its tests' port's.

        Returns:
          Them; none for a step of no seconds, which never started.

        """
        entry: catalog.Entry | None = self.entries.get(step.corpus)
        if entry is None or not step.seconds:
            return ()
        held: list[tuple[str, str]] = [
            (step.corpus, each)
            for each in (
                suite_checkouts.checkouts(self.jobs[step.corpus], step.name)
                if step.corpus in self.jobs
                else ()
            )
        ]
        if suite_checkouts.binds(step.name) and entry.port:
            held.append(("port", str(entry.port)))
        return tuple(held)


def broken(steps: list[schedule_sim.Step], kept: Kept, cpus: int, memory: float) -> list[str]:
    """Check the run as recorded against the model: what the solver is held to and the run wasn't.

    Returns:
      A line for each: a step started before one it waits for ended, two steps held a lock at once,
      or the steps running held more than the machine's CPUs or memory.

    """
    by: dict[tuple[str, str], schedule_sim.Step] = {(step.corpus, step.name): step for step in steps}
    ends: dict[tuple[str, str], float] = {}

    def end(step: schedule_sim.Step) -> float:
        key: tuple[str, str] = (step.corpus, step.name)
        if key not in ends:
            waited: list[float] = [
                end(by[step.corpus, name]) for name in step.after if (step.corpus, name) in by
            ]
            ends[key] = step.started + step.seconds if step.seconds else max(waited, default=0.0)
        return ends[key]

    found: list[str] = []
    ran: list[schedule_sim.Step] = [step for step in steps if step.seconds]
    for step in ran:
        for name in sorted(step.after):
            other: schedule_sim.Step | None = by.get((step.corpus, name))
            if other is not None and step.started + _SLACK < end(other):
                found.append(
                    f"{step.corpus}/{step.name} started {end(other) - step.started:.0f}s before {name} ended"
                )
    holding: dict[tuple[str, str], list[schedule_sim.Step]] = {}
    for step in ran:
        for lock in kept.locks(step):
            holding.setdefault(lock, []).append(step)
    for lock, held in holding.items():
        held.sort(key=lambda step: step.started)
        for first, second in zip(held, held[1:]):
            if second.started + _SLACK < end(first):
                found.append(
                    f"{second.corpus}/{second.name} started {end(first) - second.started:.0f}s before"
                    f" {first.corpus}/{first.name} freed {'/'.join(lock)}"
                )
    beside: list[schedule_sim.Step] = [step for step in ran if step.name not in kept.last]
    most: tuple[int, float] = (0, 0.0)
    for step in beside:
        running: list[schedule_sim.Step] = [
            other for other in beside if other.started <= step.started < end(other) - _SLACK
        ]
        most = (
            max(most[0], sum(min(other.cpus, cpus) for other in running)),
            max(most[1], sum(min(other.memory, memory) for other in running)),
        )
    if most[0] > cpus:
        found.append(f"its steps held {most[0]} CPUs at once, of {cpus}")
    if most[1] > memory:
        found.append(f"its steps held {most[1]:.1f} GB at once, of {memory:g}")
    return found


def solve(
    steps: list[schedule_sim.Step],
    kept: Kept,
    machine: tuple[int, float],
    seconds: float,
    in_stages: bool = False,
) -> tuple[float, float, list[str]]:
    """Schedule the steps with CP-SAT, `seconds` at most; `in_stages`, each stage after the one before it ends.

    Returns:
      The shortest schedule found and the least the solver proved, both in seconds with the steps
      held to the end after; and the steps by when the schedule starts them.

    """
    cpus: int
    memory: float
    cpus, memory = machine
    work: list[schedule_sim.Step] = [step for step in steps if step.name not in kept.last]
    timed: float = sum(step.seconds for step in steps if step.name in kept.last)
    model: cp_model.CpModel = cp_model.CpModel()
    horizon: int = math.ceil(sum(step.seconds for step in work)) + len(work) + 1
    starts: dict[tuple[str, str], cp_model.IntVar] = {}
    intervals: dict[tuple[str, str], cp_model.IntervalVar] = {}
    step: schedule_sim.Step
    for step in work:
        key: tuple[str, str] = (step.corpus, step.name)
        starts[key] = model.new_int_var(0, horizon, f"start {key}")
        intervals[key] = model.new_fixed_size_interval_var(starts[key], math.ceil(step.seconds), f"{key}")
    for step in work:
        name: str
        for name in step.after:
            if (step.corpus, name) in intervals:
                model.add(starts[step.corpus, step.name] >= intervals[step.corpus, name].end_expr())
    if in_stages:
        stage: dict[tuple[str, str], int] = staged(work)
        ends: list[cp_model.IntVar] = [
            model.new_int_var(0, horizon, f"stage {index} ends") for index in range(len(stages.BUILT_IN))
        ]
        for key, index in stage.items():
            model.add(ends[index] >= intervals[key].end_expr())
            if index:
                model.add(starts[key] >= ends[index - 1])
        for index in range(1, len(ends)):
            model.add(ends[index] >= ends[index - 1])
    running: list[schedule_sim.Step] = [step for step in work if step.seconds]
    model.add_cumulative(
        [intervals[step.corpus, step.name] for step in running],
        [min(step.cpus, cpus) for step in running],
        cpus,
    )
    model.add_cumulative(
        [intervals[step.corpus, step.name] for step in running],
        [min(math.ceil(step.memory * _TENTHS), math.floor(memory * _TENTHS)) for step in running],
        math.floor(memory * _TENTHS),
    )
    held: dict[tuple[str, str], list[cp_model.IntervalVar]] = {}
    for step in running:
        for lock in kept.locks(step):
            held.setdefault(lock, []).append(intervals[step.corpus, step.name])
    for each in held.values():
        model.add_no_overlap(each)
    end: cp_model.IntVar = model.new_int_var(0, horizon, "end")
    model.add_max_equality(end, [interval.end_expr() for interval in intervals.values()])
    model.minimize(end)
    solver: cp_model.CpSolver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_workers = 2  # light: other runs may be measuring
    status: int = solver.solve(model)
    if status not in {cp_model.OPTIMAL, cp_model.FEASIBLE}:
        return math.inf, solver.best_objective_bound + timed, []
    order: list[str] = [
        f"{key[0]}/{key[1]}" for key in sorted(starts, key=lambda key: solver.value(starts[key]))
    ]
    return solver.objective_value + timed, solver.best_objective_bound + timed, order


def main() -> None:
    """Print each run's minutes, its shortest schedule's, the order that starts steps in, and what it broke."""
    parser = argparse.ArgumentParser()
    parser.add_argument("folders", type=Path, nargs="+")
    parser.add_argument("--cpus", type=int, default=16)
    parser.add_argument("--memory", type=float, default=36.0, help="gigabytes the steps share")
    parser.add_argument("--given", action="store_true", help="steps hold what the runner gave them")
    parser.add_argument("--only", choices=["cpus", "memory"], default="", help="with --given: that alone")
    parser.add_argument("--seconds", type=float, default=60.0, help="the most the solver takes on each run")
    parser.add_argument("--staged", action="store_true", help="each built-in stage after the one before it")
    parser.add_argument(
        "--pauses", type=float, default=0.0, help="seconds between the stages, left out of recorded"
    )
    args = parser.parse_args()
    folder: Path
    for folder in args.folders:
        kept: Kept = Kept(folder)
        steps: list[schedule_sim.Step] = schedule_sim.read(
            folder, given=args.given, only=args.only, taken=True
        )
        kept.waits(steps)
        ran: list[schedule_sim.Step] = [step for step in steps if step.seconds]
        first: float = min(step.started for step in ran)
        recorded: float = max(step.started + step.seconds for step in ran) - first - args.pauses
        found: float
        least: float
        order: list[str]
        found, least, order = solve(steps, kept, (args.cpus, args.memory), args.seconds, args.staged)
        print(f"{folder.name}: {len(ran)} steps, {args.cpus} CPUs, {args.memory:g} GB")
        print(
            f"  recorded {recorded / 60:.1f} min; solver {found / 60:.1f} min, proved at least {least / 60:.1f}"
        )
        print(f"  first to start: {', '.join(order[:12])}")
        breaks: list[str] = broken(steps, kept, args.cpus, args.memory)
        print(
            f"  the run broke {len(breaks)} of the model's holds"
            + ("" if breaks else ": the model is the runner's")
        )
        for line in breaks[:20]:
            print(f"    {line}")


if __name__ == "__main__":
    main()
