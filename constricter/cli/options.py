# SPDX-License-Identifier: MIT
"""The command's options: parsed from the command line over `[tool.constricter]`'s defaults."""

import argparse
import os
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Final, cast

from constricter import __version__
from constricter.cli import baseline
from constricter.cli.config import (
    DEFAULT_BASELINE,
    config_defaults,
    project_root,
    unknown_codes,
    unknown_fix_kinds,
)
from constricter.cli.explain import explain
from constricter.cli.paths import STDIN, excluded
from constricter.cli.protocol import SERVERS, runs
from constricter.cli.report import Format, Result
from constricter.offences import (
    LEVELS,
    MAX_LENGTH,
    MESSAGES,
    NESTING,
    OPT_IN,
    Checks,
    FixPolicy,
    Level,
    Offence,
)

_ALL: Final = 100  # percent


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


def _fix_kinds(text: str) -> list[str]:
    """Read a comma-separated list of `--fix` mechanisms (`copy,constructor`).

    Returns:
      Them.

    Raises:
      argparse.ArgumentTypeError: One isn't a mechanism's id.

    """
    kinds: list[str] = [kind.strip() for kind in text.split(",") if kind.strip()]
    unknown: list[str]
    if unknown := unknown_fix_kinds(kinds):
        message: str = f"no --fix mechanism is called {', '.join(unknown)} (see docs/FIXES.md)"
        raise argparse.ArgumentTypeError(message)
    return kinds


def _gigabytes(text: str) -> float:
    """Read `--infer-memory`: a positive number of gigabytes (GiB).

    Returns:
      It.

    Raises:
      ArgumentTypeError: It isn't one.

    """
    try:
        value: float = float(text)
    except ValueError:
        value = 0.0
    if not value > 0:
        message: str = f"expected a positive number of gigabytes, got {text!r}"
        raise argparse.ArgumentTypeError(message)
    return value


def _bytes(gigabytes: float | None) -> int | None:
    """Turn gigabytes (GiB) into bytes.

    Returns:
      Them, or `None` for none.

    """
    return None if gigabytes is None else int(gigabytes * (1 << 30))


