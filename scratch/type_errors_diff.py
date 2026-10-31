"""Compare two runs' new type errors from their `tables/type-errors.csv`: what the new run alone has.

  local/.venv/bin/python -m scratch.type_errors_diff OLD_RUN NEW_RUN [--corpus NAME] [--rows]

Keys an error by its corpus, step, path, message and the fix blamed (its name and annotation), the
line left out since it moves with the fixes above it. Prints the counts gained and lost by corpus,
by step and by mechanism, each as old, new and the change, largest change first; `--rows` also
lists the new run's errors the old one lacks, and `--corpus` keeps one corpus's.
"""

import argparse
import csv
from collections import Counter
from pathlib import Path

_Key = tuple[str, str, str, str, str, str]


def errors(run: Path, corpus: str | None) -> Counter[_Key]:
    """Count each error in `run`'s table, keyed without its line."""
    found: Counter[_Key] = Counter()
    with (run / "tables" / "type-errors.csv").open(encoding="utf-8", newline="") as table:
        for row in csv.DictReader(table):
            if corpus is None or row["corpus"] == corpus:
                found[
                    row["corpus"],
                    row["run"],
                    row["mechanisms"],
                    row["path"],
                    row["message"],
                    row["fix"] + ": " + row["annotation"],
                ] += 1
    return found


def by(found: Counter[_Key], field: int) -> Counter[str]:
    """Sum `found` by one field of its key."""
    summed: Counter[str] = Counter()
    for key, count in found.items():
        summed[key[field]] += count
    return summed


def main() -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--corpus")
    parser.add_argument("--rows", action="store_true")
    options: argparse.Namespace = parser.parse_args()
    old: Counter[_Key] = errors(options.old, options.corpus)
    new: Counter[_Key] = errors(options.new, options.corpus)
    print(f"errors: {old.total()} to {new.total()}")
    for title, field in (("corpus", 0), ("step", 1), ("mechanisms", 2)):
        before: Counter[str] = by(old, field)
        after: Counter[str] = by(new, field)
        names: list[str] = sorted(
            set(before) | set(after), key=lambda name: (-abs(after[name] - before[name]), name)
        )
        print(f"\n| {title} | old | new | change |\n| --- | ---: | ---: | ---: |")
        for name in names:
            if after[name] != before[name]:
                print(f"| {name} | {before[name]} | {after[name]} | {after[name] - before[name]:+} |")
    if options.rows:
        print()
        for key, count in sorted((new - old).items()):
            print(f"{count}x {' | '.join(key)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
