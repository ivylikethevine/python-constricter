# SPDX-License-Identifier: MIT
"""The runner's queue for the machine (`sizing.Slots`): no step waiting holds back what could start."""

import threading
import time

import pytest

from tests.corpus import sizing


def _waiting(slots: sizing.Slots, count: int) -> bool:
    """Wait for `count` steps to be waiting for `slots`, 5 seconds at most.

    Returns:
      Whether they are.

    """
    for _ in range(500):
        if len(slots.waiting) >= count:
            return True
        time.sleep(0.01)
    return False


def _started(
    slots: sizing.Slots,
    wanted: sizing.Wanted,
    locks: tuple[threading.Lock, ...],
    into: list[str],
) -> None:
    held: int = slots.take(wanted, locks)
    into.append(f"{wanted.lasting:g}")
    slots.give(held, 0, locks)


def test_a_step_held_back_holds_back_none_after_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """A long one kept waiting for one past its patience doesn't keep a brief one from starting."""
    monkeypatch.setattr(sizing, "_PATIENCE", 0.0)
    slots: sizing.Slots = sizing.Slots(4, 10)
    held: int = slots.take(sizing.Wanted(2, 0))
    started: list[str] = []
    waits: list[sizing.Wanted] = [
        sizing.Wanted(3, 0, 3.0),  # doesn't fit: what's free is kept for it
        sizing.Wanted(1, 0, 2.0, seconds=600.0),  # lasts longer, fits, but is kept waiting
        sizing.Wanted(1, 0, 1.0, seconds=20.0),  # brief: starts
    ]
    threads: list[threading.Thread] = []
    count: int
    wanted: sizing.Wanted
    for count, wanted in enumerate(waits, 1):
        threads.append(threading.Thread(target=_started, args=(slots, wanted, (), started), daemon=True))
        threads[-1].start()
        assert _waiting(slots, count) or started
    threads[-1].join(5)
    assert started == ["1"]
    slots.give(held)
    each: threading.Thread
    for each in threads:
        each.join()
    assert sorted(started) == ["1", "2", "3"]


def test_a_port_is_taken_as_its_step_starts() -> None:
    """Not held while it waits: another step goes on meanwhile, and one wanting the port waits for it."""
    slots: sizing.Slots = sizing.Slots(4, 10)
    port: threading.Lock = threading.Lock()
    held: int = slots.take(sizing.Wanted(1, 0), (port,))
    started: list[str] = []
    second: threading.Thread = threading.Thread(
        target=_started,
        args=(slots, sizing.Wanted(1, 0, 2.0), (port,), started),
        daemon=True,
    )
    second.start()
    assert _waiting(slots, 1)
    _started(slots, sizing.Wanted(1, 0, 1.0), (), started)
    assert started == ["1"]
    slots.give(held, 0, (port,))
    second.join(5)
    assert started == ["1", "2"]
    assert not port.locked()
