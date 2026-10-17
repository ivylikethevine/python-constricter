# SPDX-License-Identifier: MIT
"""A suite's steps: each part starts once the fixes it reads are made, on checkouts of the suite's own."""

from pathlib import Path
from typing import Final, cast

import pytest

from tests.corpus import catalog, corpus_suite, suite_steps
from tests.corpus.catalog import PYTEST, Suite
from tests.corpus.corpus_suite import Outcome
from tests.corpus.pipeline import Job, Record, Store
from tests.corpus.run_config import Run, parse
from tests.corpus.trees import Tree

_SUITE: Final = Suite("https://example.invalid/a", "1", "src/a", (), PYTEST, (("mypy",),), at_once=2)
_PASSED: Final[Record] = {"counts": {"passed": 2}, "failed": []}
_FAILED: Final[Record] = {"counts": {"passed": 1, "failed": 1}, "failed": ["t::f"]}
_FAILING: Final = "tests/test_a.py::test_a"  # a test a run failed
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


def test_the_tests_as_released_are_an_earlier_runs(tmp_path: Path) -> None:
    """The latest at the suite's tag, of any version, saying whose; not one stopped, nor this run's."""
    runs: Path = tmp_path / "runs"
    job: Job = _job(runs / "this")
    assert suite_steps.earlier(job) is None
    found: Record = _PASSED | {"tag": "1", "seconds": 3.0, "stopped": False}
    written: tuple[tuple[str, str, Record], ...] = (
        ("old", "0.3.6", found),
        ("other-tag", "dev", found | {"tag": "0"}),
        ("stopped", "dev", found | {"stopped": True}),
        ("this", "dev", found | {"seconds": 1.0}),
    )
    folder: str
    version: str
    record: Record
    for folder, version, record in written:
        Store(runs / folder).write("a", version, "tests-released", record)
    assert suite_steps.earlier(job) == found | {"from": "old"}


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


def test_a_fixed_runs_failures_are_the_fixs_only_if_it_has_them_both_times() -> None:
    """And no released run does; a test the catalog names is listed apart, and is no difference."""
    released: Outcome = Outcome({"passed": 9, "skipped": 1}, frozenset())
    failing: Outcome = Outcome({"passed": 8, "failed": 1, "skipped": 1}, frozenset({_FAILING}))
    other: Outcome = Outcome({"passed": 8, "failed": 1, "skipped": 1}, frozenset({"tests/test_b.py::test_b"}))
    assert suite_steps.weighed([released], [released], frozenset()) == {
        "counts": released.counts,
        "failed": [],
        "same": True,
        "new": [],
    }
    twice: Record = suite_steps.weighed([failing, failing], [released, released], frozenset())
    assert (twice["same"], twice["new"], twice["differs"]) == (False, [_FAILING], True)
    once: Record = suite_steps.weighed([failing, other], [released, released], frozenset())
    assert (once["new"], once["differs"], len(cast("list[Record]", once["again"]))) == ([], False, 1)
    named: Record = suite_steps.weighed([failing, failing], [released, released], frozenset({_FAILING}))
    assert (named["new"], named["named"], named["differs"]) == ([], [_FAILING], False)
    theirs: Record = suite_steps.weighed([failing, failing], [released, failing], frozenset())
    assert (theirs["new"], theirs["gone"], theirs["differs"]) == ([], [], False)
    gone: Record = suite_steps.weighed([released, released], [failing, failing], frozenset())
    assert (gone["gone"], gone["differs"]) == ([_FAILING], True)
    skipping: Outcome = Outcome({"passed": 8, "skipped": 2}, frozenset())
    assert suite_steps.weighed([skipping, skipping], [released, released], frozenset())["differs"]
    black: catalog.Suite | None = catalog.load().entries["black"].suite
    assert black is not None
    assert [test.rpartition("::")[2] for test, _ in black.differs] == ["test_piping"]
    flaky: Outcome = Outcome({}, frozenset({"tests/test_black.py::BlackTestCase::test_piping", _FAILING}))
    whole: catalog.Suite = black._replace(differs=(("tests/test_black.py", "its tests come and go"),))
    assert suite_steps.told(black, [flaky]) == suite_steps.told(whole, [flaky]) == flaky.failed - {_FAILING}
    assert corpus_suite.read("ERROR - 2026-10-13 - logged\nFAILED tests/test_a.py::test_a - x\n").failed == {
        _FAILING,
    }


def test_a_unittest_summary_names_its_failures_and_not_its_counts() -> None:
    """Django's runner heads each failure and error; its `FAILED (failures=N, ...)` line names none."""
    output: str = (
        "FAIL: test_a (pkg.tests.Case.test_a)\nTraceback...\n\nERROR: test_b (pkg.tests.Case.test_b)\n"
        "Traceback...\n\nRan 3 tests in 0.1s\n\nFAILED (failures=1, errors=1, skipped=1)\n"
    )
    found: Outcome = corpus_suite.read(output)
    assert found.failed == {"test_a (pkg.tests.Case.test_a)", "test_b (pkg.tests.Case.test_b)"}
    assert found.counts == {"ran": 3, "failures": 1, "errors": 1, "skipped": 1}


def test_a_pytest_failure_is_named_whole_before_its_reason() -> None:
    """A parametrized id may hold a space (`test_x[a b]`); the ` - reason` after it varies between runs.

    A captured log record (its level padded to eight columns, then `logger:file:line`) names no test.
    """
    output: str = (
        "FAILED tests/test_a.py::test_x[a b] - AssertionError: 1 != 2\n"
        "ERROR tests/test_a.py::test_y - RuntimeError\nERROR - 2026-10-13 12:00:00 - pkg - a logged line\n"
        'ERROR    sphinx.util.docutils:logging.py:141 Duplicate target name: "section"\n'
        "=== 1 failed, 1 error, 2 passed in 0.10s ===\n"
    )
    found: Outcome = corpus_suite.read(output)
    assert found.failed == {"tests/test_a.py::test_x[a b]", "tests/test_a.py::test_y"}
    assert found.counts == {"failed": 1, "error": 1, "passed": 2}
