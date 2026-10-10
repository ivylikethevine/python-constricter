# SPDX-License-Identifier: MIT
"""The steps `tests/corpus/super_corpora.py` runs on a corpus, each in its own process, and what they give.

- `table`: the check at every level, `--fix`, `--fix --likely` and `--fix --unsafe-fixes` on copies,
  and the typed share after each (`corpus_table.measure`);
- `census`: every untyped binding, and why those with no fix have none (`corpus_untyped.census`);
- `infer-CHECKER`, for each type checker installed: `--fix --unsafe-fixes --infer-with CHECKER` on
  a copy, from this checkout's root, whose settings point the checker at its environment;
- `tests` and `types`, for a package with a suite (`corpus_suite.Suite`): its own tests and type
  checks as released and after `--fix --unsafe-fixes`, each new error traced to its fix and that
  fix's tier, and after the runs under it where that one doesn't say whose fixes a difference is;
- `traced`, where the run asks for it and the suite's tests can be traced
  (`corpus_suite.traceable`): their trace, taken by a witness told every fix of
  `--fix --unsafe-fixes`, which holds each fixed binding's value to its annotation as the tests run
  (`corpus_guesses`); then `--fix --unsafe-fixes --infer-from` the trace, and the package's type
  checks after, or its tests where it has no checks;
- `check`: one check at `suffocate`, in the step's own process, timed, with each fix's mechanisms,
  the main process's share of it, and what the second round (the files whose callers type their
  parameters) costs, read from a second, profiled check.

`CORPUS_JOBS` and `CORPUS_SUITE_WORKERS` size constricter's and a suite's processes; with
`CORPUS_TYPES_APART` set, a suite's type checks run on checkouts of their own, one for each fixed
run, at once and beside its tests; with `CORPUS_ASSURE` set, they run after `--fix` alone too,
whatever the first run found.
"""

import cProfile
import json
import os
import pstats
import resource
import shutil
import subprocess  # runs this checkout's constricter
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.cli import command as cli
from constricter.cli import paths
from tests.corpus import corpus_guesses, corpus_suite, corpus_table, corpus_untyped
from tests.corpus.corpus_table import DEV, Corpus, Measured, Typed

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"
# What `pstats` keeps of a function (its file, first line and name), and of its calls: the last
# two are its own time and its whole time.
_Function: TypeAlias = tuple[str, int, str]
_Timing: TypeAlias = tuple[int, int, float, float, object]

_ROOT: Final = Path(__file__).resolve().parents[2]
_CHECKERS: Final = ("basedpyright", "ty", "pyrefly")
TABLE: Final = "table"
CENSUS: Final = "census"
CHECK: Final = "check"
TESTS: Final = "tests"
TYPES: Final = "types"
TRACED: Final = "traced"
SUITED: Final = frozenset({TESTS, TYPES, TRACED})  # the steps of a package's suite
INFER: Final = "infer-"
JOBS_VARIABLE: Final = "CORPUS_JOBS"
WORKERS_VARIABLE: Final = "CORPUS_SUITE_WORKERS"
APART_VARIABLE: Final = "CORPUS_TYPES_APART"  # set: a suite's type checks get checkouts of their own
ASSURE_VARIABLE: Final = "CORPUS_ASSURE"  # set: a suite's type checks run after `--fix` alone too
# What a new type error is traced to: a certain fix, a likely guess, another guess, or nothing.
CERTAIN: Final = "certain"
LIKELY: Final = "likely"
GUESS: Final = "guess"
UNTRACED: Final = "untraced"
TIERS: Final = (CERTAIN, LIKELY, GUESS, UNTRACED)
_SECOND_ROUND: Final = "_called_again"  # `cli.command`'s function that checks files again
_WHOLE: Final = "_check_all"  # and the one that checks them all, that round included
NONE: Final = corpus_table.NONE


class Sizes(NamedTuple):
    """How the machine sizes a run: its CPUs and memory, and each constricter's and suite's processes."""

    cpus: int
    memory: int | None  # bytes; `None` where the system doesn't say
    jobs: int
    workers: int


