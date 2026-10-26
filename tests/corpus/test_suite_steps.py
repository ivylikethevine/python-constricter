"""A suite's steps: each part starts once the fixes it reads are made, on checkouts of the suite's own."""

import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Final, TypeAlias, cast

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
_KEY: Final = 12  # the characters of a parser's key
_AGAIN: Final = "again"  # in a tests record: the released tests run once more
_RELEASED: Final = "tests-released"  # the released tests, every fixed run's baseline
_UNION: Final = "infer-union"  # the fix with every source at once


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
    """Its fix (the trace's, for the traced tests), its kind as released, and the part that may stand for it.

    The tests as released wait for the traced tests where an earlier run's record of them is there
    to confirm, and the run would run them.
    """
    job: Job = _job(tmp_path / "this")
    needs: dict[str, frozenset[str]] = suite_steps.needs(job)
    union: str = "tests-infer-union"
    assert needs["traced"] == {"fix-unsafe"}
    assert needs[_RELEASED] == frozenset()
    assert needs[_UNION] == {"traced"}
    assert needs[union] == {_UNION, _RELEASED}
    assert needs["tests-fix-unsafe"] == {"fix-unsafe", _RELEASED, "tests-infer-trace", union}
    assert needs["tests-fix-certain"] == {"fix-certain", _RELEASED, "tests-fix-unsafe", union}
    assert needs["tests-infer-trace"] == {"traced", _RELEASED, union}
    assert needs["tests-infer-ty"] == {"infer-ty", _RELEASED, union}
    assert needs["types-fix-certain"] == {"fix-certain", "types-released", "types-fix-unsafe"}
    assert needs["types-fix-unsafe"] == {"fix-unsafe", "types-released", "types-infer-trace"}
    assert needs["tests"] == {
        _RELEASED,
        "tests-fix-certain",
        "tests-fix-unsafe",
        "tests-infer-ty",
        "tests-infer-trace",
        union,
    }
    Store(tmp_path / "old").write("a", "0.3.6", _RELEASED, _keyed(_PASSED))
    assert suite_steps.needs(job)[_RELEASED] == {"traced"}
    untraced: Job = job._replace(run=parse({"steps": {"tests": True, _RELEASED: False}}))
    assert suite_steps.needs(untraced)[_RELEASED] == frozenset()
    assert suite_steps.needs(untraced)["tests-fix-unsafe"] == {"fix-unsafe", _RELEASED}
    assert _UNION not in suite_steps.needs(untraced)  # no checker: the guesses' fix is every source's
    unhinted: Job = job._replace(
        run=parse({"steps": {"tests": True, "infer-with": ["ty"], "tests-hinted": False}}),
    )
    assert _UNION not in suite_steps.waiting(unhinted)
    switched: Job = job._replace(
        run=parse({"steps": {"tests": True, "infer-with": ["ty"], "tests-union": False}}),
    )
    assert _UNION not in suite_steps.waiting(switched)
    assert suite_steps.needs(switched)["tests-infer-ty"] == {"infer-ty", _RELEASED}


def _keyed(record: Record, environment: str = "e1") -> Record:
    """Give a released part's record the keys an earlier run's is taken by.

    Returns:
      It, at the suite's tag, read by this parser, on a checkout with `environment`.

    """
    keys: Record = {"tag": "1", "seconds": 3.0, "stopped": False, "parser": corpus_suite.parser()}
    return record | keys | {"environment": environment}


def test_each_part_has_a_checkout_of_its_kind(tmp_path: Path) -> None:
    """The tests' parts take the suite's `at_once` in turn; their whole every one, to run some again."""
    job: Job = _job(tmp_path)
    assert [suite_steps.checkouts(job, name)[0] for name in (_RELEASED, "tests-fix-certain")] == [
        "run0",
        "run1",
    ]
    assert suite_steps.checkouts(job, "tests") == ("run0", "run1")
    assert suite_steps.checkouts(job, "tests-infer-union") == ("run0",)
    assert not suite_steps.checkouts(job, _UNION)
    assert suite_steps.checkouts(job, "traced") == ("traced",)
    assert suite_steps.checkouts(job, "types-fix-unsafe") == ("types",)
    assert not suite_steps.checkouts(job, "types")
    assert suite_steps.binds("tests-fix-unsafe")
    assert not suite_steps.binds("types-released")


