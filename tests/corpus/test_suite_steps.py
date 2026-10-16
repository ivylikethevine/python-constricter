# SPDX-License-Identifier: MIT
"""A suite's steps: each part starts once the fixes it reads are made, on checkouts of the suite's own."""

from pathlib import Path
from typing import Final, cast

import pytest

from tests.corpus import corpus_suite, suite_steps
from tests.corpus.catalog import PYTEST, Suite
from tests.corpus.pipeline import Job, Record, Store
from tests.corpus.run_config import Run, parse
from tests.corpus.trees import Tree

_SUITE: Final = Suite("https://example.invalid/a", "1", "src/a", (), PYTEST, (("mypy",),), at_once=2)
_PASSED: Final[Record] = {"counts": {"passed": 2}, "failed": []}
_FAILED: Final[Record] = {"counts": {"passed": 1, "failed": 1}, "failed": ["t::f"]}
_WHOLE: Final = "fix-unsafe"  # the guesses' fix step, whose run may stand for a tier's


def _job(tmp_path: Path) -> Job:
    asked: Record = {
        "fix": ["certain", "unsafe"],
        "infer-with": ["ty"],
        "traced": True,
        "tests": True,
        "types": True,
    }
    run: Run = parse({"steps": asked})
    return Job(run, Store(tmp_path), Tree("a", "1", tmp_path, tmp_path, suite=_SUITE), "dev")


def test_each_part_waits_for_what_it_reads(tmp_path: Path) -> None:
    """Its fix (the trace's, for the traced tests), its kind as released; a tier's tests the guesses'."""
    needs: dict[str, frozenset[str]] = suite_steps.needs(_job(tmp_path))
    assert needs["traced"] == {"fix-unsafe"}
    assert needs["tests-released"] == frozenset()
    assert needs["tests-fix-unsafe"] == {"fix-unsafe", "tests-released"}
    assert needs["tests-fix-certain"] == {"fix-certain", "tests-released", "tests-fix-unsafe"}
    assert needs["tests-infer-trace"] == {"traced", "tests-released"}
    assert needs["types-fix-certain"] == {"fix-certain", "types-released"}
    assert needs["tests"] == {
        "tests-released",
        "tests-fix-certain",
        "tests-fix-unsafe",
        "tests-infer-ty",
        "tests-infer-trace",
    }


def test_each_part_has_a_checkout_of_its_kind(tmp_path: Path) -> None:
    """The tests' parts take the suite's `at_once` in turn; their whole every one, to run some again."""
    job: Job = _job(tmp_path)
    assert [suite_steps.checkouts(job, name)[0] for name in ("tests-released", "tests-fix-certain")] == [
        "run0",
        "run1",
    ]
    assert suite_steps.checkouts(job, "tests") == ("run0", "run1")
    assert suite_steps.checkouts(job, "traced") == ("traced",)
    assert suite_steps.checkouts(job, "types-fix-unsafe") == ("types",)
    assert not suite_steps.checkouts(job, "types")
    assert suite_steps.binds("tests-fix-unsafe")
    assert not suite_steps.binds("types-released")


def test_the_tests_gather_their_parts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A tier the guesses' run stands for is theirs; a fixed run that differs runs again, as released does."""
    job: Job = _job(tmp_path)
    parts: dict[str, Record] = {
        "tests-released": _PASSED | {"tag": "1", "seconds": 3.0, "stopped": False},
        "tests-fix-unsafe": _PASSED,
        "tests-fix-certain": {"implied": _WHOLE},
        "tests-infer-ty": _FAILED,
        "tests-infer-trace": {"skipped": "the fix made no patch"},
    }
    name: str
    record: Record
    for name, record in parts.items():
        job.store.write("a", job.recorded, name, record)
    again: list[str] = []

    def fixed_run(_job: Job, step: str, kept: str, _base: Path) -> corpus_suite.Outcome:
        again.append(f"{step}{kept}")
        return corpus_suite.Outcome({"passed": 1, "failed": 1}, frozenset({"t::f"}))

    def prepared(_job: Job, name: str) -> Path:
        return tmp_path / name

    def reset(_root: Path, _suite: Suite) -> None:
        pass

    def tested(_root: Path, _suite: Suite, _keep: Path | None) -> corpus_suite.Outcome:
        return corpus_suite.Outcome({"passed": 2}, frozenset())

    monkeypatch.setattr(suite_steps, "prepared", prepared)
    monkeypatch.setattr(suite_steps, "_fixed_run", fixed_run)
    monkeypatch.setattr(corpus_suite, "reset", reset)
    monkeypatch.setattr(corpus_suite, "tested", tested)
    gathered: Record = suite_steps.tests(job)
    assert again == ["infer-ty-again"]
    assert gathered["seconds"] == parts["tests-released"]["seconds"]
    assert gathered["varies"] is False
    fixed: dict[str, Record] = cast("dict[str, Record]", gathered["fixed"])
    assert list(fixed) == ["fix-certain", "fix-unsafe", "infer-ty"]
    assert fixed["fix-certain"]["implied"] == _WHOLE
    assert fixed["infer-ty"]["new"] == ["t::f"]
