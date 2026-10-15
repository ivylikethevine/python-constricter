# SPDX-License-Identifier: MIT
"""A run's steps on a corpus package's own suite: they wait for the run's fixes, and share one checkout.

Each works on the suite's checkout at its pinned tag, taken back to the tag's source in between,
with a fix step's patch applied for a fixed run: the very fix the run's other outputs count.

- `tests`: the package's own tests as released, and after each of the run's fixes, the trace's
  too; a fixed run that differs is run again, with the released tests, and only what it fails both
  times and no released run did is the fix's (`weighed`);
- `traced`, for a suite whose tests can be traced, with this checkout: the tests under a witness
  told every fix of `fix-unsafe`, each fix's verdict kept; and `infer-trace`, a fix by their trace;
- `types`, for a suite with type checks: its own checkers' errors as released and after each fix,
  each new one traced to the fix it's about.
"""

import itertools
import json
import os
import subprocess  # applies a fix's patch to a suite's checkout
import time
from collections import Counter
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Final, TypeAlias, cast

from constricter.offences import Tier
from tests.corpus import corpus_guesses, corpus_suite
from tests.corpus.pipeline import (
    FIX,
    IMPLIED,
    INFER,
    TESTS,
    TRACE,
    TRACED,
    TYPES,
    Job,
    Record,
    fix,
    fixing,
)
from tests.corpus.run_config import CERTAIN, DEV, LIKELY, UNSAFE

_Entry: TypeAlias = dict[str, object]
_WHOLE: Final = f"{FIX}{UNSAFE}"  # the fix step that makes every guess: the tiers' fixes are among its own
_APART: Final = "types"  # names the checkout a suite's type checks run on, beside its tests' own
_TRACED_KIND: Final = "traced"  # the mechanism of a fix that rests on a trace
# The counts a test moves between, failing where it passed or passing where it was expected to fail
# (altair's does from run to run): a run's others say what else changed.
_MOVED: Final = frozenset({"passed", "failed", "error", "failures", "errors", "xfailed", "xpassed"})


def _outcome(outcome: corpus_suite.Outcome) -> Record:
    """Lay a test run's outcome out for a record.

    Returns:
      Its summary counts and the tests that failed.

    """
    return {"counts": outcome.counts, "failed": sorted(outcome.failed)}


def _others(outcome: corpus_suite.Outcome) -> dict[str, int]:
    return {kind: count for kind, count in outcome.counts.items() if kind not in _MOVED}


def weighed(
    runs: Sequence[corpus_suite.Outcome],
    released: Sequence[corpus_suite.Outcome],
    named: frozenset[str],
) -> Record:
    """Lay a fixed run's outcome out beside the released tests', and say what of it is the fix's.

    `runs`: the fixed run's outcomes, a second where its first differed from the first of
    `released`, the released tests' (run again then too). A suite's own failures come and go, so a
    failure is the fix's only if every fixed run has it and no released run does (`new`), and a
    released failure is gone only if every released run has it and no fixed run does (`gone`).
    `named`: the tests the catalog says a fix may change (`Suite.differs`), listed apart.

    Returns:
      The first run's counts and failures, and whether it's the released tests' (`same`); where it
      isn't, what's new and gone, the tests named among them, and whether the run differs by more
      than those: by a test not named, or by its other counts (the skipped, say).

    """
    none: list[str] = []
    found: Record = _outcome(runs[0]) | {"same": runs[0] == released[0], "new": none}
    if found["same"]:
        return found
    ever: frozenset[str] = released[0].failed.union(*(each.failed for each in released))
    always: frozenset[str] = released[0].failed.intersection(*(each.failed for each in released))
    new: frozenset[str] = runs[0].failed.intersection(*(each.failed for each in runs)) - ever
    gone: frozenset[str] = always - runs[0].failed.union(*(each.failed for each in runs))
    calm: bool = any(_others(runs[-1]) == _others(each) for each in released)
    return found | {
        "new": sorted(new - named),
        "gone": sorted(gone - named),
        "named": sorted((new | gone) & named),
        "differs": bool(new - named or gone - named or not calm),
        "again": [_outcome(each) for each in runs[1:]],
    }