def test_the_tests_as_released_are_an_earlier_runs(tmp_path: Path) -> None:
    """Those at the suite's tag, of any version, read by this parser, on the same checkout, latest first.

    Each says whose run it is: the run that ran them, where a run took its record from another.
    Not one stopped, nor this run's.
    """
    runs: Path = tmp_path / "runs"
    job: Job = _job(runs / "this")
    assert not suite_steps.earlier(job)
    found: Record = _keyed(_PASSED)
    written: tuple[tuple[str, str, Record], ...] = (
        ("old", "0.3.6", found),
        ("other-tag", "dev", found | {"tag": "0"}),
        ("other-parser", "dev", found | {"parser": "0"}),
        ("other-checkout", "dev", _keyed(_FAILED, "e2")),
        ("stopped", "dev", found | {"stopped": True}),
        ("copied", "dev", found | {"from": "older", "confirmed": "traced"}),
        ("this", "dev", found | {"seconds": 1.0}),
    )
    when: int
    folder: str
    version: str
    record: Record
    for when, (folder, version, record) in enumerate(written):
        Store(runs / folder).write("a", version, _RELEASED, record)
        os.utime(runs / folder / "records" / "a" / version / "tests-released.json", (when, when))
    assert suite_steps.earlier(job) == [
        found | {"from": "older"},
        _keyed(_FAILED, "e2") | {"from": "other-checkout"},
        found | {"from": "old"},
    ]
    assert suite_steps.earlier(job, "e2") == [_keyed(_FAILED, "e2") | {"from": "other-checkout"}]


