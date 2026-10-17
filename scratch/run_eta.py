# SPDX-License-Identifier: MIT
"""Project when a corpus run will end, from a finished run of the same steps.

  local/.venv/bin/python -m scratch.run_eta local/corpus-runs/0.3.9-rc.1-10-16-2026-1902 \\
      local/corpus-runs/0.3.7-rc.1-10-16-2026-0156 [--err local/runs/mega-0.3.9-rc.1.err]

Each step the running folder's `runner.log` records as done is weighted by the seconds the same
corpus and step took in the reference folder's `tables/steps.csv` (a step the reference lacks gets
the median), and the run is assumed to spend its wall clock on the remaining weight at the rate it
spent it on the done weight. Prints steps done of total, elapsed, the share of the weight done, the
projected end in local time, and the `problem:` lines of `--err` so far. Rough early on: the first
steps are the quick ones.
"""

import argparse
import csv
import re
import statistics
import tomllib
from datetime import datetime
from pathlib import Path

_DONE = re.compile(r"^\d\d:\d\d:\d\d \S+ on (?P<corpus>.+?): (?P<step>[\w-]+): ")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("--err", type=Path)
    args = parser.parse_args()

    weights: dict[tuple[str, str], float] = {}
    with (args.reference / "tables" / "steps.csv").open(newline="") as file:
        for row in csv.DictReader(file):
            weights[(row["corpus"], row["step"])] = float(row["seconds"])
    median = statistics.median(weights.values())
    total = sum(weights.values())

    with (args.run / "facts.toml").open("rb") as file:
        started = datetime.fromisoformat(tomllib.load(file)["started"])
    log = args.run / "runner.log"
    done: dict[tuple[str, str], float] = {}
    if log.exists():
        for line in log.read_text().splitlines():
            match = _DONE.match(line)
            if match:
                key = (match["corpus"], match["step"])
                done[key] = weights.get(key, median)
    done_weight = sum(done.values())
    now = datetime.now().astimezone()
    elapsed = now - started
    share = done_weight / total if total else 0.0
    print(f"steps done: {len(done)} of {len(weights)} (reference); elapsed {elapsed.seconds // 60} min; weight done {share:.1%}")
    if share > 0:
        remaining = elapsed * (1 - share) / share
        print(f"projected end: {(now + remaining).strftime('%H:%M')} local (about {int(remaining.total_seconds() // 60)} min to go)")
    else:
        print(f"projected end: no step done yet; the reference took {int(total)} step-seconds")
    if args.err and args.err.exists():
        problems = [line for line in args.err.read_text().splitlines() if line.startswith("problem:")]
        print(f"problems so far: {len(problems)}")
        for line in problems[-10:]:
            print("  " + line)


if __name__ == "__main__":
    main()