def _patched(job: Job, step: str, base: Path | None = None) -> str | None:
    """Take the suite's checkout to its tag's source, then apply the patch a fix step kept.

    `base`: another checkout of the suite, in place of the tree's.

    But for the files git doesn't track there (a build's generated `_version.py`): `reset` can't
    take one back to what it was, and the next patch wouldn't apply.

    Returns:
      `None` once it's applied; why it wasn't, where git refuses it.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base = cast("Path", job.tree.base) if base is None else base
    corpus_suite.reset(base, suite)
    patch: Path = job.store.path(job.tree.name, job.recorded, step, ".patch")
    untracked: str = subprocess.run(
        ["git", "ls-files", "--others", "--", suite.source],
        capture_output=True,
        text=True,
        check=False,
        cwd=base,
    ).stdout
    kept: list[str] = [f"--exclude={path}" for path in untracked.splitlines() if path.endswith(".py")]
    applied: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", f"--directory={suite.source}", *kept, str(patch)],
        capture_output=True,
        text=True,
        check=False,
        cwd=base,
    )
    return applied.stderr.strip() if applied.returncode else None


def _made(job: Job, step: str) -> dict[str, list[corpus_suite.Fix]]:
    """Read the fixes a fix step listed (`<step>.fixes.jsonl`), as the suite's checkout names their files.

    Returns:
      Them, per file.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    listed: Path = job.store.path(job.tree.name, job.recorded, step, ".fixes.jsonl")
    found: dict[str, list[corpus_suite.Fix]] = {}
    line: str
    for line in listed.read_text(encoding="utf-8").splitlines() if listed.exists() else ():
        each: _Entry = cast("_Entry", json.loads(line))
        path: str = f"{suite.source}/{each['path']}"
        found.setdefault(path, []).append(
            corpus_suite.Fix(
                path,
                cast("int", each["line"]),
                str(each["name"]),
                str(each["annotation"]),
                "+".join(cast("list[str]", each["kinds"])),
                each["tier"] != CERTAIN,
                each["tier"] == LIKELY,
                tuple(cast("list[str]", each["imports"])),
            ),
        )
    return found


def _error(each: corpus_suite.Blamed) -> Record:
    """Lay a new type error out for a record, with the fix it's traced to.

    Returns:
      Where it is, what it says, its fix's mechanisms (`(untraced)` with none), and the fix.

    """
    about: corpus_suite.Fix | None = each.fix
    return {
        "path": each.complaint.path,
        "line": each.complaint.line,
        "message": each.complaint.message,
        "kind": each.kind,
        "fix": about and {"name": about.name, "annotation": about.annotation, "line": about.line},
    }


def apart(job: Job) -> Path:
    """Clone and install the checkout a suite's type checks run on, beside its tests' own (once).

    Returns:
      It.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    return corpus_suite.checkout(job.tree.name, suite, _APART, variables=job.tree.variables)


def types(job: Job) -> Record:
    """Run the corpus package's own type checks as released, and after each fix the run made of it.

    Each fixed run is the checkout with a fix step's patch applied. An error the fixed run has that
    the released one hasn't is new, and is traced to the fix it's about (`corpus_suite.blamed`). On
    a checkout of the suite of their own (installed the first time), so they run beside its tests.

    Returns:
      The step's record: the released errors' count, and each fixed run's, with those gone and
      each new one.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = apart(job)
    corpus_suite.reset(base, suite)
    os.environ.update(job.tree.variables or {})
    start: float = time.perf_counter()
    released: list[corpus_suite.Complaint] = corpus_suite.complaints(base, suite)
    seconds: float = time.perf_counter() - start
    fixed: dict[str, Record] = {}
    step: str
    for step in fixing(job.run):
        if job.store.path(job.tree.name, job.recorded, step, ".patch").exists():
            refused: str | None
            if (refused := _patched(job, step, base)) is not None:
                fixed[step] = {"error": refused}
                continue
            change: str = subprocess.run(
                ["git", "diff", "--shortstat"],
                capture_output=True,
                text=True,
                check=False,
                cwd=base,
            ).stdout.strip()
            found: corpus_suite.Compared = corpus_suite.blamed(
                base,
                corpus_suite.complaints(base, suite),
                released,
                (_made(job, step), change),
            )
            fixed[step] = {
                "change": found.change,
                "errors": found.errors,
                "gone": found.gone,
                "new": [_error(each) for each in found.new],
                "kinds": dict(Counter(each.kind for each in found.new).most_common()),
            }
    corpus_suite.reset(base, suite)
    return {
        "checks": [" ".join(check) for check in suite.checks],
        "released": len(released),
        "seconds": round(seconds, 1),
        "fixed": fixed,
    }


