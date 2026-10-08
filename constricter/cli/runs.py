# SPDX-License-Identifier: MIT
"""What checking one file gives the CLI, in each mode."""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from typing import TypeAlias, cast

from constricter.cli.report import Result
from constricter.fix.core.known import Observed, Returns
from constricter.offences import Offence
from constricter.rules.checker import Coverage

# The lines one round of `--fix` added to a file: for each, its cell (`None` outside a notebook)
# and the line (from 1) it went before.
Added: TypeAlias = tuple[tuple[int | None, int], ...]


@dataclass(frozen=True)
class CheckRun:
    """What checking one file found (and fixed, or would fix), in check/fix/diff mode."""

    results: list[Result] = field(default_factory=list[Result])
    baselined: int = 0
    fixed: int = 0  # --fix: how many offences it fixed
    text: str = ""  # --diff: the diff; --fix on standard input: the fixed source
    error: str = ""
    returned: Returns = field(default_factory=Returns)  # what its unannotated functions return
    calls: Observed = field(default_factory=Observed)  # what it passes checked files' functions
    # --fix: the offences it fixed, each where it was before any fix, and each round's added lines.
    made: list[Result] = field(default_factory=list[Result])
    rounds: tuple[Added, ...] = ()


@dataclass(frozen=True)
class BaselineRun:
    """One file's offences, unfiltered, for --write-baseline."""

    found: list[Offence] = field(default_factory=list[Offence])
    error: str = ""
    returned: Returns = field(default_factory=Returns)  # what its unannotated functions return


@dataclass(frozen=True)
class CoverageRun:
    """One file's annotation coverage, for --coverage."""

    coverage: Coverage | None = None
    error: str = ""


FileRun: TypeAlias = CheckRun | BaselineRun | CoverageRun


def merged(before: FileRun, after: FileRun) -> FileRun:
    """Join a file's two `--fix` rounds' `CheckRun`s: what's left is the later's, what's fixed is both's.

    The later round's fixes are placed on the lines they had before the earlier ones' (see `_original`).

    Returns:
      The joined run.

    """
    first: CheckRun = cast("CheckRun", before)
    later: CheckRun = cast("CheckRun", after)
    made: list[Result] = [
        result._replace(offence=replace(result.offence, line=_original(result.offence, first.rounds)))
        for result in later.made
    ]
    return replace(
        later,
        fixed=first.fixed + later.fixed,
        made=[*first.made, *made],
        rounds=(*first.rounds, *later.rounds),
    )


def _original(offence: Offence, rounds: Sequence[Added]) -> int:
    """Find the line an offence was on before `rounds` of fixes added lines to its file.

    Returns:
      It; for an offence on an added line (a declaration, fixed again), the line that one went before.

    """
    line: int = offence.line
    added: Added
    for added in reversed(rounds):
        before: list[int] = [at for cell, at in added if cell == offence.cell]
        # The added lines above it: the first went where it says, each next one a line further down.
        line -= sum(at + index < line for index, at in enumerate(before))
    return line
