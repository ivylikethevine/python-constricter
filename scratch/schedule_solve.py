"""Find the shortest schedule of finished corpus runs' steps with a solver, beside how long each took.

The runs' steps as `schedule_sim.read` has them (each's seconds, CPUs and memory as measured, or as
the runner gave them with `--given`, and the steps of its corpus it waits for), scheduled by
OR-Tools' CP-SAT as a resource-constrained project: the steps' CPUs and memory each held within the
machine's at every moment (`AddCumulative`), a suite's tests one at a time per port, and each step
after those it waits for. The timed steps follow, one at a time, alone. Prints, for each run, how
long it took, the shortest schedule found and the bound the solver proved, and the order its first
steps start in: what the runner's own order could aim for.

Needs OR-Tools, which the project doesn't depend on; `uv` installs it for one run, from releases
older than a week:

    uv run --exclude-newer "$(date -d '7 days ago' +%F)" --with ortools python scratch/schedule_solve.py \\
        FOLDER... [--cpus 16] [--memory 36] [--given] [--seconds 60]
"""

import argparse
import math
import sys
from pathlib import Path

from ortools.sat.python import cp_model

sys.path.insert(0, str(Path(__file__).parent))
import schedule_sim  # noqa: E402  # the sibling script that reads a run's steps

_TENTHS = 10  # memory in tenths of a gigabyte: the solver's demands are whole numbers


def solve(steps: list[schedule_sim.Step], cpus: int, memory: float, seconds: float) -> tuple[float, float, list[str]]:
    """Schedule the steps with CP-SAT, `seconds` at most.

    Returns:
      The shortest schedule found and the least the solver proved, both in seconds with the timed
      steps after; and the steps by when the schedule starts them.

    """
    work: list[schedule_sim.Step] = [step for step in steps if step.name not in schedule_sim._TIMED]
    timed: float = sum(step.seconds for step in steps if step.name in schedule_sim._TIMED)
    model: cp_model.CpModel = cp_model.CpModel()
    horizon: int = math.ceil(sum(step.seconds for step in work)) + 1
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
    model.add_cumulative(list(intervals.values()), [min(step.cpus, cpus) for step in work], cpus)
    model.add_cumulative(
        list(intervals.values()),
        [min(math.ceil(step.memory * _TENTHS), math.floor(memory * _TENTHS)) for step in work],
        math.floor(memory * _TENTHS),
    )
    ports: dict[str, str] = schedule_sim.ports()
    bound: dict[str, list[cp_model.IntervalVar]] = {}
    for step in work:
        if schedule_sim.binds(step.name) and step.corpus in ports:
            bound.setdefault(ports[step.corpus], []).append(intervals[step.corpus, step.name])
    for each in bound.values():
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
    """Print each run's minutes, its shortest schedule's, and the order that schedule starts steps in."""
    parser = argparse.ArgumentParser()
    parser.add_argument("folders", type=Path, nargs="+")
    parser.add_argument("--cpus", type=int, default=16)
    parser.add_argument("--memory", type=float, default=36.0, help="gigabytes the steps share")
    parser.add_argument("--given", action="store_true", help="steps hold what the runner gave them")
    parser.add_argument("--seconds", type=float, default=60.0, help="the most the solver takes on each run")
    args = parser.parse_args()
    folder: Path
    for folder in args.folders:
        steps: list[schedule_sim.Step] = schedule_sim.read(folder, given=args.given)
        first: float = min(step.started for step in steps)
        recorded: float = max(step.started + step.seconds for step in steps) - first
        found: float
        least: float
        order: list[str]
        found, least, order = solve(steps, args.cpus, args.memory, args.seconds)
        print(f"{folder.name}: {len(steps)} steps, {args.cpus} CPUs, {args.memory:g} GB")
        print(f"  recorded {recorded / 60:.1f} min; solver {found / 60:.1f} min, proved at least {least / 60:.1f}")
        print(f"  first to start: {', '.join(order[:12])}")


if __name__ == "__main__":
    main()