def traced(job: Job) -> Record:
    """Trace the corpus package's tests under the witness, then fix a copy by their trace.

    The witness is told each fix of the run's `fix-unsafe` step, and holds each fixed binding's value
    to the fix's annotation as the tests bind it (`corpus_guesses`): each fix's verdict is kept, a
    line each, with the types the trace saw (`traced.verdicts.jsonl`). The fix by the trace is a
    fix step of its own, `infer-trace` (`--fix --unsafe-fixes --infer-from` the trace), which the
    suite's tests and type checks then run after as they do any other.

    Returns:
      The step's record: the traced tests' summary, outcome and seconds, and by tier the fixes a
      test could tell of, those whose every value fit and those one of whose didn't.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = cast("Path", job.tree.base)
    made: dict[str, list[corpus_suite.Fix]] = _made(job, f"{FIX}{UNSAFE}")
    os.environ.update(job.tree.variables or {})
    os.environ[corpus_suite.TRACER_VARIABLE] = corpus_guesses.TRACER
    os.environ[corpus_guesses.WITNESS_VARIABLE] = corpus_guesses.expected(base, made)
    start: float = time.perf_counter()
    ran: tuple[str, corpus_suite.Outcome] | None = corpus_suite.traced(
        base,
        suite,
        job.store.logged(job.tree.name, job.recorded, TRACED).with_name("tests-traced.txt"),
    )
    seconds: float = time.perf_counter() - start
    if ran is None:
        return {"error": "nothing runs its tests traced"}
    step: str = f"{INFER}{TRACE}"
    by_trace: Record = fix(job, step, ("--unsafe-fixes", "--infer-from", str(base / corpus_suite.TRACE_FILE)))
    job.store.write(job.tree.name, job.recorded, step, by_trace)
    resting: int = sum(
        _TRACED_KIND in one.kinds.split("+") for one in itertools.chain(*_made(job, step).values())
    )
    record: Record = {"summary": ran[0], "resting": resting, "seconds": round(seconds, 1)} | _outcome(ran[1])
    record["stopped"] = corpus_suite.stopped(ran[1])  # for running too long: its trace is a part of one
    return record | {key: dict(count) for key, count in _judged(job, made).items()}


def _judged(job: Job, made: dict[str, list[corpus_suite.Fix]]) -> dict[str, Counter[str]]:
    """Read the witness's verdict on each of the fixes `made`, and keep each, a line each.

    With the types the trace saw the binding hold (`traced.verdicts.jsonl`).

    Returns:
      By tier, the fixes a traced test could tell of, those whose every value fit, and those one
      of whose didn't.

    """
    base: Path = cast("Path", job.tree.base)
    judged: corpus_guesses.Verdicts = corpus_guesses.verdicts(base)
    seen: corpus_guesses.Seen = corpus_guesses.seen(base, corpus_suite.TRACE_FILE)
    counts: dict[str, Counter[str]] = {"told": Counter(), "held": Counter(), "differed": Counter()}
    lines: list[str] = []
    each: corpus_suite.Fix
    for each in itertools.chain.from_iterable(made.values()):
        verdict: corpus_guesses.Verdict = corpus_guesses.verdict(judged, each.path, each.line, each.name)
        level: str = Tier.of(unsafe=each.unsafe, likely=each.likely).value
        counts["told"][level] += bool(verdict.fit or verdict.differ)
        counts["held"][level] += bool(verdict.fit and not verdict.differ)
        counts["differed"][level] += bool(verdict.differ)
        lines.append(
            json.dumps(
                {
                    "path": each.path,
                    "line": each.line,
                    "name": each.name,
                    "annotation": each.annotation,
                    "tier": level,
                    "kinds": each.kinds.split("+"),
                    "verdict": list(verdict),
                    "seen": list(corpus_guesses.held(seen, each.path, each.line, each.name)),
                },
            ),
        )
    _ = job.store.path(job.tree.name, job.recorded, TRACED, ".verdicts.jsonl").write_text(
        "".join(f"{line}\n" for line in lines),
        encoding="utf-8",
    )
    return counts


def _fixed_run(job: Job, step: str, kept: str) -> corpus_suite.Outcome | str:
    """Run the suite's tests on its checkout with a fix step's patch applied, their output kept as `kept`.

    Returns:
      Their outcome; why the patch wasn't applied, where git refuses it.

    """
    refused: str | None
    if (refused := _patched(job, step)) is not None:
        return refused
    return corpus_suite.tested(
        cast("Path", job.tree.base),
        cast("corpus_suite.Suite", job.tree.suite),
        job.store.logged(job.tree.name, job.recorded, TESTS).with_name(f"tests-{step}{kept}.txt"),
    )


def tests(job: Job) -> Record:
    """Run the corpus package's own tests as released, and after each fix the run made of it.

    Each fixed run is the checkout with a fix step's patch applied: the very fix the run's other
    outputs count, the trace's too. Where a fixed run differs, the released tests run once more,
    and so does each fixed run that differed: what differs between the two says whose a failure is
    (`weighed`). Tests stopped as released for running too long have no fixed run.

    Returns:
      The step's record: each run's outcome, and whether the released tests vary.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = cast("Path", job.tree.base)
    kept: Path = job.store.logged(job.tree.name, job.recorded, TESTS)
    corpus_suite.reset(base, suite)
    os.environ.update(job.tree.variables or {})  # what the suite's commands need set
    start: float = time.perf_counter()
    released: list[corpus_suite.Outcome] = [
        corpus_suite.tested(base, suite, kept.with_name("tests-released.txt")),
    ]
    record: Record = {"tag": suite.tag, "seconds": round(time.perf_counter() - start, 1)}
    if corpus_suite.stopped(released[0]):
        return record | {"released": _outcome(released[0]), "fixed": {}, "stopped": True}
    patched: list[str] = [
        step
        for step in fixing(job.run)
        if job.store.path(job.tree.name, job.recorded, step, ".patch").exists()
    ]
    if not job.run.steps.tests_hinted:
        patched = [step for step in patched if not step.startswith(INFER)]
    first: dict[str, corpus_suite.Outcome | str] = _first(job, patched, released[0])
    corpus_suite.reset(base, suite)
    again: dict[str, corpus_suite.Outcome | str] = {}
    if any(ran != released[0] for ran in first.values() if not isinstance(ran, str)):
        released.append(corpus_suite.tested(base, suite, kept.with_name("tests-released-again.txt")))
        again = {
            step: _fixed_run(job, step, "-again")
            for step, ran in first.items()
            if not isinstance(ran, str) and ran != released[0]
        }
        corpus_suite.reset(base, suite)
        record["varies"] = released[1] != released[0]
        record["again"] = _outcome(released[1])
    named: frozenset[str] = told(suite, [*released, *_both(*first.values(), *again.values())])
    fixed: dict[str, Record] = {
        step: {"error": ran}
        if isinstance(ran, str)
        else weighed(_both(ran, again.get(step)), released, named)
        for step, ran in first.items()
    }
    none: list[str] = []
    same: Record = _outcome(released[0]) | {"same": True, "new": none, IMPLIED: _WHOLE}
    return record | {
        "released": _outcome(released[0]),
        "fixed": {step: fixed.get(step, same) for step in patched},
    }


