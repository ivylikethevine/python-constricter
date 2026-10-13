# SPDX-License-Identifier: MIT
"""A run's steps, and the records they write: the only data any of its outputs is made from.

Each step measures one corpus with one version, through `launch.run`, and writes one JSON record
under the run's folder: `records/<corpus>/<version>/<step>.json`. A step whose record is there isn't
run again, so a stopped run resumes. The run starts each in a process of its own (`python -m
tests.corpus --step`), and adds what its processes used to its record (`sizing.USED`).

- `check`: the files, the offences per code at `suffocate`, each level's errors and warnings, and
  the fixes offered, by tier;
- `fix-certain`, `fix-likely`, `fix-unsafe`: `--fix` with that tier's options on a copy: what it
  fixed (by tier and by mechanisms, where the version lists its fixes), the files it broke, what a
  second pass would still fix, the bindings typed after, and the copy's diff, kept as a patch;
- `infer-CHECKER`: the same with `--unsafe-fixes --infer-with CHECKER`, a type checker's hints;
- `census`: every untyped binding a check at `suffocate` reports, classified
  (`corpus_untyped.census`): those with no fix, and their values' shapes;
- `coverage`: the bindings typed as released;
- `timing`: a check at `suffocate`, timed in one process and with the run's `jobs`, several times;
- `profile`: the same check in one process `py-spy` samples: where constricter's own time goes.

`suite_steps` has the steps that run a corpus package's own suite, after these.

A fix step keeps each fix it made (`<step>.fixes.jsonl`), and the census each binding
(`census.rows.jsonl`), a line each, beside its record.

Every count of typed bindings is this checkout's `--coverage`, whatever the version.
"""

import difflib
import json
import os
import re
import shutil
import statistics
import subprocess  # runs a check under `py-spy`
import sys
import time
import traceback
from collections import Counter
from collections.abc import Callable, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import Level
from constricter.cli import paths
from tests.corpus import corpus_profile, corpus_table, corpus_untyped, launch
from tests.corpus.run_config import CERTAIN, DEV, FIXES, LIKELY, Run
from tests.corpus.trees import Tree

Record: TypeAlias = dict[str, object]
_Entry: TypeAlias = dict[str, object]
_Listed: TypeAlias = list[_Entry] | _Entry | None  # what `--format=json` may print
CHECK: Final = "check"
COVERAGE: Final = "coverage"
FIX: Final = "fix-"
INFER: Final = "infer-"
CENSUS: Final = "census"
TIMING: Final = "timing"
PROFILE: Final = "profile"
_PY_SPY: Final = "py-spy"
_RATE: Final = 100  # samples a second
_TOP: Final = 25  # the functions a profile's report and record list
TESTS: Final = "tests"
TYPES: Final = "types"
TRACED: Final = "traced"
TRACE: Final = "trace"  # after `INFER`: the fix step by a suite's tests' trace
GUESS: Final = "guess"
_SUFFOCATE: Final = "--level=suffocate"
_NAME: Final = re.compile(r"'([^']+)'")  # the name an offence's message quotes
_ERROR: Final = "error"  # an offence's severity, in `--format=json`
_TYPED: Final = re.compile(r"^Total: (\d+)/(\d+) typed", re.MULTILINE)  # `--coverage`'s summary


class Store(NamedTuple):
    """A run's folder: its records, its logs, and the copies its fixes work on."""

    root: Path

    def path(self, corpus: str, version: str, step: str, suffix: str = ".json") -> Path:
        """Find where a step's record is kept.

        Returns:
          The path.

        """
        return self.root / "records" / corpus.replace(" ", "-") / version / f"{step}{suffix}"

    def read(self, corpus: str, version: str, step: str) -> Record | None:
        """Read a step's record.

        Returns:
          It, or `None` if the step hasn't run.

        """
        path: Path = self.path(corpus, version, step)
        return cast("Record", json.loads(path.read_text(encoding="utf-8"))) if path.exists() else None

    def write(self, corpus: str, version: str, step: str, record: Record) -> None:
        """Keep a step's record."""
        path: Path = self.path(corpus, version, step)
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def logged(self, corpus: str, version: str, step: str) -> Path:
        """Find where what a step says is kept, making its directory.

        Returns:
          The path.

        """
        path: Path = self.root / "logs" / corpus.replace(" ", "-") / version / f"{step}.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def log(self, corpus: str, version: str, step: str, errors: str) -> None:
        """Keep what a step's constricter wrote to standard error, if anything."""
        if errors.strip():
            path: Path = self.logged(corpus, version, step)
            file: IO[str]
            with path.open("a", encoding="utf-8") as file:
                _ = file.write(errors)


