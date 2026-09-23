# SPDX-License-Identifier: MIT
"""Profile constricter over a large real codebase, to find its own slowest parts.

  local/.venv/bin/python tests/corpus/corpus_profile.py [PATH] [--top N]   # default: the standard library

It checks PATH as the corpus job does (`suffocate`, `--all-scopes`, every fix worked out), in this
one process (`--jobs=1`, so the profiler sees everything), under `cProfile`, and prints, as
Markdown: each constricter module's share of the time spent in its own code, then its N slowest
functions by their own time (not what they call) and by their whole time (what they call too), and
how much went to everything that isn't constricter, and to what (`ast`'s parsing and walking). The
profile itself is written to local/profile/NAME.prof, for `python -m pstats` or snakeviz. CI's
Corpus job adds the Markdown to its summary and keeps the profile.
"""

import cProfile
import os
import pstats
import sys
import sysconfig
import time
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

import constricter
from constricter.cli import command as cli

OUT: Final = Path("local/profile")
_PACKAGE: Final = Path(constricter.__file__).resolve().parent
_TOP: Final = 25
_TOP_OPTION: Final = "--top"
_CHECK: Final = [
    "--level=suffocate",
    "--all-scopes",
    "--jobs=1",
    "--exit-zero",
    "-q",
    "--output-file",
    os.devnull,
]
# What `pstats` keeps of a function: its file, first line and name.
_Function: TypeAlias = tuple[str, int, str]
# And of its calls: primitive calls, all calls, its own time, its whole time, and its callers.
_Timing: TypeAlias = tuple[int, int, float, float, dict[_Function, tuple[int, int, float, float]]]


class Row(NamedTuple):
    """One of constricter's functions: where, how often it was called, its own and its whole time."""

    where: str  # module:line (function)
    calls: int
    own: float
    whole: float


def profiled(root: Path) -> tuple[cProfile.Profile, float]:
    """Check `root` under the profiler.

    Returns:
      The profile, and how long the check took (wall-clock, profiled).

    """
    profile: cProfile.Profile = cProfile.Profile()
    start: float = time.perf_counter()
    profile.enable()
    try:
        _ = cli.main([*_CHECK, str(root)])
    finally:
        profile.disable()
    return profile, time.perf_counter() - start


def rows(stats: pstats.Stats, *, own: bool = True) -> list[Row]:
    """List constricter's own functions from a profile (not `own`: everything else's).

    Returns:
      Them, as rows.

    """
    # `stats` and `total_tt` are `pstats.Stats`' own attributes, which its stubs leave out.
    timings: dict[_Function, _Timing] = cast("dict[_Function, _Timing]", vars(stats)["stats"])
    found: list[Row] = []
    function: _Function
    timing: _Timing
    for function, timing in timings.items():
        path: Path = Path(function[0])
        if path.is_relative_to(_PACKAGE) is own:
            module: str = (
                path.relative_to(_PACKAGE.parent).with_suffix("").as_posix().replace("/", ".")
                if own
                else path.name  # a builtin's is `~`
            )
            found.append(Row(f"{module}:{function[1]} ({function[2]})", timing[1], timing[2], timing[3]))
    return found


def report(name: str, seconds: float, stats: pstats.Stats, top: int) -> str:
    """Write the profile's findings as Markdown.

    Returns:
      It.

    """
    found: list[Row] = rows(stats)
    total: float = cast("float", vars(stats)["total_tt"])
    own: float = sum(row.own for row in found)
    modules: dict[str, float] = {}
    row: Row
    for row in found:
        module: str = row.where.split(":", 1)[0]
        modules[module] = modules.get(module, 0.0) + row.own
    outside: float = total - own
    lines: list[str] = [
        f"### Profile: {name}",
        "",
        (
            f"{seconds:.1f}s profiled; {own:.1f}s ({own / total:.0%}) in constricter's own code, "
            f"{outside:.1f}s ({outside / total:.0%}) outside it (`ast`, the standard library)."
        ),
        "",
        "| Module | Own time | Share |",
        "| --- | ---: | ---: |",
        *(
            f"| `{module}` | {spent:.2f}s | {spent / total:.1%} |"
            for module, spent in sorted(modules.items(), key=lambda item: -item[1])
        ),
        "",
        f"Slowest {top} functions by their own time:",
        "",
        *_table(sorted(found, key=lambda row: -row.own)[:top], total),
        "",
        f"Slowest {top} functions by their whole time (what they call included):",
        "",
        *_table(sorted(found, key=lambda row: -row.whole)[:top], total),
        "",
        f"Where the time outside constricter went, the slowest {top} by their own time (`ast.walk`, ...):",
        "",
        *_table(sorted(rows(stats, own=False), key=lambda row: -row.own)[:top], total),
    ]
    return "\n".join(lines) + "\n"


def _table(chosen: Sequence[Row], total: float) -> list[str]:
    """Tabulate functions.

    Returns:
      The table's lines.

    """
    return [
        "| Function | Calls | Own | Whole |",
        "| --- | ---: | ---: | ---: |",
        *(
            f"| `{row.where}` | {row.calls:,} | {row.own:.2f}s ({row.own / total:.1%}) | {row.whole:.2f}s |"
            for row in chosen
        ),
    ]


def main(argv: Sequence[str]) -> int:
    """Profile the check, save the profile, and print the report.

    Returns:
      0.

    """
    top: int = int(argv[argv.index(_TOP_OPTION) + 1]) if _TOP_OPTION in argv else _TOP
    named: list[str] = [
        arg for index, arg in enumerate(argv) if not arg.startswith("-") and argv[index - 1] != _TOP_OPTION
    ]
    root: Path = Path(named[0]) if named else Path(sysconfig.get_paths()["stdlib"])
    name: str = "stdlib" if not named else root.name
    profile: cProfile.Profile
    seconds: float
    profile, seconds = profiled(root)
    OUT.mkdir(parents=True, exist_ok=True)
    profile.dump_stats(OUT / f"{name}.prof")
    stats: pstats.Stats = pstats.Stats(profile)
    _ = sys.stdout.write(report(name, seconds, stats, top))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
