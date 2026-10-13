# SPDX-License-Identifier: MIT
"""Check a directory's files in one process on N threads, and say how the time and the findings change.

  local/.venv-ft/bin/python -X gil=0 -m scratch.threads_probe DIR [THREADS ...]   # free-threaded
  local/.venv/bin/python -m scratch.threads_probe DIR 1                           # the usual build

A probe of whether a free-threaded Python could check files on threads where `--jobs` starts
processes: no index pickled, none read again in each worker. It indexes `DIR` once, then for each
thread count (1 2 4 8 by default) checks every file once, each with what the index says of it
(`schedule.outside`), in no order and one round: not what the command reports, but the same work for
every count. It prints the seconds, the speed-up over one thread, and how many files' findings
differ from one thread's: constricter's caches are a process's, shared by its threads unguarded, so
a difference is a race. The collector is off throughout, as the command has it.
"""

import gc
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from constricter.cli import command, schedule
from constricter.cli.options import Options
from constricter.cli.paths import python_files
from constricter.fix.index import decorated, installed, plain, project
from constricter.rules import parsed


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    counts = [int(each) for each in argv[1:]] or [1, 2, 4, 8]
    options = Options.parse(["--level=suffocate", "--exit-zero", "--jobs=1", argv[0]])
    paths = list(python_files(options.input.paths, options.input.exclude))
    gil = getattr(sys, "_is_gil_enabled", lambda: True)()
    print(f"Python {sys.version.split()[0]}, GIL {'on' if gil else 'off'}: {len(paths)} files")
    gc.disable()
    start = time.perf_counter()
    modules = plain.settled(
        decorated.passed(installed.with_installed(project.index(paths), installed.search_path())),
        options.checks.plain_bases,
    )
    print(f"indexed in {time.perf_counter() - start:.1f}s")

    def check(path: Path) -> tuple[str, ...]:
        try:
            run = command._check_path(path, schedule.outside(modules, path, {}), options)
        except Exception as error:  # a race's crash is a finding of the probe
            return (f"{type(error).__name__}: {error}",)
        return (run.error, *sorted(f"{r.offence.line}:{r.offence.code}:{r.offence.edit}" for r in run.results))

    first: list[tuple[str, ...]] | None = None
    alone = 0.0
    for count in counts:
        parsed.budget(1)  # no tree kept from the run before: each count parses every file
        start = time.perf_counter()
        with ThreadPoolExecutor(count) as pool:
            found = list(pool.map(check, paths))
        seconds = time.perf_counter() - start
        if first is None:
            first, alone = found, seconds
        differ = sum(one != other for one, other in zip(first, found, strict=True))
        crashed = sum(len(each) == 1 and ": " in each[0] and not each[0].startswith(":") for each in found)
        print(
            f"{count:>2} threads: {seconds:6.1f}s, {alone / seconds:4.1f}x, "
            f"{differ} files differ from the first count's, {crashed} crashed or unread",
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
