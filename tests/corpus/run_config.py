"""A run file: what `python -m tests.corpus RUN.toml` measures, with what, and how it's written.

    [run]
    label = "0.3.7-rc.1"             # names the run's folder, and `dev` in its tables
    output = "corpus-runs"           # each execution writes a folder of its own under it
    versions = ["0.3.1", "dev"]      # releases from PyPI, and `dev`: this checkout; or `NAME=PATH`,
                                     # the constricter the Python at PATH runs (another checkout's)
    formats = ["json", "markdown", "csv"]
    jobs = 0                         # constricter's worker processes: 0 is every CPU
    at-once = 1                      # the corpora found side by side: cloned, installed
    suite-seconds = 1800             # how long a suite's tests may run before they're stopped
    suite-workers = 0                # the most processes a suite's tests take: 0, as many as fit
    cpus = 0                         # the CPUs the steps share: 0 is the machine's (see `sizing`)
    memory = 0                       # and the gigabytes: 0 is most of what's free as the run starts
    share = 0                        # or the percent of the machine's CPUs and memory they share, and
                                     # are held to where systemd starts them (`--share`): 0, as above
    options = ["--vague", "0"]       # given to every constricter command of the run: a run at a setting

    [corpora]
    include = ["original"]           # corpora or sets of `corpora.toml`, or directories
    install = true                   # false: a suite's corpus is cloned alone, with no environment

    [steps]
    check = true                     # offences per code, and errors and warnings at each level
    fix = ["certain", "likely", "unsafe"]   # each on a copy: fixed, broken, a second pass, typed after
    coverage = true                  # the bindings typed as released
    infer-with = ["basedpyright"]    # `--fix --unsafe-fixes --infer-with` each, on a copy
    census = true                    # every untyped binding, classified: what has no fix, and why
    tests = true                     # a suite's own tests, as released and after each fix
    types = true                     # its own type checks, each new error traced to its fix
    traced = true                    # its tests traced: each fix held to what they bind; a fix by the trace

    timing = 3                       # a check timed that many times, in one process and with `jobs`
    timing-beside = false            # true: the timed checks run beside the other steps, not alone at the
                                     # end: their instructions compare across runs, their seconds don't
    profile = true                   # a check in one process `py-spy` samples
    tests-hinted = true              # false: no test run after a checker's hints or the trace's fix
    tests-released = true            # false: the tests as released not run, their record the latest
                                     # earlier run's at the suite's tag on the same checkout; true:
                                     # run, unless the traced tests confirm it (`suite_steps.taken`)
    tests-union = true               # false: no test run after every fix at once (`infer-union`),
                                     # which stands for each fix's where it's the released tests'
    every-level = false              # true: a check at each level, not one the levels are read from

    [publish]
    runs-md = "docs/RUNS.md"         # and a section a version there, of the per-version tables
    replace = false                  # over a section that's already there
    section = "Super corpora"        # or one section of that heading: every table of the run's last version

    [stages]                         # what `--stage NAME` runs: its steps, by name or `fnmatch` pattern
    fixes = ["check", "fix-*", "infer-*", "census", "coverage"]   # with none, `stages.BUILT_IN`'s
    suites = ["traced", "infer-union", "tests", "tests-*", "types", "types-*"]
    timed = ["timing", "profile"]

A key this doesn't know is an error, not ignored: a misspelt step would otherwise measure nothing.
"""

import argparse
import contextlib
import getpass
import json
import os
import tomllib
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import __version__
from tests.corpus.stages import BUILT_IN, Stages

DEV: Final = "dev"
CHECKOUT: Final = __version__.partition("+")[0]  # this checkout's version, without its commit: `0.5.1.dev3`
NAMED: Final = "="  # in a version: after its name, the Python that runs it
JSON: Final = "json"
MARKDOWN: Final = "markdown"
CSV: Final = "csv"
FORMATS: Final = (JSON, MARKDOWN, CSV)
CERTAIN: Final = "certain"
LIKELY: Final = "likely"
UNSAFE: Final = "unsafe"
# Each fix a run can make on a copy, and the options that make it beside `--fix`.
FIXES: Final = {CERTAIN: (), LIKELY: ("--likely",), UNSAFE: ("--unsafe-fixes",)}
CHECKERS: Final = ("basedpyright", "ty", "pyrefly")  # what `--infer-with` can start
WHOLE: Final = 100  # a share's percent of the whole machine
_KEYS: Final = {
    "run": {
        "label",
        "output",
        "versions",
        "formats",
        "jobs",
        "at-once",
        "suite-seconds",
        "suite-workers",
        "cpus",
        "memory",
        "share",
        "options",
    },
    "corpora": {"include", "install"},
    "publish": {"runs-md", "replace", "section"},
    "steps": {
        "check",
        "fix",
        "infer-with",
        "census",
        "coverage",
        "tests",
        "types",
        "traced",
        "timing",
        "timing-beside",
        "profile",
        "tests-hinted",
        "every-level",
        "tests-released",
        "tests-union",
    },
}
_RUNS_MD: Final = "runs-md"
_STAGES: Final = "stages"  # the table regrouping the steps
_STAMP: Final = "%m-%d-%Y-%H%M"  # a run's folder: its label, then the month, day, year and time it started
ROOT: Final = Path(__file__).resolve().parents[2]  # the checkout
FACTS: Final = "facts.toml"  # in a run's folder: the run as it was read, the commit, the machine
STARTED: Final = "started"  # in its facts: when its first execution started
REPORT: Final = "report.json"  # in a run's folder once it ends: its facts, records and tables
_Table: TypeAlias = dict[str, object]


