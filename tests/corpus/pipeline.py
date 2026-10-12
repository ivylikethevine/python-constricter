# SPDX-License-Identifier: MIT
"""A run's steps, and the records they write: the only data any of its outputs is made from.

Each step measures one corpus with one version, through `launch.run`, and writes one JSON record
under the run's folder: `records/<corpus>/<version>/<step>.json`. A step whose record is there isn't
run again, so a stopped run resumes.

- `check`: the files, the offences per code at `suffocate`, each level's errors and warnings, and
  the fixes offered, by tier;
- `fix-certain`, `fix-likely`, `fix-unsafe`: `--fix` with that tier's options on a copy: what it
  fixed (by tier and by mechanisms, where the version lists its fixes), the files it broke, what a
  second pass would still fix, the bindings typed after, and the copy's diff, kept as a patch;
- `coverage`: the bindings typed as released.

Every count of typed bindings is this checkout's `--coverage`, whatever the version.
"""

import difflib
import json
import re
import shutil
import sys
import time
from collections import Counter
from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import Level
from constricter.cli import paths
from tests.corpus import corpus_table, launch
from tests.corpus.catalog import Tree
from tests.corpus.run_config import CERTAIN, DEV, FIXES, LIKELY, Run

Record: TypeAlias = "dict[str, object]"
_Entry: TypeAlias = "dict[str, object]"
_Listed: TypeAlias = "list[_Entry] | _Entry | None"  # what `--format=json` may print
CHECK: Final = "check"
COVERAGE: Final = "coverage"
FIX: Final = "fix-"
GUESS: Final = "guess"
_SUFFOCATE: Final = "--level=suffocate"
_ERROR: Final = "error"  # an offence's severity, in `--format=json`
_TYPED: Final = re.compile(r"^Total: (\d+)/(\d+) typed", re.MULTILINE)  # `--coverage`'s summary
_AT_ONCE: Final = 4  # a corpus's steps running side by side


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

    def log(self, corpus: str, version: str, step: str, errors: str) -> None:
        """Keep what a step's constricter wrote to standard error, if anything."""
        if errors.strip():
            path: Path = self.root / "logs" / corpus.replace(" ", "-") / version / f"{step}.log"
            path.parent.mkdir(parents=True, exist_ok=True)
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
        entries = _entries(ran.output) or []  # the last level's are `suffocate`'s: every code
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


def fix(job: Job, mode: str) -> Record:
    """Fix a copy of the corpus with `mode`'s options, then ask a second pass what it would still fix.

    Returns:
      The step's record; its `fixed` is `None` where the fix crashed or the version hasn't the options.

    """
    step: str = f"{FIX}{mode}"
    where: launch.Place
    valid: list[Path]
    where, valid = launch.copied(job.tree, job.work(step))
    options: list[str] = [*FIXES[mode], _SUFFOCATE]
    record: Record = {"options": ["--fix", *FIXES[mode]], "fixed": None}
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
        made: list[_Entry] = [
            cast("_Entry", e["fix"]) for e in entries or [] if e.get("fixed") and e.get("fix")
        ]
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


def coverage(job: Job) -> Record:
    """Count the corpus's bindings typed as released.

    Returns:
      The step's record.

    """
    return {"typed": _typed(job, launch.place(job.tree, job.work(COVERAGE)))}


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
        found[f"{FIX}{mode}"] = partial(fix, mode=mode)
    if run.steps.coverage:
        found[COVERAGE] = coverage
    return found


def measure(job: Job) -> None:
    """Run each of the run's steps on the job that has no record yet, side by side, and keep each one's."""
    start: float = time.perf_counter()
    path: Path = job.store.path(job.tree.name, job.recorded, CHECK)
    path.parent.mkdir(parents=True, exist_ok=True)
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(_AT_ONCE) as pool:
        running: dict[str, Future[Record]] = {
            name: pool.submit(step, job)
            for name, step in steps(job.run).items()
            if job.store.read(job.tree.name, job.recorded, name) is None
        }
    name: str
    done: Future[Record]
    for name, done in running.items():
        job.store.write(job.tree.name, job.recorded, name, done.result())
    seconds: float = time.perf_counter() - start
    _ = sys.stderr.write(f"{job.recorded} on {job.tree.name}: {len(running)} steps in {seconds:.1f}s\n")
