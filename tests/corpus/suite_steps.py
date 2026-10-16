# SPDX-License-Identifier: MIT
"""A run's steps on a corpus package's own suite: each starts once the fixes it reads are made.

Each works on a checkout of the suite's own (`checkouts`) at its pinned tag, taken back to the tag's
source in between, with a fix step's patch applied for a fixed run: the very fix the run's other
outputs count. None is the tree the run's other steps copy, so none waits for them to have.

- `traced`, for a suite whose tests can be traced, with this checkout: the tests under a witness
  told every fix of `fix-unsafe`, each fix's verdict kept; and `infer-trace`, a fix by their trace;
- the parts of `tests` (`pipeline.part`): the package's own tests as released (or as an earlier
  run found them, `earlier`), and after each of the run's fixes, the trace's too, each a step that
  starts once its fix is made; then `tests`, which runs a fixed run that differs again, with the
  released tests, and keeps only what it fails both times and no released run did as the fix's
  (`weighed`);
- the parts of `types`, for a suite with type checks: its own checkers' errors as released and after
  each fix, each new one traced to the fix it's about; then `types`, which gathers them.
"""

import itertools
import json
import os
import queue
import subprocess  # applies a fix's patch to a suite's checkout
import time
from collections import Counter
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import Final, TypeAlias, cast

from constricter.offences import Tier
from tests.corpus import corpus_guesses, corpus_suite
from tests.corpus.pipeline import (
    FIX,
    IMPLIED,
    INFER,
    RELEASED,
    TESTS,
    TRACE,
    TRACED,
    TYPES,
    Job,
    Record,
    fix,
    fixing,
    part,
    parts,
)
from tests.corpus.run_config import CERTAIN, DEV, LIKELY, UNSAFE

_Entry: TypeAlias = dict[str, object]
_WHOLE: Final = f"{FIX}{UNSAFE}"  # the fix step that makes every guess: the tiers' fixes are among its own
_RUN: Final = "run"  # numbered, names the checkouts a suite's tests run on (`Suite.at_once` of them)
_SKIPPED: Final = "skipped"  # in a part's record: why it has no run
_REFUSED: Final = "error"  # and why a fix's patch wasn't applied
_COUNTS: Final = "counts"  # and a test run's outcome's counts, where it has one
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


def prepared(job: Job, name: str) -> Path:
    """Clone and install the checkout of the suite `name`d, which a step of its own works on (once).

    Returns:
      It.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    return corpus_suite.checkout(job.tree.name, suite, name, variables=job.tree.variables)


def checkouts(job: Job, name: str) -> tuple[str, ...]:
    """Name the checkouts a suite step works on: each holds one step at a time.

    A part of its tests: one of its `Suite.at_once` (`run0`, `run1`), by the part's place, so that
    many go side by side; `tests`, which runs some again, every one. Its traced tests, and the parts
    of its type checks: a checkout each kind.

    Returns:
      Their names; none for a step that runs nothing of the suite's.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    tested: list[str] = parts(job.run, TESTS)
    if name in tested:
        return (f"{_RUN}{tested.index(name) % max(1, suite.at_once)}",)
    if name == TESTS:
        return tuple(f"{_RUN}{index}" for index in range(min(max(1, suite.at_once), len(tested))))
    if name == TRACED:
        return (TRACED,)
    return (TYPES,) if name in parts(job.run, TYPES) else ()


def binds(name: str) -> bool:
    """Check whether a step runs a suite's tests, which bind its port, if it has one.

    Returns:
      Whether it does.

    """
    return name in {TESTS, TRACED} or name.startswith(f"{TESTS}-")


def _read(job: Job, name: str) -> Record | None:
    return job.store.read(job.tree.name, job.recorded, name)


