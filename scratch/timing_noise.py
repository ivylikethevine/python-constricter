"""Compare two corpus runs' timing tables, to see how far the published seconds move run to run.

  local/.venv/bin/python -m scratch.timing_noise corpus-runs/A corpus-runs/B

Reads each folder's `tables/timing.csv` and, for every corpus in both, prints the seconds in one
process and with jobs, their change from A to B, and the instructions' change where hyperfine
counted them; then the median and the largest absolute change of each column. Two runs at the same
code (a version bump apart) give the noise floor a timing change has to clear; `timing = 1` runs
hold one sample each, so this is the single-sample noise.
"""

import csv
import statistics
import sys
from pathlib import Path


def _read(folder: Path) -> dict[str, dict[str, str]]:
    with (folder / "tables" / "timing.csv").open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = {}
        for row in reader:
            # The header repeats `with jobs`: name the columns by position.
            rows[row[0]] = dict(zip(["corpus", "constricter", "jobs", "one", "jobs_s", "runs", "g_one", "g_jobs", "by"], row, strict=False))
        del header
        return rows


def _pct(a: str, b: str) -> float | None:
    try:
        x, y = float(a), float(b)
    except ValueError:
        return None
    return (y - x) / x * 100 if x else None


def main(argv: list[str]) -> int:
    a, b = (_read(Path(arg)) for arg in argv[1:3])
    changes: dict[str, list[float]] = {"one": [], "jobs_s": [], "g_one": [], "g_jobs": []}
    print(f"{'corpus':20} {'one A':>8} {'one B':>8} {'%':>7} {'jobs A':>8} {'jobs B':>8} {'%':>7} {'G one %':>8} {'G jobs %':>9}")
    for corpus in sorted(set(a) & set(b)):
        ra, rb = a[corpus], b[corpus]
        cells = []
        for key in ("one", "jobs_s", "g_one", "g_jobs"):
            pct = _pct(ra[key], rb[key])
            if pct is not None:
                changes[key].append(pct)
            cells.append(pct)
        one, jobs_s, g_one, g_jobs = cells
        fmt = lambda p: f"{p:+7.2f}" if p is not None else f"{'-':>7}"  # noqa: E731
        print(
            f"{corpus:20} {ra['one']:>8} {rb['one']:>8} {fmt(one)} {ra['jobs_s']:>8} {rb['jobs_s']:>8} {fmt(jobs_s)}"
            f" {fmt(g_one):>8} {fmt(g_jobs):>9}"
        )
    print()
    for key, label in (("one", "seconds, one process"), ("jobs_s", "seconds, with jobs"), ("g_one", "instructions, one process"), ("g_jobs", "instructions, with jobs")):
        values = [abs(v) for v in changes[key]]
        if values:
            print(f"{label:28} median |change| {statistics.median(values):5.2f}%  largest {max(values):5.2f}%  over {len(values)} corpora")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