class Census(NamedTuple):
    """A corpus's untyped bindings: how many, how `--fix` leaves them, and the unfixed ones' shapes."""

    untyped: int
    guessed: int  # with a fix that's only a guess
    unfixed: int  # with no fix at all
    unparsed: int  # in files that don't parse, left out of the rest
    shapes: Counter[str]  # the unfixed ones' values' shapes


class Checked(NamedTuple):
    """One timed check of a corpus at `suffocate`, with the CPUs the run gives it."""

    files: int
    seconds: float
    main: float  # the main process's CPU seconds
    workers: float  # the worker processes'
    whole: float  # a profiled check's time, and its second round's (see `_SECOND_ROUND`)
    second: float
    certain: Counter[str]  # the fixes resting on each mechanism: a fix on several counts for each
    guesses: Counter[str]


class Inferred(NamedTuple):
    """What `--fix --unsafe-fixes --infer-with` a checker did to a copy of a corpus."""

    fixed: int | None  # `None`: it crashed
    broken: int
    typed: Typed


# A fixed run of a suite's tests: its label, the fix's size, its outcome and its seconds.
_Run: TypeAlias = tuple[str, str, corpus_suite.Outcome, float]
_Fixes: TypeAlias = Mapping[str, Sequence[corpus_suite.Fix]]  # a run's fixes, per file


class Tested(NamedTuple):
    """A package's own tests: as released, then after each fix (its label, size, outcome and seconds)."""

    tag: str
    released: corpus_suite.Outcome
    seconds: float
    fixed: list[_Run]
    fixes: _Fixes  # every fix the first fixed run made, per file: each with its tier
    again: bool = False  # whether `released` is a second run's, a fixed run having differed from the first
    varies: bool = False  # whether the released tests' failures differ from run to run


class Typechecked(NamedTuple):
    """A package's own type checks: as released, then after each fix (its label and comparison)."""

    checks: str
    released: int
    fixed: list[tuple[str, corpus_suite.Compared]]
    versions: str = ""  # each checker's own, as it says it (see `_versions`)


class Traced(NamedTuple):
    """A package's tests' trace, and what `--fix --unsafe-fixes --infer-from` it did to its source.

    `compared`: its type checks after, beside the released source's; `tested`, for a package with
    no checks: its tests' outcome as released and after.
    """

    summary: str  # the traced tests'
    resting: int  # the fixes that rest on the trace
    change: str  # the fix's size, as `git diff --shortstat` puts it
    seen: corpus_guesses.Seen  # the types each binding held as the traced tests ran
    verdicts: corpus_guesses.Verdicts  # how each fixed binding's values stood to its fix's annotation
    compared: corpus_suite.Compared | None = None
    tested: tuple[corpus_suite.Outcome, corpus_suite.Outcome] | None = None


class Unset(NamedTuple):
    """A suite that couldn't be set up here: why (the clone's or an install command's failure)."""

    reason: str


Value: TypeAlias = Measured | Census | Checked | Inferred | Tested | Typechecked | Traced | Unset
_Modes: TypeAlias = list[tuple[str, tuple[str, ...]]]  # each fixed run's label, and its options


class Step(NamedTuple):
    """One step's result as it's kept: what it gave (`None`: it failed), and what it took.

    Its seconds, the CPU seconds of its processes, and the most memory they held (bytes): one of
    them, or all of them at once where the run samples its tree (`corpora_cpu`).
    """

    seconds: float
    value: Value | None
    cpu: float = 0.0
    memory: int = 0


Steps: TypeAlias = dict[str, Step]  # a corpus's steps' results, by their names


def tier(blamed: corpus_suite.Blamed) -> str:
    """Name what a new error is traced to.

    Returns:
      One of `TIERS`.

    """
    return UNTRACED if blamed.fix is None else fix_tier(blamed.fix)


def fix_tier(fix: corpus_suite.Fix) -> str:
    """Name a fix's tier.

    Returns:
      `CERTAIN`, `LIKELY` or `GUESS`.

    """
    if not fix.unsafe:
        return CERTAIN
    return LIKELY if fix.likely else GUESS


