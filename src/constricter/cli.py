# SPDX-License-Identifier: MIT
"""The `constricter` command (see README)."""

import argparse
import contextlib
import difflib
import itertools
import json
import os
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field, replace
from enum import Enum
from fnmatch import fnmatch
from functools import partial
from pathlib import Path
from typing import Final, TextIO, cast

from constricter import __version__, baseline, fixes, notebook, project
from constricter.checker import (
    DEFAULT_CHECKS,
    LEVELS,
    MESSAGES,
    NESTING,
    Checks,
    Coverage,
    Level,
    Offence,
    annotation_coverage,
    check_source,
)
from constricter.config import DEFAULT_BASELINE, config_defaults, project_root, unknown_codes
from constricter.explain import explain
from constricter.noqa import lines, unsuppressed
from constricter.report import Format, Result, render, statistics

_SKIPPED_DIRS: frozenset[str] = frozenset(
    {"__pycache__", "node_modules", "venv", "site-packages", "build", "dist"},
)
EXIT_CLEAN: Final = 0
EXIT_FOUND: Final = 1
EXIT_ERROR: Final = 2
_ALL: Final = 100  # percent


def _excluded(path: Path, patterns: Sequence[str]) -> bool:
    text: str = path.as_posix()
    return any(fnmatch(text, p) or fnmatch(path.name, p) for p in patterns)


def python_files(paths: Sequence[Path], exclude: Sequence[str] = ()) -> Iterator[Path]:
    """Find the files to check.

    Yields:
      Each file given, and each `*.py` under each directory given.

    """
    path: Path
    found: Path
    for path in paths:
        if not path.is_dir():
            if not _excluded(path, exclude):
                yield path
            continue
        for found in sorted([*path.rglob("*.py"), *path.rglob(f"*{notebook.SUFFIX}")]):
            parts: tuple[str, ...] = found.relative_to(path).parts[:-1]
            if any(p.startswith(".") or p in _SKIPPED_DIRS for p in parts):
                continue
            if not _excluded(found, exclude):
                yield found


STDIN: Final = Path("-")


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


def _fixed(
    raw: str,
    name: Path,
    offences: Sequence[Offence],
) -> tuple[str, list[tuple[str, list[str], list[str]]]]:
    """Add each fixable offence's annotation to `raw`, the text of `name`.

    Returns:
      The new text, and each changed part (the file, or a notebook's cell): its label and old and
      new lines.

    """
    if name.suffix == notebook.SUFFIX:
        text: str
        cells: list[notebook.Cell]
        text, cells = notebook.fix(raw, offences)
        return text, [(f"{name}:cell {c.number}", c.old, c.new) for c in cells]
    old: list[str] = lines(raw)
    new: list[str] = fixes.apply(old, offences)
    return "".join(new), [(str(name), old, new)] if new != old else []


def _diff(raw: str, name: Path, offences: Sequence[Offence]) -> str:
    return "".join(
        "".join(difflib.unified_diff(old, new, label, label))
        for label, old, new in _fixed(raw, name, offences)[1]
    )


def fix_file(path: Path, offences: Sequence[Offence]) -> int:
    """Add each fixable offence's annotation to `path` (a notebook's, in its cells).

    Returns:
      How many offences were fixed.

    """
    count: int
    if not (count := sum(1 for o in offences if o.fix)):
        return 0
    _ = path.write_bytes(_fixed(_read(path), path, offences)[0].encode())
    return count


def _at_least(minimum: int) -> Callable[[str], int]:
    """Make a reader of whole numbers, for `--nesting` and `--jobs`.

    Returns:
      A reader that rejects numbers below `minimum`.

    """

    def read(text: str) -> int:
        """Read `text`.

        Returns:
          The whole number `text` is.

        Raises:
          argparse.ArgumentTypeError: It isn't one.

        """
        if not text.isdigit() or int(text) < minimum:
            message: str = f"expected a whole number of at least {minimum}, not {text!r}"
            raise argparse.ArgumentTypeError(message)
        return int(text)

    return read


def _percent(text: str) -> float:
    """Read a percentage, 0 to 100.

    Returns:
      The percentage.

    Raises:
      argparse.ArgumentTypeError: `text` isn't one.

    """
    value: float
    try:
        value = float(text)
    except ValueError:
        value = -1.0
    if not 0 <= value <= _ALL:
        message: str = f"expected a percentage from 0 to 100, not {text!r}"
        raise argparse.ArgumentTypeError(message)
    return value


