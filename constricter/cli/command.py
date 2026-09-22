# SPDX-License-Identifier: MIT
"""The `constricter` command (see README)."""

import contextlib
import difflib
import itertools
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace
from functools import partial
from pathlib import Path
from typing import Final, NamedTuple, TextIO, TypeAlias, cast

from constricter import notebook
from constricter.cli import baseline
from constricter.cli.options import Mode, Options, Output
from constricter.cli.paths import STDIN, python_files
from constricter.cli.report import Format, Result, fix_reasons, render, statistics
from constricter.fix import fixes, project
from constricter.noqa import lines, unsuppressed
from constricter.offences import (
    DEFAULT_CHECKS,
    Checks,
    Offence,
)
from constricter.rules.checker import Coverage, annotation_coverage, check_source

EXIT_CLEAN: Final = 0
EXIT_FOUND: Final = 1
EXIT_ERROR: Final = 2
_ALL: Final = 100  # percent


def _read(path: Path) -> str:
    """Read `path`; `-` is standard input.

    Returns:
      Its text.

    """
    return sys.stdin.read() if path == STDIN else path.read_bytes().decode("utf-8")


def _source(raw: str, name: Path) -> tuple[str, list[notebook.Line]]:
    """Extract the Python in `raw`: a notebook's code cells, joined.

    Returns:
      The source, and each line's cell if it's a notebook.

    """
    return notebook.parse(raw, str(name)) if name.suffix == notebook.SUFFIX else (raw, [])


def check_text(
    raw: str,
    name: Path,
    checks: Checks = DEFAULT_CHECKS,
    *,
    calls: Mapping[str, str] | None = None,
) -> list[Offence]:
    """Return the offences in `raw`, the text of `name`, that no `# noqa` suppresses.

    A notebook's code cells are checked as one module, and each offence placed in its cell.
    Raises `ValueError` for a `.ipynb` that isn't a notebook.

    Returns:
      The unsuppressed offences, a notebook's placed in their cells.

    """
    source: str
    where: list[notebook.Line]
    source, where = _source(raw, name)
    offences: list[Offence] = unsuppressed(
        check_source(source, str(name), checks, calls=calls),
        lines(source),
    )
    return (
        [replace(o, line=where[o.line - 1].line, cell=where[o.line - 1].cell) for o in offences]
        if where
        else offences
    )


# One changed part of a fixed file (the file, or a notebook's cell): its label, old and new lines.
_Change: TypeAlias = tuple[str, list[str], list[str]]
# One JSON value a coverage report holds, and one file's row of them.
_Scalar: TypeAlias = str | int | float
_Row: TypeAlias = dict[str, _Scalar]


class Fixed(NamedTuple):
    """`raw`, fixed: its new text, and each changed part (the file, or a notebook's cell)."""

    text: str
    changes: list[_Change]  # each part's label and old and new lines


def _fixed(raw: str, name: Path, offences: Sequence[Offence]) -> Fixed:
    """Add each fixable offence's annotation to `raw`, the text of `name`.

    Returns:
      The new text, and each changed part.

    """
    if name.suffix == notebook.SUFFIX:
        text: str
        cells: list[notebook.Cell]
        text, cells = notebook.fix(raw, offences)
        return Fixed(text, [(f"{name}:cell {c.number}", c.old, c.new) for c in cells])
    old: list[str] = lines(raw)
    new: list[str] = fixes.apply(old, offences)
    return Fixed("".join(new), [(str(name), old, new)] if new != old else [])


def _diff(raw: str, name: Path, offences: Sequence[Offence]) -> str:
    return "".join(
        "".join(difflib.unified_diff(old, new, label, label))
        for label, old, new in _fixed(raw, name, offences).changes
    )


def fix_file(path: Path, offences: Sequence[Offence]) -> int:
    """Add each fixable offence's annotation to `path` (a notebook's, in its cells).

    Returns:
      How many offences were fixed.

    """
    count: int
    if not (count := sum(1 for o in offences if o.fix)):
        return 0
    _ = path.write_bytes(_fixed(_read(path), path, offences).text.encode())
    return count


@dataclass(frozen=True)
class _CheckRun:
    """What checking one file found (and fixed, or would fix), in check/fix/diff mode."""

    results: list[Result] = field(default_factory=list[Result])
    baselined: int = 0
    fixed: int = 0  # --fix: how many offences it fixed
    text: str = ""  # --diff: the diff; --fix on standard input: the fixed source
    error: str = ""


@dataclass(frozen=True)
class _BaselineRun:
    """One file's offences, unfiltered, for --write-baseline."""

    found: list[Offence] = field(default_factory=list[Offence])
    error: str = ""


@dataclass(frozen=True)
class _CoverageRun:
    """One file's annotation coverage, for --coverage."""

    coverage: Coverage | None = None
    error: str = ""


