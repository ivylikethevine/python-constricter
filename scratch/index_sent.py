"""Measure telling `--jobs` workers the index: its pickled size, one load of it, and each telling's cost.

  local/.venv/bin/python -m scratch.index_sent [CORPUS ...] [--jobs 2 4 8 16] [--runs 3]

For each corpus (the standard library and pandas by default), the index a run's first round
builds (read in this process, then with installed packages, as `rounds.checked_all` has it),
pickled as `schedule.sent` does; one `pickle.loads` of it, what each worker pays; then for each
worker count, workers started as a run starts them and told the index, `--runs` times: the median
seconds of the telling, and the most memory this process held during it above what it held before
(its peak resident set, reset through `/proc/self/clear_refs`). Outside a sandbox: the fork server
needs a socket. Linux only.
"""

import argparse
import pickle
import statistics
import time
from pathlib import Path

from constricter.cli import schedule
from constricter.cli.paths import python_files
from constricter.cli.workers import Workers
from constricter.fix.index import decorated, plain, project
from constricter.fix.index.stubs import installed
from tests.corpus import catalog, trees


def _peak() -> int:
    """Read this process's peak resident set, in kB."""
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if line.startswith("VmHWM:"):
            return int(line.split()[1])
    raise LookupError("VmHWM")


def _resident() -> int:
    """Read this process's resident set, in kB."""
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1])
    raise LookupError("VmRSS")


def measure(name: str, counts: list[int], runs: int) -> None:
    tree = trees.found(catalog.load().entry(name), settle=False)
    paths = list(python_files([tree.root]))
    modules = plain.settled(
        decorated.passed(installed.with_installed(project.index(paths), installed.search_path()))
    )
    start = time.perf_counter()
    told = schedule.sent(modules)
    pickled = time.perf_counter() - start
    start = time.perf_counter()
    _ = pickle.loads(told)
    loaded = time.perf_counter() - start
    print(
        f"{name}: {len(paths)} files, index {len(told) / 1e6:.1f} MB pickled in {pickled:.2f}s, loaded in {loaded:.2f}s"
    )
    for count in counts:
        seconds: list[float] = []
        held: list[int] = []
        with Workers(paths, count) as workers:
            workers.tell(schedule.know, schedule.sent(project.Index({}, [])))  # started
            for _ in range(runs):
                Path("/proc/self/clear_refs").write_text("5", encoding="utf-8")
                before = _resident()
                start = time.perf_counter()
                workers.tell(schedule.know, schedule.sent(modules))
                seconds.append(time.perf_counter() - start)
                held.append(_peak() - before)
        print(
            f"  {count:2} workers: tell {statistics.median(seconds):.2f}s,"
            f" {statistics.median(held) / 1024:.0f} MB more held at most",
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpora", nargs="*", default=["standard library", "pandas"])
    parser.add_argument("--jobs", type=int, nargs="+", default=[1, 2, 4, 8, 16])
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    for name in args.corpora:
        measure(name, args.jobs, args.runs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
