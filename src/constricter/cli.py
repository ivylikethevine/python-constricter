# SPDX-License-Identifier: MIT
"""The `constricter` command (see README)."""

import argparse
import difflib
import os
import sys
from collections.abc import Callable, Iterator, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from fnmatch import fnmatch
from functools import partial
from pathlib import Path
from typing import Final, cast

from constricter import __version__
from constricter.checker import LEVELS, MESSAGES, NESTING, Level, Offence, check_source
from constricter.config import config_defaults, unknown_codes
from constricter.explain import explain
from constricter.noqa import lines, unsuppressed
from constricter.report import Format, Result, render, statistics

_SKIPPED_DIRS: frozenset[str] = frozenset(
  {"__pycache__", "node_modules", "venv", "site-packages", "build", "dist"}
)
EXIT_CLEAN: Final = 0
EXIT_FOUND: Final = 1
EXIT_ERROR: Final = 2


def _excluded(path: Path, patterns: Sequence[str]) -> bool:
  text: str = path.as_posix()
  return any(fnmatch(text, p) or fnmatch(path.name, p) for p in patterns)


def python_files(paths: Sequence[Path], exclude: Sequence[str] = ()) -> Iterator[Path]:
  """Yield each file given and each `*.py` under each directory given."""
  path: Path
  found: Path
  for path in paths:
    if not path.is_dir():
      if not _excluded(path, exclude):
        yield path
      continue
    for found in sorted(path.rglob("*.py")):
      parts: tuple[str, ...] = found.relative_to(path).parts[:-1]
      if any(p.startswith(".") or p in _SKIPPED_DIRS for p in parts):
        continue
      if not _excluded(found, exclude):
        yield found


def check_file(
  path: Path, *, type_comments: bool = False, all_scopes: bool = False, nesting: int = NESTING
) -> list[Offence]:
  """Return the offences in `path` that no `# noqa` suppresses."""
  source: str = path.read_bytes().decode("utf-8")
  offences: list[Offence] = check_source(
    source, str(path), type_comments=type_comments, all_scopes=all_scopes, nesting=nesting
  )
  return unsuppressed(offences, lines(source))


def _fixed(source: str, offences: Sequence[Offence]) -> list[str]:
  """Return `source`'s lines with each fixable offence's annotation added."""
  text: list[str] = lines(source)
  o: Offence
  for o in sorted((o for o in offences if o.fix), key=lambda o: (o.line, o.col), reverse=True):
    raw: bytes = text[o.line - 1].encode()
    end: int = o.col + len(o.name.encode())  # `col` counts bytes, as `ast` does
    text[o.line - 1] = (raw[:end] + f": {o.fix}".encode() + raw[end:]).decode()
  return text


def fix_file(path: Path, offences: Sequence[Offence]) -> int:
  """Add each fixable offence's annotation to `path`; return how many were fixed."""
  count: int
  if not (count := sum(1 for o in offences if o.fix)):
    return 0
  _ = path.write_bytes("".join(_fixed(path.read_bytes().decode("utf-8"), offences)).encode())
  return count


def diff_file(path: Path, offences: Sequence[Offence]) -> str:
  """Return the unified diff `fix_file` would make to `path` (empty if none)."""
  source: str = path.read_bytes().decode("utf-8")
  return "".join(difflib.unified_diff(lines(source), _fixed(source, offences), str(path), str(path)))


def _at_least(minimum: int) -> Callable[[str], int]:
  """Return a reader of whole numbers of at least `minimum`, for `--nesting` and `--jobs`."""

  def read(text: str) -> int:
    """Read `text`.

    Raises:
      argparse.ArgumentTypeError: It isn't one.

    """
    if not text.isdigit() or int(text) < minimum:
      message: str = f"expected a whole number of at least {minimum}, not {text!r}"
      raise argparse.ArgumentTypeError(message)
    return int(text)

  return read


def _codes(text: str) -> list[str]:
  """Read a comma-separated list of codes or code prefixes (`LVA001,LVA00`).

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
  _ = parser.add_argument("paths", nargs="*", type=Path, help="files and directories (default: .)")
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
    "--type-comments", action="store_true", help="count `x = 1  # type: int` as annotated"
  )
  _ = parser.add_argument(
    "--all-scopes", action="store_true", help="also check module and class bodies (LVA004)"
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
    "--ignore", type=_codes, default=[], metavar="CODES", help="don't report these codes or prefixes"
  )
  _ = parser.add_argument(
    "--fix", action="store_true", help="add the annotations a value makes unambiguous, in place"
  )
  _ = parser.add_argument(
    "--diff", action="store_true", help="print what --fix would change, and change nothing"
  )
  _ = parser.add_argument(
    "--statistics", action="store_true", help="print counts per code instead of each offence (text)"
  )
  _ = parser.add_argument("--explain", choices=list(MESSAGES), metavar="CODE", help="explain a code and exit")
  _ = parser.add_argument(
    "--jobs",
    "-j",
    type=_at_least(0),
    default=1,
    metavar="N",
    help="check N files at a time (0: one per CPU; default: 1)",
  )
  _ = parser.add_argument("--quiet", "-q", action="store_true", help="don't print the text summary line")
  _ = parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
  return parser


class _Mode(Enum):
  """What to do with what's found."""

  CHECK = "check"
  FIX = "fix"
  DIFF = "diff"


@dataclass(frozen=True)
class _Checks:
  """The options the checker itself takes."""

  type_comments: bool
  all_scopes: bool
  nesting: int


