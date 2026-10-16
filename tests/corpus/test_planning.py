# SPDX-License-Identifier: MIT
"""The order a run's steps start in, planned by OR-Tools' CP-SAT from what they took before."""

import importlib.util
from typing import Final

import pytest

from tests.corpus import catalog, planning, sizing
from tests.corpus.run_config import Run, parse

_ALL: Final = 16  # the machine's CPUs here


def test_steps_that_cant_share_the_machine_are_planned_one_after_another() -> None:
    """Each held to what the runner holds for it, more than half the memory: none overlaps another."""
    if importlib.util.find_spec("ortools") is None:
        pytest.skip("OR-Tools isn't installed: the dev group has it")
    run: Run = parse({"steps": {"fix": ["certain", "unsafe"]}})
    before: dict[tuple[str, str], sizing.Before] = {
        ("pip", name): sizing.Before(float(_ALL), 10.0, 20 * sizing.GIB) for name in ("check", "fix-certain")
    }
    plan: sizing.Plan = sizing.Plan(run, _ALL, 32 * sizing.GIB, before)
    ranks: dict[tuple[str, str], float] = planning.ranks(run, [catalog.load().entry("pip")], plan)
    assert set(ranks) == {("pip", "check"), ("pip", "fix-certain")}
    assert abs(ranks["pip", "check"] - ranks["pip", "fix-certain"]) >= before["pip", "check"].seconds


def test_nothing_is_planned_without_ortools(monkeypatch: pytest.MonkeyPatch) -> None:
    """The runner's own rules order every step then."""

    def missing(_name: str) -> None:
        return None

    monkeypatch.setattr("importlib.util.find_spec", missing)
    plan: sizing.Plan = sizing.Plan(Run(), _ALL, 32 * sizing.GIB, {})
    assert not planning.ranks(Run(), [catalog.load().entry("pip")], plan)
