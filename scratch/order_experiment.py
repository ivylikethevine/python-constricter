"""Check a corpus with the check order's method-name edges dropped: the parallel check's ceiling.

  local/.venv/bin/python -m scratch.order_experiment [--no-loose] [--fork] -- CONSTRICTER-ARGS...

With `--no-loose`, `loose.needs` (a file waiting for a module whose classes have an unannotated
method of a name it calls, 12,704 of the standard library's 13,091 edges) gives no edge: files
wait only for the functions they import. Without it, the check runs as `python -m constricter`
does. The plan is built in the main process, so the workers are untouched. `--fork` starts the
workers by forking, which a sandbox allows (it denies the forkserver's socket). The check's time
goes to standard error. Compare the two runs' `--format=json` outputs, sorted, to see what those
edges carried; time both with `--jobs=0`.
"""

import multiprocessing
import sys
import time

from constricter.cli import command
from constricter.fix.index import loose


def main() -> int:
    args = sys.argv[1:]
    options = args[: args.index("--")] if "--" in args else args
    if "--no-loose" in options:
        loose.needs = lambda _catalog, _module: set()  # type: ignore[assignment]
    if "--fork" in options:
        multiprocessing.set_start_method("fork", force=True)
    if "--" in args:
        args = args[args.index("--") + 1 :]
    start = time.perf_counter()
    status = command.main(args)
    print(f"check: {time.perf_counter() - start:.2f}s", file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(main())
