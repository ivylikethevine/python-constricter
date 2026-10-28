"""A check's rounds: every file, then again each one `--fix` changed in a way a second check sees.

Each round knows the index of what the files offer each other, the type checker's hints with
`--infer-with`, and the runs kept from the last.
"""

import contextlib
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast

from constricter import notebook, traced
from constricter.cli import collecting, schedule
from constricter.cli.options import Guesses, Mode, Options
from constricter.cli.paths import STDIN
from constricter.cli.reading import READ_ERRORS, read_text
from constricter.cli.runs import CheckRun, FileRun, merged
from constricter.cli.workers import Workers, running, started
from constricter.empty import Empty
from constricter.fix.core.known import Callee, Hints, Outside
from constricter.fix.index import callers, decorated, loose, plain, project
from constricter.fix.index.stubs import installed
from constricter.offences import UNANNOTATED_ATTRIBUTE, UNANNOTATED_PARAMETER, Edit, Fix

if TYPE_CHECKING:  # slow to import, and only needed for `--infer-with`
    from constricter.cli.lsp import hints

_PY: Final = ".py"  # a module the index names (not a notebook)
_Hinted: TypeAlias = dict[Path, tuple[Hints, ...]]  # each file's hints, a checker's each
HINT_ROUNDS: Final = 4  # with `--fix`: how many times a file is fixed, at most (see `settled`)
# The fix kinds a scope's check comes to late, once the scope is read: what was bound to such a
# name's value before had no type yet, and has one once the fix is written.
_LATE_KINDS: Final = frozenset({"optional", "filled"})


def settled(
    paths: Sequence[Path],
    check: Callable[[Path, Outside], FileRun],
    options: Options,
    session: "hints.Session | None",
) -> list[FileRun]:
    """Check every file, then again each one `--fix` changed in a way a second check would see.

    Until a round changes nothing, `HINT_ROUNDS` at most: a second pass is then left nothing. With
    `--likely` or `--unsafe-fixes` and no type checker's hints, the files a round changed are indexed
    again, and the others checked again too where that changes what they know from outside: what
    reads a guess another file declares (an attribute LVA013's declares) now knows its type.

    Returns:
      What each file found, a file's rounds joined.

    """
    runs: list[FileRun]
    modules: project.Index
    runs, modules = _called_again(
        paths,
        checked_all(paths, check, options, session),
        check,
        options,
        session,
    )
    fixing: bool = options.mode is Mode.FIX
    onward: bool = fixing and session is None and options.guesses is not Guesses.NONE
    # A signature written (LVA014, LVA015) changes what the other files know of the file whatever
    # the guesses: it's indexed again, and they're checked again where that reaches them.
    signing: bool = fixing and session is None and (options.checks.returns or options.checks.parameters)
    again: list[int] = [
        index
        for index, run in enumerate(runs)
        if fixing and paths[index] != STDIN and _unsettled(run, session, options.guesses)
    ]
    changed: list[int] = [
        at for at in range(len(runs)) if _reaching(paths[at], runs[at], onward=onward, signing=signing)
    ]
    for _ in range(HINT_ROUNDS - 1):
        held: dict[int, FileRun] = {}
        if changed:
            modules = _reindexed(modules, [paths[i] for i in changed], options)
            held = {i: run for i, run in enumerate(runs) if i not in again and paths[i] != STDIN}
        if not again and not held:
            break
        fresh: list[tuple[int, FileRun]]
        latest: project.Index
        fresh, latest = _round(paths, runs, (again, held), _How(check, options, session), modules)
        modules = latest if onward or signing else modules
        again = [index for index, run in fresh if _unsettled(run, session, options.guesses)]
        changed = [
            index for index, run in fresh if _reaching(paths[index], run, onward=onward, signing=signing)
        ]
    return runs


def _reaching(path: Path, run: FileRun, *, onward: bool, signing: bool) -> bool:
    """Check whether a round of `--fix` changed a file in a way the other files may see.

    Returns:
      Whether it fixed anything, where `onward` (guesses on); else whether it wrote a signature,
      where `signing` (LVA014 or LVA015 selected).

    """
    if not _changed(path, run):
        return False
    return onward or (
        signing
        and any(
            isinstance(made.offence.edit, Fix)
            and (made.offence.edit.edit is Edit.SIGNATURE or made.offence.code == UNANNOTATED_PARAMETER)
            for made in cast("CheckRun", run).made
        )
    )


