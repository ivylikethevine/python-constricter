"""Measure what a check knows of each file from outside it (`across.outside`), by its pickled size.

  local/.venv/bin/python -m scratch.outside_size                       # the standard library
  local/.venv/bin/python -m scratch.outside_size pandas --top 20       # another corpus, its 20 largest

Indexes the corpus as a check does, works out each file's `Outside` in this process, and prints the
total, the median, the largest and, over those past 1 MB, which fields hold the most. A table worked
out only when it's asked for (`own_types.Lineages`) is counted as far as it's worked out: none of
it, here. Runs in a sandbox; about 25 seconds for the standard library.
"""

import argparse
import pickle
import statistics
import time
import warnings
from collections import Counter

from constricter.fix.index import across
from constricter.fix.index import decorated, plain, project
from constricter.fix.index.stubs import installed
from tests.corpus import corpus_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", nargs="?", default="standard library")
    parser.add_argument("--top", type=int, default=12)
    args = parser.parse_args()
    warnings.simplefilter("ignore")  # the standard library's tests have invalid escapes
    root = next(each.root for each in corpus_table.corpora() if each.name == args.corpus)
    paths = sorted(root.rglob("*.py"))
    start = time.perf_counter()
    modules = plain.settled(
        decorated.passed(installed.with_installed(project.index(paths), installed.search_path())),
        (),
    )
    print(f"{args.corpus}: {len(paths)} files indexed in {time.perf_counter() - start:.0f}s")
    sizes: list[tuple[int, str]] = []
    fields: Counter[str] = Counter()
    start = time.perf_counter()
    for path in paths:
        known = across.outside(modules, path, {})
        size = len(pickle.dumps(known, pickle.HIGHEST_PROTOCOL))
        sizes.append((size, str(path.relative_to(root))))
        if size > 1_000_000:
            for field in known.__dataclass_fields__:
                fields[field] += len(pickle.dumps(getattr(known, field), pickle.HIGHEST_PROTOCOL))
    total = sum(size for size, _ in sizes)
    median = statistics.median(size for size, _ in sizes)
    print(
        f"worked out in {time.perf_counter() - start:.0f}s: {total / 2**20:.1f} MiB, median {median / 1024:.0f} KiB"
    )
    for size, name in sorted(sizes, reverse=True)[: args.top]:
        print(f"  {size / 1024:7.0f} KiB  {name}")
    if fields:
        print(
            "past 1 MB, by field:",
            ", ".join(f"{name} {size / 2**20:.0f} MiB" for name, size in fields.most_common(8)),
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
