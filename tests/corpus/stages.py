"""A run in stages: groups of its steps, each run at its own time into one folder, joined by their records.

Built in, in the order they're meant to run (`BUILT_IN`): `fixes` (the check, each fix, the checkers'
hints, the census and coverage), `traced` (a suite's traced tests, and every source's fixes at
once, which read their trace), `tests` (a suite's own tests and type checks, as released and after
each fix) and `timed` (the timed checks and the profile, each with nothing beside it). A run file's
`[stages]` table regroups them: each stage a list of step names or `fnmatch` patterns of them.

A step is the stage's that names it outright, else the first in the table whose pattern matches it;
one in none is an error, a misspelt stage measuring nothing. A step whose needs are another stage's,
with no record yet, is left for when they have one (`runnable`). A stage is in once each of its
steps the run has has a record (`left`).
"""

from collections.abc import Callable, Iterable, Mapping, Sequence
from fnmatch import fnmatchcase
from typing import Final, TypeAlias

Stages: TypeAlias = tuple[tuple[str, tuple[str, ...]], ...]  # each stage's name and its steps' patterns

BUILT_IN: Final[Stages] = (
    ("fixes", ("check", "fix-*", "infer-*", "census", "coverage")),
    ("traced", ("traced", "infer-union")),
    ("tests", ("tests", "tests-*", "types", "types-*")),
    ("timed", ("timing", "profile")),
)
_GLOB: Final = frozenset("*?[")  # what makes a pattern of a step's name


def stage_of(step: str, stages: Stages) -> str:
    """Find the stage a step is in: the one naming it outright, else the first whose pattern matches.

    Returns:
      Its name.

    Raises:
      ValueError: no stage has it.

    """
    name: str
    patterns: tuple[str, ...]
    for name, patterns in stages:
        if step in patterns:
            return name
    for name, patterns in stages:
        if any(_GLOB & set(pattern) and fnmatchcase(step, pattern) for pattern in patterns):
            return name
    message: str = f"the step {step!r} is in none of the stages {', '.join(name for name, _ in stages)}"
    raise ValueError(message)


def named(stage: str, stages: Stages) -> str:
    """Check a stage `--stage` names is one of the run's.

    Returns:
      It.

    Raises:
      SystemExit: it isn't.

    """
    if stage not in {name for name, _ in stages}:
        message: str = f"--stage {stage!r} is none of {', '.join(name for name, _ in stages)}"
        raise SystemExit(message)
    return stage


def chosen(stage: str | None, stages: Stages) -> Callable[[str], bool]:
    """Say which steps an execution runs: those of `stage`, or every one (`None`).

    Returns:
      What tells them.

    """
    if stage is None:
        return _every
    return lambda step: stage_of(step, stages) == stage


def _every(_step: str) -> bool:
    return True


def runnable(
    names: Sequence[str],
    needs: Mapping[str, frozenset[str]],
    recorded: Callable[[str], bool],
) -> tuple[list[str], list[str]]:
    """Split a corpus's steps of this execution (`names`, in order) by whether what they need will be there.

    A step needing one of them runs after it; one needing another stage's step runs only once that
    step has a record (`recorded`), and is left for later otherwise, with what needs it in turn.

    Returns:
      Those to run, and those left.

    """
    kept: list[str] = []
    later: list[str] = []
    among: frozenset[str] = frozenset(names)
    name: str
    for name in names:  # those a step needs come before it
        need: frozenset[str] = needs.get(name, frozenset())
        if all(each in kept or (each not in among and recorded(each)) for each in need):
            kept.append(name)
        else:
            later.append(name)
    return kept, later


def left(stages: Stages, missing: Iterable[str]) -> list[str]:
    """Name the stages still to run: those with a step of the run that has no record.

    `missing`: those steps, of every corpus and version.

    Returns:
      Them, in the table's order.

    """
    lacking: frozenset[str] = frozenset(stage_of(step, stages) for step in missing)
    return [name for name, _ in stages if name in lacking]
