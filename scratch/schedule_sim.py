"""Replay finished corpus runs' steps under other schedules, to see which ends soonest and how near the best.

Reads every `records/<corpus>/<version>/<step>.json` of each run folder given: each step's seconds,
CPU seconds and peak memory as measured, and when it started. A step needs its average CPUs
(`cpu / seconds`, at least 1) and its peak memory with the runner's 25% margin; with `--given`, what
the runner gave it. Its order within a corpus is the runner's: `traced` after `fix-unsafe`;
`infer-trace` after `traced`; `tests` and `types` after every fix; a suite's `tests` and `traced` one
at a time per port; `timing` and `profile` last, one at a time, alone.

For each run it prints how long it took, the least any schedule could take (`bounds`), and how long
each order replays in. `--sweep` searches the runner's settings, its order, `_PATIENCE` and
`_BESIDE`, for the ones that end soonest over every run given together.

    python3 scratch/schedule_sim.py FOLDER... [--cpus 16] [--memory 36] [--given] [--sweep]
"""

import argparse
import heapq
import itertools
import json
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_TIMED = {"timing", "profile"}
_SUITE = {"tests", "traced"}
_MARGIN = 1.25
_PATIENCE = 300.0  # the runner's: a step waits so long before what's free is kept for it
_BESIDE = 300.0  # and a step whose last run took so long at most starts beside it


@dataclass
class Step:
    """One step as recorded."""

    corpus: str
    name: str
    seconds: float
    cpus: int
    memory: float
    started: float
    cpu: float = 0.0  # its CPU seconds
    group: str = ""
    after: set[str] = field(default_factory=set)  # this corpus's steps it waits for


def read(folder: Path, *, given: bool = False) -> list[Step]:
    """Read a run's steps, each with the steps of its corpus it waits for.

    With `given`, a step holds the CPUs and memory the runner gave it, not what it used.
    """
    steps: list[Step] = []
    for record in sorted(folder.glob("records/*/*/*.json")):
        used = json.loads(record.read_text()).get("used") or {}
        if not used.get("seconds"):
            continue
        seconds = float(used["seconds"])
        cpu = float(used.get("cpu", 0))
        cpus = max(1, min(16, round(cpu / seconds)))
        memory = float(used.get("memory", 0)) * _MARGIN
        if given and used.get("given"):
            cpus, memory = int(used["given"]["cpus"]), float(used["given"]["memory"])
        steps.append(
            Step(record.parts[-3], record.stem, seconds, cpus, memory, float(used.get("started", 0)), cpu),
        )
    names: dict[str, set[str]] = {}
    for step in steps:
        names.setdefault(step.corpus, set()).add(step.name)
    for step in steps:
        own = names[step.corpus]
        fixes = {name for name in own if name.startswith(("fix-", "infer-"))}
        if step.name == "traced":
            step.after = {"fix-unsafe"} & own
        elif step.name == "infer-trace":
            step.after = {"traced"} & own
        elif step.name in {"tests", "types"}:
            step.after = fixes | ({"traced"} & own)
    return steps


def groups(steps: list[Step]) -> None:
    """Name each step's corpus's group of size and time, as `corpora.toml`'s sets have it."""
    with (_ROOT / "tests" / "corpus" / "corpora.toml").open("rb") as file:
        sets = tomllib.load(file)["sets"]
    by: dict[str, str] = {}
    for group in ("fast-small", "fast-large", "slow-small", "slow-large"):
        for name in sets.get(group, []):
            by[name.replace(" ", "-")] = group
    for step in steps:
        step.group = by.get(step.corpus, "")


def ports() -> dict[str, str]:
    """Each corpus's suite's port, where it binds one."""
    with (_ROOT / "tests" / "corpus" / "corpora.toml").open("rb") as file:
        entries = tomllib.load(file)["corpus"]
    return {name.replace(" ", "-"): entry["port"] for name, entry in entries.items() if "port" in entry}


def chain(steps: list[Step]) -> dict[int, float]:
    """Each step's seconds with the longest line of its corpus's steps waiting for it."""
    memo: dict[int, float] = {}

    def length(step: Step) -> float:
        if id(step) not in memo:
            later = [other for other in steps if other.corpus == step.corpus and step.name in other.after]
            memo[id(step)] = step.seconds + max((length(other) for other in later), default=0.0)
        return memo[id(step)]

    for step in steps:
        _ = length(step)
    return memo


def bounds(steps: list[Step], cpus: int, memory: float) -> dict[str, float]:
    """The least time any schedule could take, by each of what limits it, in seconds.

    Its longest chain of steps that wait for each other; its CPU seconds over every CPU; its
    memory held over its seconds, over the memory shared; each before the timed steps, which
    follow one another alone.
    """
    work = [step for step in steps if step.name not in _TIMED]
    timed = sum(step.seconds for step in steps if step.name in _TIMED)
    longest = chain(work)
    return {
        "chain": max(longest.values(), default=0.0) + timed,
        "cpu": sum(step.cpu for step in work) / cpus + timed,
        "memory": sum(step.memory * step.seconds for step in work) / memory + timed,
    }