class Steps(NamedTuple):
    """What a run measures on each corpus with each version."""

    check: bool = True
    fix: tuple[str, ...] = (CERTAIN, LIKELY, UNSAFE)
    coverage: bool = True
    infer: tuple[str, ...] = ()  # the type checkers whose hints `--infer-with` takes, each on a copy
    census: bool = True
    tests: bool = False  # a suite's own tests take minutes: asked for
    types: bool = False  # and its own type checks
    traced: bool = False  # and its tests once more, traced (it needs `fix`'s `unsafe`)
    timing: int = 0  # how many times a check is timed, each way: 0 is not at all
    profile: bool = False
    timing_beside: bool = (
        False  # the timed steps beside the others, not alone at the end (see `sizing.TIMED`)
    )
    tests_hinted: bool = True  # a suite's tests after each checker's hints and the trace's fix too
    every_level: bool = False  # a check at each level, not one at `suffocate` the others are read from
    tests_released: bool = True  # the tests as released run, unless the traced tests confirm an earlier run's
    tests_union: bool = True  # the tests once after every fix at once, standing for each fix's where released


class Publish(NamedTuple):
    """Where a run's tables go beside its folder."""

    runs_md: Path | None = None  # docs/RUNS.md: a section a version, of the tables `corpus_table` lays out
    replace: bool = False  # over a section that's there
    section: str = ""  # its heading, for one section of the whole run in place of a version's


class Run(NamedTuple):
    """A run file, read."""

    label: str = CHECKOUT
    output: Path = Path("corpus-runs")
    versions: tuple[str, ...] = (DEV,)
    formats: tuple[str, ...] = FORMATS
    jobs: int = 0
    include: tuple[str, ...] = ("original",)
    steps: Steps = Steps()
    at_once: int = 1  # the corpora found side by side: their steps wait for the machine alone
    publish: Publish = Publish()
    install: bool = True  # a suite's corpus installed with its tests' dependencies, not cloned alone
    suite_seconds: int = 1800  # how long a suite's tests may run before they're stopped
    suite_workers: int = 0  # the most processes a suite's tests take: 0, as many as fit (`sizing`)
    cpus: int = 0  # the CPUs the steps share: 0 is the machine's
    memory: float = 0.0  # the gigabytes they share: 0 is most of what's free as the run starts
    share: int = 0  # the percent of the machine's CPUs and memory they share, held to it: 0, as above
    minus: tuple[str, ...] = ()  # corpora or sets left out of `include`'s (`--minus`)
    options: tuple[str, ...] = ()  # given to every constricter command of the run (`launch.configure`)
    stages: Stages = BUILT_IN  # what `--stage` runs of it (see `stages`)

    def folder(self, now: datetime) -> Path:
        """Name the folder an execution started at `now` writes.

        Returns:
          It: `<output>/<label>-<month>-<day>-<year>-<hour><minute>`.

        """
        return self.output / f"{self.label}-{now.strftime(_STAMP)}"

    def recorded(self, version: str) -> str:
        """Name a version as the run's tables do: a release as itself, `dev` as `<label>+dev`.

        And one written `NAME=PATH`, another Python's constricter, as `NAME`.

        Returns:
          The name.

        """
        return f"{self.label}+{DEV}" if version == DEV else version.partition(NAMED)[0]


def _among(given: object, known: tuple[str, ...], what: str) -> tuple[str, ...]:
    """Check each of `given`, a list of names, is one of `known`.

    Returns:
      Them.

    Raises:
      ValueError: one isn't.

    """
    names: tuple[str, ...] = tuple(cast("list[str]", given))
    name: str
    for name in names:
        if name not in known:
            message: str = f"{what} {name!r} is none of {', '.join(known)}"
            raise ValueError(message)
    return names