def lower(
    found: corpus_suite.Compared,
    check: Callable[[tuple[str, tuple[str, ...]]], corpus_suite.Compared],
    *,
    assure: bool,
) -> list[tuple[str, corpus_suite.Compared]]:
    """Type-check the runs under `corpus_suite.ALL` that its comparison `found` calls for.

    A trace is by line, not by cause, and an untraced error is no tier's. So after `--fix --likely`
    where a new error is untraced, or traced to a certain or a likely fix; then after `--fix` where
    that run has one untraced or traced to a certain fix, or `assure` asks for it whatever was
    found. `check` fixes with a run's options and compares.

    Returns:
      Each run made: its label and comparison.

    """
    likely: tuple[str, tuple[str, ...]]
    certain: tuple[str, tuple[str, ...]]
    likely, certain = corpus_suite.LOWER
    runs: list[tuple[str, corpus_suite.Compared]] = []
    doubted: bool = False
    if {tier(each) for each in found.new} - {GUESS}:
        below: corpus_suite.Compared = check(likely)
        runs.append((likely[0], below))
        doubted = bool({tier(each) for each in below.new} & {CERTAIN, UNTRACED})
    if assure or doubted:
        runs.append((certain[0], check(certain)))
    return runs


def assured(kept: Step | None) -> bool:
    """Check whether a kept `types` step has the `--fix` run `ASSURE_VARIABLE` asks for.

    Returns:
      Whether it has.

    """
    return (
        kept is not None
        and isinstance(kept.value, Typechecked)
        and corpus_suite.LOWER[1][0] in dict(kept.value.fixed)
    )


def checkers() -> list[str]:
    """Find the type checkers `--infer-with` can start here: on `PATH`, or beside this Python.

    Returns:
      Their names, in `_CHECKERS`' order.

    """
    beside: str = str(Path(sys.executable).parent)
    path: str = os.pathsep.join((beside, os.environ.get("PATH", os.defpath)))
    return [name for name in _CHECKERS if shutil.which(name, path=path) is not None]


