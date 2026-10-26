"""Check a tree in this process and print its seconds and the most memory the process held.

  local/.venv/bin/python scratch/peak_rss.py PATH [--jobs N] [-- OPTIONS...]

Run from the checkout to measure (`python` puts the script's directory first, so the checkout's
`constricter` is imported from the working directory only with `-m`: here the script inserts it).
The check is `--level=suffocate --all-scopes`, its output dropped; `ru_maxrss` is this process's own
peak, its workers' not counted (use `--jobs 1` to measure a check whole).
"""

import resource
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from constricter.cli.command import main  # noqa: E402  # from the working directory's checkout

args: list[str] = sys.argv[1:]
extra: list[str] = args[args.index("--") + 1 :] if "--" in args else []
args = args[: args.index("--")] if "--" in args else args
jobs: str = args[args.index("--jobs") + 1] if "--jobs" in args else "1"
path: str = args[0]
start: float = time.perf_counter()
_ = main(
    [
        f"--jobs={jobs}",
        "--level=suffocate",
        "--all-scopes",
        "--exit-zero",
        "-q",
        "--output-file",
        "/dev/null",
        *extra,
        path,
    ],
    leaving=True,
)
seconds: float = time.perf_counter() - start
peak: int = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
print(f"{seconds:.1f}s, peak {peak / 2**30:.2f} GiB")