def _codes(text: str) -> list[str]:
    """Read a comma-separated list of codes or code prefixes (`LVA001,LVA00`).

    Returns:
      The codes, upper-cased.

    Raises:
      argparse.ArgumentTypeError: One matches no code.

    """
    codes: list[str] = [code.strip().upper() for code in text.split(",") if code.strip()]
    unknown: list[str]
    if unknown := unknown_codes(codes):
        message: str = f"no code starts with {', '.join(unknown)}"
        raise argparse.ArgumentTypeError(message)
    return codes


def _parser() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="constricter",
        description="Report local variables that aren't typed where they're first bound.",
    )
    _ = parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="files and directories (default: .); `-` reads standard input",
    )
    _ = parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="skip paths matching this glob (repeatable), e.g. 'tests/fixtures/*'",
    )
    _ = parser.add_argument(
        "--level",
        choices=LEVELS,
        default="strict",
        help="which codes are errors rather than warnings (default: strict)",
    )
    _ = parser.add_argument(
        "--format",
        type=Format,
        choices=list(Format),
        default=Format.TEXT,
        help="output format (default: text)",
    )
    _ = parser.add_argument(
        "--type-comments",
        action="store_true",
        help="count `x = 1  # type: int` as annotated",
    )
    _ = parser.add_argument(
        "--all-scopes",
        action="store_true",
        help="also check module and class bodies (LVA004)",
    )
    _ = parser.add_argument(
        "--nesting",
        type=_at_least(1),
        default=NESTING,
        metavar="N",
        help=f"report an annotation nested N deep (LVA006; default: {NESTING})",
    )
    _ = parser.add_argument(
        "--select",
        type=_codes,
        default=[],
        metavar="CODES",
        help="report only these codes or prefixes (LVA001,LVA00)",
    )
    _ = parser.add_argument(
        "--ignore",
        type=_codes,
        default=[],
        metavar="CODES",
        help="don't report these codes or prefixes",
    )
    _ = parser.add_argument(
        "--fix",
        action="store_true",
        help="add the annotations a value makes unambiguous, in place",
    )
    _ = parser.add_argument(
        "--unsafe-fixes",
        action="store_true",
        help="with --fix or --diff: also apply guesses (a call to a class that may be generic)",
    )
    _ = parser.add_argument(
        "--diff",
        action="store_true",
        help="print what --fix would change, and change nothing",
    )
    _ = parser.add_argument(
        "--statistics",
        action="store_true",
        help="print counts per code instead of each offence (text)",
    )
    _ = parser.add_argument(
        "--coverage",
        action="store_true",
        help="print the share of first bindings that are typed, per file",
    )
    _ = parser.add_argument(
        "--fail-under",
        type=_percent,
        metavar="PCT",
        help="with --coverage (which it implies): exit 1 if the typed share is below PCT",
    )
    _ = parser.add_argument(
        "--baseline",
        type=Path,
        metavar="FILE",
        help="don't report the offences recorded in this baseline file",
    )
    _ = parser.add_argument(
        "--write-baseline",
        action="store_true",
        help=f"record every offence found in the baseline file (default: {DEFAULT_BASELINE}), and exit",
    )
    _ = parser.add_argument(
        "--explain",
        choices=list(MESSAGES),
        metavar="CODE",
        help="explain a code and exit",
    )
    _ = parser.add_argument(
        "--jobs",
        "-j",
        type=_at_least(0),
        default=1,
        metavar="N",
        help="check N files at a time (0: one per CPU; default: 1)",
    )
    _ = parser.add_argument(
        "--stdin-filename",
        type=Path,
        default=STDIN,
        metavar="PATH",
        help="with `-` as the path: the name to report standard input under (a `.ipynb` is a notebook)",
    )
    _ = parser.add_argument("--exit-zero", action="store_true", help="exit 0 even when offences are errors")
    _ = parser.add_argument(
        "--output-file",
        type=Path,
        metavar="FILE",
        help="write the report to FILE, not stdout",
    )
    _ = parser.add_argument("--quiet", "-q", action="store_true", help="don't print the text summary line")
    _ = parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


class _Mode(Enum):
    """What to do with what's found."""

    CHECK = "check"
    FIX = "fix"
    DIFF = "diff"
    WRITE_BASELINE = "write-baseline"
    COVERAGE = "coverage"