def parse(data: _Table) -> Run:
    """Read a run file's tables.

    Returns:
      The run; what a table leaves out has `Run`'s default.

    Raises:
      ValueError: a table or a key this doesn't know, or a format or a fix that isn't one.

    """
    section: str
    for section in data:
        if section == _STAGES:  # its keys are the stages' own names
            continue
        unknown: set[str] = set(cast("_Table", data[section])) - _KEYS.get(section, set())
        if section not in _KEYS or unknown:
            message: str = f"unknown in the run file: [{section}] {', '.join(sorted(unknown))}".rstrip()
            raise ValueError(message)
    run: _Table = cast("_Table", data.get("run", {}))
    steps: _Table = cast("_Table", data.get("steps", {}))
    publish: _Table = cast("_Table", data.get("publish", {}))
    default: Run = Run()
    return Run(
        str(run.get("label", default.label)),
        Path(str(run.get("output", default.output))),
        tuple(cast("list[str]", run.get("versions", default.versions))),
        _among(run.get("formats", default.formats), FORMATS, "format"),
        cast("int", run.get("jobs", default.jobs)),
        tuple(cast("list[str]", cast("_Table", data.get("corpora", {})).get("include", default.include))),
        Steps(
            bool(steps.get("check", default.steps.check)),
            _among(steps.get("fix", default.steps.fix), tuple(FIXES), "fix"),
            bool(steps.get("coverage", default.steps.coverage)),
            _among(steps.get("infer-with", default.steps.infer), CHECKERS, "checker"),
            bool(steps.get("census", default.steps.census)),
            bool(steps.get("tests", default.steps.tests)),
            bool(steps.get("types", default.steps.types)),
            bool(steps.get("traced", default.steps.traced)),
            cast("int", steps.get("timing", default.steps.timing)),
            bool(steps.get("profile", default.steps.profile)),
            bool(steps.get("timing-beside", default.steps.timing_beside)),
            bool(steps.get("tests-hinted", default.steps.tests_hinted)),
            bool(steps.get("every-level", default.steps.every_level)),
            bool(steps.get("tests-released", default.steps.tests_released)),
            bool(steps.get("tests-union", default.steps.tests_union)),
        ),
        cast("int", run.get("at-once", default.at_once)),
        Publish(
            Path(str(publish[_RUNS_MD])) if _RUNS_MD in publish else None,
            bool(publish.get("replace")),
            str(publish.get("section", "")),
        ),
        bool(cast("_Table", data.get("corpora", {})).get("install", default.install)),
        cast("int", run.get("suite-seconds", default.suite_seconds)),
        cast("int", run.get("suite-workers", default.suite_workers)),
        cast("int", run.get("cpus", default.cpus)),
        float(cast("float", run.get("memory", default.memory))),
        percent(run.get("share", default.share)),
        options=tuple(cast("list[str]", run.get("options", default.options))),
        stages=_staged(cast("_Table", data.get(_STAGES, {}))),
    )


def _staged(table: _Table) -> Stages:
    """Read a run file's `[stages]`: each stage's steps, by name or pattern.

    Returns:
      Them, in the file's order; `stages.BUILT_IN` where it has none. A stage that isn't a list of
      step names raises `ValueError` (`_patterns`).

    """
    if not table:
        return BUILT_IN
    return tuple((name, _patterns(name, given)) for name, given in table.items())


def _patterns(name: str, given: object) -> tuple[str, ...]:
    """Read stage `name`'s steps, by name or pattern.

    Returns:
      Them.

    Raises:
      ValueError: They aren't a list of step names.

    """
    if not isinstance(given, list) or not all(isinstance(each, str) for each in cast("list[object]", given)):
        message: str = f"the stage {name!r} isn't a list of step names"
        raise ValueError(message)
    return tuple(cast("list[str]", given))


def directory(corpus: str) -> str:
    """Name a corpus's folder in a run's records, logs and work: its name, a space a dash.

    Returns:
      It.

    """
    return corpus.replace(" ", "-")


def percent(given: object) -> int:
    """Read a share of the machine, in percent.

    Returns:
      It: 1 to 100, or 0 for none given.

    Raises:
      ValueError: it isn't a whole number from 0 to 100.

    """
    if isinstance(given, bool) or not isinstance(given, int) or not 0 <= given <= WHOLE:
        message: str = f"share must be a percent, 1 to {WHOLE} (0: the machine's): {given!r}"
        raise ValueError(message)
    return given