def _constricter(args: Sequence[str]) -> str:
    """Run this checkout's constricter from its root, where its own settings point the checkers at its venv.

    Returns:
      Its standard output.

    """
    beside: str = str(Path(sys.executable).parent)
    done: subprocess.CompletedProcess[str] = subprocess.run(
        [sys.executable, "-I", "-W", "ignore", "-m", "constricter", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        cwd=_ROOT,
        env={**os.environ, "PATH": os.pathsep.join((beside, os.environ.get("PATH", os.defpath)))},
    )
    _ = sys.stderr.write(done.stderr)  # a crash's traceback, into the step's log
    return done.stdout


def table_step(corpus: Corpus) -> Measured:
    """Check and fix the corpus as `corpus_table.py` does.

    Returns:
      What it gave.

    """
    return corpus_table.measure(corpus, DEV)


def census_step(corpus: Corpus) -> Census:
    """Take the census of the corpus's untyped bindings.

    Returns:
      Its counts.

    """
    corpus_table.WORK.mkdir(parents=True, exist_ok=True)
    bindings: list[corpus_untyped.Binding]
    unparsed: int
    bindings, unparsed = corpus_untyped.census(corpus)
    return Census(
        len(bindings),
        sum(b.fixed and b.unsafe for b in bindings),
        sum(not b.fixed for b in bindings),
        unparsed,
        Counter(b.shape for b in bindings if not b.fixed),
    )


def infer_step(corpus: Corpus, checker: str) -> Inferred:
    """Fix a copy of the corpus with the checker's hints too.

    Returns:
      What that did.

    """
    found: corpus_table.Fixed = corpus_table.fixed_copy(
        corpus,
        f"{INFER}{checker}",
        ("--unsafe-fixes", f"--infer-with={checker}"),
        _constricter,
        second=False,
    )
    return Inferred(found.fixed, found.broken, found.typed or Typed(0, 0))


def tests_step(corpus: Corpus, suite: corpus_suite.Suite) -> Tested:
    """Run the corpus package's own tests as released, and after `--fix --unsafe-fixes`.

    Each run's output is kept in `corpus_suite.WORK`'s `outputs/`. Where the fixed run's outcome
    differs from the released one's, the released tests are run again, and that run stands for
    them: a first run after a clone has differed from every later one, fixed or not. A fixed run
    that still differs is fixed and run again too, and its second outcome stands: a test that fails
    one run in some isn't the fix's (see `_settled`). One that differs even so is followed by the
    runs under it (`corpus_suite.LOWER`), down to the first that's the same as released.

    Returns:
      Their outcomes.

    """
    root: Path = corpus_suite.checkout(corpus.name, suite)
    kept: Path = corpus_suite.WORK / "outputs" / root.name
    corpus_suite.reset(root, suite)
    start: float = time.perf_counter()
    released: corpus_suite.Outcome = corpus_suite.tested(root, suite, kept / "released.txt")
    seconds: float = time.perf_counter() - start
    fixed: list[_Run] = []
    fixes: _Fixes = {}
    label: str
    # One stopped as released (waiting on a server no one started) would be after each fix too.
    for label in () if corpus_suite.stopped(released) else [mode[0] for mode in corpus_suite.MODES]:
        ran: _Run
        ran, fixes = _fixed_run((root, kept), suite, label)
        fixed.append(ran)
    corpus_suite.reset(root, suite)
    if all(outcome == released for _, _, outcome, _ in fixed):
        return Tested(suite.tag, released, seconds, fixed, fixes)
    varies: bool
    released, varies = _settled((root, kept), suite, released, fixed)
    if fixed[0][2] != released:
        fixed += _lowered((root, kept), suite, released)
    return Tested(suite.tag, released, seconds, fixed, fixes, again=True, varies=varies)


def _fixed_run(
    where: tuple[Path, Path],
    suite: corpus_suite.Suite,
    label: str,
    kept: str = "",
) -> tuple[_Run, _Fixes]:
    """Fix the checkout's source as the run of `label` does (see `corpus_suite.OPTIONS`), and run its tests.

    `where`: the checkout and where its outputs are kept, this run's under its label and `kept`.

    Returns:
      The run, and the fixes it made.

    """
    fixes: _Fixes
    change: str
    fixes, change = corpus_suite.fixed_and_listed(where[0], suite, *corpus_suite.OPTIONS[label])
    start: float = time.perf_counter()
    outcome: corpus_suite.Outcome = corpus_suite.tested(
        where[0],
        suite,
        where[1] / f"{label.replace(' ', '')}{kept}.txt",
    )
    return (label, change, outcome, time.perf_counter() - start), fixes


def _lowered(
    where: tuple[Path, Path],
    suite: corpus_suite.Suite,
    released: corpus_suite.Outcome,
) -> list[_Run]:
    """Run the tests after each fix under `corpus_suite.ALL`'s, down to the first the same as `released`.

    `where`: the checkout and where its outputs are kept.

    Returns:
      Each run made.

    """
    runs: list[_Run] = []
    label: str
    for label in (mode[0] for mode in corpus_suite.LOWER):
        runs.append(_fixed_run(where, suite, label)[0])
        corpus_suite.reset(where[0], suite)
        if runs[-1][2] == released:
            break
    return runs


def _settled(
    where: tuple[Path, Path],
    suite: corpus_suite.Suite,
    first: corpus_suite.Outcome,
    fixed: list[_Run],
) -> tuple[corpus_suite.Outcome, bool]:
    """Run again what differed, to tell a fix's failures from a suite's own that come and go.

    `where`: the checkout and where its outputs are kept. The released tests, then each fixed run
    of `fixed` that differs from them, replaced by its second outcome. If one still differs, the
    released tests a third time: where their own failures differ among the three runs, a fixed run
    that fails nothing both times but what they failed is taken for the released one.

    Returns:
      The released tests' second outcome, and whether their failures vary.

    """
    root: Path = where[0]
    released: corpus_suite.Outcome = corpus_suite.tested(root, suite, where[1] / "released-again.txt")
    both: dict[str, frozenset[str]] = {}  # what each fixed run failed both times
    at: int
    label: str
    outcome: corpus_suite.Outcome
    for at, (label, _, outcome, _) in enumerate(fixed):
        if outcome != released:
            fixed[at] = _fixed_run(where, suite, label, "-again")[0]
            second: corpus_suite.Outcome = fixed[at][2]
            both[label] = outcome.failed & second.failed
            corpus_suite.reset(root, suite)
    if all(outcome == released for _, _, outcome, _ in fixed):
        return released, False
    seen: list[frozenset[str]] = [
        first.failed,
        released.failed,
        corpus_suite.tested(root, suite, where[1] / "released-third.txt").failed,
    ]
    if len(set(seen)) == 1:
        return released, False
    ever: frozenset[str] = seen[0].union(*seen)
    fixed[:] = [
        (label, change, released if both.get(label, outcome.failed) <= ever else outcome, took)
        for label, change, outcome, took in fixed
    ]
    return released, True


def types_step(corpus: Corpus, suite: corpus_suite.Suite) -> Typechecked:
    """Run the corpus package's own type checks as released, and after every fix (the checkers' hints' too).

    Then after the runs under that one its errors call for (see `lower`), on its checkout.

    Returns:
      Their errors, each new one traced to its fix.

    """
    modes: _Modes = list(corpus_suite.MODES)
    hinting: str
    if hinting := ",".join(checkers()):
        modes.append((f"--infer-with {hinting}", ("--unsafe-fixes", "--infer-with", hinting)))
    # With `APART_VARIABLE` set, a checkout for the released source and each fixed run, all
    # type-checked at once; else the tests' own, one run after another.
    apart: bool = bool(os.environ.get(APART_VARIABLE))
    roots: list[Path] = [
        corpus_suite.checkout(corpus.name, suite, f"types{at}" if apart else "") for at in range(len(modes))
    ]
    first: Path = corpus_suite.checkout(corpus.name, suite, "types-released") if apart else roots[0]
    root: Path
    for root in dict.fromkeys((first, *roots)):
        corpus_suite.reset(root, suite)
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(len(modes) + 1 if apart else 1) as pool:
        released: Future[list[corpus_suite.Complaint]] = pool.submit(corpus_suite.complaints, first, suite)
        comparing: list[Future[corpus_suite.Compared]] = [
            pool.submit(
                corpus_suite.compared,
                each,
                suite,
                released.result,
                options,
            )
            for each, (_, options) in zip(roots, modes, strict=True)
        ]
    under: list[tuple[str, corpus_suite.Compared]] = lower(
        comparing[0].result(),
        lambda mode: corpus_suite.compared(roots[0], suite, released.result, mode[1]),
        assure=bool(os.environ.get(ASSURE_VARIABLE)),
    )
    for root in dict.fromkeys(roots):
        corpus_suite.reset(root, suite)
    found: list[tuple[str, corpus_suite.Compared]] = [
        (label, each.result()) for (label, _), each in zip(modes, comparing, strict=True)
    ]
    return Typechecked(
        "; ".join(" ".join(check) for check in suite.checks),
        len(released.result()),
        [found[0], *under, *found[1:]],
        _versions(roots[0], suite),
    )


def _versions(root: Path, suite: corpus_suite.Suite) -> str:
    """Ask each of the suite's type checkers its version, in the checkout's environment.

    Returns:
      What each says (`mypy 1.18.2 (compiled: yes)`), `; ` between them; `?` for one that doesn't.

    """
    said: list[str] = []
    check: tuple[str, ...]
    for check in suite.checks:
        module: bool = tuple(check[:2]) == ("python", "-m")
        command: list[str] = [
            str(root / ".venv" / "bin" / check[0]),
            *check[1 : 3 if module else 1],
            "--version",
        ]
        done: subprocess.CompletedProcess[str] = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            cwd=root,
        )
        said.append((done.stdout.strip() or "?").splitlines()[0])
    return "; ".join(dict.fromkeys(said))


