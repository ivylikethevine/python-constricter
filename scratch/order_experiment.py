"""Check a corpus with the check order's method-name edges dropped: the parallel check's ceiling.

  local/.venv/bin/python -m scratch.order_experiment [--no-loose] -- CONSTRICTER-ARGS...

With `--no-loose`, `loose.needs` (a file waiting for a module whose classes have an unannotated
method of a name it calls, 12,704 of the standard library's 13,091 edges) gives no edge: files
wait only for the functions they import. Without it, the check runs as `python -m constricter`
does. The plan is built in the main process, so the workers are untouched. Compare the two runs'
`--format=json` outputs to see what those edges carried; time both with `--jobs=0`.
"""

import sys

from constricter.cli import command
from constricter.fix.index import loose


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--no-loose":
        loose.needs = lambda _catalog, _module: set()  # type: ignore[assignment]
        args = args[1:]
    if args and args[0] == "--":
        args = args[1:]
    return command.main(args)


if __name__ == "__main__":
    sys.exit(main())
