# SPDX-License-Identifier: MIT
"""Profile constricter over a large real codebase, to find its own slowest parts.

  local/.venv/bin/python tests/corpus/corpus_profile.py [PATH] [--top N] [--jobs N]   # the standard library

It checks PATH as the corpus job does (`suffocate`, `--all-scopes`, every fix worked out), in a
process of its own that `py-spy` samples from outside, its workers too (`--jobs`, 1 unless given):
a sample is a moment one of them was running, and where. It prints, as Markdown: each constricter
module's share of the samples that ended in its own code, then its N slowest functions by their own
time (not what they call) and by their whole time (what they call too), and how much went to
everything that isn't constricter, and to what (`ast`'s parsing and walking). The samples are
written to local/profile/NAME.txt, a line a stack (`flamegraph.pl`'s input, and speedscope's). CI's
Profile job adds the Markdown to its summary and keeps the samples.
"""

import os
import shutil
import subprocess  # runs the check under `py-spy`
import sys
import sysconfig
import time
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Final, NamedTuple

import constricter

OUT: Final = Path("local/profile")
_PACKAGE: Final = Path(constricter.__file__).resolve().parent
_TOP: Final = 25
_TOP_OPTION: Final = "--top"
_JOBS_OPTION: Final = "--jobs"
_RATE: Final = 100  # samples a second, of each process
_PY_SPY: Final = "py-spy"
# The check as the corpus job runs it, its output dropped: `--jobs` and the path follow.
CHECK: Final = [
    "-m",
    "constricter",
    "--level=suffocate",
    "--all-scopes",
    "--exit-zero",
    "-q",
    "--output-file",
    os.devnull,
]
_PROCESS: Final = "process "  # what a stack's first frame starts with: the process it's of


class Row(NamedTuple):
    """One function: where, its own time and its whole time, in seconds of one process running."""

    where: str  # module:line (function)
    own: float
    whole: float
    ours: bool  # whether it's one of constricter's