def traced_step(corpus: Corpus, suite: corpus_suite.Suite) -> Traced:
    """Trace the corpus package's tests, fix its source with their trace, and check what that did.

    The tests are traced by the witness (`corpus_guesses.WITNESS`), told the fixes of
    `--fix --unsafe-fixes`: its verdict on each binding it saw bound is kept.

    By its own type checks, beside the released source's errors; by its tests, where it has none.

    Returns:
      The trace's summary, the fixes resting on it, and the checks' or the tests' outcome.

    Raises:
      RuntimeError: nothing runs the suite's tests traced.

    """
    root: Path = corpus_suite.checkout(corpus.name, suite)
    os.environ[corpus_suite.TRACER_VARIABLE] = corpus_guesses.TRACER
    os.environ[corpus_guesses.WITNESS_VARIABLE] = corpus_guesses.expected(
        root,
        corpus_suite.fixed_and_listed(root, suite, *corpus_suite.ALL[1])[0],
    )
    summary: str | None
    if (summary := corpus_suite.traced(root, suite)) is None:
        message: str = f"nothing runs {corpus.name}'s tests traced"
        raise RuntimeError(message)
    judged: corpus_guesses.Verdicts = corpus_guesses.verdicts(root)
    options: tuple[str, ...] = corpus_suite.TRACE_MODE[1]
    seen: corpus_guesses.Seen = corpus_guesses.seen(root, corpus_suite.TRACE_FILE)
    if suite.checks:
        released: list[corpus_suite.Complaint] = corpus_suite.complaints(root, suite)
        found: corpus_suite.Compared = corpus_suite.compared(root, suite, lambda: released, options)
        corpus_suite.reset(root, suite)
        return Traced(summary, corpus_suite.resting(found.fixes), found.change, seen, judged, found)
    kept: Path = corpus_suite.WORK / "outputs" / root.name
    before: corpus_suite.Outcome = corpus_suite.tested(root, suite, kept / "traced-released.txt")
    fixes: dict[str, list[corpus_suite.Fix]]
    change: str
    fixes, change = corpus_suite.fixed_and_listed(root, suite, *options)
    after: corpus_suite.Outcome = corpus_suite.tested(root, suite, kept / "traced-fixed.txt")
    corpus_suite.reset(root, suite)
    return Traced(summary, corpus_suite.resting(fixes), change, seen, judged, None, (before, after))


