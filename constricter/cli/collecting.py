"""The garbage collector, as the command runs it: by hand, once per file checked.

A check keeps every file's tree (see `parsed`), and allocates a great deal for each file, little of it
cyclic. Left to itself, the collector looked through the kept trees again and again as the check
allocated: a third of the standard library's check (34s, 21s without). So while the command runs,
it's off: what indexing built is frozen (never looked through again), and after each file, only
what's been allocated since (the young generations) is collected, which bounds what a cycle can hold.
Not on a free-threaded build, whose collector has no generations: each collection there looks through
everything, and one after every file made a check several times as long. Its cycles wait for the run's
end (a check of pandas held 2.9 GB so, to 2.7 GB).
"""

import contextlib
import gc
import sysconfig
from collections.abc import Generator
from typing import Final

_YOUNG: Final = 1  # the generations collected after each file: 0 and 1, never the frozen or the old
_FREEZES: Final = hasattr(gc, "freeze")  # PyPy's collector has no freezing
# Whether the collector has generations: a free-threaded build's has none, its GIL on or off.
_YOUNGER: Final = not sysconfig.get_config_var("Py_GIL_DISABLED")


@contextlib.contextmanager
def by_hand(*, leaving: bool = False) -> Generator[None]:
    """Turn automatic collection off for the command's run, and back as it was after.

    Not for a process that leaves once the run's done (`leaving`): turned on again, the collector
    looked through all the run left alive, at once (a check of pandas: 3.4s, for nothing).

    Yields:
      Nothing: the run.

    """
    was: bool = gc.isenabled()
    gc.disable()
    try:
        yield
    finally:
        if _FREEZES and not leaving:
            gc.unfreeze()
        if was and not leaving:
            gc.enable()


def indexed() -> None:
    """Freeze what indexing built (the kept trees, the index): it lives until the check takes it."""
    if _FREEZES:
        gc.freeze()


def sweep() -> None:
    """Collect what the file just checked left behind (see the module docstring)."""
    if _YOUNGER:
        _ = gc.collect(_YOUNG)
