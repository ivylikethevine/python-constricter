# SPDX-License-Identifier: MIT
"""The garbage collector, as the command runs it: by hand, once per file checked.

A check keeps every file's tree (see `parsed`), and allocates a great deal for each file, little of it
cyclic. Left to itself, the collector looked through the kept trees again and again as the check
allocated: a third of the standard library's check (34s, 21s without). So while the command runs,
it's off: what indexing built is frozen (never looked through again), and after each file, only
what's been allocated since (the young generations) is collected, which bounds what a cycle can hold.
"""

import contextlib
import gc
from collections.abc import Generator
from typing import Final

_YOUNG: Final = 1  # the generations collected after each file: 0 and 1, never the frozen or the old


@contextlib.contextmanager
def by_hand() -> Generator[None]:
    """Turn automatic collection off for the command's run, and back as it was after.

    Yields:
      Nothing: the run.

    """
    was: bool = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        gc.unfreeze()
        if was:
            gc.enable()


def indexed() -> None:
    """Freeze what indexing built (the kept trees, the index): it lives until the check takes it."""
    gc.freeze()


def sweep() -> None:
    """Collect what the file just checked left behind (see the module docstring)."""
    _ = gc.collect(_YOUNG)