class Job(NamedTuple):
    """One corpus measured with one version, in one run."""

    run: Run
    store: Store
    tree: Tree
    version: str

    @property
    def recorded(self) -> str:
        """The version as the run records it."""
        return self.run.recorded(self.version)

    def work(self, step: str) -> Path:
        """Find the directory a step works in: a copy it fixes, or a place with no settings.

        Returns:
          The path.

        """
        return self.store.root / "work" / self.tree.name.replace(" ", "-") / self.recorded / step


def tier(offered: _Entry) -> str:
    """Name a fix's tier, from `--format=json`'s `fix` object.

    Returns:
      `certain`, `likely` (a guess `--likely` applies) or `guess`.

    """
    return CERTAIN if not offered.get("unsafe") else LIKELY if offered.get("likely") else GUESS


def _entries(output: str) -> list[_Entry] | None:
    """Read `--format=json`'s output.

    Returns:
      Its entries, or `None` if it isn't a list: the run crashed.

    """
    try:
        listed: _Listed = cast("_Listed", json.loads(output or "[]"))
    except ValueError:
        return None
    return listed if isinstance(listed, list) else None


def _typed(job: Job, where: launch.Place) -> list[int] | None:
    """Count the bindings at `where` that are typed, with this checkout's `--coverage`.

    Returns:
      The typed ones and all of them, or `None` if it printed no summary.

    """
    ran: launch.Ran = launch.run(DEV, where, ["--coverage"], job.run.jobs)
    found: re.Match[str] | None = _TYPED.search(ran.output)
    return [int(found[1]), int(found[2])] if found else None


def check(job: Job) -> Record:
    """Check the corpus at every level, the levels at once.

    Returns:
      The step's record.

    Raises:
      RuntimeError: a check printed no report: it crashed.

    """
    where: launch.Place = launch.place(job.tree, job.work(CHECK))

    def at(level: Level) -> launch.Ran:
        return launch.run(
            job.version,
            where,
            ["--format=json", f"--level={level.name.lower()}"],
            job.run.jobs,
        )

    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(len(Level)) as pool:
        runs: list[launch.Ran] = list(pool.map(at, Level))
    levels: dict[str, list[int]] = {}
    entries: list[_Entry] = []
    level: Level
    ran: launch.Ran
    for level, ran in zip(Level, runs, strict=True):
        job.store.log(job.tree.name, job.recorded, CHECK, ran.errors)
        listed: list[_Entry] | None
        if (listed := _entries(ran.output)) is None:
            message: str = f"the check at {level.name.lower()} crashed ({ran.status}): {ran.errors[-2000:]}"
            raise RuntimeError(message)
        entries = listed  # the last level's are `suffocate`'s: every code
        errors: int = sum(entry["severity"] == _ERROR for entry in entries)
        levels[level.name.lower()] = [errors, len(entries) - errors]
    fixes: list[_Entry] = [cast("_Entry", entry["fix"]) for entry in entries if entry.get("fix")]
    return {
        "files": sum(1 for _ in paths.python_files([job.tree.root])),
        "codes": dict(Counter(str(entry["code"]) for entry in entries)),
        "levels": levels,
        "offered": dict(Counter(tier(each) for each in fixes)),
        "seconds": round(max(ran.seconds for ran in runs), 1),
    }


def _patch(tree: Tree, where: launch.Place) -> str:
    """Compare a fixed copy with the tree it's a copy of.

    Returns:
      Their unified diff, each file named by its path under the tree.

    """
    lines: list[str] = []
    copy: Path
    for copy in sorted(paths.python_files([where.target])):
        name: str = copy.relative_to(where.target).as_posix()
        before: bytes = (tree.root / name).read_bytes()
        after: bytes = copy.read_bytes()
        if before != after:
            lines.extend(
                difflib.unified_diff(
                    before.decode("utf-8", "surrogateescape").splitlines(keepends=True),
                    after.decode("utf-8", "surrogateescape").splitlines(keepends=True),
                    f"a/{name}",
                    f"b/{name}",
                ),
            )
    return "".join(lines)


def _listed(job: Job, step: str, where: launch.Place, entries: list[_Entry]) -> list[_Entry]:
    """Keep each fix a run made, a line each, beside the step's record (`<step>.fixes.jsonl`).

    Returns:
      The fixes, as `--format=json` gives each one's `fix`.

    """
    made: list[_Entry] = []
    lines: list[str] = []
    entry: _Entry
    for entry in entries:
        offered: _Entry | None = cast("_Entry | None", entry.get("fix"))
        if offered and entry.get("fixed"):
            named: re.Match[str] | None = _NAME.search(str(entry["message"]))
            made.append(offered)
            lines.append(
                json.dumps(
                    {
                        "path": (where.cwd / str(entry["path"])).relative_to(where.target).as_posix(),
                        "line": entry["line"],
                        "name": named[1] if named else "",
                        "annotation": offered["annotation"],
                        "tier": tier(offered),
                        "kinds": offered["kinds"],
                        "imports": offered.get("imports", []),
                    },
                ),
            )
    _ = job.store.path(job.tree.name, job.recorded, step, ".fixes.jsonl").write_text(
        "".join(f"{line}\n" for line in lines),
        encoding="utf-8",
    )
    return made


