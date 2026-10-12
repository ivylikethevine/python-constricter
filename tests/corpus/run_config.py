# SPDX-License-Identifier: MIT
"""A run file: what `python -m tests.corpus RUN.toml` measures, with what, and how it's written.

    [run]
    label = "0.3.6-rc.1"             # names the run's folder, and `dev` in its tables
    output = "local/corpus-runs"     # each execution writes a folder of its own under it
    versions = ["0.3.1", "dev"]      # releases from PyPI, and `dev`: this checkout
    formats = ["json", "markdown", "csv"]
    jobs = 0                         # constricter's worker processes: 0 is every CPU

    [corpora]
    include = ["seven"]              # corpora or sets of `corpora.toml`

    [steps]
    check = true                     # offences per code, and errors and warnings at each level
    fix = ["certain", "likely", "unsafe"]   # each on a copy: fixed, broken, a second pass, typed after
    coverage = true                  # the bindings typed as released

A key this doesn't know is an error, not ignored: a misspelt step would otherwise measure nothing.
"""

import tomllib
from datetime import datetime
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from constricter import __version__

DEV: Final = "dev"
JSON: Final = "json"
MARKDOWN: Final = "markdown"
CSV: Final = "csv"
FORMATS: Final = (JSON, MARKDOWN, CSV)
CERTAIN: Final = "certain"
LIKELY: Final = "likely"
UNSAFE: Final = "unsafe"
# Each fix a run can make on a copy, and the options that make it beside `--fix`.
FIXES: Final = {CERTAIN: (), LIKELY: ("--likely",), UNSAFE: ("--unsafe-fixes",)}
_KEYS: Final = {
    "run": {"label", "output", "versions", "formats", "jobs"},
    "corpora": {"include"},
    "steps": {"check", "fix", "coverage"},
}
_STAMP: Final = "%m-%d-%Y-%H%M"  # a run's folder: its label, then the month, day, year and time it started
_Table: TypeAlias = dict[str, object]


class Steps(NamedTuple):
    """What a run measures on each corpus with each version."""

    check: bool = True
    fix: tuple[str, ...] = (CERTAIN, LIKELY, UNSAFE)
    coverage: bool = True


class Run(NamedTuple):
    """A run file, read."""

    label: str = __version__
    output: Path = Path("local/corpus-runs")
    versions: tuple[str, ...] = (DEV,)
    formats: tuple[str, ...] = FORMATS
    jobs: int = 0
    include: tuple[str, ...] = ("seven",)
    steps: Steps = Steps()

    def folder(self, now: datetime) -> Path:
        """Name the folder an execution started at `now` writes.

        Returns:
          It: `<output>/<label>-<month>-<day>-<year>-<hour><minute>`.

        """
        return self.output / f"{self.label}-{now.strftime(_STAMP)}"

    def recorded(self, version: str) -> str:
        """Name a version as the run's tables do: a release as itself, `dev` as `<label>+dev`.

        Returns:
          The name.

        """
        return f"{self.label}+{DEV}" if version == DEV else version


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
        ),
    )


def read(path: Path) -> Run:
    """Read the run file at `path`.

    Returns:
      The run.

    """
    file: IO[bytes]
    with path.open("rb") as file:
        return parse(tomllib.load(file))