def cpu(who: int) -> float:
    """Read the CPU seconds this process (`RUSAGE_SELF`) or its finished children have used.

    Returns:
      Them.

    """
    used: resource.struct_rusage = resource.getrusage(who)
    return used.ru_utime + used.ru_stime


def _whole(profile: cProfile.Profile, name: str) -> float:
    """Read a profile for the whole time of `cli.command`'s function `name`.

    Returns:
      Its seconds, what it calls included; 0 if it wasn't called.

    """
    # `stats` is `pstats.Stats`' own attribute, which its stubs leave out.
    timings: dict[_Function, _Timing] = cast(
        "dict[_Function, _Timing]",
        vars(pstats.Stats(profile))["stats"],
    )
    module: str = str(Path(cli.__file__).resolve())
    return sum(
        timing[3]
        for function, timing in timings.items()
        if function[2] == name and str(Path(function[0]).resolve()) == module
    )


class _Timed(NamedTuple):
    """One check here: its seconds, the main process's and the workers' CPU seconds, its results."""

    seconds: float
    main: float
    workers: float
    results: list[dict[str, _Json]]


def _timed(args: Sequence[str], out: Path) -> _Timed:
    """Check with `args`, which write the results to `out`, in this process.

    Returns:
      Its timings and results.

    """
    before: tuple[float, float] = (cpu(resource.RUSAGE_SELF), cpu(resource.RUSAGE_CHILDREN))
    start: float = time.perf_counter()
    _ = cli.main(args)
    seconds: float = time.perf_counter() - start
    return _Timed(
        seconds,
        cpu(resource.RUSAGE_SELF) - before[0],
        cpu(resource.RUSAGE_CHILDREN) - before[1],
        cast("list[dict[str, _Json]]", json.loads(out.read_text(encoding="utf-8") or "[]")),
    )


