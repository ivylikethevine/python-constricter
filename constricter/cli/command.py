# SPDX-License-Identifier: MIT
"""The `constricter` command (see README)."""

import codecs
import contextlib
import difflib
import io
import itertools
import json
import sys
import tokenize
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace
from functools import partial
from pathlib import Path
from typing import Final, NamedTuple, TextIO, TypeAlias, cast

from constricter import notebook
from constricter.cli import baseline, hints
from constricter.cli.options import Mode, Options, Output
from constricter.cli.paths import STDIN, python_files
from constricter.cli.report import Format, Result, fix_reasons, render, statistics
from constricter.fix import fixes, project
from constricter.fix.known import Hints, Outside
from constricter.noqa import lines, unsuppressed
from constricter.offences import (
    DEFAULT_CHECKS,
    Checks,
    Edit,
    Offence,
)
from constricter.rules.checker import Coverage, annotation_coverage, check_source

EXIT_CLEAN: Final = 0
EXIT_FOUND: Final = 1
EXIT_ERROR: Final = 2
_ALL: Final = 100  # percent


def _encoding(path: Path, data: bytes) -> str:
    """Find the encoding of `path`, whose bytes are `data`: a notebook's is UTF-8 (it's JSON).

    Returns:
      A module's, as Python finds it: a PEP 263 declaration (`# -*- coding: latin-1 -*-`), a BOM
      (`utf-8-sig`), or UTF-8. Raises `SyntaxError` for an unknown or contradictory one.

    """
    return (
        "utf-8" if path.suffix == notebook.SUFFIX else tokenize.detect_encoding(io.BytesIO(data).readline)[0]
    )


def _read(path: Path) -> str:
    """Read `path`, in its encoding; `-` is standard input.

    Returns:
      Its text.

    """
    if path == STDIN:
        return sys.stdin.read()
    data: bytes = path.read_bytes()
    return data.decode(_encoding(path, data))


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
    outside: Outside | None = None,
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
        check_source(source, str(name), checks, outside=outside),
        lines(source),
    )
    return [_placed(o, where) for o in offences] if where else offences


def _placed(offence: Offence, where: list[notebook.Line]) -> Offence:
    """Place an offence from a notebook's joined module in its cell, its declaration's line too.

    Returns:
      The offence, its `line` (and a `Edit.DECLARE` fix's statement line) counted in its `cell`; a
      fix that would add an import isn't offered.

    """
    line: notebook.Line = where[offence.line - 1]
    placed: Offence = replace(offence, line=line.line, cell=line.cell)
    if offence.edit is not None and offence.edit.imports:  # a notebook's cells have no import block
        return replace(placed, edit=None)
    if offence.edit is not None and offence.edit.edit is Edit.DECLARE:
        statement: int = where[offence.edit.span[0] - 1].line
        placed = replace(placed, edit=offence.edit._replace(span=(statement, offence.edit.span[1])))
    return placed


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
    """Add each fixable offence's annotation to `path` (a notebook's, in its cells), in its encoding.

    Raises `UnicodeEncodeError`, leaving the file as it was, when an annotation can't be written in
    the file's encoding (a PEP 263 declaration's).

    Returns:
      How many offences were fixed.

    """
    count: int
    if not (count := sum(1 for o in offences if o.edit is not None)):
        return 0
    data: bytes = path.read_bytes()
    encoding: str = _encoding(path, data)
    _ = path.write_bytes(_fixed(data.decode(encoding), path, offences).text.encode(encoding))
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
HINT_ROUNDS: Final = 4  # with `--fix --infer-with`: how many times each file is fixed, at most


def _shown_lines(raw: str, name: Path) -> dict[tuple[int | None, int], str]:
    """Map each line of `raw` (a notebook's, in its cells) to its text, as offences are placed.

    Returns:
      Each line's text, by its cell (`None` outside a notebook) and line number.

    """
    source: str
    where: list[notebook.Line]
    source, where = _source(raw, name)
    return {
        (where[index].cell if where else None, where[index].line if where else index + 1): text
        for index, text in enumerate(source.splitlines())
    }


def _checked(path: Path, name: Path, checks: Checks, outside: Outside) -> tuple[str, list[Offence]]:
    """Read `path` and check it as `name`; raises what reading or parsing it does.

    Returns:
      Its text, and its offences.

    """
    raw: str = _read(path)
    return raw, check_text(raw, name, checks, outside=outside)


