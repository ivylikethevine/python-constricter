"""Replay a finished corpus run's steps under other queueing orders, to see which ends soonest.

Reads every `records/<corpus>/<version>/<step>.json` of the run folder given: each step's seconds,
CPU seconds and peak memory as measured, and when it started. A step needs its average CPUs
(`cpu / seconds`, at least 1) and its peak memory with the runner's 25% margin. Its order within a
corpus is the runner's: `traced` after `fix-unsafe`; `infer-trace` after `traced`; `tests` and
`types` after every fix; a suite's `tests` and `traced` one at a time per port; `timing` and
`profile` last, one at a time, alone. Prints the recorded run's length beside each order's.

    python3 scratch/schedule_sim.py local/corpus-runs/FOLDER [--cpus 16] [--memory 36] [--given]
"""

import argparse
import heapq
import json
import tomllib
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_TIMED = {"timing", "profile"}
_SUITE = {"tests", "traced"}
_MARGIN = 1.25
_PATIENCE = 300.0


@dataclass
class Step:
    """One step as recorded."""

    corpus: str
    name: str
    seconds: float
    cpus: int
    memory: float
    started: float
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
        cpus = max(1, min(16, round(float(used.get("cpu", 0)) / seconds)))
        memory = float(used.get("memory", 0)) * _MARGIN
        if given and used.get("given"):
            cpus, memory = int(used["given"]["cpus"]), float(used["given"]["memory"])
        steps.append(Step(record.parts[-3], record.stem, seconds, cpus, memory, float(used.get("started", 0))))
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
    by = {(step.corpus, step.name): step for step in steps}
    memo: dict[int, float] = {}

    def length(step: Step) -> float:
        if id(step) not in memo:
            later = [other for other in steps if other.corpus == step.corpus and step.name in other.after]
            memo[id(step)] = step.seconds + max((length(other) for other in later), default=0.0)
        return memo[id(step)]

    for step in by.values():
        _ = length(step)
    return memo


def simulate(
    steps: list[Step],
    cpus: int,
    memory: float,
    key: Callable[[Step], float],
    *,
    patience: bool,
    short: float = 0.0,
) -> float:
    """Run the steps on `cpus` and `memory`, the ready one with the least `key` first.

    With `patience`, a step that has waited `_PATIENCE` seconds and doesn't fit keeps every
    other from starting, as the runner does, but those lasting `short` seconds at most.
    """
    port = ports()
    work = [step for step in steps if step.name not in _TIMED]
    done: set[tuple[str, str]] = set()
    running: list[tuple[float, int, Step]] = []
    waiting = sorted(work, key=key)
    ready_at: dict[int, float] = {id(step): 0.0 for step in work if not step.after}
    now, free_cpus, free_memory, bound = 0.0, cpus, memory, set()
    while waiting or running:
        held = False
        for step in list(waiting):
            if not step.after <= {name for corpus, name in done if corpus == step.corpus}:
                continue
            ready_at.setdefault(id(step), now)
            fits = step.cpus <= free_cpus and step.memory <= free_memory
            busy = step.name in _SUITE and port.get(step.corpus) in bound
            if fits and not busy and (not held or step.seconds <= short):
                waiting.remove(step)
                free_cpus -= step.cpus
                free_memory -= step.memory
                if step.name in _SUITE and step.corpus in port:
                    bound.add(port[step.corpus])
                heapq.heappush(running, (now + step.seconds, id(step), step))
            elif patience and not fits and now - ready_at[id(step)] >= _PATIENCE:
                held = True
        if not running:
            break  # what's left can never fit
        now, _, ended = heapq.heappop(running)
        free_cpus += ended.cpus
        free_memory += ended.memory
        if ended.name in _SUITE and ended.corpus in port:
            bound.discard(port[ended.corpus])
        done.add((ended.corpus, ended.name))
    return now + sum(step.seconds for step in steps if step.name in _TIMED)


def main() -> None:
    """Print the recorded run's minutes and each order's."""
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--cpus", type=int, default=16)
    parser.add_argument("--memory", type=float, default=36.0, help="gigabytes the steps share")
    parser.add_argument("--given", action="store_true", help="steps hold what the runner gave them")
    args = parser.parse_args()
    steps = read(args.folder, given=args.given)
    groups(steps)
    first = min(step.started for step in steps)
    recorded = max(step.started + step.seconds for step in steps) - first
    longest = chain(steps)
    rank = {"slow-large": 0, "slow-small": 1, "fast-large": 2, "fast-small": 3, "": 4}
    chained: Callable[[Step], float] = lambda step: -longest[id(step)]  # noqa: E731
    orders: dict[str, tuple[Callable[[Step], float], bool, float]] = {
        "longest chain first, held (the runner's)": (chained, True, 0.0),
        "longest chain first, held, 5-minute steps beside": (chained, True, _PATIENCE),
        "longest chain first, backfilled": (chained, False, 0.0),
        "longest step first, backfilled": (lambda step: -step.seconds, False, 0.0),
        "most memory first, backfilled": (lambda step: -step.memory, False, 0.0),
        "slow-large group first, backfilled": (lambda step: rank[step.group] * 1e6 - longest[id(step)], False, 0.0),
        "shortest step first, backfilled": (lambda step: step.seconds, False, 0.0),
    }
    print(f"{len(steps)} steps, {args.cpus} CPUs, {args.memory:g} GB")
    print(f"{'recorded':<50} {recorded / 60:6.1f} min")
    for name, (key, held, short) in orders.items():
        minutes: float = simulate(steps, args.cpus, args.memory, key, patience=held, short=short) / 60
        print(f"{name:<50} {minutes:6.1f} min")


if __name__ == "__main__":
    main()
