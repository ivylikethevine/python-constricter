# SPDX-License-Identifier: MIT
"""Time a check of the standard library and pandas with this checkout and another, side by side.

  local/.venv/bin/python tests/corpus/corpus_timing.py OTHER [--runs N]   # OTHER: another checkout's root

Each is checked as the corpus job does (`suffocate`, `--all-scopes`) by each checkout's
`constricter` (its standard-library tables generated), in one process (`--jobs=1`) and on every
CPU (`--jobs=0`), N times (3) under `hyperfine`, which has to be installed. It prints, as Markdown,
each check's mean time and its spread with this checkout and with the other, and their ratio; the
runs' own times are written to local/profile/timing.json.
"""

import importlib.util
import json
import shlex
import shutil
import subprocess  # runs `hyperfine`
import sys
import sysconfig
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple, TypedDict, cast

from tests.corpus.corpus_profile import CHECK

OUT: Final = Path("local/profile")
_ROOT: Final = Path(__file__).resolve().parent.parent.parent
_HYPERFINE: Final = "hyperfine"
_RUNS: Final = 3
_RUNS_OPTION: Final = "--runs"
_JOBS: Final = (1, 0)  # one process, then every CPU
_PANDAS: Final = "pandas"
# Not the directory it's run from (`-P`): each checkout's `constricter` is on `PYTHONPATH`.
_CHECK: Final = ("-P", *CHECK)


class _Result(TypedDict):
    """What `hyperfine` keeps of one command: its name, and its runs' mean and spread in seconds."""

    command: str
    mean: float
    stddev: float | None


class Timed(NamedTuple):
    """One check, timed with both checkouts: its corpus, its `--jobs`, and each one's mean and spread."""

    corpus: str
    jobs: int
    this: tuple[float, float]
    other: tuple[float, float]


def corpora() -> list[tuple[str, Path]]:
    """Find what's checked: the standard library, and pandas where it's installed.

    Returns:
      Each one's name and directory.

    """
    found: list[tuple[str, Path]] = [("standard library", Path(sysconfig.get_paths()["stdlib"]))]
    origin: str | None
    if (origin := getattr(importlib.util.find_spec(_PANDAS), "origin", None)) is not None:
        found.append((_PANDAS, Path(origin).parent))
    return found


def timed(corpus: tuple[str, Path], jobs: int, other: Path, runs: int) -> Timed:
    """Time one check with this checkout and with `other`, `runs` times each.

    Returns:
      Both means and spreads.

    Raises:
      SystemExit: `hyperfine` isn't installed, or a check failed.

    """
    hyperfine: str | None
    if (hyperfine := shutil.which(_HYPERFINE)) is None:
        missing: str = f"{_HYPERFINE} isn't installed"
        raise SystemExit(missing)
    OUT.mkdir(parents=True, exist_ok=True)
    out: Path = (OUT / "timing.json").resolve()
    commands: list[str] = []
    checkout: Path
    for checkout in (_ROOT, other.resolve()):
        words: list[str] = [sys.executable, *_CHECK, f"--jobs={jobs}", str(corpus[1])]
        commands += [
            "--command-name",
            str(checkout),
            f"PYTHONPATH={shlex.quote(str(checkout))} {shlex.join(words)}",
        ]
    done: subprocess.CompletedProcess[bytes] = subprocess.run(
        # A check exits 2 for a file it can't read (the standard library's tests have some).
        [hyperfine, "--ignore-failure", "--runs", str(runs), "--export-json", str(out), *commands],
        stdout=subprocess.DEVNULL,
        cwd=OUT,  # no `pyproject.toml` above the checks but this checkout's own, for both
        check=False,
    )
    if done.returncode:
        raise SystemExit(done.returncode)
    results: list[_Result] = cast("dict[str, list[_Result]]", json.loads(out.read_text("utf-8")))["results"]
    this: _Result
    theirs: _Result
    this, theirs = results
    return Timed(
        corpus[0],
        jobs,
        (this["mean"], this["stddev"] or 0.0),
        (theirs["mean"], theirs["stddev"] or 0.0),
    )


def report(found: Sequence[Timed], other: Path, runs: int) -> str:
    """Write the timings as Markdown.

    Returns:
      A table, a row a check.

    """
    lines: list[str] = [
        f"A check's seconds, the mean of {runs} runs and their spread, with this checkout and `{other}`:",
        "",
        "| Corpus | `--jobs` | This | Other | This / other |",
        "| --- | ---: | ---: | ---: | ---: |",
        *(_row(each) for each in found),
    ]
    return "\n".join(lines) + "\n"


def _row(each: Timed) -> str:
    this: str = f"{each.this[0]:.1f} ± {each.this[1]:.1f}"
    other: str = f"{each.other[0]:.1f} ± {each.other[1]:.1f}"
    return f"| {each.corpus} | {each.jobs} | {this} | {other} | {each.this[0] / each.other[0]:.2f} |"


def main(argv: Sequence[str]) -> int:
    """Time every check with both checkouts and print the table.

    Returns:
      0; 2 without another checkout to compare with.

    """
    runs: int = int(argv[argv.index(_RUNS_OPTION) + 1]) if _RUNS_OPTION in argv else _RUNS
    named: list[str] = [
        arg for index, arg in enumerate(argv) if not arg.startswith("-") and argv[index - 1] != _RUNS_OPTION
    ]
    if not named or not (Path(named[0]) / "constricter").is_dir():
        _ = sys.stderr.write(f"usage: {Path(__file__).name} OTHER [{_RUNS_OPTION} N]\n")
        return 2
    other: Path = Path(named[0])
    found: list[Timed] = [timed(corpus, jobs, other, runs) for corpus in corpora() for jobs in _JOBS]
    _ = sys.stdout.write(report(found, other, runs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
