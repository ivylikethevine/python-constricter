# SPDX-License-Identifier: MIT
"""A run file: what `python -m tests.corpus RUN.toml` measures, with what, and how it's written.

    [run]
    label = "0.3.6-rc.1"             # names the run's folder, and `dev` in its tables
    output = "local/corpus-runs"     # each execution writes a folder of its own under it
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

    [corpora]
    include = ["seven"]              # corpora or sets of `corpora.toml`, or directories
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
    profile = true                   # a check in one process `py-spy` samples
    tests-hinted = true              # false: no test run after a checker's hints or the trace's fix
    every-level = false              # true: a check at each level, not one the levels are read from

    [publish]
    runs-md = "docs/RUNS.md"         # and a section a version there, of the per-version tables
    replace = false                  # over a section that's already there
    section = "Super corpora"        # or one section of that heading: every table of the run's last version

A key this doesn't know is an error, not ignored: a misspelt step would otherwise measure nothing.
"""

import tomllib
from datetime import datetime
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import __version__

DEV: Final = "dev"
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
_WHOLE: Final = 100  # a share's percent of the whole machine
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
        "profile",
        "tests-hinted",
        "every-level",
    },
}
_RUNS_MD: Final = "runs-md"
_STAMP: Final = "%m-%d-%Y-%H%M"  # a run's folder: its label, then the month, day, year and time it started
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
    tests_hinted: bool = True  # a suite's tests after each checker's hints and the trace's fix too
    every_level: bool = False  # a check at each level, not one at `suffocate` the others are read from


class Publish(NamedTuple):
    """Where a run's tables go beside its folder."""

    runs_md: Path | None = None  # docs/RUNS.md: a section a version, of the tables `corpus_table` lays out
    replace: bool = False  # over a section that's there
    section: str = ""  # its heading, for one section of the whole run in place of a version's


class Run(NamedTuple):
    """A run file, read."""

    label: str = __version__
    output: Path = Path("local/corpus-runs")
    versions: tuple[str, ...] = (DEV,)
    formats: tuple[str, ...] = FORMATS
    jobs: int = 0
    include: tuple[str, ...] = ("seven",)
    steps: Steps = Steps()
    at_once: int = 1  # the corpora found side by side: their steps wait for the machine alone
    publish: Publish = Publish()
    install: bool = True  # a suite's corpus installed with its tests' dependencies, not cloned alone
    suite_seconds: int = 1800  # how long a suite's tests may run before they're stopped
    suite_workers: int = 0  # the most processes a suite's tests take: 0, as many as fit (`sizing`)
    cpus: int = 0  # the CPUs the steps share: 0 is the machine's
    memory: float = 0.0  # the gigabytes they share: 0 is most of what's free as the run starts
    share: int = 0  # the percent of the machine's CPUs and memory they share, held to it: 0, as above

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
            bool(steps.get("tests-hinted", default.steps.tests_hinted)),
            bool(steps.get("every-level", default.steps.every_level)),
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
    )


def percent(given: object) -> int:
    """Read a share of the machine, in percent.

    Returns:
      It: 1 to 100, or 0 for none given.

    Raises:
      ValueError: it isn't a whole number from 0 to 100.

    """
    if isinstance(given, bool) or not isinstance(given, int) or not 0 <= given <= _WHOLE:
        message: str = f"share must be a percent, 1 to {_WHOLE} (0: the machine's): {given!r}"
        raise ValueError(message)
    return given


def read(path: Path) -> Run:
    """Read the run file at `path`.

    Returns:
      The run.

    """
    file: IO[bytes]
    with path.open("rb") as file:
        return parse(tomllib.load(file))
