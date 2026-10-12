# SPDX-License-Identifier: MIT
"""A run's steps on a corpus package's own suite: they wait for the run's fixes, and share one checkout.

Each works on the suite's checkout at its pinned tag, taken back to the tag's source in between,
with a fix step's patch applied for a fixed run: the very fix the run's other outputs count.

- `tests`: the package's own tests as released, and after each of the run's fixes;
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
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import TYPE_CHECKING, Final, TypeAlias, cast

from tests.corpus import corpus_guesses, corpus_suite
from tests.corpus.pipeline import (
    FIX,
    GUESS,
    INFER,
    TESTS,
    TRACE,
    TRACED,
    TYPES,
    Job,
    Record,
    fix,
    fixing,
    settled,
)
from tests.corpus.run_config import CERTAIN, DEV, LIKELY, UNSAFE

if TYPE_CHECKING:
    from pathlib import Path

_Entry: TypeAlias = dict[str, object]
_TRACED_KIND: Final = "traced"  # the mechanism of a fix that rests on a trace


def _outcome(outcome: corpus_suite.Outcome, released: corpus_suite.Outcome | None = None) -> Record:
    """Lay a test run's outcome out for a record, beside the released run's where it's a fixed one.

    Returns:
      Its summary counts and the tests that failed; and whether it's the released run's, with the
      failures that one hasn't.

    """
    found: Record = {"counts": outcome.counts, "failed": sorted(outcome.failed)}
    if released is not None:
        found |= {"same": outcome == released, "new": sorted(outcome.failed - released.failed)}
    return found


def _patched(job: Job, step: str) -> str | None:
    """Take the suite's checkout to its tag's source, then apply the patch a fix step kept.

    Returns:
      `None` once it's applied; why it wasn't, where git refuses it.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    corpus_suite.reset(cast("Path", job.tree.base), suite)
    patch: Path = job.store.path(job.tree.name, job.recorded, step, ".patch")
    applied: subprocess.CompletedProcess[str] = subprocess.run(
        ["git", "apply", "--whitespace=nowarn", f"--directory={suite.source}", str(patch)],
        capture_output=True,
        text=True,
        check=False,
        cwd=job.tree.base,
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


def types(job: Job) -> Record:
    """Run the corpus package's own type checks as released, and after each fix the run made of it.

    Each fixed run is the checkout with a fix step's patch applied. An error the fixed run has that
    the released one hasn't is new, and is traced to the fix it's about (`corpus_suite.blamed`).

    Returns:
      The step's record: the released errors' count, and each fixed run's, with those gone and
      each new one.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = cast("Path", job.tree.base)
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
            if (refused := _patched(job, step)) is not None:
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
      The step's record: the traced tests' summary, and by tier the fixes a test could tell of,
      those whose every value fit and those one of whose didn't.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = cast("Path", job.tree.base)
    made: dict[str, list[corpus_suite.Fix]] = _made(job, f"{FIX}{UNSAFE}")
    os.environ.update(job.tree.variables or {})
    os.environ[corpus_suite.TRACER_VARIABLE] = corpus_guesses.TRACER
    os.environ[corpus_guesses.WITNESS_VARIABLE] = corpus_guesses.expected(base, made)
    summary: str | None
    if (summary := corpus_suite.traced(base, suite)) is None:
        return {"error": "nothing runs its tests traced"}
    step: str = f"{INFER}{TRACE}"
    by_trace: Record = fix(job, step, ("--unsafe-fixes", "--infer-from", str(base / corpus_suite.TRACE_FILE)))
    job.store.write(job.tree.name, job.recorded, step, by_trace)
    resting: int = sum(
        _TRACED_KIND in one.kinds.split("+") for one in itertools.chain(*_made(job, step).values())
    )
    record: Record = {"summary": summary, "resting": resting}
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
        level: str = LIKELY if each.likely else GUESS if each.unsafe else CERTAIN
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


def tests(job: Job) -> Record:
    """Run the corpus package's own tests as released, and after each fix the run made of it.

    Each fixed run is the checkout with a fix step's patch applied: the very fix the run's other
    outputs count. Where a fixed run differs, the released tests run once more: a suite whose own
    failures change from run to run says nothing by a difference.

    Returns:
      The step's record: each run's outcome, and whether the released tests vary.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = cast("Path", job.tree.base)
    kept: Path = job.store.root / "logs" / job.tree.name.replace(" ", "-") / job.recorded
    corpus_suite.reset(base, suite)
    os.environ.update(job.tree.variables or {})  # what the suite's commands need set
    start: float = time.perf_counter()
    released: corpus_suite.Outcome = corpus_suite.tested(base, suite, kept / "tests-released.txt")
    record: Record = {"tag": suite.tag, "seconds": round(time.perf_counter() - start, 1)}
    fixed: dict[str, Record] = {}
    step: str
    for step in fixing(job.run):
        if job.store.path(job.tree.name, job.recorded, step, ".patch").exists():
            refused: str | None = _patched(job, step)
            fixed[step] = (
                _outcome(corpus_suite.tested(base, suite, kept / f"tests-{step}.txt"), released)
                if refused is None
                else {"error": refused}
            )
    corpus_suite.reset(base, suite)
    if any(not ran.get("same", True) for ran in fixed.values()):
        again: corpus_suite.Outcome = corpus_suite.tested(base, suite, kept / "tests-released-again.txt")
        record["varies"] = again != released
        record["again"] = _outcome(again)
    return record | {"released": _outcome(released), "fixed": fixed}


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


def measure(job: Job) -> list[str]:
    """Run each of these steps the job's run asks for that has no record yet, one after another.

    Returns:
      The steps that failed.

    """
    failed: list[str] = []
    name: str
    step: Callable[[Job], Record]
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(1) as pool:
        for name, step in waiting(job).items():
            if job.store.read(job.tree.name, job.recorded, name) is None:
                done: Future[Record] = pool.submit(step, job)
                if not settled(job, name, done):
                    failed.append(name)
    return failed
