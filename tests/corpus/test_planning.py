"""The order a run's steps start in, planned by OR-Tools' CP-SAT from what they took before."""

import importlib.util
from typing import Final

import pytest

from tests.corpus import catalog, planning, sizing
from tests.corpus.run_config import Run, parse

_ALL: Final = 16  # the machine's CPUs here
_CHECK: Final = "check"  # the step a stage of its own runs alone
# The check, measured on two fast-large corpora and a slow-large one.
_CHECKED: Final = {
    (corpus, _CHECK): sizing.Before(1.0, seconds, sizing.GIB)
    for corpus, seconds in (("pip", 100.0), ("tox", 300.0), ("pandas", 5000.0))
}
_ALIKE: Final = 200.0  # the median of the fast-large corpora's
_SLOW: Final = 5000.0  # the one slow-large corpus's


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


def test_a_stage_plans_its_own_steps_alone() -> None:
    """Another stage's start after this one's end: planned beside it, they'd order this one's wrongly."""
    if importlib.util.find_spec("ortools") is None:
        pytest.skip("OR-Tools isn't installed: the dev group has it")
    run: Run = parse({"steps": {"fix": ["certain", "unsafe"]}})
    before: dict[tuple[str, str], sizing.Before] = {
        ("pip", name): sizing.Before(1.0, 10.0, sizing.GIB) for name in (_CHECK, "fix-certain")
    }
    plan: sizing.Plan = sizing.Plan(run, _ALL, 32 * sizing.GIB, before)
    staged: dict[tuple[str, str], float] = planning.ranks(
        run,
        [catalog.load().entry("pip")],
        plan,
        lambda name: name == _CHECK,
    )
    assert set(staged) == {("pip", _CHECK)}


def test_a_step_no_run_measured_on_its_corpus_is_planned() -> None:
    """The check of pdm, unmeasured, has a rank beside the check of pandas, measured."""
    if importlib.util.find_spec("ortools") is None:
        pytest.skip("OR-Tools isn't installed: the dev group has it")
    run: Run = parse({"steps": {"fix": ["certain"]}})
    plan: sizing.Plan = sizing.Plan(run, _ALL, 32 * sizing.GIB, _CHECKED)
    known: catalog.Catalog = catalog.load()
    ranks: dict[tuple[str, str], float] = planning.ranks(
        run,
        [known.entry(name) for name in ("pandas", "pdm")],
        plan,
        lambda name: name == _CHECK,
    )
    assert set(ranks) == {("pandas", _CHECK), ("pdm", _CHECK)}


def test_a_step_no_run_measured_takes_its_like_corpora_seconds() -> None:
    """The median of its set's (pdm's fast-large: pip's and tox's), or else of every corpus that ran it."""
    known: catalog.Catalog = catalog.load()
    assert planning.like(_CHECKED, "pdm", _CHECK, known) == pytest.approx(_ALIKE)
    slow: dict[tuple[str, str], sizing.Before] = {("pandas", _CHECK): _CHECKED["pandas", _CHECK]}
    assert planning.like(slow, "pdm", _CHECK, known) == pytest.approx(_SLOW)
    assert planning.like(_CHECKED, "pdm", "fix-certain", known) is None  # none ran it: the rules order it


def test_nothing_is_planned_without_ortools(monkeypatch: pytest.MonkeyPatch) -> None:
    """The runner's own rules order every step then."""

    def missing(_name: str) -> None:
        return None

    monkeypatch.setattr("importlib.util.find_spec", missing)
    plan: sizing.Plan = sizing.Plan(Run(), _ALL, 32 * sizing.GIB, {})
    assert not planning.ranks(Run(), [catalog.load().entry("pip")], plan)
