# SPDX-License-Identifier: MIT
"""The runner's sizing: what a step is given, and its queue for the machine (`sizing.Slots`)."""

import math
import threading
import time
from pathlib import Path
from typing import Final

import pytest

from tests.corpus import catalog, pipeline, sizing
from tests.corpus.run_config import parse
from tests.corpus.trees import Tree

_RUNNING: Final = "running big: 2 CPUs"  # in the queue's report
_KEPT: Final = "what's free is kept for"


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


def _ranked(slots: sizing.Slots, wanted: sizing.Wanted, rank: float, into: list[str]) -> None:
    held: int = slots.take(wanted, (), f"{wanted.lasting:g}", rank)
    into.append(f"{wanted.lasting:g}")
    slots.give(held, 0, (), f"{wanted.lasting:g}")


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


def test_a_step_going_before_a_kept_one_isnt_kept_for_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """Past its patience, one ranked after a small long step that fits doesn't hold it back."""
    monkeypatch.setattr(sizing, "_PATIENCE", 0.0)
    slots: sizing.Slots = sizing.Slots(4, 10)
    held: int = slots.take(sizing.Wanted(2, 0))
    started: list[str] = []
    waits: list[tuple[sizing.Wanted, float]] = [
        (sizing.Wanted(3, 0, 3.0), 2.0),  # doesn't fit: what's free is kept for it from those after it
        (sizing.Wanted(1, 0, 2.0, seconds=600.0), 1.0),  # planned first: starts
        (sizing.Wanted(1, 0, 4.0, seconds=600.0), math.inf),  # lasts longer, but isn't planned: kept
    ]
    threads: list[threading.Thread] = []
    count: int
    wanted: sizing.Wanted
    rank: float
    for count, (wanted, rank) in enumerate(waits, 1):
        threads.append(threading.Thread(target=_ranked, args=(slots, wanted, rank, started), daemon=True))
        threads[-1].start()
        assert _waiting(slots, count) or started
    threads[1].join(5)
    threads[2].join(0.3)
    assert started == ["2"]
    slots.give(held)
    each: threading.Thread
    for each in threads:
        each.join()
    assert sorted(started) == ["2", "3", "4"]


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


def test_a_step_that_ends_before_a_kept_one_could_start_starts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Beside one past its patience, a step ending before what's running frees enough for it; no longer."""
    monkeypatch.setattr(sizing, "_PATIENCE", 0.0)
    monkeypatch.setattr(sizing, "_BESIDE", 0.0)
    slots: sizing.Slots = sizing.Slots(4, 10)
    held: int = slots.take(sizing.Wanted(2, 0, seconds=600.0), (), "big")
    started: list[str] = []
    waits: list[sizing.Wanted] = [
        sizing.Wanted(3, 0, 3.0),  # waits for `big`, which ends in 600s
        sizing.Wanted(1, 0, 2.0, seconds=900.0),  # would end after it: kept waiting
        sizing.Wanted(1, 0, 1.0, seconds=60.0),  # ends before it: starts
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
    report: str = "\n".join(slots.report())
    assert _RUNNING in report
    assert _KEPT in report
    slots.give(held, 0, (), "big")
    each: threading.Thread
    for each in threads:
        each.join()
    assert sorted(started) == ["1", "2", "3"]


def test_a_suite_traced_by_its_script_is_one_process(tmp_path: Path) -> None:
    """Its tests' workers aren't kept for it: it's given what any other step is."""
    celery: catalog.Entry = catalog.load().entries["celery"]
    assert celery.suite is not None
    suite: catalog.Suite = celery.suite._replace(script=("runtests.py",))
    plan: sizing.Plan = sizing.Plan(parse({"run": {"jobs": 2}}), 8, 64 * sizing.GIB, {})
    tree: Tree = Tree("celery", "1", tmp_path, tmp_path, suite=suite)
    assert plan.wanted(tree, pipeline.TRACED) == sizing.Wanted(2, 2 * (sizing.GIB + sizing.GIB // 4))
