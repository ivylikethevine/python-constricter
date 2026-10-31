"""A run's census rows with no fix, grouped, for choosing what inference to build next.

    local/.venv/bin/python -m scratch.census_mine corpus-runs/FOLDER [--by shape|unfixed|dotted|source]
        [--shape TEXT] [--unfixed TEXT] [--corpus NAME ...] [--binding KIND] [--top N] [--samples N]

Reads every corpus's `records/*/*/census.rows.jsonl` (the `census` step's rows), keeps the bindings
`--fix` offers nothing for, filters them by a substring of their shape, their `unfixed` reason,
their corpus or their statement, and counts them by the field `--by` names, each group with sample
values. Runs nothing: for mining a finished run without checking a corpus again.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("folder", type=Path)
    parser.add_argument("--by", default="shape")
    parser.add_argument("--shape", default="")
    parser.add_argument("--unfixed", default=None)
    parser.add_argument("--corpus", nargs="*", default=[])
    parser.add_argument("--binding", default="")
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument("--samples", type=int, default=3)
    parser.add_argument("--fixed", action="store_true", help="the fixed bindings instead")
    args = parser.parse_args()
    counts: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    path: Path
    for path in sorted(args.folder.glob("records/*/*/census.rows.jsonl")):
        line: str
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["fixed"] != args.fixed or args.shape not in row["shape"]:
                continue
            if args.unfixed is not None and args.unfixed != row["unfixed"]:
                continue
            if (args.corpus and row["corpus"] not in args.corpus) or args.binding not in row["binding"]:
                continue
            key: str = str(row[args.by])
            counts[key] += 1
            if len(samples[key]) < args.samples:
                samples[key].append(
                    f"{row['corpus']}:{row['path']}:{row['line']} {row['name']} = {row['source']}"
                )
    print(f"{sum(counts.values()):,} bindings")
    key: str
    count: int
    for key, count in counts.most_common(args.top):
        print(f"{count:7,}  {key}")
        sample: str
        for sample in samples[key]:
            print(f"           {sample}")


if __name__ == "__main__":
    main()
