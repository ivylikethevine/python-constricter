"""Compare two corpus runs' fixes and new test failures, corpus by corpus, from their kept records.

  local/.venv/bin/python -m scratch.run_fixes_diff OLD_RUN NEW_RUN [--step STEP] [--rows N]
      [--failures]

Reads each run's `records/<corpus>/<version>/<step>.fixes.jsonl` and keys a fix by its path, name,
annotation and tier, the line left out since it moves with the fixes above it. Prints each corpus's
count withdrawn and added for `--step` (every fix step by default) with the first `--rows` of each.
`--failures` also lists, per corpus and step, the tests failing in the new run's suite and not the
old one's, and those the other way round, from `<step>.tests.jsonl`.
"""

import argparse
import json
from collections import Counter
from pathlib import Path

_STEPS = (
    "fix-certain",
    "fix-likely",
    "fix-unsafe",
    "infer-basedpyright",
    "infer-pyrefly",
    "infer-ty",
    "infer-union",
    "infer-trace",
)
_FAILED = ("failed", "error")

_Fix = tuple[str, str, str, str]


def lines(path: Path) -> list[dict[str, object]]:
    """Read a JSON-lines record, or nothing where the step wrote none."""
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def fixes(run: Path, corpus: str, step: str) -> Counter[_Fix]:
    """Count `step`'s fixes on `corpus` in `run`, keyed without their line."""
    found: Counter[_Fix] = Counter()
    for version in sorted((run / "records" / corpus).glob("*")):
        for fix in lines(version / f"{step}.fixes.jsonl"):
            found[(str(fix["path"]), str(fix["name"]), str(fix["annotation"]), str(fix["tier"]))] += 1
    return found


def failing(run: Path, corpus: str, step: str) -> set[str]:
    """List the tests `step`'s suite failed or errored on `corpus` in `run`."""
    return {
        str(test["id"])
        for version in sorted((run / "records" / corpus).glob("*"))
        for test in lines(version / f"tests-{step}.tests.jsonl")
        if test["outcome"] in _FAILED
    }


def main() -> None:
    """Print what the new run withdrew, added and failed against the old one."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--step", action="append", default=[])
    parser.add_argument("--rows", type=int, default=0)
    parser.add_argument("--failures", action="store_true")
    given = parser.parse_args()
    corpora = sorted({each.name for run in (given.old, given.new) for each in (run / "records").iterdir()})
    steps = given.step or list(_STEPS)
    for step in steps:
        print(f"-- {step}: corpus, withdrawn, added")
        for corpus in corpora:
            old, new = fixes(given.old, corpus, step), fixes(given.new, corpus, step)
            withdrawn, added = old - new, new - old
            if withdrawn or added:
                print(f"{corpus:<22}{sum(withdrawn.values()):>6}{sum(added.values()):>6}")
                for mark, side in (("-", withdrawn), ("+", added)):
                    for fix in sorted(side)[: given.rows]:
                        print(f"  {mark} {fix[0]}: {fix[1]}: {fix[2]} ({fix[3]})")
    if given.failures:
        for step in steps:
            for corpus in corpora:
                old_set, new_set = failing(given.old, corpus, step), failing(given.new, corpus, step)
                for mark, side in (("+", new_set - old_set), ("-", old_set - new_set)):
                    for test in sorted(side):
                        print(f"{step} {corpus} {mark} {test}")


if __name__ == "__main__":
    main()
