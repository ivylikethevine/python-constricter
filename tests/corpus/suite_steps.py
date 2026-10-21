# SPDX-License-Identifier: MIT
"""A run's steps on a corpus package's own suite: each starts once the fixes it reads are made.

Each works on a checkout of the suite's own (`checkouts`) at its pinned tag, taken back to the tag's
source in between, with a fix step's patch applied for a fixed run: the very fix the run's other
outputs count. None is the tree the run's other steps copy, so none waits for them to have.

- `traced`, for a suite whose tests can be traced, with this checkout: the tests under a witness
  told every fix of `fix-unsafe`, each fix's verdict kept; and `infer-trace`, a fix by their trace;
- the parts of `tests` (`pipeline.part`): the package's own tests as released (or as an earlier
  run found them, `taken`), and after each of the run's fixes, the trace's too, each a step that
  starts once its fix is made, unless another fix's part stands for it (`standing`): first the one
  after every source's fixes at once (`union`, a fix step of its own), which stands for them all
  where it's the released tests', so that most suites' tests run twice, not eight times; then `tests`,
  which runs one fixed run again for each outcome with a failure new or gone, and keeps only what
  it fails both times and no released run did as the fix's (`weighed`);
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
    FROM,
    IMPLIED,
    INFER,
    PATCH,
    RELEASED,
    TESTS,
    TRACE,
    TRACED,
    TYPES,
    UNION,
    Job,
    Record,
    fix,
    fixing,
    part,
    parts,
    united,
)
from tests.corpus.run_config import CERTAIN, DEV, LIKELY, UNSAFE

_Entry: TypeAlias = dict[str, object]
_Fixes: TypeAlias = frozenset[
    tuple[str, int, str, str, tuple[str, ...]]
]  # a fix step's, as `_fixes` reads them
_Key: TypeAlias = tuple[tuple[tuple[str, int], ...], frozenset[str]]  # an outcome, hashable (`_key`)
_WHOLE: Final = f"{FIX}{UNSAFE}"  # the fix step that makes every guess: the tiers' fixes are among its own
_TRACE: Final = f"{INFER}{TRACE}"  # the fix step by the traced tests, which holds the guesses' fixes (mostly)
_UNION: Final = (
    f"{INFER}{UNION}"  # the fix step with every source at once, whose tests may stand for each fix's
)
_RUN: Final = "run"  # numbered, names the checkouts a suite's tests run on (`Suite.at_once` of them)
_SKIPPED: Final = "skipped"  # in a part's record: why it has no run
_REFUSED: Final = "error"  # and why a fix's patch wasn't applied
_COUNTS: Final = "counts"  # and a test run's outcome's counts, where it has one
_SAME: Final = "same"  # a part's `patch`: the standing fix's is the same as its own
_WITHIN: Final = "within"  # or holds its own, and its run was the released tests'
_EVERY: Final = "union"  # or is every fix's at once, and its run was the released tests'
_ENVIRONMENT: Final = "environment"  # in a released part's record: its checkout's (`corpus_suite.installed`)
_PARSER: Final = "parser"  # and what read the tests' output (`corpus_suite.parser`)
CONFIRMED: Final = "confirmed"  # in a taken record: the step whose outcome equals it (the traced tests)
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

    `runs`: the fixed run's outcomes, a second where its first had a failure new or gone against
    `released`, the released tests': this run's, those of earlier runs on the same checkout, the
    traced tests' and the released tests' run again. A suite's own failures come and go, so a
    failure is the fix's only if every fixed run has it and no released run does (`new`), and a
    released failure is gone only if every released run has it and no fixed run does (`gone`).
    `named`: the tests the catalog says a fix may change (`Suite.differs`), listed apart.

    Returns:
      The first run's counts and failures, and whether it's the released tests' (`same`); where it
      isn't, what's new and gone, the tests named among them, whether the run differs by a test not
      named (`differs`), and whether its other counts (the skipped, say) are some released run's
      (`calm`): where they aren't and no failure is new or gone, they moved as the released tests'
      own do between runs (sqlalchemy's skips, by its drivers' order).

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
        "differs": bool(new - named or gone - named),
        "calm": calm,
        "again": [_outcome(each) for each in runs[1:]],
    }


def _key(outcome: corpus_suite.Outcome) -> _Key:
    return tuple(sorted(outcome.counts.items())), outcome.failed


def _fixes(job: Job, step: str) -> _Fixes | None:
    """Read the fixes a fix step listed, as a set: where, the name, the annotation, the imports it adds.

    Returns:
      Them; `None` where the version lists none.

    """
    if not job.store.path(job.tree.name, job.recorded, step, ".fixes.jsonl").exists():
        return None
    return frozenset(
        (each.path, each.line, each.name, each.annotation, each.imports)
        for each in itertools.chain.from_iterable(_made(job, step).values())
    )


def _within(step: str, other: str, mine: _Fixes | None, theirs: _Fixes | None) -> bool:
    """Check whether the fix `other` made holds every fix `step` made, and more.

    By the fixes each listed; where the version lists none, a tier's are among the guesses' own.

    Returns:
      Whether it does.

    """
    if mine is not None and theirs is not None:
        return mine < theirs
    return _implied(step) and other == _WHOLE


def standing(job: Job, kind: str, step: str, clean: Callable[[Record], bool]) -> Record | None:
    """Find a part of `kind` that stands for the fix `step`'s, which then needn't run.

    One after a fix whose patch is the same, whatever its run gave; or one after a fix whose
    patch holds this one's and whose run was the released tests' or checks' (`clean`): fewer
    annotations don't fail where more passed. A part that is itself implied stands by the one it's
    implied by. For the tests, the part after every source's fixes at once (`union`) stands for
    each fix's where its run was the released tests': a binding two sources type has the first's
    there, not each fix's own, the same assumption one step further.

    Returns:
      The part's record: the fix step whose part stands for it, and how (`patch`); `None` where
      none does.

    """
    if kind == TESTS and step != _UNION and united(job.run):
        every: Record | None = _read(job, part(TESTS, _UNION))
        if every is not None and _COUNTS in every and clean(every):
            return {IMPLIED: _UNION, PATCH: _EVERY}
    mine: _Fixes | None = _fixes(job, step)
    within: list[str] = []
    seen: set[str] = set()
    name: str
    for name in parts(job.run, kind)[1:]:
        other: str = name.removeprefix(f"{kind}-")
        record: Record | None = _read(job, name)
        if other == step or record is None or _SKIPPED in record or _REFUSED in record:
            continue
        target: str = str(record[IMPLIED]) if IMPLIED in record else other
        ran: Record | None = _read(job, part(kind, target)) if target != other else record
        if target == step or target in seen or ran is None:
            continue
        seen.add(target)
        theirs: _Fixes | None = _fixes(job, target)
        if mine is not None and mine == theirs:
            return {IMPLIED: target, PATCH: _SAME}
        if _within(step, target, mine, theirs) and clean(ran):
            within.append(target)
    return {IMPLIED: within[0], PATCH: _WITHIN} if within else None


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
    if name == part(TESTS, _UNION):  # after the released tests', before every other part
        return (f"{_RUN}0",)
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
      As released, its errors and its checkout's environment; after a fix, their count, those gone
      and each new one; the part that stands for it (`implied`); why it has none (`skipped`), or
      why the fix's patch wasn't applied.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = prepared(job, TYPES)
    os.environ.update(job.tree.variables or {})
    step: str
    corpus_suite.reset(base, suite)
    if (step := name.removeprefix(f"{TYPES}-")) == RELEASED:
        start: float = time.perf_counter()
        found: list[corpus_suite.Complaint] = corpus_suite.complaints(base, suite)
        return {
            "seconds": round(time.perf_counter() - start, 1),
            "errors": [list(each) for each in found],
            _ENVIRONMENT: corpus_suite.installed(base),
        }
    released: Record | None
    if (released := _read(job, part(TYPES, RELEASED))) is None:
        return {_SKIPPED: "the checks as released have no record"}
    if not job.store.path(job.tree.name, job.recorded, step, ".patch").exists():
        return {_SKIPPED: "the fix made no patch"}
    stood: Record | None
    if (
        stood := standing(job, TYPES, step, lambda ran: not ran.get("new") and not ran.get("gone"))
    ) is not None:
        return stood
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
      each new one; a part another stands for (`implied`) as that one's.

    Raises:
      RuntimeError: the checks as released have no record: their part failed.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    released: Record | None
    if (released := _read(job, part(TYPES, RELEASED))) is None:
        message: str = "the checks as released have no record"
        raise RuntimeError(message)
    steps: list[str] = [name.removeprefix(f"{TYPES}-") for name in parts(job.run, TYPES)[1:]]
    got: dict[str, Record] = {}
    step: str
    for step in steps:
        read: Record | None = _read(job, part(TYPES, step))
        if read is not None and _SKIPPED not in read:
            got[step] = read
    fixed: dict[str, Record] = {step: record for step, record in got.items() if IMPLIED not in record}
    for step in steps:
        if step in got and IMPLIED in got[step]:
            fixed[step] = _stood(fixed, got[step], {})
    return {
        "checks": [" ".join(check) for check in suite.checks],
        "released": len(cast("list[object]", released["errors"])),
        "seconds": released["seconds"],
        "fixed": {step: fixed[step] for step in steps if step in fixed},
    }


def _stood(fixed: dict[str, Record], record: Record, default: Record) -> Record:
    """Lay an implied part out as the record of the part that stands for it, saying so.

    Returns:
      That part's record (`default` where it has none), with the step it's implied by and how.

    """
    target: str = str(record[IMPLIED])
    return fixed.get(target, default) | {IMPLIED: target, PATCH: record.get(PATCH, _WITHIN)}


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
        _data(job, f"{step}{kept}"),
    )


def _data(job: Job, run: str) -> Path:
    """Find where a test run's tests go, a line each (see `corpus_suite.Test`), beside its record.

    Returns:
      The path: `records/<corpus>/<version>/tests-<run>.tests.jsonl`.

    """
    return job.store.path(job.tree.name, job.recorded, f"{TESTS}-{run}", ".tests.jsonl")


def _ran(record: Record) -> corpus_suite.Outcome:
    return corpus_suite.Outcome(
        cast("dict[str, int]", record["counts"]),
        frozenset(cast("list[str]", record["failed"])),
    )


def _implied(step: str) -> bool:  # a tier's fix step, whose fixes are among the guesses' own
    return step != _WHOLE and step.startswith(FIX)


def earlier(job: Job, environment: str | None = None) -> list[Record]:
    """Find the suite's tests as released in earlier runs beside this one, at the suite's tag.

    Any version's: the released tests don't run constricter. Each read by this parser
    (`corpus_suite.parser`) and, where `environment` is given, run on a checkout installed the same
    (`corpus_suite.installed`); not one stopped for running too long.

    Returns:
      Their records, the latest first, each saying whose run it is (`from`): the run that ran the
      tests, where a run took its record from another.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    name: str = part(TESTS, RELEASED)
    corpus: str = job.tree.name.replace(" ", "-")
    paths: list[Path] = sorted(
        job.store.root.parent.glob(f"*/records/{corpus}/*/{name}.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    found: list[Record] = []
    path: Path
    for path in paths:
        folder: Path = path.parents[3]  # the run's: `records/CORPUS/VERSION/` under it
        if folder.resolve() == job.store.root.resolve():
            continue
        record: Record = cast("Record", json.loads(path.read_text(encoding="utf-8")))
        keyed: bool = record.get("tag") == suite.tag and record.get(_PARSER) == corpus_suite.parser()
        if environment is not None and record.get(_ENVIRONMENT) != environment:
            continue
        if keyed and not record.get("stopped") and _COUNTS in record:
            found.append(
                {key: each for key, each in record.items() if key != CONFIRMED}
                | {FROM: record.get(FROM, folder.name)},
            )
    return found


def confirmed(job: Job, record: Record) -> bool:
    """Check whether the traced tests' outcome equals a released `record`'s, from an earlier run.

    Returns:
      Whether it does: the released tests then need no run of their own.

    """
    trace: Record | None = _read(job, TRACED)
    return trace is not None and _COUNTS in trace and not trace.get("stopped") and _ran(trace) == _ran(record)


def taken(job: Job) -> Record | None:
    """Take the suite's tests as released from the latest earlier run on the same checkout (`earlier`).

    Where the run doesn't run them (`tests-released = false`); or where it does, but the traced
    tests' outcome equals the record's (`confirmed`): the tests haven't changed.

    Returns:
      The record, saying whose it is and what confirmed it; `None` where they run.

    """
    base: Path = prepared(job, checkouts(job, part(TESTS, RELEASED))[0])
    found: list[Record]
    if not (found := earlier(job, corpus_suite.installed(base))):
        return None
    if not job.run.steps.tests_released:
        return found[0]
    return found[0] | {CONFIRMED: TRACED} if confirmed(job, found[0]) else None


def _tests_part(job: Job, name: str) -> Record:
    """Run a part of a suite's own tests on its checkout (`checkouts`): as released, or after a fix.

    None runs after tests stopped as released for running too long, nor one another fix's part
    stands for (`standing`).

    Returns:
      Its outcome, as released with how long it took and the keys a later run may take it by
      (the tag, the checkout's environment, the parser); the part that stands for it (`implied`);
      why it has none (`skipped`), or why the fix's patch wasn't applied.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    base: Path = prepared(job, checkouts(job, name)[0])
    os.environ.update(job.tree.variables or {})  # what the suite's commands need set
    step: str
    if (step := name.removeprefix(f"{TESTS}-")) == RELEASED:
        corpus_suite.reset(base, suite)
        start: float = time.perf_counter()
        kept: Path = job.store.logged(job.tree.name, job.recorded, TESTS).with_name("tests-released.txt")
        ran: corpus_suite.Outcome = corpus_suite.tested(base, suite, kept, _data(job, RELEASED))
        took: float = round(time.perf_counter() - start, 1)
        keys: Record = {_ENVIRONMENT: corpus_suite.installed(base), _PARSER: corpus_suite.parser()}
        return (
            {"tag": suite.tag, "seconds": took, "stopped": corpus_suite.stopped(ran)} | keys | _outcome(ran)
        )
    released: Record | None = _read(job, part(TESTS, RELEASED))
    if released is None or released["stopped"]:
        return {_SKIPPED: "the tests as released have no record, or ran too long"}
    if not job.store.path(job.tree.name, job.recorded, step, ".patch").exists():
        return {_SKIPPED: "the fix made no patch"}
    stood: Record | None
    if (
        step != _UNION
        and (stood := standing(job, TESTS, step, lambda ran: _COUNTS in ran and _ran(ran) == _ran(released)))
        is not None
    ):
        return stood
    fixed: corpus_suite.Outcome | str = _fixed_run(job, step, "", base)
    corpus_suite.reset(base, suite)
    return {_REFUSED: fixed} if isinstance(fixed, str) else _outcome(fixed)


def tests(job: Job) -> Record:
    """Gather the parts of a suite's own tests: as released, and after each fix the run made.

    The released tests' other runs are samples of them too (`_samples`): the traced tests', and
    the released tests' in earlier runs on the same checkout. Where a fixed run has a failure new
    or gone against them all, one fixed run with that outcome runs once more, side by side on the
    tests' checkouts, and the released tests too where no other run of theirs is there: what
    differs between the two says whose a failure is (`weighed`). A fixed run whose failures are the
    released tests' doesn't run again, whatever its other counts. Tests stopped as released for
    running too long have no fixed run.

    Returns:
      The step's record: each run's outcome, the samples, and whether the released tests vary.

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
    record |= {FROM: released_record[FROM]} if FROM in released_record else {}
    if released_record["stopped"]:
        return record | {"released": _outcome(released[0]), "fixed": {}, "stopped": True}
    samples: dict[str, corpus_suite.Outcome] = _samples(job, released_record)
    released += samples.values()
    patched: list[str]
    first: dict[str, corpus_suite.Outcome | str]
    implied: dict[str, Record]
    patched, first, implied = _gathered(job)
    runs: dict[str, corpus_suite.Outcome] = {
        step: ran for step, ran in first.items() if isinstance(ran, corpus_suite.Outcome)
    }
    named: frozenset[str] = told(suite, [*released, *runs.values()])
    again: dict[str, corpus_suite.Outcome | str]
    once: corpus_suite.Outcome | None
    again, once = _reruns(job, runs, released, named)
    if once is not None:
        released.append(once)
        record["again"] = _outcome(once)
    if again:
        named = told(suite, [*released, *runs.values(), *_both(*again.values())])
    record["varies"] = any(each != released[0] for each in released[1:])
    record["samples"] = {name: _outcome(each) for name, each in samples.items()}
    if united(job.run):
        record[UNION] = _union_run(job, released, named)
    return record | {
        "released": _outcome(released[0]),
        "fixed": _fixed((patched, first, implied), again, released, named),
    }


def _union_run(job: Job, released: Sequence[corpus_suite.Outcome], named: frozenset[str]) -> Record:
    """Lay the tests after every source's fixes at once out beside the released tests' (`weighed`).

    Returns:
      Its record: the run weighed, where it ran; else why it didn't (`skipped`, or the patch refused).

    """
    got: Record | None
    if (got := _read(job, part(TESTS, _UNION))) is None:
        return {_SKIPPED: "it failed"}
    return weighed([_ran(got)], released, named) if _COUNTS in got else got


def union(job: Job) -> Record:
    """Fix a copy with every source at once: the guesses, each checker's hints, then the trace's.

    `--fix --unsafe-fixes --infer-with` the run's checkers, in its order, and `--infer-from` the
    traced tests' trace where the run made one. A binding more than one source types gets the
    first's, as a user asking for every source gets it. The suite's tests after it
    (`tests-infer-union`) stand for each fix's where they're the released tests' (`standing`).

    Returns:
      The step's record, as `pipeline.fix` keeps a fix step's.

    """
    extra: list[str] = ["--unsafe-fixes", "--infer-with", ",".join(job.run.steps.infer)]
    trace: Record | None = _read(job, TRACED)
    if trace is not None and _COUNTS in trace:
        extra += ["--infer-from", str(prepared(job, TRACED) / corpus_suite.TRACE_FILE)]
    return fix(job, _UNION, extra)


def _reruns(
    job: Job,
    runs: dict[str, corpus_suite.Outcome],
    released: Sequence[corpus_suite.Outcome],
    named: frozenset[str],
) -> tuple[dict[str, corpus_suite.Outcome | str], corpus_suite.Outcome | None]:
    """Run one of `runs`, the fixed runs, again for each outcome with a failure new or gone.

    Against `released`, the released tests' runs; and those once more, where no other run of
    theirs is there.

    Returns:
      Each fixed run with such an outcome's second run (the one run for its outcome): its outcome,
      or why its patch wasn't applied; and the released tests', where they ran.

    """
    chosen: dict[_Key, str] = {}  # the fixed run that runs again for each outcome
    step: str
    ran: corpus_suite.Outcome
    for step, ran in runs.items():
        found: Record = weighed([ran], released, named)
        if found.get("new") or found.get("gone"):
            _ = chosen.setdefault(_key(ran), step)
    if not chosen:
        return {}, None
    more: dict[str, corpus_suite.Outcome | str] = _again(
        job,
        [*([RELEASED] if len(released) == 1 else []), *chosen.values()],
    )
    once: corpus_suite.Outcome | None = (
        cast("corpus_suite.Outcome", more.pop(RELEASED)) if RELEASED in more else None
    )
    return {step: more[chosen[_key(ran)]] for step, ran in runs.items() if _key(ran) in chosen}, once


def _fixed(
    gathered: tuple[list[str], dict[str, corpus_suite.Outcome | str], dict[str, Record]],
    again: dict[str, corpus_suite.Outcome | str],
    released: Sequence[corpus_suite.Outcome],
    named: frozenset[str],
) -> dict[str, Record]:
    """Lay each fixed run out beside the released tests' (`weighed`), as `_gathered` read the parts.

    A part another stands for is laid out as that one's, saying so.

    Returns:
      Each one's record, by its fix step, in the parts' order.

    """
    patched: list[str]
    first: dict[str, corpus_suite.Outcome | str]
    implied: dict[str, Record]
    patched, first, implied = gathered
    fixed: dict[str, Record] = {
        step: {"error": ran}
        if isinstance(ran, str)
        else weighed(_both(ran, again.get(step)), released, named)
        for step, ran in first.items()
    }
    none: list[str] = []
    same: Record = _outcome(released[0]) | {"same": True, "new": none}
    step: str
    for step in patched:
        if step in implied:
            fixed[step] = _stood(fixed, implied[step], same)
    return {step: fixed.get(step, same) for step in patched}


def _samples(job: Job, released: Record) -> dict[str, corpus_suite.Outcome]:
    """Find the released tests' other runs: traced in this run, and as released in earlier runs.

    Those on a checkout installed as this run's `released` record's was (`earlier`).

    Returns:
      Each by whose it is: `traced`, or the earlier run's folder.

    """
    found: dict[str, corpus_suite.Outcome] = {}
    trace: Record | None = _read(job, TRACED)
    if trace is not None and _COUNTS in trace and not trace.get("stopped"):
        found[TRACED] = _ran(trace)
    environment: str | None = cast("str | None", released.get(_ENVIRONMENT))
    record: Record
    for record in earlier(job, environment) if environment is not None else ():
        _ = found.setdefault(str(record[FROM]), _ran(record))
    return found


def _gathered(job: Job) -> tuple[list[str], dict[str, corpus_suite.Outcome | str], dict[str, Record]]:
    """Read the parts of a suite's tests after a fix.

    Returns:
      Each fix step that made a patch; each one's run: its outcome, or why its patch wasn't
      applied; and the record of each one another's part stands for.

    """
    patched: list[str] = []
    first: dict[str, corpus_suite.Outcome | str] = {}
    implied: dict[str, Record] = {}
    name: str
    for name in parts(job.run, TESTS)[1:]:
        got: Record = _read(job, name) or {_SKIPPED: "it failed"}
        if _SKIPPED not in got:
            patched.append(name.removeprefix(f"{TESTS}-"))
        if _REFUSED in got:
            first[patched[-1]] = str(got[_REFUSED])
        elif _COUNTS in got:
            first[patched[-1]] = _ran(got)
        elif IMPLIED in got:
            implied[patched[-1]] = got
    return patched, first, implied


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
        return corpus_suite.tested(base, suite, kept, _data(job, f"{RELEASED}-again"))

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
        if united(job.run):
            found[_UNION] = union
            found[part(TESTS, _UNION)] = partial(_tests_part, name=part(TESTS, _UNION))
        found[TESTS] = tests
    if suite is not None and suite.checks and job.run.steps.types:
        found |= {name: partial(_types_part, name=name) for name in parts(job.run, TYPES)}
        found[TYPES] = types
    return found


def needs(job: Job) -> dict[str, frozenset[str]]:
    """Say which steps each suite step waits for: those whose records or patches it reads.

    A part after a fix waits for the fix (`infer-trace`'s, for the traced tests) and for its kind's
    part as released; a tier's for the guesses', and the guesses' for the trace's, whose run may
    stand for theirs (`standing`); each of the tests' for the part after every source's fixes at
    once, which may stand for them all, and that one for its fix (`infer-union`), which waits for
    the traced tests, whose trace it reads. The tests as released wait for the traced tests where
    those may confirm an earlier run's record of them (`taken`). Each kind's step waits for its
    parts, and the traced tests for `fix-unsafe`, whose fixes they hold.

    Returns:
      Each step's, by its name: only steps the run has.

    """
    names: dict[str, Callable[[Job], Record]] = waiting(job)
    every: frozenset[str] = frozenset((*names, *fixing(job.run)))
    found: dict[str, frozenset[str]] = {TRACED: frozenset({_WHOLE})} if TRACED in names else {}
    confirmable: bool = TRACED in names and job.run.steps.tests_released and bool(earlier(job))
    joined: str = part(TESTS, _UNION) if _UNION in names else ""
    kind: str
    for kind in (TESTS, TYPES):
        if kind not in names:
            continue
        own: list[str] = parts(job.run, kind)
        found[kind] = frozenset(own) | ({joined} if kind == TESTS and joined else frozenset())
        found[own[0]] = frozenset({TRACED}) if kind == TESTS and confirmable else frozenset()
        if kind == TESTS and joined:
            found[_UNION] = frozenset({TRACED}) & every
            found[joined] = frozenset({_UNION, own[0]})
        name: str
        for name in own[1:]:
            step: str = name.removeprefix(f"{kind}-")
            stands: str = part(kind, _WHOLE) if _implied(step) else ""
            stands = part(kind, _TRACE) if step == _WHOLE and TRACED in names else stands
            made: str = TRACED if step == _TRACE else step
            found[name] = frozenset({made, own[0], stands, joined if kind == TESTS else ""}) & every
    return found
