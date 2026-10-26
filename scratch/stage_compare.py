"""Compare one stage's steps across two corpus runs, from their records: where the time went.

  local/.venv/bin/python -m scratch.stage_compare BEFORE_FOLDER AFTER_FOLDER
  local/.venv/bin/python -m scratch.stage_compare BEFORE AFTER --stage traced --top 25

Prints, for each run, the stage's wall time (its first step's start to its last's end), its steps'
seconds, CPU seconds and minutes waited, and its CPUs busy on average; then each corpus's seconds
in both, and the steps whose seconds or waits changed most. A step's times are its record's `used`
(`scratch/run_timeline.py`); one with none, or taken from an earlier run, is left out.
"""

import argparse
import fnmatch
import tomllib
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from scratch.run_timeline import Step, steps

_STAGES: dict[str, tuple[str, ...]] = {
    "fixes": ("check", "fix-*", "infer-basedpyright", "infer-ty", "infer-pyrefly", "census", "coverage"),
    "traced": ("traced", "infer-union", "infer-trace"),
    "tests": ("tests", "tests-*", "types", "types-*"),
    "timed": ("timing", "profile"),
}


def _staged(folder: Path, stage: str) -> list[Step]:
    facts = tomllib.loads((folder / "facts.toml").read_text(encoding="utf-8"))
    started = datetime.fromisoformat(str(facts["started"])).timestamp()
    patterns = _STAGES[stage]
    return [
        each
        for each in steps(folder)
        if each.start >= started - 60 and any(fnmatch.fnmatchcase(each.name, p) for p in patterns)
    ]


def _summary(name: str, found: list[Step]) -> None:
    wall = max(each.end for each in found) - min(each.start for each in found)
    cpu = sum(each.cpu for each in found)
    print(
        f"{name}: {len(found)} steps, {wall / 60:.1f} minutes, {sum(e.end - e.start for e in found):.0f}s"
        f" of steps, {cpu:.0f} CPU seconds ({cpu / wall:.1f} CPUs busy), {sum(e.waited for e in found) / 60:.0f}"
        " minutes waited"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--stage", default="tests", choices=sorted(_STAGES))
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()
    before = {(e.corpus, e.name): e for e in _staged(args.before, args.stage)}
    after = {(e.corpus, e.name): e for e in _staged(args.after, args.stage)}
    if not before or not after:
        print("no measured steps in one of them")
        return 1
    _summary(args.before.name, list(before.values()))
    _summary(args.after.name, list(after.values()))
    print(f"only before: {sorted(set(before) - set(after))}")
    print(f"only after: {sorted(set(after) - set(before))}")
    corpora: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for key, each in before.items():
        corpora[key[0]][0] += each.end - each.start
        corpora[key[0]][2] += each.cpu
    for key, each in after.items():
        corpora[key[0]][1] += each.end - each.start
        corpora[key[0]][3] += each.cpu
    print("\ncorpus: seconds before, after; CPU seconds before, after")
    for corpus, (one, two, cpu_one, cpu_two) in sorted(corpora.items(), key=lambda kv: kv[1][0] - kv[1][1]):
        print(f"  {corpus:20} {one:7.0f} {two:7.0f} {two - one:+7.0f}   {cpu_one:7.0f} {cpu_two:7.0f}")
    both = sorted(set(before) & set(after))
    print(f"\nthe {args.top} steps whose seconds changed most: before, after (CPUs given; minutes waited)")
    for key in sorted(
        both, key=lambda k: -abs((after[k].end - after[k].start) - (before[k].end - before[k].start))
    )[: args.top]:
        one, two = before[key], after[key]
        print(
            f"  {key[0]:18} {key[1]:26} {one.end - one.start:6.0f}s ({one.given}; {one.waited / 60:4.1f})"
            f" {two.end - two.start:6.0f}s ({two.given}; {two.waited / 60:4.1f})"
        )
    print(f"\nthe {args.top} steps whose waits changed most: before, after (minutes)")
    for key in sorted(both, key=lambda k: -abs(after[k].waited - before[k].waited))[: args.top]:
        print(f"  {key[0]:18} {key[1]:26} {before[key].waited / 60:5.1f} {after[key].waited / 60:5.1f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
