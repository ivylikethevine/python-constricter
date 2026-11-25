"""Replay a finished corpus run's steps under the runner's holds in other start orders, to see which a first run could use.

Each step holds what the runner gave it (`schedule_sim.read --given`) for the seconds it took, waits
for the steps it waits for (`suite_steps.needs`, as `schedule_solve.Kept` reads them) and takes the
locks the runner gives it (its checkouts, its tests' port). Whenever a step ends, the steps waiting
that fit start, in the order's turn, as `sizing.Slots.take` starts them without its patience rule.
Each order is a key; the least goes first:

- `as run`: the step's start in the run, which gives back the run's own order;
- `longest line, measured`: the seconds of the step and the longest line of its corpus's steps
  waiting for it, as the run measured them: what the runner's `lasting` ranks by once a run measured
  every step;
- `steps behind it`: what a first run knows without a measurement, how many steps of its corpus wait
  for it, all the way down, a suite's tests sharing a checkout counted one after another: the
  runner's own count (`tests.corpus.planning.behind`), its order among steps none measured;
- `set, then steps behind it`: the corpus's set by size and time in `corpora.toml`, slow-large first,
  then as above.

    local/.venv/bin/python scripts/scratch/start_order.py FOLDER [--cpus 16] [--memory 36] [--at-once CORPUS=N]...

`--at-once` gives a suite that many fixed test runs side by side, where its catalog entry doesn't.
Writes nothing; a second on 16CPU/60GB.
"""

import argparse
import heapq
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(1, str(Path(__file__).parents[2]))
import schedule_sim  # noqa: E402  # the sibling scripts
from schedule_solve import Kept  # noqa: E402

from tests.corpus import planning  # noqa: E402

_SETS = ("slow-large", "slow-small", "fast-large", "fast-small")
_ROOT = Path(__file__).resolve().parents[2]

Key = Callable[[schedule_sim.Step], float]


def replay(steps: list[schedule_sim.Step], kept: Kept, cpus: int, memory: float, key: Key) -> float:
    """Start the steps as the runner would in the order `key` gives, each for its recorded seconds.

    Returns:
      When the last ends, in seconds, the timed steps after it one at a time.

    """
    work: list[schedule_sim.Step] = [step for step in steps if step.name not in kept.last]
    waiting: list[schedule_sim.Step] = sorted(work, key=key)
    done: set[tuple[str, str]] = set()
    names: set[tuple[str, str]] = {(step.corpus, step.name) for step in work}
    held: set[tuple[str, str]] = set()
    running: list[tuple[float, int, schedule_sim.Step]] = []
    now: float = 0.0
    free: tuple[int, float] = (cpus, memory)
    while waiting or running:
        for step in list(waiting):
            needed: set[tuple[str, str]] = {(step.corpus, name) for name in step.after} & names
            locks: set[tuple[str, str]] = set(kept.locks(step))
            fits: bool = min(step.cpus, cpus) <= free[0] and min(step.memory, memory) <= free[1]
            if needed <= done and not locks & held and (fits or not running):
                waiting.remove(step)
                free = (free[0] - min(step.cpus, cpus), free[1] - min(step.memory, memory))
                held |= locks
                heapq.heappush(running, (now + step.seconds, id(step), step))
        if not running:
            break  # what's left waits on what never ran
        ended: schedule_sim.Step
        now, _, ended = heapq.heappop(running)
        free = (free[0] + min(ended.cpus, cpus), free[1] + min(ended.memory, memory))
        held -= set(kept.locks(ended))
        done.add((ended.corpus, ended.name))
    return now + sum(step.seconds for step in steps if step.name in kept.last)


def longest(steps: list[schedule_sim.Step]) -> dict[int, float]:
    """Find each step's seconds and the longest line of its corpus's steps waiting for it, as recorded.

    Returns:
      It, by the step's `id`.

    """
    found: dict[int, float] = {}
    by: dict[str, list[schedule_sim.Step]] = {}
    for step in steps:
        by.setdefault(step.corpus, []).append(step)

    def length(step: schedule_sim.Step) -> float:
        if id(step) not in found:
            found[id(step)] = 0.0  # a cycle, were there one, ends here
            later: list[schedule_sim.Step] = [other for other in by[step.corpus] if step.name in other.after]
            found[id(step)] = step.seconds + max((length(other) for other in later), default=0.0)
        return found[id(step)]

    for step in steps:
        _ = length(step)
    return found


def counted(steps: list[schedule_sim.Step], kept: Kept) -> dict[int, float]:
    """Count each step's steps behind it as the runner does (`tests.corpus.planning.behind`), corpus by corpus.

    Returns:
      It, by the step's `id`.

    """
    found: dict[int, float] = {}
    by: dict[str, list[schedule_sim.Step]] = {}
    for step in steps:
        by.setdefault(step.corpus, []).append(step)
    for own in by.values():
        named: dict[str, schedule_sim.Step] = {step.name: step for step in own}
        counts: dict[str, int] = planning.behind(
            list(named),
            {name: frozenset(step.after) for name, step in named.items()},
            lambda name, named=named: frozenset("/".join(lock) for lock in kept.locks(named[name])),
        )
        found |= {id(named[name]): float(count) for name, count in counts.items()}
    return found


def main() -> None:
    """Print the run's minutes as recorded, and as replayed in each order."""
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--cpus", type=int, default=16)
    parser.add_argument("--memory", type=float, default=36.0, help="gigabytes the steps share")
    parser.add_argument("--at-once", action="append", default=[], metavar="CORPUS=N")
    args = parser.parse_args()
    at_once: dict[str, int] = {
        name: int(count) for name, _, count in (each.partition("=") for each in args.at_once)
    }
    kept: Kept = Kept(args.folder, at_once)
    steps: list[schedule_sim.Step] = schedule_sim.read(args.folder, given=True, taken=True)
    kept.waits(steps)
    ran: list[schedule_sim.Step] = [step for step in steps if step.seconds]
    first: float = min(step.started for step in ran)
    recorded: float = max(step.started + step.seconds for step in ran) - first
    with (_ROOT / "tests" / "corpus" / "corpora.toml").open("rb") as file:
        sets: dict[str, list[str]] = tomllib.load(file)["sets"]
    group: dict[str, int] = {
        name.replace(" ", "-"): rank for rank, each in enumerate(_SETS) for name in sets.get(each, [])
    }
    lines: dict[int, float] = longest(steps)
    behind: dict[int, float] = counted(steps, kept)
    orders: dict[str, Key] = {
        "as run": lambda step: step.started,
        "longest line, measured": lambda step: -lines[id(step)],
        "steps behind it": lambda step: -behind[id(step)],
        "set, then steps behind it": lambda step: group.get(step.corpus, len(_SETS)) * 1e6 - behind[id(step)],
    }
    print(
        f"{args.folder.name}: {len(ran)} steps, {args.cpus} CPUs, {args.memory:g} GB, at once {at_once or '-'}"
    )
    print(f"  {'recorded':<28} {recorded / 60:5.1f} min")
    for name, key in orders.items():
        print(f"  {name:<28} {replay(steps, kept, args.cpus, args.memory, key) / 60:5.1f} min")


if __name__ == "__main__":
    main()