def sampled(root: Path, name: str, jobs: int) -> tuple[Path, float]:
    """Check `root` in a process `py-spy` samples, its workers too.

    Returns:
      Where the samples are (a line a stack, with how many times it was seen), and how long the
      check took (wall-clock, sampled).

    Raises:
      SystemExit: `py-spy` isn't installed, or couldn't sample the check.

    """
    spy: str | None
    if (spy := shutil.which(_PY_SPY) or shutil.which(_PY_SPY, path=str(Path(sys.executable).parent))) is None:
        missing: str = f"{_PY_SPY} isn't installed: uv sync --group dev --group corpus"
        raise SystemExit(missing)
    OUT.mkdir(parents=True, exist_ok=True)
    out: Path = OUT / f"{name}.txt"
    out.unlink(missing_ok=True)
    recording: list[str] = [spy, "record", "--format", "raw", "--function", "--full-filenames"]
    recording += ["--subprocesses", "--rate", str(_RATE), "--output", str(out), "--"]
    start: float = time.perf_counter()
    done: subprocess.CompletedProcess[bytes] = subprocess.run(
        [*recording, sys.executable, *CHECK, f"{_JOBS_OPTION}={jobs}", str(root)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=False,
    )
    seconds: float = time.perf_counter() - start
    if not out.exists():  # it exits non-zero for a worker it lost track of, with the samples written
        failed: str = (
            f"{_PY_SPY} wrote no samples ({done.returncode}): {done.stderr.decode(errors='replace')}"
        )
        raise SystemExit(failed)
    return out, seconds


def stacks(samples: Path) -> Iterator[tuple[list[str], int]]:
    """Read the samples `py-spy` wrote.

    Yields:
      Each stack seen, outermost frame first (not the process's own), and how many times.

    """
    line: str
    for line in samples.read_text(encoding="utf-8").splitlines():
        stack: str
        count: str
        stack, _, count = line.rpartition(" ")
        frames: list[str] = [frame for frame in stack.split(";") if not frame.startswith(_PROCESS)]
        if frames and count.isdigit():
            yield frames, int(count)


def _where(frame: str) -> tuple[str, bool]:
    """Name a frame (`function (file:line)`) as a row does.

    Returns:
      `module:line (function)`, and whether it's one of constricter's; another's module is its
      file's name.

    """
    function: str
    place: str
    function, _, place = frame.rpartition(" (")
    file: str
    number: str
    file, _, number = place.removesuffix(")").rpartition(":")
    path: Path = Path(file)
    ours: bool = path.is_relative_to(_PACKAGE)
    module: str = (
        path.relative_to(_PACKAGE.parent).with_suffix("").as_posix().replace("/", ".") if ours else path.name
    )
    return f"{module}:{number} ({function})", ours


def rows(samples: Path) -> list[Row]:
    """Count each function's samples: those it was running in, and those it was anywhere in the stack of.

    Returns:
      A row a function.

    """
    own: dict[str, int] = {}
    whole: dict[str, int] = {}
    frames: list[str]
    count: int
    for frames, count in stacks(samples):
        own[frames[-1]] = own.get(frames[-1], 0) + count
        frame: str
        for frame in set(frames):
            whole[frame] = whole.get(frame, 0) + count
    named: dict[str, tuple[str, bool]] = {frame: _where(frame) for frame in whole}
    return [
        Row(named[frame][0], own.get(frame, 0) / _RATE, seen / _RATE, named[frame][1])
        for frame, seen in whole.items()
    ]


def report(name: str, seconds: float, found: Sequence[Row], top: int) -> str:
    """Write the profile's findings as Markdown.

    Returns:
      It.

    """
    total: float = sum(row.own for row in found) or 1.0
    ours: list[Row] = [row for row in found if row.ours]
    own: float = sum(row.own for row in ours)
    modules: dict[str, float] = {}
    row: Row
    for row in ours:
        module: str = row.where.split(":", 1)[0]
        modules[module] = modules.get(module, 0.0) + row.own
    outside: float = total - own
    lines: list[str] = [
        f"### Profile: {name}",
        "",
        (
            f"{seconds:.1f}s sampled, {total:.1f}s of its processes running; {own:.1f}s ({own / total:.0%}) "
            f"in constricter's own code, {outside:.1f}s ({outside / total:.0%}) outside it (`ast`, the "
            "standard library)."
        ),
        "",
        "| Module | Own time | Share |",
        "| --- | ---: | ---: |",
        *(
            f"| `{module}` | {spent:.2f}s | {spent / total:.1%} |"
            for module, spent in sorted(modules.items(), key=lambda item: -item[1])
            if spent
        ),
        "",
        f"Slowest {top} functions by their own time:",
        "",
        *_table(sorted(ours, key=lambda row: -row.own)[:top], total),
        "",
        f"Slowest {top} functions by their whole time (what they call included):",
        "",
        *_table(sorted(ours, key=lambda row: -row.whole)[:top], total),
        "",
        f"Where the time outside constricter went, the slowest {top} by their own time (`ast.walk`, ...):",
        "",
        *_table(sorted((row for row in found if not row.ours), key=lambda row: -row.own)[:top], total),
    ]
    return "\n".join(lines) + "\n"


def _table(chosen: Sequence[Row], total: float) -> list[str]:
    """Tabulate functions.

    Returns:
      The table's lines.

    """
    return [
        "| Function | Own | Whole |",
        "| --- | ---: | ---: |",
        *(f"| `{row.where}` | {row.own:.2f}s ({row.own / total:.1%}) | {row.whole:.2f}s |" for row in chosen),
    ]


def main(argv: Sequence[str]) -> int:
    """Sample the check, keep the samples, and print the report.

    Returns:
      0.

    """
    top: int = int(argv[argv.index(_TOP_OPTION) + 1]) if _TOP_OPTION in argv else _TOP
    jobs: int = int(argv[argv.index(_JOBS_OPTION) + 1]) if _JOBS_OPTION in argv else 1
    named: list[str] = [
        arg
        for index, arg in enumerate(argv)
        if not arg.startswith("-") and argv[index - 1] not in {_TOP_OPTION, _JOBS_OPTION}
    ]
    root: Path = Path(named[0]) if named else Path(sysconfig.get_paths()["stdlib"])
    name: str = "stdlib" if not named else root.name
    samples: Path
    seconds: float
    samples, seconds = sampled(root, name, jobs)
    _ = sys.stdout.write(report(name, seconds, rows(samples), top))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