def _types_part(job: Job, name: str) -> Record:
    """Run a part of a suite's own type checks on their checkout: as released, or after a fix.

    An error the fixed run has that the released one hasn't is new, and is traced to the fix it's
    about (`corpus_suite.blamed`).

    Returns:
      As released, its errors; after a fix, their count, those gone and each new one; why it has
      none (`skipped`), or why the fix's patch wasn't applied.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = prepared(job, TYPES)
    os.environ.update(job.tree.variables or {})
    step: str
    corpus_suite.reset(base, suite)
    if (step := name.removeprefix(f"{TYPES}-")) == RELEASED:
        start: float = time.perf_counter()
        found: list[corpus_suite.Complaint] = corpus_suite.complaints(base, suite)
        return {"seconds": round(time.perf_counter() - start, 1), "errors": [list(each) for each in found]}
    released: Record | None
    if (released := _read(job, part(TYPES, RELEASED))) is None:
        return {_SKIPPED: "the checks as released have no record"}
    if not job.store.path(job.tree.name, job.recorded, step, ".patch").exists():
        return {_SKIPPED: "the fix made no patch"}
    refused: str | None
    if (refused := _patched(job, step, base)) is not None:
        return {_REFUSED: refused}
    change: str = subprocess.run(
        ["git", "diff", "--shortstat"],
        capture_output=True,
        text=True,
        check=False,
        cwd=base,
    ).stdout.strip()
    errors: list[list[str | int]] = cast("list[list[str | int]]", released["errors"])
    compared: corpus_suite.Compared = corpus_suite.blamed(
        base,
        corpus_suite.complaints(base, suite),
        [corpus_suite.Complaint(str(path), int(line), str(said)) for path, line, said in errors],
        (_made(job, step), change),
    )
    corpus_suite.reset(base, suite)
    return {
        "change": compared.change,
        "errors": compared.errors,
        "gone": compared.gone,
        "new": [_error(each) for each in compared.new],
        "kinds": dict(Counter(each.kind for each in compared.new).most_common()),
    }


def types(job: Job) -> Record:
    """Gather the parts of a suite's own type checks: as released, and after each fix the run made.

    Returns:
      The step's record: the released errors' count, and each fixed run's, with those gone and
      each new one.

    Raises:
      RuntimeError: the checks as released have no record: their part failed.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    released: Record | None
    if (released := _read(job, part(TYPES, RELEASED))) is None:
        message: str = "the checks as released have no record"
        raise RuntimeError(message)
    fixed: dict[str, Record] = {}
    name: str
    for name in parts(job.run, TYPES)[1:]:
        got: Record | None = _read(job, name)
        if got is not None and _SKIPPED not in got:
            fixed[name.removeprefix(f"{TYPES}-")] = got
    return {
        "checks": [" ".join(check) for check in suite.checks],
        "released": len(cast("list[object]", released["errors"])),
        "seconds": released["seconds"],
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
    base: Path = prepared(job, TRACED)
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
    base: Path = prepared(job, TRACED)
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


def _fixed_run(job: Job, step: str, kept: str, base: Path) -> corpus_suite.Outcome | str:
    """Run the suite's tests on checkout `base` with a fix step's patch applied, their output kept as `kept`.

    Returns:
      Their outcome; why the patch wasn't applied, where git refuses it.

    """
    refused: str | None
    if (refused := _patched(job, step, base)) is not None:
        return refused
    return corpus_suite.tested(
        base,
        cast("corpus_suite.Suite", job.tree.suite),
        job.store.logged(job.tree.name, job.recorded, TESTS).with_name(f"tests-{step}{kept}.txt"),
    )


def _ran(record: Record) -> corpus_suite.Outcome:
    return corpus_suite.Outcome(
        cast("dict[str, int]", record["counts"]),
        frozenset(cast("list[str]", record["failed"])),
    )


def _implied(step: str) -> bool:  # a tier's fix step, whose fixes are among the guesses' own
    return step != _WHOLE and step.startswith(FIX)


def earlier(job: Job) -> Record | None:
    """Find the suite's tests as released in the latest earlier run beside this one, at the suite's tag.

    Any version's: the released tests don't run constricter. Not one stopped for running too long.

    Returns:
      Its record, saying whose run it is (`from`); `None` where no earlier run has one.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    name: str = part(TESTS, RELEASED)
    corpus: str = job.tree.name.replace(" ", "-")
    found: list[Path] = sorted(
        job.store.root.parent.glob(f"*/records/{corpus}/*/{name}.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    path: Path
    for path in found:
        folder: Path = path.parents[3]  # the run's: `records/CORPUS/VERSION/` under it
        if folder.resolve() == job.store.root.resolve():
            continue
        record: Record = cast("Record", json.loads(path.read_text(encoding="utf-8")))
        if record.get("tag") == suite.tag and not record.get("stopped") and _COUNTS in record:
            return record | {"from": folder.name}
    return None


def _tests_part(job: Job, name: str) -> Record:
    """Run a part of a suite's own tests on its checkout (`checkouts`): as released, or after a fix.

    None runs after tests stopped as released for running too long. A tier's doesn't where the
    guesses' run was the released tests': it stands for theirs, whose fixes are among its own.

    Returns:
      Its outcome, as released with how long it took; why it has none (`skipped`), or why the fix's
      patch wasn't applied.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = prepared(job, checkouts(job, name)[0])
    os.environ.update(job.tree.variables or {})  # what the suite's commands need set
    step: str
    if (step := name.removeprefix(f"{TESTS}-")) == RELEASED:
        corpus_suite.reset(base, suite)
        start: float = time.perf_counter()
        kept: Path = job.store.logged(job.tree.name, job.recorded, TESTS).with_name("tests-released.txt")
        ran: corpus_suite.Outcome = corpus_suite.tested(base, suite, kept)
        took: float = round(time.perf_counter() - start, 1)
        return {"tag": suite.tag, "seconds": took, "stopped": corpus_suite.stopped(ran)} | _outcome(ran)
    released: Record | None = _read(job, part(TESTS, RELEASED))
    if released is None or released["stopped"]:
        return {_SKIPPED: "the tests as released have no record, or ran too long"}
    if not job.store.path(job.tree.name, job.recorded, step, ".patch").exists():
        return {_SKIPPED: "the fix made no patch"}
    whole: Record | None = _read(job, part(TESTS, _WHOLE)) if _implied(step) else None
    if whole is not None and _COUNTS in whole and _ran(whole) == _ran(released):
        return {IMPLIED: _WHOLE}
    fixed: corpus_suite.Outcome | str = _fixed_run(job, step, "", base)
    corpus_suite.reset(base, suite)
    return {_REFUSED: fixed} if isinstance(fixed, str) else _outcome(fixed)


def tests(job: Job) -> Record:
    """Gather the parts of a suite's own tests: as released, and after each fix the run made.

    Where a fixed run differs, the released tests run once more, and so does each fixed run that
    differed, side by side on the tests' checkouts: what differs between the two says whose a
    failure is (`weighed`). Tests stopped as released for running too long have no fixed run.

    Returns:
      The step's record: each run's outcome, and whether the released tests vary.

    Raises:
      RuntimeError: the tests as released have no record: their part failed.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    released_record: Record | None
    if (released_record := _read(job, part(TESTS, RELEASED))) is None:
        message: str = "the tests as released have no record"
        raise RuntimeError(message)
    released: list[corpus_suite.Outcome] = [_ran(released_record)]
    record: Record = {"tag": suite.tag, "seconds": released_record["seconds"]}
    if released_record["stopped"]:
        return record | {"released": _outcome(released[0]), "fixed": {}, "stopped": True}
    patched: list[str]
    first: dict[str, corpus_suite.Outcome | str]
    patched, first = _gathered(job)
    differ: list[str] = [
        step for step, ran in first.items() if not isinstance(ran, str) and ran != released[0]
    ]
    again: dict[str, corpus_suite.Outcome | str] = {}
    if differ:
        runs: dict[str, corpus_suite.Outcome | str] = _again(job, [RELEASED, *differ])
        released.append(cast("corpus_suite.Outcome", runs.pop(RELEASED)))
        again = runs
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


def _gathered(job: Job) -> tuple[list[str], dict[str, corpus_suite.Outcome | str]]:
    """Read the parts of a suite's tests after a fix.

    Returns:
      Each fix step that made a patch, and each one's run: its outcome, or why its patch wasn't
      applied; none where the guesses' run stands for it.

    """
    patched: list[str] = []
    first: dict[str, corpus_suite.Outcome | str] = {}
    name: str
    for name in parts(job.run, TESTS)[1:]:
        got: Record = _read(job, name) or {_SKIPPED: "it failed"}
        if _SKIPPED not in got:
            patched.append(name.removeprefix(f"{TESTS}-"))
        if _REFUSED in got:
            first[patched[-1]] = str(got[_REFUSED])
        elif _COUNTS in got:
            first[patched[-1]] = _ran(got)
    return patched, first


def _again(job: Job, steps: Sequence[str]) -> dict[str, corpus_suite.Outcome | str]:
    """Run the tests as released (`RELEASED`) and after the fix `steps` once more, side by side.

    On the tests' checkouts, as many at once as there are.

    Returns:
      Each run's outcome, or why its patch wasn't applied, by its fix step.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    free: queue.SimpleQueue[Path] = queue.SimpleQueue()
    name: str
    for name in checkouts(job, TESTS):
        free.put(prepared(job, name))
    kept: Path = job.store.logged(job.tree.name, job.recorded, TESTS).with_name("tests-released-again.txt")

    def again(step: str, base: Path) -> corpus_suite.Outcome | str:
        if step != RELEASED:
            return _fixed_run(job, step, "-again", base)
        corpus_suite.reset(base, suite)
        return corpus_suite.tested(base, suite, kept)

    def run(step: str) -> corpus_suite.Outcome | str:
        base: Path = free.get()
        try:
            return again(step, base)
        finally:
            corpus_suite.reset(base, suite)
            free.put(base)

    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, free.qsize())) as pool:
        return dict(zip(steps, pool.map(run, steps), strict=True))


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
    """List the steps `job`'s run asks for that wait for its fixes, each on checkouts of its own.

    Returns:
      Each by its name; none for a corpus with no suite.

    """
    suite: corpus_suite.Suite | None = job.tree.suite
    found: dict[str, Callable[[Job], Record]] = {}
    if suite is not None and job.run.steps.traced and corpus_suite.traceable(suite) and job.version == DEV:
        found[TRACED] = traced
    if suite is not None and job.run.steps.tests:
        found |= {name: partial(_tests_part, name=name) for name in parts(job.run, TESTS)}
        found[TESTS] = tests
    if suite is not None and suite.checks and job.run.steps.types:
        found |= {name: partial(_types_part, name=name) for name in parts(job.run, TYPES)}
        found[TYPES] = types
    return found


def needs(job: Job) -> dict[str, frozenset[str]]:
    """Say which steps each suite step waits for: those whose records or patches it reads.

    A part after a fix waits for the fix (`infer-trace`'s, for the traced tests) and for its kind's
    part as released; a tier's tests for the guesses', whose run may stand for theirs. Each kind's
    step waits for its parts, and the traced tests for `fix-unsafe`, whose fixes they hold.

    Returns:
      Each step's, by its name: only steps the run has.

    """
    names: dict[str, Callable[[Job], Record]] = waiting(job)
    every: frozenset[str] = frozenset((*names, *fixing(job.run)))
    found: dict[str, frozenset[str]] = {TRACED: frozenset({_WHOLE})} if TRACED in names else {}
    kind: str
    for kind in (TESTS, TYPES):
        if kind not in names:
            continue
        own: list[str] = parts(job.run, kind)
        found[kind] = frozenset(own)
        found[own[0]] = frozenset()
        name: str
        for name in own[1:]:
            step: str = name.removeprefix(f"{kind}-")
            standing: str = part(kind, _WHOLE) if kind == TESTS and _implied(step) else ""
            made: str = TRACED if step == f"{INFER}{TRACE}" else step
            found[name] = frozenset({made, own[0], standing}) & every
    return found
