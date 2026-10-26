"""A suite's checkouts, the fix that stands for another's run, and the suite's type checks on them.

Each checkout (`checkouts`) is the suite's own at its pinned tag (`prepared`), a fix step's patch
applied for a fixed run (`patched_checkout`). A fix's part needn't run where another's stands for it
(`standing`): the same patch, or one holding it whose run was the released tests'. The type checks'
parts (`types`) run on such checkouts too; the tests' are `suite_steps`'.
"""

import itertools
import os
import subprocess  # applies a fix's patch to a suite's checkout
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path
from typing import Final, TypeAlias, cast

from tests.corpus import corpus_suite, jsonl
from tests.corpus.pipeline import (
    FIX,
    FIX_UNSAFE,
    IMPLIED,
    INFER_UNION,
    PATCH,
    RELEASED,
    TESTS,
    TRACED,
    TYPES,
    Job,
    Record,
    part,
    parts,
    united,
)
from tests.corpus.run_config import CERTAIN, LIKELY

_Entry: TypeAlias = dict[str, object]
_Fixes: TypeAlias = frozenset[
    tuple[str, int, str, str, tuple[str, ...]]
]  # a fix step's, as `_fixes` reads them
_RUN: Final = "run"  # numbered, names the checkouts a suite's tests run on (`Suite.at_once` of them)
SKIPPED: Final = "skipped"  # in a part's record: why it has no run
REFUSED: Final = "error"  # and why a fix's patch wasn't applied
COUNTS: Final = "counts"  # and a test run's outcome's counts, where it has one
_SAME: Final = "same"  # a part's `patch`: the standing fix's is the same as its own
_WITHIN: Final = "within"  # or holds its own, and its run was the released tests'
_EVERY: Final = "union"  # or is every fix's at once, and its run was the released tests'
ENVIRONMENT: Final = "environment"  # in a released part's record: its checkout's (`corpus_suite.installed`)


def _fixes(job: Job, step: str) -> _Fixes | None:
    """Read the fixes a fix step listed, as a set: where, the name, the annotation, the imports it adds.

    Returns:
      Them; `None` where the version lists none.

    """
    if not job.store.path(job.tree.name, job.recorded, step, ".fixes.jsonl").exists():
        return None
    return frozenset(
        (each.path, each.line, each.name, each.annotation, each.imports)
        for each in itertools.chain.from_iterable(fixes_made(job, step).values())
    )


def _within(step: str, other: str, mine: _Fixes | None, theirs: _Fixes | None) -> bool:
    """Check whether the fix `other` made holds every fix `step` made, and more.

    By the fixes each listed; where the version lists none, a tier's are among the guesses' own.

    Returns:
      Whether it does.

    """
    if mine is not None and theirs is not None:
        return mine < theirs
    return implied_by(step) and other == FIX_UNSAFE


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
    if kind == TESTS and step != INFER_UNION and united(job.run):
        every: Record | None = read_record(job, part(TESTS, INFER_UNION))
        if every is not None and COUNTS in every and clean(every):
            return {IMPLIED: INFER_UNION, PATCH: _EVERY}
    mine: _Fixes | None = _fixes(job, step)
    within: list[str] = []
    seen: set[str] = set()
    name: str
    for name in parts(job.run, kind)[1:]:
        other: str = name.removeprefix(f"{kind}-")
        record: Record | None = read_record(job, name)
        if other == step or record is None or SKIPPED in record or REFUSED in record:
            continue
        target: str = str(record[IMPLIED]) if IMPLIED in record else other
        ran: Record | None = read_record(job, part(kind, target)) if target != other else record
        if target == step or target in seen or ran is None:
            continue
        seen.add(target)
        theirs: _Fixes | None = _fixes(job, target)
        if mine is not None and mine == theirs:
            return {IMPLIED: target, PATCH: _SAME}
        if _within(step, target, mine, theirs) and clean(ran):
            within.append(target)
    return {IMPLIED: within[0], PATCH: _WITHIN} if within else None


def patched_checkout(job: Job, step: str, base: Path | None = None) -> str | None:
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


def fixes_made(job: Job, step: str) -> dict[str, list[corpus_suite.Fix]]:
    """Read the fixes a fix step listed (`<step>.fixes.jsonl`), as the suite's checkout names their files.

    Returns:
      Them, per file.

    """
    suite: corpus_suite.Suite = cast("corpus_suite.Suite", job.tree.suite)
    listed: Path = job.store.path(job.tree.name, job.recorded, step, ".fixes.jsonl")
    found: dict[str, list[corpus_suite.Fix]] = {}
    each: _Entry
    for each in jsonl.read(listed):
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
    if name == part(TESTS, INFER_UNION):  # after the released tests', before every other part
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


def read_record(job: Job, name: str) -> Record | None:
    """Read one of the job's step's records.

    Returns:
      It, or `None` where the step has none.

    """
    return job.store.read(job.tree.name, job.recorded, name)


def types_part(job: Job, name: str) -> Record:
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
            ENVIRONMENT: corpus_suite.installed(base),
        }
    released: Record | None
    if (released := read_record(job, part(TYPES, RELEASED))) is None:
        return {SKIPPED: "the checks as released have no record"}
    if not job.store.path(job.tree.name, job.recorded, step, ".patch").exists():
        return {SKIPPED: "the fix made no patch"}
    stood: Record | None
    if (
        stood := standing(job, TYPES, step, lambda ran: not ran.get("new") and not ran.get("gone"))
    ) is not None:
        return stood
    refused: str | None
    if (refused := patched_checkout(job, step, base)) is not None:
        return {REFUSED: refused}
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
        (fixes_made(job, step), change),
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
    if (released := read_record(job, part(TYPES, RELEASED))) is None:
        message: str = "the checks as released have no record"
        raise RuntimeError(message)
    steps: list[str] = [name.removeprefix(f"{TYPES}-") for name in parts(job.run, TYPES)[1:]]
    got: dict[str, Record] = {}
    step: str
    for step in steps:
        read: Record | None = read_record(job, part(TYPES, step))
        if read is not None and SKIPPED not in read:
            got[step] = read
    fixed: dict[str, Record] = {step: record for step, record in got.items() if IMPLIED not in record}
    for step in steps:
        if step in got and IMPLIED in got[step]:
            fixed[step] = stood_for(fixed, got[step], {})
    return {
        "checks": [" ".join(check) for check in suite.checks],
        "released": len(cast("list[object]", released["errors"])),
        "seconds": released["seconds"],
        "fixed": {step: fixed[step] for step in steps if step in fixed},
    }


def stood_for(fixed: dict[str, Record], record: Record, default: Record) -> Record:
    """Lay an implied part out as the record of the part that stands for it, saying so.

    Returns:
      That part's record (`default` where it has none), with the step it's implied by and how.

    """
    target: str = str(record[IMPLIED])
    return fixed.get(target, default) | {IMPLIED: target, PATCH: record.get(PATCH, _WITHIN)}


def implied_by(step: str) -> bool:
    """Check whether a fix step is a tier's, whose fixes are among the guesses' own (`fix-unsafe`).

    Returns:
      Whether it is.

    """
    return step != FIX_UNSAFE and step.startswith(FIX)