def _checkers(text: str) -> list[str]:
    """Read `--infer-with`'s checkers: comma-separated, each once, in the order they're preferred.

    Returns:
      Them.

    Raises:
      ArgumentTypeError: One isn't a checker it knows.

    """
    checkers: list[str] = [checker.strip() for checker in text.split(",") if checker.strip()]
    unknown: list[str]
    if unknown := [checker for checker in checkers if checker not in SERVERS]:
        message: str = f"unknown checker {', '.join(unknown)} (known: {', '.join(sorted(SERVERS))})"
        raise argparse.ArgumentTypeError(message)
    return list(dict.fromkeys(checkers))


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
        help="skip a path, file or directory matching this glob (repeatable), e.g. 'tests/fixtures/*'",
    )
    _ = parser.add_argument(
        "--level",
        choices=LEVELS,
        default="strict",
        help="which codes are errors rather than warnings (default: strict)",
    )
    _ = parser.add_argument(
        "--max",
        action="store_true",
        help="the strictest check: suffocate everywhere, all scopes, the opt-in codes (command line only)",
    )
    _ = parser.add_argument(
        "--max-fix",
        action="store_true",
        help="--max, --fix --unsafe-fixes, and every installed checker's hints (command line only)",
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
        "--max-length",
        type=_at_least(1),
        default=MAX_LENGTH,
        metavar="N",
        help=f"report a fixed-length tuple annotation of more than N types (LVA011; default: {MAX_LENGTH})",
    )
    _ = parser.add_argument(
        "--select",
        type=_codes,
        default=[],
        metavar="CODES",
        help="report only these codes or prefixes (LVA001,LVA00)",
    )
    _ = parser.add_argument(
        "--extend-select",
        type=_codes,
        default=[],
        metavar="CODES",
        help="also report these codes (an opt-in one, like LVA012, by its full code)",
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
        "--fix-select",
        type=_fix_kinds,
        default=[],
        metavar="KINDS",
        help="offer only fixes these mechanisms decide (literal,copy,...; default: all)",
    )
    _ = parser.add_argument(
        "--fix-ignore",
        type=_fix_kinds,
        default=[],
        metavar="KINDS",
        help="never offer a fix one of these mechanisms decided",
    )
    _ = parser.add_argument(
        "--unsafe-fix-select",
        type=_fix_kinds,
        default=[],
        metavar="KINDS",
        help="treat guesses from these mechanisms (constructor, narrow) as certain",
    )
    _ = parser.add_argument(
        "--infer-with",
        type=_checkers,
        default=[],
        metavar="CHECKERS",
        help="type what --fix can't with these type checkers' inferred types, as guesses (basedpyright,ty)",
    )
    _ = parser.add_argument(
        "--infer-memory",
        type=_gigabytes,
        metavar="GB",
        help="with --infer-with: the most memory each checker's servers use together (default: 8)",
    )
    _ = parser.add_argument(
        "--diff",
        action="store_true",
        help="print what --fix would change, and change nothing",
    )
    _ = parser.add_argument(
        "--show-fixes",
        action="store_true",
        help="after the report, list each fix and how the value decided it (text)",
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


class Mode(Enum):
    """What to do with what's found."""

    CHECK = "check"
    FIX = "fix"
    DIFF = "diff"
    WRITE_BASELINE = "write-baseline"
    COVERAGE = "coverage"


@dataclass(frozen=True)
class Input:
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
class Filter:
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
        text: str = path.as_posix()
        glob: str
        level: str
        for glob, level in self.per_path.items():
            if excluded(path, [glob], text):
                return LEVELS[level]
        return self.level

    def results(self, path: Path, offences: Sequence[Offence]) -> list[Result]:
        """Filter `path`'s offences.

        Returns:
          Those reported at its level.

        """
        level: Level = self.level_for(path)
        text: str = path.as_posix()
        ignored: tuple[str, ...] = (
            *self.ignore,
            *(
                code
                for glob, codes in self.per_file_ignores.items()
                if excluded(path, [glob], text)
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
class Output:
    """How the report looks, where it goes, and how the command exits."""

    fmt: Format
    statistics: bool
    quiet: bool
    show_fixes: bool = False
    fail_under: float | None = None  # --coverage's threshold
    exit_zero: bool = False
    output_file: Path | None = None


@dataclass(frozen=True)
class Options:
    """The command's parsed options."""

    input: Input
    checks: Checks
    unsafe_fixes: bool
    filter: Filter
    output: Output
    mode: Mode
    jobs: int
    infer_with: tuple[str, ...] = ()  # the type checkers whose inferred types `--fix` guesses with
    infer_memory: int | None = None  # bytes each checker's servers may use together (`--infer-memory`)

    @classmethod
    def parse(cls, argv: Sequence[str] | None) -> "Options":
        """Parse `argv` over the defaults `pyproject.toml` sets; `--explain` prints and exits.

        Returns:
          The options.

        """
        parser: argparse.ArgumentParser = _parser()
        try:
            parser.set_defaults(**config_defaults(Path.cwd()))
        except ValueError as error:
            parser.error(str(error))
        args: argparse.Namespace = _maximal(parser.parse_args(argv))
        code: str | None
        if (code := cast("str | None", args.explain)) is not None:
            _ = sys.stdout.write(explain(code))
            parser.exit()
        paths: list[Path] = cast("list[Path]", args.paths) or [Path()]
        if STDIN in paths and len(paths) > 1:
            parser.error("`-` (standard input) must be the only path")
        mode: Mode = _mode(parser, args)
        return cls(
            input=Input(paths, cast("list[str]", args.exclude), cast("Path", args.stdin_filename)),
            checks=Checks(
                type_comments=cast("bool", args.type_comments),
                all_scopes=cast("bool", args.all_scopes),
                nesting=cast("int", args.nesting),
                max_length=cast("int", args.max_length),
                narrower=tuple(
                    (name, tuple(wider))
                    for name, wider in cast("dict[str, list[str]]", getattr(args, "narrower", {})).items()
                ),
                final=bool(OPT_IN & {*_select(args), *cast("list[str]", args.extend_select)}),
                fixes=FixPolicy(
                    frozenset(cast("list[str]", args.fix_select)),
                    frozenset(cast("list[str]", args.fix_ignore)),
                    frozenset(cast("list[str]", args.unsafe_fix_select)),
                ),
            ),
            unsafe_fixes=cast("bool", args.unsafe_fixes),
            filter=_filter(parser, args, mode),
            output=Output(
                fmt=cast("Format", args.format),
                statistics=cast("bool", args.statistics),
                quiet=cast("bool", args.quiet),
                show_fixes=cast("bool", args.show_fixes),
                fail_under=cast("float | None", args.fail_under),
                exit_zero=cast("bool", args.exit_zero),
                output_file=cast("Path | None", args.output_file),
            ),
            mode=mode,
            # Standard input can only be read once, in this process.
            jobs=1 if paths == [STDIN] else cast("int", args.jobs) or os.cpu_count() or 1,
            infer_with=tuple(cast("list[str]", args.infer_with)),
            infer_memory=_bytes(cast("float | None", args.infer_memory)),
        )


def _maximal(args: argparse.Namespace) -> argparse.Namespace:
    """Apply `--max-fix` (`--max`, every fix, every installed checker) and `--max`.

    `--max`: `suffocate` for every path (over `per-path-levels`), all scopes, the opt-in codes.

    Returns:
      The arguments.

    """
    if cast("bool", args.max_fix):
        args.max = args.fix = args.unsafe_fixes = True
        chosen: list[str] = cast("list[str]", args.infer_with)
        args.infer_with = [
            *chosen,
            *(checker for checker in SERVERS if checker not in chosen and runs(checker)),
        ]
    if cast("bool", args.max):
        args.level = Level.SUFFOCATE.name.lower()
        args.per_path_levels = {}
        args.all_scopes = True
        args.extend_select = [*cast("list[str]", args.extend_select), *sorted(OPT_IN)]
    return args


def _filter(parser: argparse.ArgumentParser, args: argparse.Namespace, mode: Mode) -> Filter:
    """Build the filter the options set, reading the baseline (the default one, if it exists).

    Returns:
      The filter.

    """
    default: Path = project_root(Path.cwd()) / DEFAULT_BASELINE
    baseline_path: Path | None = cast("Path | None", args.baseline) or (
        default if mode is Mode.WRITE_BASELINE or default.is_file() else None
    )
    entries: baseline.Entries = {}
    if baseline_path is not None and mode is not Mode.WRITE_BASELINE:
        try:
            entries = baseline.read(baseline_path)
        except ValueError as error:
            parser.error(str(error))
    return Filter(
        level=LEVELS[cast("str", args.level)],
        per_path=cast("dict[str, str]", getattr(args, "per_path_levels", {})),
        select=_select(args) + cast("list[str]", args.extend_select) if _select(args) else [],
        ignore=[c.upper() for c in cast("list[str]", args.ignore)],
        per_file_ignores=cast("dict[str, list[str]]", getattr(args, "per_file_ignores", {})),
        baseline_file=baseline_path,
        entries=entries,
    )


def _select(args: argparse.Namespace) -> list[str]:
    """Read `--select`.

    Returns:
      Its codes, upper-cased.

    """
    return [c.upper() for c in cast("list[str]", args.select)]


def _mode(parser: argparse.ArgumentParser, args: argparse.Namespace) -> Mode:
    """Decide the mode; more than one of `--fix`, `--diff` and `--write-baseline` is an error.

    Returns:
      What the options ask for.

    """
    modes: list[Mode] = [
        mode
        for mode, chosen in (
            (Mode.FIX, cast("bool", args.fix)),
            (Mode.DIFF, cast("bool", args.diff)),
            (Mode.WRITE_BASELINE, cast("bool", args.write_baseline)),
            (
                Mode.COVERAGE,
                cast("bool", args.coverage) or cast("float | None", args.fail_under) is not None,
            ),
        )
        if chosen
    ]
    if len(modes) > 1:
        parser.error("--fix, --diff, --write-baseline and --coverage can't be combined")
    return modes[0] if modes else Mode.CHECK