@dataclass(frozen=True)
class _Input:
    """What to check: paths (`-` is standard input, reported as `stdin_name`) and globs to skip."""

    paths: list[Path]
    exclude: list[str]
    stdin_name: Path = STDIN

    def name(self, path: Path) -> Path:
        """Name `path` for reports.

        Returns:
          The name it's reported, levelled and baselined under.

        """
        return self.stdin_name if path == STDIN else path


@dataclass(frozen=True)
class _Filter:
    """Which offences are reported, and at which level."""

    level: Level
    per_path: dict[str, str]
    select: list[str]
    ignore: list[str]
    per_file_ignores: dict[str, list[str]] = field(default_factory=dict[str, list[str]])
    baseline_file: Path | None = None
    entries: baseline.Entries = field(default_factory=dict[str, dict[str, int]])

    def unbaselined(self, path: Path, offences: list[Offence]) -> tuple[list[Offence], int]:
        """Match `path`'s offences against the baseline.

        Returns:
          The offences it doesn't cover, and how many it does.

        """
        if self.baseline_file is None:
            return offences, 0
        return baseline.remaining(offences, self.entries.get(baseline.key(path, self.baseline_file), {}))

    def level_for(self, path: Path) -> Level:
        """Decide `path`'s level.

        Returns:
          The level of the first `per-path-levels` glob it matches, else `--level`'s.

        """
        glob: str
        level: str
        for glob, level in self.per_path.items():
            if _excluded(path, [glob]):
                return LEVELS[level]
        return self.level

    def results(self, path: Path, offences: Sequence[Offence]) -> list[Result]:
        """Filter `path`'s offences.

        Returns:
          Those reported at its level.

        """
        level: Level = self.level_for(path)
        ignored: tuple[str, ...] = (
            *self.ignore,
            *(
                code
                for glob, codes in self.per_file_ignores.items()
                if _excluded(path, [glob])
                for code in codes
            ),
        )
        return [
            Result(path, o, level)
            for o in offences
            if o.is_reported(level)
            and (not self.select or o.code.startswith(tuple(self.select)))
            and not o.code.startswith(ignored)
        ]


@dataclass(frozen=True)
class _Output:
    """How the report looks, where it goes, and how the command exits."""

    fmt: Format
    statistics: bool
    quiet: bool
    fail_under: float | None = None  # --coverage's threshold
    exit_zero: bool = False
    output_file: Path | None = None


@dataclass(frozen=True)
class _Options:
    """The command's parsed options."""

    input: _Input
    checks: Checks
    unsafe_fixes: bool
    filter: _Filter
    output: _Output
    mode: _Mode
    jobs: int

    @classmethod
    def parse(cls, argv: Sequence[str] | None) -> "_Options":
        """Parse `argv` over the defaults `pyproject.toml` sets; `--explain` prints and exits.

        Returns:
          The options.

        """
        parser: argparse.ArgumentParser = _parser()
        try:
            parser.set_defaults(**config_defaults(Path.cwd()))
        except ValueError as error:
            parser.error(str(error))
        args: argparse.Namespace = parser.parse_args(argv)
        code: str | None
        if (code := cast("str | None", args.explain)) is not None:
            _ = sys.stdout.write(explain(code))
            parser.exit()
        paths: list[Path] = cast("list[Path]", args.paths) or [Path()]
        if STDIN in paths and len(paths) > 1:
            parser.error("`-` (standard input) must be the only path")
        mode: _Mode = _mode(parser, args)
        return cls(
            input=_Input(paths, cast("list[str]", args.exclude), cast("Path", args.stdin_filename)),
            checks=Checks(
                type_comments=cast("bool", args.type_comments),
                all_scopes=cast("bool", args.all_scopes),
                nesting=cast("int", args.nesting),
            ),
            unsafe_fixes=cast("bool", args.unsafe_fixes),
            filter=_filter(parser, args, mode),
            output=_Output(
                fmt=cast("Format", args.format),
                statistics=cast("bool", args.statistics),
                quiet=cast("bool", args.quiet),
                fail_under=cast("float | None", args.fail_under),
                exit_zero=cast("bool", args.exit_zero),
                output_file=cast("Path | None", args.output_file),
            ),
            mode=mode,
            # Standard input can only be read once, in this process.
            jobs=1 if paths == [STDIN] else cast("int", args.jobs) or os.cpu_count() or 1,
        )