@dataclass(frozen=True)
class _Filter:
  """Which offences are reported, and at which level."""

  level: Level
  per_path: dict[str, str]
  select: list[str]
  ignore: list[str]

  def level_for(self, path: Path) -> Level:
    """Return the level of the first `per-path-levels` glob `path` matches, else `--level`'s."""
    glob: str
    level: str
    for glob, level in self.per_path.items():
      if _excluded(path, [glob]):
        return LEVELS[level]
    return self.level

  def results(self, path: Path, offences: Sequence[Offence]) -> list[Result]:
    """Return the offences in `path` that are reported, at its level."""
    level: Level = self.level_for(path)
    return [
      Result(path, o, level)
      for o in offences
      if o.is_reported(level)
      and (not self.select or o.code.startswith(tuple(self.select)))
      and not o.code.startswith(tuple(self.ignore))
    ]


@dataclass(frozen=True)
class _Output:
  """How the report looks."""

  fmt: Format
  statistics: bool
  quiet: bool


@dataclass(frozen=True)
class _Options:
  """The command's parsed options."""

  paths: list[Path]
  exclude: list[str]
  checks: _Checks
  filter: _Filter
  output: _Output
  mode: _Mode
  jobs: int

  @classmethod
  def parse(cls, argv: Sequence[str] | None) -> "_Options":
    """Parse `argv` over the defaults `pyproject.toml` sets; `--explain` prints and exits."""
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
    fix: bool = cast("bool", args.fix)
    diff: bool = cast("bool", args.diff)
    if fix and diff:
      parser.error("--fix and --diff can't be combined")
    return cls(
      paths=cast("list[Path]", args.paths) or [Path()],
      exclude=cast("list[str]", args.exclude),
      checks=_Checks(
        type_comments=cast("bool", args.type_comments),
        all_scopes=cast("bool", args.all_scopes),
        nesting=cast("int", args.nesting),
      ),
      filter=_Filter(
        level=LEVELS[cast("str", args.level)],
        per_path=cast("dict[str, str]", getattr(args, "per_path_levels", {})),
        select=[c.upper() for c in cast("list[str]", args.select)],
        ignore=[c.upper() for c in cast("list[str]", args.ignore)],
      ),
      output=_Output(
        fmt=cast("Format", args.format),
        statistics=cast("bool", args.statistics),
        quiet=cast("bool", args.quiet),
      ),
      mode=_Mode.FIX if fix else _Mode.DIFF if diff else _Mode.CHECK,
      jobs=cast("int", args.jobs) or os.cpu_count() or 1,
    )


@dataclass(frozen=True)
class _FileRun:
  """What checking one file found (and fixed, or would fix)."""

  results: list[Result] = field(default_factory=list[Result])
  fixed: int = 0
  diff: str = ""
  error: str = ""


def _check_path(path: Path, options: _Options) -> _FileRun:
  """Check (and fix, or diff) one file; a file that can't be read or parsed is an error."""
  checks: _Checks = options.checks
  offences: list[Offence]
  try:
    offences = check_file(
      path, type_comments=checks.type_comments, all_scopes=checks.all_scopes, nesting=checks.nesting
    )
  except (OSError, UnicodeDecodeError, SyntaxError) as error:
    return _FileRun(error=f"{path}: error: {error}")
  results: list[Result] = options.filter.results(path, offences)
  reported: list[Offence] = [r.offence for r in results]
  if options.mode is _Mode.DIFF:
    return _FileRun(diff=diff_file(path, reported))
  if options.mode is _Mode.FIX:
    return _FileRun([r for r in results if not r.offence.fix], fix_file(path, reported))
  return _FileRun(results)


def _check_all(options: _Options) -> tuple[list[_FileRun], int]:
  """Check every file (`--jobs` at a time), in order; return what each found, and how many."""
  paths: list[Path] = list(python_files(options.paths, options.exclude))
  check: Callable[[Path], _FileRun] = partial(_check_path, options=options)
  if options.jobs == 1 or len(paths) <= 1:
    return [check(path) for path in paths], len(paths)
  pool: ProcessPoolExecutor
  with ProcessPoolExecutor(max_workers=options.jobs) as pool:
    return list(pool.map(check, paths)), len(paths)


def main(argv: Sequence[str] | None = None) -> int:
  """Run the command; return its exit status."""
  options: _Options = _Options.parse(argv)
  runs: list[_FileRun]
  files: int
  runs, files = _check_all(options)
  _ = sys.stderr.write("".join(f"{run.error}\n" for run in runs if run.error))
  failed: bool = any(run.error for run in runs)
  if options.mode is _Mode.DIFF:
    diffs: str = "".join(run.diff for run in runs)
    _ = sys.stdout.write(diffs)
    return EXIT_ERROR if failed else EXIT_FOUND if diffs else EXIT_CLEAN
  results: list[Result] = [result for run in runs for result in run.results]
  output: _Output = options.output
  text: bool = output.fmt is Format.TEXT
  line: str
  for line in statistics(results) if text and output.statistics else render(output.fmt, results):
    _ = sys.stdout.write(f"{line}\n")
  errors: int = sum(r.offence.is_error(r.level) for r in results)
  if text and not output.quiet:
    summary: str = f"Found {errors} error(s) and {len(results) - errors} warning(s) in {files} file(s)"
    fixed: int = sum(run.fixed for run in runs)
    _ = sys.stdout.write(f"{summary}; fixed {fixed}.\n" if options.mode is _Mode.FIX else f"{summary}.\n")
  return EXIT_ERROR if failed else EXIT_FOUND if errors else EXIT_CLEAN