class _How(NamedTuple):
    """How a round checks its files: the check, the options, and the type checkers' session."""

    check: Callable[[Path, Outside], FileRun]
    options: Options
    session: "hints.Session | None"


def _round(
    paths: Sequence[Path],
    runs: list[FileRun],
    todo: tuple[Sequence[int], Mapping[int, FileRun]],
    how: "_How",
    modules: project.Index,
) -> tuple[list[tuple[int, FileRun]], project.Index]:
    """Check files of `paths` again, knowing `modules`: each one's new run is joined to its `runs`.

    `todo`: the files to check, by index, and those held, each with its last run: checked only where
    they know anything else from outside now (see `schedule.Rounds`). `how`: the check, the options
    and the type checkers' session.

    Returns:
      Each file the round checked, with this round's run alone; and the index, with what their
      functions return.

    """
    again: Sequence[int]
    held: Mapping[int, FileRun]
    again, held = todo
    which: list[int] = sorted({*again, *held})
    redone: list[FileRun]
    latest: project.Index
    redone, latest = checked_all(
        [paths[i] for i in which],
        how.check,
        how.options,
        how.session,
        _Known(modules, {at: held[i] for at, i in enumerate(which) if i in held}),
    )
    fresh: list[tuple[int, FileRun]] = [
        (index, run) for index, run in zip(which, redone, strict=True) if run is not held.get(index)
    ]
    index: int
    run: FileRun
    for index, run in fresh:
        runs[index] = merged(runs[index], run)
    return fresh, latest


def _changed(path: Path, run: FileRun) -> bool:
    """Check whether a round of `--fix` changed a file the index has (not standard input or a notebook).

    Returns:
      Whether it fixed anything there.

    """
    return path.suffix == _PY and bool(cast("CheckRun", run).fixed)


def _reindexed(modules: project.Index, paths: Sequence[Path], options: Options) -> project.Index:
    """Index again the files at `paths`, which `--fix` changed: in the run's workers, if it has them.

    Returns:
      The index, with them as they are now (see `project.spliced`).

    """
    found: list[project.Module | None] = (
        started(paths, options.jobs).read() if running() else [project.read(path) for path in paths]
    )
    return project.spliced(modules, found)


def _unsettled(run: FileRun, session: "hints.Session | None", guesses: Guesses) -> bool:
    """Check whether a round of `--fix` changed a file in a way that changes what's inferred there.

    Returns:
      Whether it fixed anything, with a type checker's hints: its new annotations change them.
      Without, whether it made a fix the scope's check comes to late (`_LATE_KINDS`): what's bound
      to such a name's value was read before its type was known. Or declared an attribute (LVA013),
      which a method above its class's may have read before its stores were seen. Or, with
      `--likely` alone, wrote a guess: what rests on it and on no other guess is certain once it's
      declared.

    """
    checked: CheckRun = cast("CheckRun", run)
    return bool(checked.fixed) and (
        session is not None
        or any(
            isinstance(made.offence.edit, Fix)
            and (
                made.offence.edit.kinds & _LATE_KINDS
                or made.offence.code == UNANNOTATED_ATTRIBUTE
                or (guesses is Guesses.LIKELY and made.offence.unsafe)
            )
            for made in checked.made
        )
    )


def _called_again(
    paths: Sequence[Path],
    first: tuple[list[FileRun], project.Index],
    check: Callable[[Path, Outside], FileRun],
    options: Options,
    session: "hints.Session | None" = None,
) -> tuple[list[FileRun], project.Index]:
    """Check again the files whose functions' unannotated parameters every call passes one type.

    Knowing those types (see `callers`), as guesses; a file among several of one module name isn't
    (which its callers call can't be told). Then the other files calling those functions, knowing
    what they now return. With `--fix` a file's rounds are joined; otherwise the last, knowing more,
    stands.

    Returns:
      What each file found, and the index, with the parameters' types.

    """
    runs: list[FileRun]
    modules: project.Index
    runs, modules = first
    found: dict[str, callers.Parameters] = callers.parameters(
        (run.calls for run in runs if isinstance(run, CheckRun)),
        modules,
    )
    names: list[str | None] = [project.module_name(path) if path.suffix == _PY else None for path in paths]
    again: list[int]
    if not (again := [at for at, name in enumerate(names) if name in found and names.count(name) == 1]):
        return runs, modules
    calling: list[int] = _calling(runs, found, again)
    before: project.Index = callers.with_parameters(modules, found)
    modules = _checked_more(paths, runs, again, _How(check, options, session), before)
    # A caller is checked again only if a function it imports now returns something else.
    calling = [
        at
        for at in calling
        if loose.returned(modules, paths[at], {}) != loose.returned(before, paths[at], {})
    ]
    return runs, _checked_more(paths, runs, calling, _How(check, options, session), modules)