def _filter(parser: argparse.ArgumentParser, args: argparse.Namespace, mode: _Mode) -> _Filter:
    """Build the filter the options set, reading the baseline (the default one, if it exists).

    Returns:
      The filter.

    """
    default: Path = project_root(Path.cwd()) / DEFAULT_BASELINE
    baseline_path: Path | None = cast("Path | None", args.baseline) or (
        default if mode is _Mode.WRITE_BASELINE or default.is_file() else None
    )
    entries: baseline.Entries = {}
    if baseline_path is not None and mode is not _Mode.WRITE_BASELINE:
        try:
            entries = baseline.read(baseline_path)
        except ValueError as error:
            parser.error(str(error))
    return _Filter(
        level=LEVELS[cast("str", args.level)],
        per_path=cast("dict[str, str]", getattr(args, "per_path_levels", {})),
        select=[c.upper() for c in cast("list[str]", args.select)],
        ignore=[c.upper() for c in cast("list[str]", args.ignore)],
        per_file_ignores=cast("dict[str, list[str]]", getattr(args, "per_file_ignores", {})),
        baseline_file=baseline_path,
        entries=entries,
    )


def _mode(parser: argparse.ArgumentParser, args: argparse.Namespace) -> _Mode:
    """Decide the mode; more than one of `--fix`, `--diff` and `--write-baseline` is an error.

    Returns:
      What the options ask for.

    """
    modes: list[_Mode] = [
        mode
        for mode, chosen in (
            (_Mode.FIX, cast("bool", args.fix)),
            (_Mode.DIFF, cast("bool", args.diff)),
            (_Mode.WRITE_BASELINE, cast("bool", args.write_baseline)),
            (
                _Mode.COVERAGE,
                cast("bool", args.coverage) or cast("float | None", args.fail_under) is not None,
            ),
        )
        if chosen
    ]
    if len(modes) > 1:
        parser.error("--fix, --diff, --write-baseline and --coverage can't be combined")
    return modes[0] if modes else _Mode.CHECK


@dataclass(frozen=True)
class _FileRun:
    """What checking one file found (and fixed, or would fix)."""

    results: list[Result] = field(default_factory=list[Result])
    fixed: int = 0
    text: str = ""  # --diff's diff, or standard input's fixed source
    error: str = ""
    baselined: int = 0
    found: list[Offence] = field(default_factory=list[Offence])  # every offence, for --write-baseline
    coverage: Coverage | None = None


def _checked(path: Path, name: Path, checks: Checks, calls: Mapping[str, str]) -> tuple[str, list[Offence]]:
    """Read `path` and check it as `name`; raises what reading or parsing it does.

    Returns:
      Its text, and its offences.

    """
    raw: str = _read(path)
    return raw, check_text(raw, name, checks, calls=calls)


def _check_path(path: Path, calls: Mapping[str, str], options: _Options) -> _FileRun:
    """Check (and fix, or diff) one file, given the imported functions' return types.

    Returns:
      What it found; a file that can't be read or parsed is an error.

    """
    name: Path = options.input.name(path)
    raw: str
    offences: list[Offence]
    try:
        raw, offences = _checked(path, name, options.checks, calls)
    except (OSError, ValueError, SyntaxError) as error:  # UnicodeDecodeError is a ValueError
        return _FileRun(error=f"{name}: error: {error}")
    if options.mode is _Mode.WRITE_BASELINE:
        return _FileRun(found=offences)
    baselined: int
    offences, baselined = options.filter.unbaselined(name, offences)
    results: list[Result] = options.filter.results(name, offences)
    unsafe: bool = options.unsafe_fixes
    fixing: list[Offence] = [r.offence for r in results if r.offence.fix and (unsafe or not r.offence.unsafe)]
    if options.mode is _Mode.DIFF:
        return _FileRun(text=_diff(raw, name, fixing))
    if options.mode is not _Mode.FIX:
        return _FileRun(results, baselined=baselined)
    left: list[Result] = [r for r in results if r.offence not in fixing]
    if path == STDIN:  # the fixed source goes to stdout
        return _FileRun(left, len(fixing), _fixed(raw, name, fixing)[0], baselined=baselined)
    return _FileRun(left, fix_file(path, fixing), baselined=baselined)