def simulate(
    steps: list[Step],
    cpus: int,
    memory: float,
    key: Callable[[Step], float],
    *,
    patience: float | None,
    beside: float = 0.0,
) -> float:
    """Run the steps on `cpus` and `memory`, the ready one with the least `key` first.

    With `patience`, a step that has waited so many seconds and doesn't fit keeps every other
    from starting, as the runner does, but those lasting `beside` seconds at most.
    """
    port = ports()
    work = [step for step in steps if step.name not in _TIMED]
    done: dict[str, set[str]] = {}
    running: list[tuple[float, int, Step]] = []
    waiting = sorted(work, key=key)
    ready_at: dict[int, float] = {}
    now, free_cpus, free_memory, bound = 0.0, cpus, memory, set()
    while waiting or running:
        held = False
        for step in list(waiting):
            if not step.after <= done.get(step.corpus, set()):
                continue
            ready_at.setdefault(id(step), now)
            fits = step.cpus <= free_cpus and step.memory <= free_memory
            busy = step.name in _SUITE and port.get(step.corpus) in bound
            if fits and not busy and (not held or step.seconds <= beside):
                waiting.remove(step)
                free_cpus -= step.cpus
                free_memory -= step.memory
                if step.name in _SUITE and step.corpus in port:
                    bound.add(port[step.corpus])
                heapq.heappush(running, (now + step.seconds, id(step), step))
            elif patience is not None and not fits and now - ready_at[id(step)] >= patience:
                held = True
        if not running:
            break  # what's left can never fit
        now, _, ended = heapq.heappop(running)
        free_cpus += ended.cpus
        free_memory += ended.memory
        if ended.name in _SUITE and ended.corpus in port:
            bound.discard(port[ended.corpus])
        done.setdefault(ended.corpus, set()).add(ended.name)
    return now + sum(step.seconds for step in steps if step.name in _TIMED)


def orders(steps: list[Step]) -> dict[str, Callable[[Step], float]]:
    """The orders a waiting step may be taken in, each a key the least of which goes first."""
    longest = chain(steps)
    rank = {"slow-large": 0, "slow-small": 1, "fast-large": 2, "fast-small": 3, "": 4}
    return {
        "longest chain": lambda step: -longest[id(step)],
        "longest step": lambda step: -step.seconds,
        "most memory": lambda step: -step.memory,
        "most CPU seconds": lambda step: -step.cpu,
        "slow-large group": lambda step: rank[step.group] * 1e6 - longest[id(step)],
        "shortest step": lambda step: step.seconds,
    }


def sweep(runs: list[list[Step]], cpus: int, memory: float) -> list[tuple[float, str, float | None, float]]:
    """Replay every run under each order, patience and beside, summing their seconds.

    Returns:
      Each setting's seconds over every run, the order's name, its patience and its beside, least first.
    """
    found: list[tuple[float, str, float | None, float]] = []
    patiences: tuple[float | None, ...] = (None, 120.0, 300.0, 600.0, 900.0)
    for name, patience, beside in itertools.product(orders(runs[0]), patiences, (0.0, 60.0, 120.0, 300.0, 600.0)):
        if patience is None and beside:
            continue  # nothing is kept waiting to start beside
        total = sum(simulate(steps, cpus, memory, orders(steps)[name], patience=patience, beside=beside) for steps in runs)
        found.append((total, name, patience, beside))
    return sorted(found, key=lambda each: each[0])


def main() -> None:
    """Print each run's minutes, its bounds and its orders'; with `--sweep`, the best settings."""
    parser = argparse.ArgumentParser()
    parser.add_argument("folders", type=Path, nargs="+")
    parser.add_argument("--cpus", type=int, default=16)
    parser.add_argument("--memory", type=float, default=36.0, help="gigabytes the steps share")
    parser.add_argument("--given", action="store_true", help="steps hold what the runner gave them")
    parser.add_argument("--sweep", action="store_true", help="search the runner's settings")
    args = parser.parse_args()
    runs: list[list[Step]] = []
    for folder in args.folders:
        steps = read(folder, given=args.given)
        groups(steps)
        runs.append(steps)
        first = min(step.started for step in steps)
        recorded = max(step.started + step.seconds for step in steps) - first
        used = sum(step.cpu for step in steps) / (recorded * args.cpus)
        print(f"{folder.name}: {len(steps)} steps, {args.cpus} CPUs, {args.memory:g} GB")
        print(f"  {'recorded':<44} {recorded / 60:6.1f} min, {used:.0%} of its CPU seconds")
        for limit, seconds in bounds(steps, args.cpus, args.memory).items():
            print(f"  {'at least, by ' + limit:<44} {seconds / 60:6.1f} min")
        for name, key in orders(steps).items():
            for patience, beside, how in ((_PATIENCE, _BESIDE, "the runner's"), (None, 0.0, "backfilled")):
                minutes = simulate(steps, args.cpus, args.memory, key, patience=patience, beside=beside) / 60
                print(f"  {name + ', ' + how:<44} {minutes:6.1f} min")
    if args.sweep:
        print(f"best over {len(runs)} run(s), minutes summed:")
        found = sweep(runs, args.cpus, args.memory)
        current = next(each for each in found if each[1:] == ("longest chain", _PATIENCE, _BESIDE))
        for total, name, patience, beside in [*found[:5], current]:
            print(f"  {name:<18} patience {patience!s:>6} beside {beside:>5.0f}  {total / 60:6.1f} min")


if __name__ == "__main__":
    main()