def test_an_earlier_runs_tests_are_taken_where_the_run_skips_them_or_the_trace_confirms_them(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """On the same checkout; the traced tests' outcome must equal the record's, where they ran."""
    runs: Path = tmp_path / "runs"
    job: Job = _job(runs / "this")

    def prepared(_job: Job, name: str) -> Path:
        return tmp_path / name

    def installed(_root: Path) -> str:
        return "e1"

    monkeypatch.setattr(suite_steps, "prepared", prepared)
    monkeypatch.setattr(corpus_suite, "installed", installed)
    assert suite_steps.taken(job) is None
    Store(runs / "old").write("a", "0.3.6", _RELEASED, _keyed(_PASSED))
    assert suite_steps.taken(job) is None  # the run runs them, and nothing confirms the record
    job.store.write("a", job.recorded, "traced", _FAILED | {"stopped": False})
    assert suite_steps.taken(job) is None
    job.store.write("a", job.recorded, "traced", _PASSED | {"stopped": False})
    assert suite_steps.taken(job) == _keyed(_PASSED) | {"from": "old", "confirmed": "traced"}
    Store(runs / "old").write("a", "0.3.6", _RELEASED, _keyed(_PASSED, "e2"))
    assert suite_steps.taken(job) is None  # another checkout's
    skipping: Job = job._replace(run=parse({"steps": {"tests": True, _RELEASED: False}}))
    job.store.write("a", job.recorded, "traced", _FAILED | {"stopped": False})
    Store(runs / "old").write("a", "0.3.6", _RELEASED, _keyed(_PASSED))
    assert suite_steps.taken(skipping) == _keyed(_PASSED) | {"from": "old"}


def _listed(job: Job, step: str, fixes: tuple[str, ...]) -> None:
    """Keep the fixes a fix step made (`<step>.fixes.jsonl`), each named, and its patch."""
    lines: list[str] = [
        json.dumps(
            {
                "path": "a.py",
                "line": index,
                "name": name,
                "annotation": "int",
                "tier": "certain",
                "kinds": ["literal"],
                "imports": [],
            },
        )
        for index, name in enumerate(fixes)
    ]
    _ = job.store.path("a", job.recorded, step, ".fixes.jsonl").write_text(
        "".join(f"{line}\n" for line in lines),
    )
    _ = job.store.path("a", job.recorded, step, ".patch").write_text("patch\n")


def test_a_part_stands_for_another_by_its_fixes_patch(tmp_path: Path) -> None:
    """The same patch, whatever its run gave; or one that holds its own and ran as released."""
    job: Job = _job(tmp_path)
    job.store.path("a", job.recorded, "x").parent.mkdir(parents=True)
    _listed(job, "fix-unsafe", ("a", "b"))
    _listed(job, "infer-trace", ("a", "b", "c"))
    _listed(job, "infer-ty", ("a", "b"))
    _listed(job, "infer-basedpyright", ("d",))
    _listed(job, "fix-certain", ("a",))
    _listed(job, "fix-likely", ("a", "b", "c"))
    job.store.write("a", job.recorded, "tests-fix-unsafe", _FAILED)
    job.store.write("a", job.recorded, "tests-infer-trace", _PASSED)
    job.store.write("a", job.recorded, "tests-fix-likely", {"implied": "infer-trace", "patch": "same"})

    def clean(record: Record) -> bool:
        return record["counts"] == _PASSED["counts"]

    assert suite_steps.standing(job, "tests", "fix-certain", clean) == {
        "implied": "infer-trace",
        "patch": "within",
    }
    assert suite_steps.standing(job, "tests", "infer-ty", clean) == {"implied": "fix-unsafe", "patch": "same"}
    assert suite_steps.standing(job, "tests", "infer-basedpyright", clean) is None
    assert suite_steps.standing(job, "types", "fix-certain", clean) is None  # no types part has run
    job.store.write("a", job.recorded, "tests-infer-trace", _FAILED)
    assert suite_steps.standing(job, "tests", "fix-certain", clean) is None
    # The tests after every source's fixes at once stand for each fix's where they're the released tests'.
    job.store.write("a", job.recorded, "tests-infer-union", _PASSED)
    step: str
    for step in ("fix-certain", "fix-unsafe", "infer-ty", "infer-basedpyright", "infer-trace"):
        assert suite_steps.standing(job, "tests", step, clean) == {"implied": _UNION, "patch": "union"}
    assert suite_steps.standing(job, "types", "infer-ty", clean) is None  # the type checks, never
    job.store.write("a", job.recorded, "tests-infer-union", _FAILED)
    assert suite_steps.standing(job, "tests", "fix-certain", clean) is None
    assert suite_steps.standing(job, "tests", "infer-ty", clean) == {"implied": "fix-unsafe", "patch": "same"}
    bare: Job = _job(tmp_path / "bare")  # a version that lists no fixes: a tier's are the guesses'
    bare.store.write("a", bare.recorded, "tests-fix-unsafe", _PASSED)
    assert suite_steps.standing(bare, "tests", "fix-certain", clean) == {
        "implied": "fix-unsafe",
        "patch": "within",
    }
    assert suite_steps.standing(bare, "tests", "infer-ty", clean) is None


def test_a_checkouts_environment_and_the_parser_key_a_record(tmp_path: Path) -> None:
    """A clone with no environment hashes to nothing's; the parser's key is its source's."""
    assert corpus_suite.installed(tmp_path) == hashlib.sha256(b"").hexdigest()
    assert len(corpus_suite.parser()) == _KEY
    assert corpus_suite.parser() == corpus_suite.parser()


def test_the_tests_gather_their_parts(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A tier the guesses' run stands for is theirs; a fixed run that differs runs again, as released does."""
    job: Job = _job(tmp_path)
    parts: dict[str, Record] = {
        _RELEASED: _PASSED | {"tag": "1", "seconds": 3.0, "stopped": False},
        "tests-infer-union": _FAILED,
        "tests-fix-unsafe": _PASSED,
        "tests-fix-certain": {"implied": _WHOLE},
        "tests-infer-ty": _FAILED,
        "tests-infer-trace": {"implied": "infer-ty", "patch": "same"},
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

    def tested(_root: Path, _suite: Suite, _keep: Path | None, _data: Path | None) -> corpus_suite.Outcome:
        return corpus_suite.Outcome({"passed": 2}, frozenset())

    monkeypatch.setattr(suite_steps, "prepared", prepared)
    monkeypatch.setattr(suite_steps, "_fixed_run", fixed_run)
    monkeypatch.setattr(corpus_suite, "reset", reset)
    monkeypatch.setattr(corpus_suite, "tested", tested)
    gathered: Record = suite_steps.tests(job)
    assert again == ["infer-ty-again"]
    assert gathered["seconds"] == parts[_RELEASED]["seconds"]
    assert (gathered["varies"], gathered["samples"]) == (False, {})
    fixed: dict[str, Record] = cast("dict[str, Record]", gathered["fixed"])
    assert list(fixed) == ["fix-certain", "fix-unsafe", "infer-ty", "infer-trace"]
    assert fixed["fix-certain"]["implied"] == _WHOLE
    assert fixed["infer-ty"]["new"] == ["t::f"]
    assert fixed["infer-trace"] == fixed["infer-ty"] | {"implied": "infer-ty", "patch": "same"}
    union: Record = cast("Record", gathered["union"])  # ran, differed, and isn't a row of the fixed runs
    assert (union["same"], union["new"]) == (False, ["t::f"])
    # Where the tests after every fix at once were the released tests', each part is theirs.
    for name in parts:
        if name != _RELEASED:
            job.store.write("a", job.recorded, name, {"implied": _UNION, "patch": "union"})
    job.store.write("a", job.recorded, "tests-infer-union", _PASSED)
    again.clear()
    stood: Record = suite_steps.tests(job)
    assert not again
    assert cast("Record", stood["union"])["same"] is True
    assert cast("dict[str, Record]", stood["fixed"])["infer-ty"] == _PASSED | {
        "same": True,
        "new": [],
        "implied": _UNION,
        "patch": "union",
    }


_Asked: TypeAlias = tuple[str, list[str]]  # a fix step asked for, and its extra options


def test_the_union_fixes_with_every_source_at_once(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Every checker's hints in the run's order, and the trace's where the tests ran traced."""
    job: Job = _job(tmp_path)
    asked: list[_Asked] = []

    def fix(_job: Job, step: str, extra: list[str]) -> Record:
        asked.append((step, list(extra)))
        return {"fixed": 1}

    def prepared(_job: Job, name: str) -> Path:
        return tmp_path / name

    monkeypatch.setattr(suite_steps, "fix", fix)
    monkeypatch.setattr(suite_steps, "prepared", prepared)
    assert suite_steps.union(job) == {"fixed": 1}
    job.store.write("a", job.recorded, "traced", {"error": "nothing runs its tests traced"})
    assert suite_steps.union(job) == {"fixed": 1}
    job.store.write("a", job.recorded, "traced", _PASSED | {"summary": "2 passed"})
    assert suite_steps.union(job) == {"fixed": 1}
    trace: str = str(tmp_path / "traced" / corpus_suite.TRACE_FILE)
    turn: Final = "--infer-in-turn"  # one checker's servers at a time
    assert asked == [
        (_UNION, ["--unsafe-fixes", "--infer-with", "ty", turn]),
        (_UNION, ["--unsafe-fixes", "--infer-with", "ty", turn]),
        (_UNION, ["--unsafe-fixes", "--infer-with", "ty", turn, "--infer-from", trace]),
    ]
    assert set(suite_steps.waiting(job)) >= {_UNION, "tests-infer-union", "tests"}


def test_one_fixed_run_runs_again_for_each_outcome_with_a_failure_new_or_gone(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Against every released run: this run's, the traced tests' and earlier runs' on the same checkout.

    Not one whose failures are theirs, whatever its other counts; nor the released tests, where
    another run of theirs is there.
    """
    runs: Path = tmp_path / "runs"
    job: Job = _job(runs / "this")
    skipping: Record = {"counts": {"passed": 1, "skipped": 1}, "failed": []}
    parts: dict[str, Record] = {
        _RELEASED: _keyed(_PASSED),
        "traced": _FAILED | {"stopped": False},
        "tests-fix-certain": {"implied": _WHOLE},
        "tests-fix-unsafe": _FAILED,
        "tests-infer-ty": _FAILED | {"failed": ["t::g"]},
        "tests-infer-trace": _FAILED | {"failed": ["t::g"]},
    }
    name: str
    record: Record
    for name, record in parts.items():
        job.store.write("a", job.recorded, name, record)
    Store(runs / "old").write("a", "0.3.6", _RELEASED, _keyed(skipping))
    Store(runs / "other").write("a", "0.3.6", _RELEASED, _keyed(_PASSED, "e2"))
    again: list[str] = []

    def fixed_run(_job: Job, step: str, kept: str, _base: Path) -> corpus_suite.Outcome:
        again.append(f"{step}{kept}")
        return corpus_suite.Outcome({"passed": 2}, frozenset())

    def tested(_root: Path, _suite: Suite, _keep: Path | None, _data: Path | None) -> corpus_suite.Outcome:
        raise AssertionError

    def prepared(_job: Job, name: str) -> Path:
        return tmp_path / name

    def reset(_root: Path, _suite: Suite) -> None:
        pass

    monkeypatch.setattr(suite_steps, "prepared", prepared)
    monkeypatch.setattr(suite_steps, "_fixed_run", fixed_run)
    monkeypatch.setattr(corpus_suite, "reset", reset)
    monkeypatch.setattr(corpus_suite, "tested", tested)
    gathered: Record = suite_steps.tests(job)
    assert again == ["infer-ty-again"]  # `t::f` is the traced tests' own; one run for `t::g`'s outcome
    assert gathered["samples"] == {"traced": _FAILED, "old": skipping}
    assert gathered["varies"] is True
    assert _AGAIN not in gathered
    fixed: dict[str, Record] = cast("dict[str, Record]", gathered["fixed"])
    assert (fixed["fix-unsafe"]["differs"], fixed["fix-unsafe"]["calm"]) == (False, True)
    assert fixed["fix-unsafe"]["again"] == []
    assert fixed["infer-ty"]["new"] == fixed["infer-trace"]["new"] == []
    assert (
        fixed["infer-ty"]["again"]
        == fixed["infer-trace"]["again"]
        == [{"counts": {"passed": 2}, "failed": []}]
    )


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
    moved: Record = suite_steps.weighed([skipping, skipping], [released, released], frozenset())
    assert (moved["differs"], moved["calm"]) == (False, False)
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


_JUNIT: Final = """<?xml version="1.0" encoding="utf-8"?>
<testsuites><testsuite name="pytest" tests="5">
<testcase classname="tests.test_a" name="test_x[a b]" file="tests/test_a.py" line="3" time="0.25"/>
<testcase classname="tests.test_a.TestB" name="test_y" file="tests/test_a.py" line="9" time="0.5">
<failure message="assert 1 == 2">Traceback</failure></testcase>
<testcase classname="tests.test_a.TestB.Inner" name="test_z" file="tests/test_a.py" line="12" time="0">
<error message="RuntimeError">Traceback</error></testcase>
<testcase classname="tests.sub.test_c" name="test_s" file="tests/sub/test_c.py" line="1" time="0.01">
<skipped type="pytest.skip" message="needs a server"/></testcase>
<testcase classname="tests.sub.test_c" name="test_f" file="tests/sub/test_c.py" line="5" time="0.02">
<skipped type="pytest.xfail" message="known"/></testcase>
<testcase classname="tests.sub.test_c.TestD" name="test_m" file="../../old/run0/tests/sub/test_c.py"
 time="0"/>
</testsuite></testsuites>
"""


# Run where pytest's rootdir is above the checkout, and a method its class inherits (`file` the base's).
_ABOVE: Final = """<testsuites><testsuite name="pytest" tests="2">
<testcase classname="suites.pkg-1.2-run0.tests.test_a" name="test_x"
 file="suites/pkg-1.2-run0/tests/test_a.py" time="0"/>
<testcase classname="suites.pkg-1.2-run0.tests.test_api.TestImage" name="test_load"
 file="suites/pkg-1.2-run0/tests/validators.py" time="0"/>
</testsuite></testsuites>
"""


def test_a_junit_report_names_each_test(tmp_path: Path) -> None:
    """Each test's node id is written back from its file and the classes after it, with its outcome."""
    report: Path = tmp_path / "part0.xml"
    _ = report.write_text(_JUNIT, encoding="utf-8")
    assert corpus_suite.junit_tests(report) == [
        corpus_suite.Test("tests/test_a.py::test_x[a b]", "passed", 0.25),
        corpus_suite.Test("tests/test_a.py::TestB::test_y", "failed", 0.5),
        corpus_suite.Test("tests/test_a.py::TestB::Inner::test_z", "error", 0.0),
        corpus_suite.Test("tests/sub/test_c.py::test_s", "skipped", 0.01, "needs a server"),
        corpus_suite.Test("tests/sub/test_c.py::test_f", "xfailed", 0.02, "known"),
        # A file outside the checkout: the path a cached rewritten module was compiled at.
        corpus_suite.Test("tests/sub/test_c.py::TestD::test_m", "passed", 0.0),
    ]
    # The class names start with the checkout's own path.
    checkout: Path = tmp_path / "suites" / "pkg-1.2-run0"
    (checkout / "tests").mkdir(parents=True)
    _ = (checkout / "tests" / "test_api.py").write_text("", encoding="utf-8")
    _ = report.write_text(_ABOVE, encoding="utf-8")
    assert [test.id for test in corpus_suite.junit_tests(report, checkout)] == [
        "tests/test_a.py::test_x",
        "tests/test_api.py::TestImage::test_load",
    ]
    _ = report.write_text("<testsuites>", encoding="utf-8")
    assert not corpus_suite.junit_tests(report)
    assert not corpus_suite.junit_tests(tmp_path / "none.xml")


def test_pytests_tests_are_read_from_their_junit_reports(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A part run by pytest writes one; every part's read gives the failed tests exactly, and a line a test.

    A logged `ERROR - ...` line names no test then. A part that wrote none leaves the text to say,
    and tests pytest doesn't run write none.
    """
    suite: Suite = Suite("", "", "", (), PYTEST)
    data: Path = tmp_path / "records" / "tests-released.tests.jsonl"
    text: str = (
        "ERROR - 2026-10-13 - logged\nFAILED tests/test_a.py::test_y - x\n=== 2 failed, 3 passed in 0.1s\n"
    )
    written: list[bool] = [True]
    ran: list[list[str]] = []

    def completed(args: list[str], *_args: object, **_options: object) -> SimpleNamespace:
        ran.append(args)
        report: str = next((word for word in args if word.startswith("--junitxml=")), "").partition("=")[2]
        if written[0] and report:
            _ = Path(report).write_text(_JUNIT, encoding="utf-8")
        return SimpleNamespace(stdout=text, stderr="")

    monkeypatch.setattr(corpus_suite, "_completed", completed)
    found: Outcome = corpus_suite.tested(tmp_path, suite, None, data)
    assert ran[0][-2:] == ["-o", "junit_family=xunit1"]  # no parts: the report's words end the command
    assert found.failed == {"tests/test_a.py::TestB::test_y", "tests/test_a.py::TestB::Inner::test_z"}
    assert found.counts == {"failed": 2, "passed": 3}
    lines: list[Record] = [json.loads(line) for line in data.read_text(encoding="utf-8").splitlines()]
    assert [(line["id"], line["outcome"], line["seconds"]) for line in lines][:2] == [
        ("tests/test_a.py::test_x[a b]", "passed", 0.25),
        ("tests/test_a.py::TestB::test_y", "failed", 0.5),
    ]
    written[0] = False
    assert corpus_suite.tested(tmp_path, suite, None, None).failed == {"tests/test_a.py::test_y"}
    raw: Suite = Suite("", "", "", (), ("python", "-m", "unittest"))
    assert corpus_suite.tested(tmp_path, raw, None, None).failed == {"tests/test_a.py::test_y"}
    assert not any(word.startswith("--junitxml=") for word in ran[-1])


def test_tests_python_c_runs_are_traced_on_their_workers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The code and its arguments under the tracer, the interpreter's own options before it.

    As Django's `runtests.py` runs, its workers forked: each records itself (`constricter.trace`).
    """
    code: str = "import runpy; runpy.run_path('tests/runtests.py', run_name='__main__')"
    suite: Suite = _SUITE._replace(tests=("python", "-Wall", "-c", code, "--parallel={workers}"), most=4)
    ran: list[list[str]] = []

    def reset(_root: Path, _suite: Suite) -> None:
        pass

    def completed(args: list[str], *_args: object, **_options: object) -> SimpleNamespace:
        ran.append(args)
        return SimpleNamespace(stdout="Ran 2 tests in 0.1s\n\nOK\n", stderr="")

    monkeypatch.delenv(corpus_suite.TRACER_VARIABLE, raising=False)
    monkeypatch.setattr(corpus_suite, "reset", reset)
    monkeypatch.setattr(corpus_suite, "_completed", completed)
    assert corpus_suite.traced(tmp_path, suite) is not None
    tracer: list[str] = ["-m", "constricter.trace", "--output", corpus_suite.TRACE_FILE, "--root", "."]
    workers: str = f"--parallel={corpus_suite.workers(suite)}"
    assert ran == [[str(tmp_path / ".venv" / "bin" / "python"), "-Wall", *tracer, "-c", code, workers]]
    assert not corpus_suite.traceable(_SUITE._replace(tests=("python", "runtests.py")))  # nor a script
