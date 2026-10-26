"""Rebuild a corpus run's timeline from its records, and show where its CPUs sat idle.

  local/.venv/bin/python -m scratch.run_timeline corpus-runs/0.4.0-rc.3-10-18-2026-1010
  local/.venv/bin/python -m scratch.run_timeline FOLDER --top 20 --every 5   # 20 longest steps, 5-minute buckets

Reads a run's records from its report, or else its `records/` (`tests.corpus.archive`): each step's
start (`used.started`; a record from before it kept one is left out) and seconds. Each step's CPU
seconds are spread evenly over its seconds, and the minutes it waited for its share of the machine
are summed. Prints the run's share of the machine's CPU seconds used, the CPUs busy in each bucket
with the steps running then, the longest steps, and each corpus's last end: the corpora that
finished last held the run open.
"""

import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

from tests.corpus import archive


class Step(NamedTuple):
    corpus: str
    name: str
    start: float
    end: float
    cpu: float
    memory: float
    given: int
    waited: float


def steps(folder: Path) -> list[Step]:
    found: list[Step] = []
    for (corpus, _, step), record in sorted(archive.kept(folder).items()):
        used = record.get("used")
        if not used or not used.get("seconds") or not used.get("started"):  # an older record kept no start
            continue
        start = used["started"]
        found.append(
            Step(
                corpus,
                step,
                start,
                start + used["seconds"],
                used.get("cpu", 0.0),
                used.get("memory", 0.0),
                used.get("given", {}).get("cpus", 0),
                used.get("waited", 0.0),
            )
        )
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--top", type=int, default=15)
    parser.add_argument("--every", type=float, default=5.0, help="minutes a bucket")
    args = parser.parse_args()
    facts = archive.facts(args.folder)
    cpus = int(facts.get("cpus", 1))
    started = datetime.fromisoformat(str(facts["started"])).timestamp()
    # A record taken from an earlier run (the tests as released, `from`) keeps that run's `used`.
    found = [each for each in steps(args.folder) if each.start >= started - 60]
    if not found:
        print("no measured steps")
        return 1
    first = min(min(each.start for each in found), started)
    last = max(each.end for each in found)
    wall = last - first
    used = sum(each.cpu for each in found)
    print(f"{args.folder.name}: {len(found)} steps, {wall / 60:.0f} minutes on {cpus} CPUs")
    print(f"CPU seconds used: {used:.0f} of {cpus * wall:.0f} ({100 * used / (cpus * wall):.0f}%)")
    print(f"before the first step: {(min(each.start for each in found) - first) / 60:.1f} minutes")
    print(f"minutes the steps waited for their share: {sum(each.waited for each in found) / 60:.0f}")
    width = args.every * 60
    print(f"\nCPUs busy each {args.every:g} minutes, and the steps running then (longest first):")
    at = first
    while at < last:
        till = at + width
        busy = 0.0
        running: list[tuple[float, str]] = []
        for each in found:
            overlap = min(till, each.end) - max(at, each.start)
            if overlap > 0:
                seconds = each.end - each.start
                busy += each.cpu * overlap / seconds if seconds else 0.0
                running.append((seconds, f"{each.corpus}:{each.name}"))
        named = ", ".join(name for _, name in sorted(running, reverse=True)[:6])
        more = f" +{len(running) - 6}" if len(running) > 6 else ""
        print(f"  {(at - first) / 60:5.0f}m  {busy / width:5.1f}  {named}{more}")
        at = till
    print(f"\nthe {args.top} longest steps:")
    for each in sorted(found, key=lambda step: step.end - step.start, reverse=True)[: args.top]:
        seconds = each.end - each.start
        print(
            f"  {each.corpus:24} {each.name:20} {seconds / 60:6.1f}m  from {(each.start - first) / 60:5.1f}m"
            f"  {each.cpu / seconds if seconds else 0:5.1f} CPUs busy of {each.given} given, {each.memory} GB,"
            f" waited {each.waited / 60:.1f}m"
        )
    ends: dict[str, float] = defaultdict(float)
    for each in found:
        ends[each.corpus] = max(ends[each.corpus], each.end)
    print("\nthe corpora that ended last:")
    for corpus, end in sorted(ends.items(), key=lambda item: item[1], reverse=True)[:10]:
        print(f"  {corpus:24} {(end - first) / 60:6.1f}m")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
