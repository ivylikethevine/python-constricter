# SPDX-License-Identifier: MIT
"""`python -m constricter`, and the `constricter` script."""

import contextlib
import os
import sys

from constricter.cli.command import main


def run() -> None:
    """Run the command, and leave with its status at once.

    Not by the interpreter's own exit, which frees every parsed file and the index an object at a
    time: a fifth of a check of a thousand files. What the command wrote is flushed first; nothing
    else waits on the exit (its workers have ended, its output file is closed).
    """
    status: int = main()
    with contextlib.suppress(OSError, ValueError):  # a reader that left, a stream closed already
        _ = sys.stdout.flush()
        _ = sys.stderr.flush()
    os._exit(status)


if __name__ == "__main__":  # not when `--jobs` workers import it
    run()