def fix(job: Job, step: str, extra: Sequence[str]) -> Record:
    """Fix a copy of the corpus with `--fix` and `extra`, then ask a second pass what it would still fix.

    Returns:
      The step's record; its `fixed` is `None` where the fix crashed or the version hasn't the options.

    """
    where: launch.Place
    valid: list[Path]
    where, valid = launch.copied(job.tree, job.work(step))
    options: list[str] = [*extra, _SUFFOCATE]
    record: Record = {"options": ["--fix", *extra], "fixed": None}
    fixed: int | None
    ran: launch.Ran
    if launch.lists_fixes(job.version):
        ran = launch.run(
            job.version,
            where,
            ["--fix", "--show-fixes", "--format=json", *options],
            job.run.jobs,
        )
        entries: list[_Entry] | None = _entries(ran.output)
        made: list[_Entry] = _listed(job, step, where, entries or [])
        fixed = None if entries is None else len(made)
        record["tiers"] = dict(Counter(tier(each) for each in made))
        record["mechanisms"] = dict(Counter("+".join(cast("list[str]", each["kinds"])) for each in made))
    else:
        ran = launch.run(job.version, where, ["--fix", *options], job.run.jobs)
        fixed = corpus_table.fixed_count(ran.output)
    job.store.log(job.tree.name, job.recorded, step, ran.errors)
    record["seconds"] = round(ran.seconds, 1)
    if fixed is not None:
        second: launch.Ran = launch.run(job.version, where, ["--diff", *options], job.run.jobs)
        record |= {
            "fixed": fixed,
            "broken": sum(not corpus_table.compiles(path) for path in valid),
            "left": second.output.count("\n+"),
            "typed": _typed(job, where),
        }
        _ = job.store.path(job.tree.name, job.recorded, step, ".patch").write_text(
            _patch(job.tree, where),
            encoding="utf-8",
            errors="surrogateescape",
        )
    shutil.rmtree(where.cwd, ignore_errors=True)
    return record


def census(job: Job) -> Record:
    """Classify every untyped binding a check at `suffocate` reports, and why those with no fix have none.

    Each binding is kept, a line each, beside the record (`census.rows.jsonl`).

    Returns:
      The step's record: the untyped bindings, those whose fix is a guess, those with none (and
      their values' shapes), and those in files that don't parse, left out of the rest.

    """
    where: launch.Place = launch.place(job.tree, job.work(CENSUS))
    ran: launch.Ran = launch.run(job.version, where, ["--format=json", _SUFFOCATE], job.run.jobs)
    job.store.log(job.tree.name, job.recorded, CENSUS, ran.errors)
    entries: list[_Entry] = _entries(ran.output) or []
    entry: _Entry
    for entry in entries:
        entry["path"] = os.path.normpath(where.cwd / str(entry["path"]))  # as the tree's root is: no `..`
    bindings: list[corpus_untyped.Binding]
    unparsed: int
    bindings, unparsed = corpus_untyped.census(
        corpus_table.Corpus(job.tree.name, job.tree.version, job.tree.root),
        json.dumps(entries),
    )
    _ = job.store.path(job.tree.name, job.recorded, CENSUS, ".rows.jsonl").write_text(
        "".join(f"{json.dumps(binding._asdict())}\n" for binding in bindings),
        encoding="utf-8",
    )
    return {
        "untyped": len(bindings),
        "guessed": sum(binding.fixed and binding.unsafe for binding in bindings),
        "unfixed": sum(not binding.fixed for binding in bindings),
        "unparsed": unparsed,
        "shapes": dict(Counter(binding.shape for binding in bindings if not binding.fixed).most_common()),
        "seconds": round(ran.seconds, 1),
    }


def coverage(job: Job) -> Record:
    """Count the corpus's bindings typed as released.

    Returns:
      The step's record.

    """
    return {"typed": _typed(job, launch.place(job.tree, job.work(COVERAGE)))}


def fixing(run: Run) -> list[str]:
    """List the run's steps that fix a copy.

    Returns:
      Their names: each tier's, then each type checker's, then the trace's (which a `traced` step
      makes, for a suite whose tests can be traced).

    """
    tiers: list[str] = [f"{FIX}{mode}" for mode in run.steps.fix]
    hinted: list[str] = [f"{INFER}{checker}" for checker in run.steps.infer]
    return [*tiers, *hinted, *([f"{INFER}{TRACE}"] if run.steps.traced else [])]