def _checked_more(
    paths: Sequence[Path],
    runs: list[FileRun],
    which: Sequence[int],
    how: "_How",
    modules: project.Index,
) -> project.Index:
    """Check the files of `paths` at `which` again, knowing `modules`, into `runs`.

    `how`: the check, the options and the type checkers' session. With `--fix` a file's rounds are
    joined; otherwise the later one stands.

    Returns:
      The index, with what their functions now return.

    """
    redone: list[FileRun]
    redone, modules = checked_all(
        [paths[at] for at in which],
        how.check,
        how.options,
        how.session,
        _Known(modules),
    )
    at: int
    run: FileRun
    for at, run in zip(which, redone, strict=True):
        runs[at] = merged(runs[at], run) if how.options.mode is Mode.FIX else run
    return modules


def _calling(
    runs: Sequence[FileRun],
    found: Mapping[str, callers.Parameters],
    again: Sequence[int],
) -> list[int]:
    """Find the files (not among `again`) calling a function whose parameters `found` types.

    Returns:
      Their indexes.

    """
    typed: set[Callee] = {(module, function) for module, functions in found.items() for function in functions}
    return [
        at
        for at, run in enumerate(runs)
        if at not in again and isinstance(run, CheckRun) and typed & run.calls.calls.keys()
    ]


class _Known(NamedTuple):
    """What a round of checks knows of the files: the index (`None`: index them), and their kept runs.

    `kept`: see `schedule.Rounds`, by the index of each file in the round's.
    """

    modules: project.Index | None = None
    kept: Mapping[int, FileRun] = Empty()


_FIRST: Final = _Known()  # a run's first round: the files indexed, none kept


def checked_all(
    paths: Sequence[Path],
    check: Callable[[Path, Outside], FileRun],
    options: Options,
    session: "hints.Session | None" = None,
    known: _Known = _FIRST,
) -> tuple[list[FileRun], project.Index]:
    """Check `paths` (`--jobs` at a time), with the `session`'s hints, knowing `known`.

    Returns:
      What each file found, and the index of every file's module.

    """
    # Before a worker starts: one forked while the servers' threads run could wait on a lock one holds.
    hinted: _Hinted = {} if session is None else session.hints(_texts(paths))
    if options.input.trace is not None:
        hinted = traced.merged(hinted, traced.load(options.input.trace), paths)
    coverage: bool = options.mode is Mode.COVERAGE  # needs nothing from the other files
    # A run's later rounds go to its workers, whatever their size: each knows what its files last knew.
    pool: Workers | None = (
        started(paths, options.jobs) if options.jobs != 1 and (len(paths) > 1 or running()) else None
    )
    modules: project.Index | None = known.modules
    if modules is None and pool:
        modules = project.Index({}, []) if coverage else pool.index()
    elif modules is None:
        modules = project.Index({}, []) if coverage else project.index(paths)
        collecting.indexed()
    if not coverage:
        modules = plain.settled(
            decorated.passed(installed.with_installed(modules, installed.search_path())),
            options.checks.plain_bases,
        )
    return schedule.checked(
        paths,
        check,
        pool,
        (modules, hinted),
        schedule.Rounds(merged if options.mode is Mode.FIX else None, known.kept),
    )


def _texts(paths: Sequence[Path]) -> dict[Path, str]:
    """Read each file to ask the type checker about (not a notebook, or standard input).

    A file that can't be read is left out: checking it reports that.

    Returns:
      Each file's text.

    """
    texts: dict[Path, str] = {}
    path: Path
    for path in paths:
        if path != STDIN and path.suffix != notebook.SUFFIX:
            with contextlib.suppress(*READ_ERRORS):
                texts[path] = read_text(path)
    return texts