def _cover_path(path: Path, _calls: Mapping[str, str], options: _Options) -> _FileRun:
    """Count one file's typed first bindings.

    Returns:
      The counts; a file that can't be read or parsed is an error.

    """
    name: Path = options.input.name(path)
    try:
        return _FileRun(coverage=annotation_coverage(_source(_read(path), name)[0], options.checks))
    except (OSError, ValueError, SyntaxError) as error:
        return _FileRun(error=f"{name}: error: {error}")


def _check_all(options: _Options) -> tuple[list[Path], list[_FileRun]]:
    """Check every file (`--jobs` at a time), in order.

    Returns:
      The names, and what each file found.

    """
    paths: list[Path] = list(python_files(options.input.paths, options.input.exclude))
    check: Callable[[Path, Mapping[str, str]], _FileRun] = partial(
        _cover_path if options.mode is _Mode.COVERAGE else _check_path,
        options=options,
    )
    names: list[Path] = [options.input.name(path) for path in paths]
    # The functions each file imports from the others, for --fix (and its hints).
    modules: dict[str, project.Module] = {} if options.mode is _Mode.COVERAGE else project.index(paths)
    calls: list[dict[str, str]] = [project.calls(modules, path) for path in paths]
    if options.jobs == 1 or len(paths) <= 1:
        return names, list(itertools.starmap(check, zip(paths, calls, strict=True)))
    pool: ProcessPoolExecutor
    with ProcessPoolExecutor(max_workers=options.jobs) as pool:
        return names, list(pool.map(check, paths, calls))


def _report(options: _Options, runs: Sequence[_FileRun], files: int) -> int:
    """Print the results.

    Returns:
      The exit status.

    """
    results: list[Result] = [result for run in runs for result in run.results]
    output: _Output = options.output
    text: bool = output.fmt is Format.TEXT
    line: str
    for line in statistics(results) if text and output.statistics else render(output.fmt, results):
        _ = sys.stdout.write(f"{line}\n")
    errors: int = sum(r.offence.is_error(r.level) for r in results)
    if text and not output.quiet:
        parts: list[str] = [
            f"Found {errors} error(s) and {len(results) - errors} warning(s) in {files} file(s)",
        ]
        if options.mode is _Mode.FIX:
            parts.append(f"fixed {sum(run.fixed for run in runs)}")
            guesses: int
            if guesses := sum(r.offence.fix is not None for r in results):
                parts.append(f"{guesses} more with --unsafe-fixes")
        if options.filter.baseline_file is not None:
            parts.append(f"{sum(run.baselined for run in runs)} baselined")
        _ = sys.stdout.write("; ".join(parts) + ".\n")
    return EXIT_FOUND if errors else EXIT_CLEAN


def _coverage(options: _Options, paths: Sequence[Path], runs: Sequence[_FileRun]) -> int:
    """Print each file's and the total annotation coverage.

    Returns:
      The exit status.

    """
    counted: list[tuple[Path, Coverage]] = [
        (path, run.coverage) for path, run in zip(paths, runs, strict=True) if run.coverage is not None
    ]
    total: Coverage = Coverage(sum(c.typed for _, c in counted), sum(c.total for _, c in counted))
    if options.output.fmt is Format.JSON:
        report: dict[str, str | int | float | list[dict[str, str | int | float]]] = {
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


def _run(options: _Options) -> int:
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
    if options.mode is _Mode.WRITE_BASELINE and options.filter.baseline_file is not None:
        file: Path = options.filter.baseline_file
        found: dict[str, list[Offence]] = {
            baseline.key(n, file): run.found for n, run in zip(names, runs, strict=True)
        }
        _ = sys.stdout.write(f"Wrote {baseline.write(file, found)} offence(s) to {file}.\n")
        status = EXIT_CLEAN
    elif options.mode is _Mode.COVERAGE:
        status = _coverage(options, names, runs)
    elif options.mode is _Mode.DIFF:
        diffs: str = "".join(run.text for run in runs)
        _ = sys.stdout.write(diffs)
        status = EXIT_FOUND if diffs else EXIT_CLEAN
    elif options.mode is _Mode.FIX and options.input.paths == [STDIN] and runs and not failed:
        _ = sys.stdout.write(runs[0].text)  # standard input, fixed, is the whole output
        status = EXIT_FOUND if any(r.offence.is_error(r.level) for r in runs[0].results) else EXIT_CLEAN
    else:
        status = _report(options, runs, len(names))
    return EXIT_ERROR if failed else status


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command.

    Returns:
      Its exit status.

    """
    options: _Options = _Options.parse(argv)
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