def _kinds(results: Sequence[dict[str, _Json]], *, unsafe: bool) -> Counter[str]:
    """Count the fixes resting on each mechanism: the certain ones, or (`unsafe`) the guesses.

    Returns:
      Each mechanism's count; a fix resting on several counts for each.

    """
    found: Counter[str] = Counter()
    result: dict[str, _Json]
    for result in results:
        fix: dict[str, _Json] | None
        if (fix := cast("dict[str, _Json] | None", result.get("fix"))) and fix["unsafe"] is unsafe:
            found.update(cast("list[str]", fix["kinds"]) or [NONE])
    return found


def check_step(corpus: Corpus) -> Checked:
    """Check the corpus at `suffocate` twice, in this process: timed, then with the main process profiled.

    Returns:
      The first check's time, each process's share of it and its fixes' mechanisms, and the
      second's rounds.

    """
    files: int = sum(1 for _ in paths.python_files([corpus.root]))
    profile: cProfile.Profile = cProfile.Profile()
    scratch: str
    with tempfile.TemporaryDirectory() as scratch:
        out: Path = Path(scratch) / "results.json"
        output: list[str] = ["--format=json", "--exit-zero", "--output-file", str(out)]
        args: list[str] = [*output, *corpus_table.EVERYWHERE, str(corpus.root)]
        timed: _Timed = _timed(args, out)
        profile.enable()
        try:
            _ = cli.main(args)
        finally:
            profile.disable()
    return Checked(
        files,
        timed.seconds,
        timed.main,
        timed.workers,
        _whole(profile, _WHOLE),
        _whole(profile, _SECOND_ROUND),
        _kinds(timed.results, unsafe=False),
        _kinds(timed.results, unsafe=True),
    )


def _suited(
    name: str,
    corpus: Corpus,
    suite: corpus_suite.Suite | None,
) -> Tested | Typechecked | Traced | Unset:
    """Run a suite's step: one of `SUITED`.

    Returns:
      What it gave, or why the suite couldn't be set up.

    Raises:
      ValueError: the corpus has no suite.

    """
    if suite is None:
        message: str = f"{corpus.name} has no suite"
        raise ValueError(message)
    steps: dict[str, Callable[[Corpus, corpus_suite.Suite], Tested | Typechecked | Traced]] = {
        TESTS: tests_step,
        TYPES: types_step,
        TRACED: traced_step,
    }
    try:
        return steps[name](corpus, suite)
    except (RuntimeError, OSError) as failure:  # `corpus_suite.checkout`'s: no clone, or no install
        return Unset(str(failure).strip().rsplit("\n", 1)[-1])


def _given(name: str, corpus: Corpus, suite: corpus_suite.Suite | None) -> Value:
    """Run step `name`.

    Returns:
      What it gave.

    """
    if name.startswith(INFER):
        return infer_step(corpus, name.removeprefix(INFER))
    if name in SUITED:
        return _suited(name, corpus, suite)
    alone: dict[str, Callable[[Corpus], Value]] = {TABLE: table_step, CENSUS: census_step, CHECK: check_step}
    return alone[name](corpus)


def run(name: str, corpus: Corpus, suite: corpus_suite.Suite | None) -> Step:
    """Run step `name` on `corpus` (whose suite is `suite`), in this process.

    Returns:
      Its result, with what it took.

    """
    start: float = time.perf_counter()
    value: Value = _given(name, corpus, suite)
    largest: int = max(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    )
    return Step(
        time.perf_counter() - start,
        value,
        cpu(resource.RUSAGE_SELF) + cpu(resource.RUSAGE_CHILDREN),
        largest * 1024,  # Linux counts it in kilobytes
    )