_FileRun: TypeAlias = _CheckRun | _BaselineRun | _CoverageRun


def _checked(path: Path, name: Path, checks: Checks, calls: Mapping[str, str]) -> tuple[str, list[Offence]]:
    """Read `path` and check it as `name`; raises what reading or parsing it does.

    Returns:
      Its text, and its offences.

    """
    raw: str = _read(path)
    return raw, check_text(raw, name, checks, calls=calls)


def _read_checked(
    path: Path,
    name: Path,
    checks: Checks,
    calls: Mapping[str, str],
) -> tuple[str, list[Offence], str]:
    """Read and check `path`, turning a read or parse error into a message instead of raising.

    Returns:
      Its text and offences (empty on error), and the error message (empty on success).

    """
    raw: str
    offences: list[Offence]
    try:
        raw, offences = _checked(path, name, checks, calls)
    except (OSError, ValueError, SyntaxError) as error:  # UnicodeDecodeError is a ValueError
        return "", [], f"{name}: error: {error}"
    return raw, offences, ""


def _check_path(path: Path, calls: Mapping[str, str], options: Options) -> _CheckRun:
    """Check (and fix, or diff) one file, given the imported functions' return types.

    Returns:
      What it found; a file that can't be read or parsed is an error.

    """
    name: Path = options.input.name(path)
    raw: str
    offences: list[Offence]
    error: str
    raw, offences, error = _read_checked(path, name, options.checks, calls)
    if error:
        return _CheckRun(error=error)
    baselined: int
    offences, baselined = options.filter.unbaselined(name, offences)
    results: list[Result] = options.filter.results(name, offences)
    unsafe: bool = options.unsafe_fixes
    fixing: list[Offence] = [r.offence for r in results if r.offence.fix and (unsafe or not r.offence.unsafe)]
    if options.mode is Mode.DIFF:
        return _CheckRun(text=_diff(raw, name, fixing))
    if options.mode is not Mode.FIX:
        return _CheckRun(results, baselined)
    left: list[Result] = [r for r in results if r.offence not in fixing]
    if path == STDIN:  # the fixed source goes to stdout
        return _CheckRun(left, baselined, len(fixing), _fixed(raw, name, fixing).text)
    return _CheckRun(left, baselined, fix_file(path, fixing))


def _baseline_path(path: Path, calls: Mapping[str, str], options: Options) -> _BaselineRun:
    """Check one file, unfiltered, for --write-baseline.

    Returns:
      Every offence found; a file that can't be read or parsed is an error.

    """
    name: Path = options.input.name(path)
    offences: list[Offence]
    error: str
    _, offences, error = _read_checked(path, name, options.checks, calls)
    return _BaselineRun(error=error) if error else _BaselineRun(found=offences)


def _cover_path(path: Path, _calls: Mapping[str, str], options: Options) -> _CoverageRun:
    """Count one file's typed first bindings.

    Returns:
      The counts; a file that can't be read or parsed is an error.

    """
    name: Path = options.input.name(path)
    try:
        return _CoverageRun(annotation_coverage(_source(_read(path), name)[0], options.checks))
    except (OSError, ValueError, SyntaxError) as error:
        return _CoverageRun(error=f"{name}: error: {error}")


def _check_all(options: Options) -> tuple[list[Path], list[_FileRun]]:
    """Check every file (`--jobs` at a time), in order.

    Returns:
      The names, and what each file found.

    """
    paths: list[Path] = list(python_files(options.input.paths, options.input.exclude))
    check: Callable[[Path, Mapping[str, str]], _FileRun]
    if options.mode is Mode.COVERAGE:
        check = partial(_cover_path, options=options)
    elif options.mode is Mode.WRITE_BASELINE:
        check = partial(_baseline_path, options=options)
    else:
        check = partial(_check_path, options=options)
    names: list[Path] = [options.input.name(path) for path in paths]
    # The functions each file imports from the others, for --fix (and its hints).
    modules: project.Index = project.Index({}, []) if options.mode is Mode.COVERAGE else project.index(paths)
    calls: list[dict[str, str]] = [project.calls(modules, path) for path in paths]
    if options.jobs == 1 or len(paths) <= 1:
        return names, list(itertools.starmap(check, zip(paths, calls, strict=True)))
    pool: ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=options.jobs) as pool:
        return names, list(pool.map(check, paths, calls))