def timing(job: Job) -> Record:
    """Time a check of the corpus at `suffocate`, in one process and with the run's `jobs`, several times.

    Returns:
      The step's record: each way's seconds, a run each, and their medians.

    """
    where: launch.Place = launch.place(job.tree, job.work(TIMING))
    options: list[str] = [_SUFFOCATE, "--exit-zero", "-q", "--output-file", os.devnull]
    one: list[float] = []
    every: list[float] = []
    for _ in range(job.run.steps.timing):  # the two ways in turn: what else the machine does falls on both
        one.append(round(launch.run(job.version, where, options, 1).seconds, 2))
        every.append(round(launch.run(job.version, where, options, job.run.jobs).seconds, 2))
    return {
        "jobs": job.run.jobs,
        "one": one,
        "every": every,
        "median one": round(statistics.median(one), 2),
        "median every": round(statistics.median(every), 2),
    }


def profile(job: Job) -> Record:
    """Check the corpus at `suffocate` in one process that `py-spy` samples from outside.

    The samples are kept beside the record (`profile.txt`: a line a stack, `flamegraph.pl`'s input
    and speedscope's), with `corpus_profile`'s report of them (`profile.md`).

    Returns:
      The step's record: the check's seconds, sampled, and constricter's slowest functions by
      their own time.

    Raises:
      RuntimeError: `py-spy` isn't installed, or wrote no samples.

    """
    where: launch.Place = launch.place(job.tree, job.work(PROFILE))
    spy: str | None
    if (spy := shutil.which(_PY_SPY, path=launch.environment(where)["PATH"])) is None:
        missing: str = f"{_PY_SPY} isn't installed: uv sync --group dev --group corpus"
        raise RuntimeError(missing)
    samples: Path = job.store.path(job.tree.name, job.recorded, PROFILE, ".txt")
    samples.unlink(missing_ok=True)
    recording: list[str] = [spy, "record", "--format", "raw", "--function", "--full-filenames"]
    recording += ["--subprocesses", "--rate", str(_RATE), "--output", str(samples), "--"]
    checking: list[str] = [_SUFFOCATE, "--exit-zero", "-q", "--output-file", os.devnull]
    start: float = time.perf_counter()
    done: subprocess.CompletedProcess[str] = subprocess.run(
        [*recording, *launch.command(job.version, where, checking, 1)],
        capture_output=True,
        text=True,
        check=False,
        cwd=where.cwd,
        env=launch.environment(where),
    )
    seconds: float = time.perf_counter() - start
    if not samples.exists():  # it exits non-zero for a worker it lost track of, with the samples written
        failed: str = f"{_PY_SPY} wrote no samples ({done.returncode}): {done.stderr[-2000:]}"
        raise RuntimeError(failed)
    found: list[corpus_profile.Row] = corpus_profile.rows(samples)
    _ = job.store.path(job.tree.name, job.recorded, PROFILE, ".md").write_text(
        corpus_profile.report(job.tree.name, seconds, found, _TOP),
        encoding="utf-8",
    )
    ours: list[corpus_profile.Row] = sorted((row for row in found if row.ours), key=lambda row: -row.own)
    return {
        "seconds": round(seconds, 1),
        "slowest": [[row.where, round(row.own, 2), round(row.whole, 2)] for row in ours[:_TOP]],
    }


def steps(run: Run) -> dict[str, Callable[[Job], Record]]:
    """List the steps `run` asks for.

    Returns:
      Each by its name.

    """
    found: dict[str, Callable[[Job], Record]] = {}
    if run.steps.check:
        found[CHECK] = check
    mode: str
    for mode in run.steps.fix:
        found[f"{FIX}{mode}"] = partial(fix, step=f"{FIX}{mode}", extra=FIXES[mode])
    checker: str
    for checker in run.steps.infer:
        found[f"{INFER}{checker}"] = partial(
            fix,
            step=f"{INFER}{checker}",
            extra=("--unsafe-fixes", f"--infer-with={checker}"),
        )
    if run.steps.census:
        found[CENSUS] = census
    if run.steps.coverage:
        found[COVERAGE] = coverage
    if run.steps.timing:
        found[TIMING] = timing
    if run.steps.profile:
        found[PROFILE] = profile
    return found


def settled(job: Job, name: str, done: Future[Record]) -> bool:
    """Keep a finished step's record; or, where it raised, its traceback in the step's log.

    Returns:
      Whether it has a record: a step that failed has none, and a resumed run makes it again.

    """
    failure: BaseException | None
    if (failure := done.exception()) is None:
        job.store.write(job.tree.name, job.recorded, name, done.result())
    else:
        job.store.log(job.tree.name, job.recorded, name, "".join(traceback.format_exception(failure)))
        _ = sys.stderr.write(f"{job.recorded} on {job.tree.name}: {name} failed: {failure!r}\n")
    return failure is None
