# SPDX-License-Identifier: MIT
"""The steps `tests/corpus/super_corpora.py` runs on a corpus, each in its own process, and what they give.

- `table`: the check at every level, `--fix` and `--fix --unsafe-fixes` on copies, and the typed
  share after each (`corpus_table.measure`);
- `census`: every untyped binding, and why those with no fix have none (`corpus_untyped.census`);
- `infer-CHECKER`, for each type checker installed: `--fix --unsafe-fixes --infer-with CHECKER` on
  a copy, from this checkout's root, whose settings point the checker at its environment;
- `tests` and `types`, for a package with a suite (`corpus_suite.Suite`): its own tests and type
  checks as released and after each fix, each new error traced to its fix;
- `check`: one check at `suffocate`, in the step's own process, timed, with each fix's mechanisms,
  the main process's share of it, and what the second round (the files whose callers type their
  parameters) costs, read from a second, profiled check.

`CORPUS_JOBS` and `CORPUS_SUITE_WORKERS` size constricter's and a suite's processes; with
`CORPUS_TYPES_APART` set, a suite's type checks run on checkouts of their own, one for each fixed
run, at once and beside its tests.
"""

import cProfile
import json
import os
import pstats
import re
import resource
import shutil
import subprocess  # runs this checkout's constricter
import sys
import tempfile
import time
from collections import Counter
from collections.abc import Callable, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.cli import command as cli
from constricter.cli import paths
from tests.corpus import corpus_suite, corpus_table, corpus_untyped
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
INFER: Final = "infer-"
JOBS_VARIABLE: Final = "CORPUS_JOBS"
WORKERS_VARIABLE: Final = "CORPUS_SUITE_WORKERS"
APART_VARIABLE: Final = "CORPUS_TYPES_APART"  # set: a suite's type checks get checkouts of their own
_EVERYWHERE: Final = ("--level=suffocate", "--all-scopes")
_FIXED: Final = re.compile(r"fixed (\d+)")
_TYPED: Final = re.compile(r"^Total: (\d+)/(\d+) typed", re.MULTILINE)  # `--coverage`'s summary
_SECOND_ROUND: Final = "_called_again"  # `cli.command`'s function that checks files again
_WHOLE: Final = "_check_all"  # and the one that checks them all, that round included
NONE: Final = "-"


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
    """One timed check of a corpus at `suffocate`, with every CPU."""

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


class Tested(NamedTuple):
    """A package's own tests: as released, then after each fix (its label, size, outcome and seconds)."""

    tag: str
    released: corpus_suite.Outcome
    seconds: float
    fixed: list[tuple[str, str, corpus_suite.Outcome, float]]
    again: bool = False  # whether `released` is a second run's, a fixed run having differed from the first


class Typechecked(NamedTuple):
    """A package's own type checks: as released, then after each fix (its label and comparison)."""

    checks: str
    released: int
    fixed: list[tuple[str, corpus_suite.Compared]]


class Unset(NamedTuple):
    """A suite that couldn't be set up here: why (the clone's or an install command's failure)."""

    reason: str


Value: TypeAlias = Measured | Census | Checked | Inferred | Tested | Typechecked | Unset
_Modes: TypeAlias = list[tuple[str, tuple[str, ...]]]  # each fixed run's label, and its options


class Step(NamedTuple):
    """One step's result as it's kept: what it gave (`None`: it failed), and what it took.

    Its seconds, the CPU seconds of its processes, and the most memory one of them held (bytes).
    """

    seconds: float
    value: Value | None
    cpu: float = 0.0
    memory: int = 0


Steps: TypeAlias = dict[str, Step]  # a corpus's steps' results, by their names


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
    root: Path
    valid: list[Path]
    root, valid = corpus_table.copied(corpus, f"{INFER}{checker}")
    jobs: str = f"--jobs={os.environ.get(JOBS_VARIABLE, '0')}"
    fixing: list[str] = ["--fix", "--unsafe-fixes", f"--infer-with={checker}", *_EVERYWHERE, jobs, str(root)]
    fixed: re.Match[str] | None = _FIXED.search(_constricter(fixing).strip().rsplit("\n", 1)[-1])
    typed: re.Match[str] | None = _TYPED.search(_constricter(["--coverage", "--all-scopes", jobs, str(root)]))
    return Inferred(
        None if fixed is None else int(fixed[1]),
        sum(not corpus_table.compiles(path) for path in valid),
        Typed(int(typed[1]), int(typed[2])) if typed else Typed(0, 0),
    )