def _read_checked(
    path: Path,
    name: Path,
    checks: Checks,
    outside: Outside,
) -> tuple[str, list[Offence], str]:
    """Read and check `path`, turning a read or parse error into a message instead of raising.

    Returns:
      Its text and offences (empty on error), and the error message (empty on success).

    """
    raw: str
    offences: list[Offence]
    try:
        raw, offences = _checked(path, name, checks, outside)
    except (OSError, ValueError, SyntaxError) as error:  # UnicodeDecodeError is a ValueError
        return "", [], f"{name}: error: {error}"
    return raw, offences, ""


def _results(raw: str, name: Path, offences: Sequence[Offence], options: Options) -> list[Result]:
    """Turn the offences in `raw`, the text of `name`, into the results to report.

    Returns:
      Each one the options don't filter out, with its source line and its fix as a text edit.

    """
    shown: dict[tuple[int | None, int], str] = _shown_lines(raw, name)
    # A notebook's cells have no file lines for an edit to point at.
    text: list[str] = [] if name.suffix == notebook.SUFFIX else lines(raw)
    return [
        r._replace(
            source=shown.get((r.offence.cell, r.offence.line), ""),
            replacements=fixes.replacements(text, r.offence) if text else (),
        )
        for r in options.filter.results(name, offences)
    ]


def _check_path(path: Path, outside: Outside, options: Options) -> _CheckRun:
    """Check (and fix, or diff) one file, given what's known of it from outside it.

    Returns:
      What it found; a file that can't be read or parsed is an error.

    """
    name: Path = options.input.name(path)
    raw: str
    offences: list[Offence]
    error: str
    raw, offences, error = _read_checked(path, name, options.checks, outside)
    if error:
        return _CheckRun(error=error)
    baselined: int
    offences, baselined = options.filter.unbaselined(name, offences)
    results: list[Result] = _results(raw, name, offences, options)
    unsafe: bool = options.unsafe_fixes
    fixing: list[Offence] = [
        r.offence for r in results if r.offence.edit is not None and (unsafe or not r.offence.unsafe)
    ]
    if options.mode is Mode.DIFF:
        return _CheckRun(text=_diff(raw, name, fixing))
    if options.mode is not Mode.FIX:
        return _CheckRun(results, baselined)
    left: list[Result] = [r for r in results if r.offence not in fixing]
    if path == STDIN:  # the fixed source goes to stdout
        return _CheckRun(left, baselined, len(fixing), _fixed(raw, name, fixing).text)
    try:
        return _CheckRun(left, baselined, fix_file(path, fixing))
    except UnicodeEncodeError as failure:  # the file is left as it was, its offences unfixed
        # Its canonical name: PyPy reports `latin1` where CPython says `latin-1`.
        encoding: str = codecs.lookup(failure.encoding).name
        message: str = f"an annotation can't be written in its encoding, {encoding}; left as it was"
        return _CheckRun(results, baselined, error=f"{name}: error: {message}")


def _baseline_path(path: Path, outside: Outside, options: Options) -> _BaselineRun:
    """Check one file, unfiltered, for --write-baseline.

    Returns:
      Every offence found; a file that can't be read or parsed is an error.

    """
    name: Path = options.input.name(path)
    offences: list[Offence]
    error: str
    _, offences, error = _read_checked(path, name, options.checks, outside)
    return _BaselineRun(error=error) if error else _BaselineRun(found=offences)