def _first(
    job: Job,
    patched: Sequence[str],
    released: corpus_suite.Outcome,
) -> dict[str, corpus_suite.Outcome | str]:
    """Run the suite's tests after each of the fixes `patched`, but those another run stands for.

    Every guess's run first: the same as `released`, it stands for the tiers under it, whose fixes
    are among its own.

    Returns:
      Each run's outcome, or why its patch wasn't applied, by its fix step; none for a tier implied.

    """
    first: dict[str, corpus_suite.Outcome | str] = {
        step: _fixed_run(job, step, "") for step in patched if step == _WHOLE
    }
    implied: bool = first.get(_WHOLE) == released
    return first | {
        step: _fixed_run(job, step, "")
        for step in patched
        if step != _WHOLE and not (implied and step.startswith(FIX))
    }


def told(suite: corpus_suite.Suite, runs: Sequence[corpus_suite.Outcome]) -> frozenset[str]:
    """Find the tests `runs` failed that the catalog says a fix may change (`Suite.differs`).

    Returns:
      Each failed test it names: by itself, or by its file or its class (`tests/test_a.py`,
      `tests/test_a.py::TestA`).

    """
    listed: tuple[str, ...] = tuple(test for test, _ in suite.differs)
    return frozenset(
        test
        for each in runs
        for test in each.failed
        if test in listed or test.startswith(tuple(f"{part}::" for part in listed))
    )


def _both(*runs: corpus_suite.Outcome | str | None) -> list[corpus_suite.Outcome]:
    return [each for each in runs if isinstance(each, corpus_suite.Outcome)]


def waiting(job: Job) -> dict[str, Callable[[Job], Record]]:
    """List the steps `job`'s run asks for that wait for its fixes: they work on the corpus's one checkout.

    Returns:
      Each by its name; none for a corpus with no suite.

    """
    suite: corpus_suite.Suite | None = job.tree.suite
    found: dict[str, Callable[[Job], Record]] = {}
    if suite is not None and job.run.steps.traced and corpus_suite.traceable(suite) and job.version == DEV:
        found[TRACED] = traced
    if suite is not None and job.run.steps.tests:
        found[TESTS] = tests
    if suite is not None and suite.checks and job.run.steps.types:
        found[TYPES] = types
    return found