def tests_step(corpus: Corpus, suite: corpus_suite.Suite) -> Tested:
    """Run the corpus package's own tests as released, and after each fix.

    Each run's output is kept in `corpus_suite.WORK`'s `outputs/`. Where a fixed run's outcome
    differs from the released one's, the released tests are run again, and that run stands for
    them: a first run after a clone has differed from every later one, fixed or not. A fixed run
    that still differs is fixed and run again too, and its second outcome stands: a test that fails
    one run in some isn't the fix's.

    Returns:
      Their outcomes.

    """
    root: Path = corpus_suite.checkout(corpus.name, suite)
    kept: Path = corpus_suite.WORK / "outputs" / root.name
    corpus_suite.reset(root, suite)
    start: float = time.perf_counter()
    released: corpus_suite.Outcome = corpus_suite.tested(root, suite, kept / "released.txt")
    seconds: float = time.perf_counter() - start
    fixed: list[tuple[str, str, corpus_suite.Outcome, float]] = []
    label: str
    options: tuple[str, ...]
    # One stopped as released (waiting on a server no one started) would be after each fix too.
    for label, options in () if corpus_suite.stopped(released) else corpus_suite.MODES:
        change: str = corpus_suite.fixed(root, suite, *options)
        start = time.perf_counter()
        outcome: corpus_suite.Outcome = corpus_suite.tested(
            root,
            suite,
            kept / f"{label.replace(' ', '')}.txt",
        )
        fixed.append((label, change, outcome, time.perf_counter() - start))
    corpus_suite.reset(root, suite)
    again: bool
    if again := any(outcome != released for _, _, outcome, _ in fixed):
        released = corpus_suite.tested(root, suite, kept / "released-again.txt")
    at: int
    for at, (label, _, outcome, _) in enumerate(fixed):
        if outcome != released:
            change = corpus_suite.fixed(root, suite, *dict(corpus_suite.MODES)[label])
            start = time.perf_counter()
            second: corpus_suite.Outcome = corpus_suite.tested(
                root,
                suite,
                kept / f"{label.replace(' ', '')}-again.txt",
            )
            fixed[at] = (label, change, second, time.perf_counter() - start)
            corpus_suite.reset(root, suite)
    return Tested(suite.tag, released, seconds, fixed, again)


def types_step(corpus: Corpus, suite: corpus_suite.Suite) -> Typechecked:
    """Run the corpus package's own type checks as released, and after each fix (the checkers' hints' too).

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
                first if apart else None,
            )
            for each, (_, options) in zip(roots, modes, strict=True)
        ]
    for root in dict.fromkeys(roots):
        corpus_suite.reset(root, suite)
    return Typechecked(
        "; ".join(" ".join(check) for check in suite.checks),
        len(released.result()),
        [(label, found.result()) for (label, _), found in zip(modes, comparing, strict=True)],
    )


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
        jobs: str = f"--jobs={os.environ.get(JOBS_VARIABLE, '0')}"
        output: list[str] = ["--format=json", "--exit-zero", "--output-file", str(out)]
        args: list[str] = [*output, *_EVERYWHERE, jobs, str(corpus.root)]
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


def _suited(name: str, corpus: Corpus, suite: corpus_suite.Suite | None) -> Tested | Typechecked | Unset:
    """Run a suite's step, `TESTS` or `TYPES`.

    Returns:
      What it gave, or why the suite couldn't be set up.

    Raises:
      ValueError: the corpus has no suite.

    """
    if suite is None:
        message: str = f"{corpus.name} has no suite"
        raise ValueError(message)
    try:
        return tests_step(corpus, suite) if name == TESTS else types_step(corpus, suite)
    except (RuntimeError, OSError) as failure:  # `corpus_suite.checkout`'s: no clone, or no install
        return Unset(str(failure).strip().rsplit("\n", 1)[-1])


def _given(name: str, corpus: Corpus, suite: corpus_suite.Suite | None) -> Value:
    """Run step `name`.

    Returns:
      What it gave.

    """
    if name.startswith(INFER):
        return infer_step(corpus, name.removeprefix(INFER))
    if name in {TESTS, TYPES}:
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