def scrubbed(text: str) -> str:
    """Write a kept file's paths as no machine's: the checkout's relative to it, the home folder's as `~`.

    A run's folder is committed: what it keeps names nothing of the machine that ran it, nor its
    user, whom pytest's temporary folders are named for (`pytest-of-<user>`, in a test's id).

    Returns:
      `text`, so written: as JSON writes a path, which is as it is but on Windows.

    """
    where: Path
    written: str
    for where, written in ((ROOT, ""), (Path.home(), "~/")):
        text = text.replace(json.dumps(f"{where}{os.sep}")[1:-1], written)
    with contextlib.suppress(OSError, KeyError):  # no user to name: nothing named for one
        text = text.replace(f"pytest-of-{getpass.getuser()}", "pytest-of-user")
    return text


def started(folder: Path) -> datetime:
    """Read when the run in `folder` first started, from its facts: its `facts.toml`, or its report's.

    What orders runs, as a file's time can't: a checkout sets every file's at once. A folder with
    no facts saying goes by its own time.

    Returns:
      It, in its zone.

    """
    with contextlib.suppress(ValueError):  # neither says, or not as a time
        when: datetime = datetime.fromisoformat(_said(folder))
        return when if when.tzinfo else when.astimezone()
    return datetime.fromtimestamp(folder.stat().st_mtime, UTC)


def _said(folder: Path) -> str:
    """Read the `started` of the facts of the run in `folder`: its `facts.toml`'s, or else its report's.

    Returns:
      It; nothing where neither says.

    """
    with contextlib.suppress(OSError, ValueError, KeyError, TypeError):
        facts: _Table = tomllib.loads((folder / FACTS).read_text(encoding="utf-8"))
        return str(facts[STARTED])
    with contextlib.suppress(OSError, ValueError, KeyError, TypeError):
        report: _Table = cast("_Table", json.loads((folder / REPORT).read_text(encoding="utf-8")))
        return str(cast("_Table", report["run"])[STARTED])
    return ""


def outside(output: Path, root: Path) -> list[str]:
    """Name what git sees of the checkout at `root` but the runs' folders under `output`.

    Returns:
      A pathspec of every path but `output`'s, as git's arguments; nothing where it isn't a folder
      under `root`, the checkout itself included.

    """
    where: Path = output.resolve()
    inside: bool = where.is_relative_to(root) and where != root
    return ["--", ".", f":(exclude){where.relative_to(root).as_posix()}"] if inside else []


def read(path: Path) -> Run:
    """Read the run file at `path`.

    Returns:
      The run.

    """
    file: IO[bytes]
    with path.open("rb") as file:
        return parse(tomllib.load(file))


RESUME: Final = "--resume"  # then a run's folder: this execution carries it on
STAGE: Final = "--stage"  # then one of the run's stages: its steps alone
JOIN: Final = "--join-anyway"  # a stage joins a folder of another commit or run file
LABEL: Final = "--label"  # then the run's label, whatever its file says
JOBS: Final = "--jobs"  # then constricter's worker processes


class Command(NamedTuple):
    """What the runner's command line says: its run file, and what it says over the file."""

    run_file: Path | None = None  # none for one step's process, which reads its folder's
    resume: Path | None = None
    stage: str | None = None
    join: bool = False
    label: str | None = None
    only: str | None = None  # a corpus or a set: the run file's, on that alone
    minus: str | None = None  # a corpus, a set or a run file: the run's corpora less its
    at_once: int | None = None  # how many corpora are found side by side
    jobs: int | None = None
    share: int | None = None  # the percent of the machine its steps share


def read_command(argv: Sequence[str], *, run_file: bool = True) -> Command:
    """Read the runner's command line (`python -m tests.corpus`); `run_file`: whether it names one.

    Returns:
      What it says. Raises `SystemExit`, with its usage, for an argument it doesn't take.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(prog="python -m tests.corpus")
    if run_file:
        _ = parser.add_argument("run_file", type=Path)
    _ = parser.add_argument(RESUME, type=Path, metavar="FOLDER")
    _ = parser.add_argument(STAGE)
    _ = parser.add_argument(JOIN, dest="join", action="store_true")
    _ = parser.add_argument(LABEL)
    _ = parser.add_argument("--only", metavar="CORPUS")
    _ = parser.add_argument("--minus", metavar="CORPUS")
    _ = parser.add_argument("--at-once", type=int)
    _ = parser.add_argument(JOBS, type=int)
    _ = parser.add_argument("--share", type=int)
    said: argparse.Namespace = parser.parse_args(argv)
    return Command(
        run_file=cast("Path | None", getattr(said, "run_file", None)),
        resume=cast("Path | None", said.resume),
        stage=cast("str | None", said.stage),
        join=cast("bool", said.join),
        label=cast("str | None", said.label),
        only=cast("str | None", said.only),
        minus=cast("str | None", said.minus),
        at_once=cast("int | None", said.at_once),
        jobs=cast("int | None", said.jobs),
        share=cast("int | None", said.share),
    )