def _cover_path(path: Path, _outside: Outside, options: Options) -> _CoverageRun:
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

    With `--infer-with`, the type checker's server runs throughout: it's asked for every file's
    hints first, and with `--fix`, each file a round changed is asked again and checked again, as its
    new annotations change what the checker infers, until a round changes nothing (at most
    `HINT_ROUNDS`). A baseline records offences, and coverage counts annotations: hints change
    neither, only what `--fix` offers.

    Returns:
      The names, and what each file found.

    """
    paths: list[Path] = list(python_files(options.input.paths, options.input.exclude))
    check: Callable[[Path, Outside], _FileRun]
    if options.mode is Mode.COVERAGE:
        check = partial(_cover_path, options=options)
    elif options.mode is Mode.WRITE_BASELINE:
        check = partial(_baseline_path, options=options)
    else:
        check = partial(_check_path, options=options)
    names: list[Path] = [options.input.name(path) for path in paths]
    if not options.infer_with or options.mode in {Mode.COVERAGE, Mode.WRITE_BASELINE}:
        return names, _checked_all(paths, check, options)[0]
    session: hints.Session
    with hints.Session(options.infer_with, Path.cwd(), options.jobs, options.infer_memory) as session:
        runs: list[_FileRun]
        modules: project.Index
        runs, modules = _checked_all(paths, check, options, session)
        # The files the last round changed: only their hints can have changed.
        again: list[int] = [
            index
            for index, run in enumerate(runs)
            if options.mode is Mode.FIX and isinstance(run, _CheckRun) and run.fixed and paths[index] != STDIN
        ]
        for _ in range(HINT_ROUNDS - 1):
            if not again:
                break
            redone: list[_FileRun] = _checked_all(
                [paths[i] for i in again],
                check,
                options,
                session,
                modules,
            )[0]
            index: int
            run: _FileRun
            for index, run in zip(again, redone, strict=True):
                runs[index] = _merged(cast("_CheckRun", runs[index]), cast("_CheckRun", run))
            again = [index for index, run in zip(again, redone, strict=True) if cast("_CheckRun", run).fixed]
    return names, runs


def _checked_all(
    paths: Sequence[Path],
    check: Callable[[Path, Outside], _FileRun],
    options: Options,
    session: hints.Session | None = None,
    modules: project.Index | None = None,
) -> tuple[list[_FileRun], project.Index]:
    """Check `paths` (`--jobs` at a time), with the `session`'s hints, and `modules` (else indexed).

    Returns:
      What each file found, and the index of every file's module.

    """
    hinted: dict[Path, tuple[Hints, ...]] = {} if session is None else session.hints(_texts(paths))
    coverage: bool = options.mode is Mode.COVERAGE  # needs nothing from the other files
    if options.jobs == 1 or len(paths) <= 1:
        if modules is None:
            modules = project.Index({}, []) if coverage else project.index(paths)
        return list(
            itertools.starmap(check, zip(paths, _outside(modules, paths, hinted), strict=True)),
        ), modules
    pool: ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=options.jobs) as pool:
        if modules is None:
            # The index, as the checks, read one file per task.
            modules = (
                project.Index({}, []) if coverage else project.index(paths, partial(pool.map, chunksize=16))
            )
        return list(pool.map(check, paths, _outside(modules, paths, hinted))), modules


def _merged(before: _CheckRun, after: _CheckRun) -> _CheckRun:
    """Join a file's two `--fix` rounds: what's left is the later round's, what's fixed is both's.

    Returns:
      The joined run.

    """
    return replace(after, fixed=before.fixed + after.fixed)


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
            # UnicodeDecodeError is a ValueError; a bad encoding declaration, a SyntaxError.
            with contextlib.suppress(OSError, ValueError, SyntaxError):
                texts[path] = _read(path)
    return texts


def _outside(
    modules: project.Index,
    paths: Sequence[Path],
    hinted: Mapping[Path, tuple[Hints, ...]],
) -> list[Outside]:
    """Find what's known of each file from outside it: what it imports from the others, and its hints.

    Returns:
      Each file's, in order.

    """
    found: list[Outside] = []
    path: Path
    for path in paths:
        imported: project.Imported = project.imported(modules, path)
        found.append(Outside(imported.calls, imported.classes, hinted.get(path, ())))
    return found


def _report(options: Options, runs: Sequence[_FileRun], files: int) -> int:
    """Print the results (`runs` is check/fix/diff mode's: every other mode has its own printing).

    Returns:
      The exit status.

    """
    checked: Sequence[_CheckRun] = cast("Sequence[_CheckRun]", runs)
    results: list[Result] = [result for run in checked for result in run.results]
    output: Output = options.output
    text: bool = output.fmt in {Format.TEXT, Format.FULL}
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
            if guesses := sum(r.offence.unsafe for r in results):
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
    try:
        names, runs = _check_all(options)
    except hints.HintError as error:
        _ = sys.stderr.write(f"constricter: error: {error}\n")
        return EXIT_ERROR
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