def _report(options: Options, runs: Sequence[_FileRun], files: int) -> int:
    """Print the results (`runs` is check/fix/diff mode's: every other mode has its own printing).

    Returns:
      The exit status.

    """
    checked: Sequence[_CheckRun] = cast("Sequence[_CheckRun]", runs)
    results: list[Result] = [result for run in checked for result in run.results]
    output: Output = options.output
    text: bool = output.fmt is Format.TEXT
    line: str
    for line in statistics(results) if text and output.statistics else render(output.fmt, results):
        _ = sys.stdout.write(f"{line}\n")
    for line in fix_reasons(results) if text and output.show_fixes else ():
        _ = sys.stdout.write(f"{line}\n")
    errors: int = sum(r.offence.is_error(r.level) for r in results)
    if text and not output.quiet:
        parts: list[str] = [
            f"Found {errors} error(s) and {len(results) - errors} warning(s) in {files} file(s)",
        ]
        if options.mode is Mode.FIX:
            parts.append(f"fixed {sum(run.fixed for run in checked)}")
            guesses: int
            if guesses := sum(r.offence.fix is not None for r in results):
                parts.append(f"{guesses} more with --unsafe-fixes")
        if options.filter.baseline_file is not None:
            parts.append(f"{sum(run.baselined for run in checked)} baselined")
        _ = sys.stdout.write("; ".join(parts) + ".\n")
    return EXIT_FOUND if errors else EXIT_CLEAN


def _coverage(options: Options, paths: Sequence[Path], runs: Sequence[_FileRun]) -> int:
    """Print each file's and the total annotation coverage (`runs` is --coverage mode's).

    Returns:
      The exit status.

    """
    covered: Sequence[_CoverageRun] = cast("Sequence[_CoverageRun]", runs)
    counted: list[tuple[Path, Coverage]] = [
        (path, run.coverage) for path, run in zip(paths, covered, strict=True) if run.coverage is not None
    ]
    total: Coverage = Coverage(sum(c.typed for _, c in counted), sum(c.total for _, c in counted))
    if options.output.fmt is Format.JSON:
        report: dict[str, _Scalar | list[_Row]] = {
            "typed": total.typed,
            "total": total.total,
            "percent": round(total.percent, 1),
            "files": [
                {"path": str(path), "typed": c.typed, "total": c.total, "percent": round(c.percent, 1)}
                for path, c in counted
            ],
        }
        _ = sys.stdout.write(json.dumps(report, indent=2) + "\n")
    else:
        path: Path
        c: Coverage
        for path, c in counted:
            _ = sys.stdout.write(f"{path}: {c.typed}/{c.total} typed ({c.percent:.1f}%)\n")
        _ = sys.stdout.write(
            f"Total: {total.typed}/{total.total} typed ({total.percent:.1f}%) in {len(counted)} file(s).\n",
        )
    threshold: float | None = options.output.fail_under
    return EXIT_FOUND if threshold is not None and total.percent < threshold else EXIT_CLEAN


def _run(options: Options) -> int:
    """Check, fix, diff, count or baseline, printing what that finds.

    Returns:
      The exit status.

    """
    names: list[Path]
    runs: list[_FileRun]
    names, runs = _check_all(options)
    _ = sys.stderr.write("".join(f"{run.error}\n" for run in runs if run.error))
    failed: bool = any(run.error for run in runs)
    status: int
    if options.mode is Mode.WRITE_BASELINE and options.filter.baseline_file is not None:
        file: Path = options.filter.baseline_file
        baselined: Sequence[_BaselineRun] = cast("Sequence[_BaselineRun]", runs)
        found: dict[str, list[Offence]] = {
            baseline.key(n, file): run.found for n, run in zip(names, baselined, strict=True)
        }
        _ = sys.stdout.write(f"Wrote {baseline.write(file, found)} offence(s) to {file}.\n")
        status = EXIT_CLEAN
    elif options.mode is Mode.COVERAGE:
        status = _coverage(options, names, runs)
    elif options.mode is Mode.DIFF:
        checked: Sequence[_CheckRun] = cast("Sequence[_CheckRun]", runs)
        diffs: str = "".join(run.text for run in checked)
        _ = sys.stdout.write(diffs)
        status = EXIT_FOUND if diffs else EXIT_CLEAN
    elif options.mode is Mode.FIX and options.input.paths == [STDIN] and runs and not failed:
        fixed: _CheckRun = cast("_CheckRun", runs[0])
        _ = sys.stdout.write(fixed.text)  # standard input, fixed, is the whole output
        status = EXIT_FOUND if any(r.offence.is_error(r.level) for r in fixed.results) else EXIT_CLEAN
    else:
        status = _report(options, runs, len(names))
    return EXIT_ERROR if failed else status


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command.

    Returns:
      Its exit status.

    """
    options: Options = Options.parse(argv)
    file: Path | None = options.output.output_file
    stream: TextIO
    with (
        file.open("w", encoding="utf-8", newline="\n")
        if file
        else contextlib.nullcontext(sys.stdout) as stream,
        contextlib.redirect_stdout(stream),
    ):
        status: int = _run(options)
    return EXIT_CLEAN if options.output.exit_zero and status == EXIT_FOUND else status
