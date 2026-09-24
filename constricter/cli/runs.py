# SPDX-License-Identifier: MIT
"""What checking one file gives the CLI, in each mode."""

from dataclasses import dataclass, field
from typing import TypeAlias

from constricter.cli.report import Result
from constricter.fix.known import Returns
from constricter.offences import Offence
from constricter.rules.checker import Coverage


@dataclass(frozen=True)
class CheckRun:
    """What checking one file found (and fixed, or would fix), in check/fix/diff mode."""

    results: list[Result] = field(default_factory=list[Result])
    baselined: int = 0
    fixed: int = 0  # --fix: how many offences it fixed
    text: str = ""  # --diff: the diff; --fix on standard input: the fixed source
    error: str = ""
    returned: Returns = field(default_factory=Returns)  # what its unannotated functions return


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
