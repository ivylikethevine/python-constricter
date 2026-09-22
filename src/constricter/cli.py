# SPDX-License-Identifier: MIT
"""The `constricter` command (see README)."""

import argparse
import json
import sys
import tomllib
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import StrEnum
from fnmatch import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeAlias, cast

from constricter import __version__
from constricter.checker import LEVELS, MESSAGES, NESTING, Level, Offence, check_source
from constricter.noqa import lines, unsuppressed

if TYPE_CHECKING:
  from datetime import date, datetime, time
  from io import BufferedReader


_Result: TypeAlias = tuple[Path, Offence]
_Toml: TypeAlias = "str | int | float | bool | datetime | date | time | list[_Toml] | dict[str, _Toml]"
_Default: TypeAlias = str | int | bool | list[str]

_SKIPPED_DIRS: frozenset[str] = frozenset(
  {"__pycache__", "node_modules", "venv", "site-packages", "build", "dist"}
)
EXIT_CLEAN: Final = 0
EXIT_FOUND: Final = 1
EXIT_ERROR: Final = 2


class Format(StrEnum):
  """The `--format` choices."""

  TEXT = "text"
  JSON = "json"
  GITHUB = "github"
  SARIF = "sarif"


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


def fix_file(path: Path, offences: Sequence[Offence]) -> int:
  """Add each fixable offence's annotation to `path`; return how many were fixed."""
  fixes: list[Offence]
  if not (fixes := sorted((o for o in offences if o.fix), key=lambda o: (o.line, o.col), reverse=True)):
    return 0
  text: list[str] = lines(path.read_bytes().decode("utf-8"))
  o: Offence
  for o in fixes:
    raw: bytes = text[o.line - 1].encode()
    end: int = o.col + len(o.name.encode())  # `col` counts bytes, as `ast` does
    text[o.line - 1] = (raw[:end] + f": {o.fix}".encode() + raw[end:]).decode()
  _ = path.write_bytes("".join(text).encode())
  return len(fixes)


def _github_escape(text: str, *, prop: bool = False) -> str:
  text = text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
  return text.replace(":", "%3A").replace(",", "%2C") if prop else text


def _severity(offence: Offence, level: Level) -> str:
  return "error" if offence.is_error(level) else "warning"


def _sarif(results: Sequence[_Result], level: Level) -> dict[str, object]:
  return {
    "version": "2.1.0",
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "runs": [
      {
        "tool": {
          "driver": {
            "name": "constricter",
            "version": __version__,
            "informationUri": "https://github.com/ivylikethevine/python-constricter",
            "rules": [
              {"id": code, "shortDescription": {"text": message.format(name="`name`")}}
              for code, message in MESSAGES.items()
            ],
          }
        },
        "results": [
          {
            "ruleId": o.code,
            "level": _severity(o, level),
            "message": {"text": o.message},
            "locations": [
              {
                "physicalLocation": {
                  "artifactLocation": {"uri": path.as_posix()},
                  "region": {"startLine": o.line, "startColumn": o.col + 1},
                }
              }
            ],
          }
          for path, o in results
        ],
      }
    ],
  }


def _render(fmt: Format, results: Sequence[_Result], level: Level) -> Iterator[str]:
  """Yield the output lines for `results` in format `fmt`."""
  path: Path
  o: Offence
  if fmt is Format.JSON:
    yield json.dumps(
      [
        {
          "path": str(path),
          "line": o.line,
          "column": o.col + 1,
          "code": o.code,
          "severity": _severity(o, level),
          "message": o.message,
        }
        for path, o in results
      ],
      indent=2,
    )
  elif fmt is Format.SARIF:
    yield json.dumps(_sarif(results, level), indent=2)
  elif fmt is Format.GITHUB:
    for path, o in results:
      location: str = f"file={_github_escape(str(path), prop=True)},line={o.line},col={o.col + 1}"
      yield f"::{_severity(o, level)} {location},title={o.code}::{_github_escape(o.message)}"
  else:
    for path, o in results:
      yield f"{path}:{o.line}:{o.col + 1}: {_severity(o, level)}: {o.code} {o.message}"


def _positive(text: str) -> int:
  """Read a whole number of at least 1, for `--nesting`.

  Raises:
    argparse.ArgumentTypeError: `text` isn't one.

  """
  if not text.isdigit() or int(text) < 1:
    message: str = f"expected a whole number of at least 1, not {text!r}"
    raise argparse.ArgumentTypeError(message)
  return int(text)


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
    type=_positive,
    default=NESTING,
    metavar="N",
    help=f"report an annotation nested N deep (LVA006; default: {NESTING})",
  )
  _ = parser.add_argument(
    "--fix", action="store_true", help="add the annotations a value makes unambiguous, in place"
  )
  _ = parser.add_argument("--quiet", "-q", action="store_true", help="don't print the text summary line")
  _ = parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
  return parser


def _pyproject(start: Path) -> Path | None:
  """Return the nearest `pyproject.toml` in `start` or above it."""
  directory: Path
  path: Path
  for directory in (start, *start.parents):
    if (path := directory / "pyproject.toml").is_file():
      return path
  return None


def _table(path: Path) -> dict[str, _Toml]:
  """Return `path`'s `[tool.constricter]` table, or an empty one.

  Raises:
    ValueError: The file isn't TOML, or `tool.constricter` isn't a table.

  """
  file: BufferedReader
  document: dict[str, _Toml]
  message: str
  with path.open("rb") as file:
    try:
      document = tomllib.load(file)
    except tomllib.TOMLDecodeError as error:
      message = f"{path}: {error}"
      raise ValueError(message) from error
  table: dict[str, _Toml]
  match document.get("tool"):
    case {"constricter": dict() as table}:
      return table
    case {"constricter": _}:
      message = f"{path}: [tool.constricter] isn't a table"
      raise ValueError(message)
    case _:
      return {}


def config_defaults(start: Path) -> dict[str, _Default]:
  """Return the option defaults in the nearest `pyproject.toml`'s `[tool.constricter]`.

  Raises:
    ValueError: The file isn't TOML, or the table has an unknown key or a wrong value.

  """
  path: Path | None
  if (path := _pyproject(start)) is None:
    return {}
  defaults: dict[str, _Default] = {}
  key: str
  value: _Toml
  for key, value in _table(path).items():
    match key, value:
      case "level", str() | int() if not isinstance(value, bool) and str(value).lower() in LEVELS:
        defaults["level"] = str(value).lower()
      case "nesting", int() if not isinstance(value, bool) and value >= 1:
        defaults["nesting"] = value
      case "exclude", list() if all(isinstance(glob, str) for glob in value):
        defaults["exclude"] = [str(glob) for glob in value]
      case (("type-comments" | "all-scopes"), bool()):
        defaults[key.replace("-", "_")] = value
      case _:
        message: str = f"{path}: [tool.constricter] has an invalid {key} = {value!r}"
        raise ValueError(message)
  return defaults


@dataclass(frozen=True)
class _Checks:
  """The options the checker itself takes."""

  type_comments: bool
  all_scopes: bool
  nesting: int


@dataclass(frozen=True)
class _Options:
  """The command's parsed options."""

  paths: list[Path]
  exclude: list[str]
  level: Level
  fmt: Format
  checks: _Checks
  fix: bool
  quiet: bool

  @classmethod
  def parse(cls, argv: Sequence[str] | None) -> "_Options":
    """Parse `argv` over the defaults `pyproject.toml` sets."""
    parser: argparse.ArgumentParser = _parser()
    try:
      parser.set_defaults(**config_defaults(Path.cwd()))
    except ValueError as error:
      parser.error(str(error))
    args: argparse.Namespace = parser.parse_args(argv)
    return cls(
      paths=cast("list[Path]", args.paths) or [Path()],
      exclude=cast("list[str]", args.exclude),
      level=LEVELS[cast("str", args.level)],
      fmt=cast("Format", args.format),
      checks=_Checks(
        type_comments=cast("bool", args.type_comments),
        all_scopes=cast("bool", args.all_scopes),
        nesting=cast("int", args.nesting),
      ),
      fix=cast("bool", args.fix),
      quiet=cast("bool", args.quiet),
    )


def _check_one(path: Path, options: _Options) -> tuple[list[Offence], int]:
  """Check (and fix) one file: the offences left, and how many were fixed."""
  checks: _Checks = options.checks
  offences: list[Offence] = [
    o
    for o in check_file(
      path, type_comments=checks.type_comments, all_scopes=checks.all_scopes, nesting=checks.nesting
    )
    if o.is_reported(options.level)
  ]
  if not options.fix:
    return offences, 0
  return [o for o in offences if not o.fix], fix_file(path, offences)


def _check_all(options: _Options) -> tuple[list[_Result], int, int, bool]:
  """Check (and fix) every file: the results left, the files, the fixes, and whether any failed."""
  results: list[_Result] = []
  files: int = 0
  fixed: int = 0
  failed: bool = False
  path: Path
  offences: list[Offence]
  count: int
  for path in python_files(options.paths, options.exclude):
    files += 1
    try:
      offences, count = _check_one(path, options)
    except (OSError, UnicodeDecodeError, SyntaxError) as error:
      _ = sys.stderr.write(f"{path}: error: {error}\n")
      failed = True
    else:
      results += [(path, o) for o in offences]
      fixed += count
  return results, files, fixed, failed


def main(argv: Sequence[str] | None = None) -> int:
  """Run the command; return its exit status."""
  options: _Options = _Options.parse(argv)
  results: list[_Result]
  files: int
  fixed: int
  failed: bool
  results, files, fixed, failed = _check_all(options)
  line: str
  for line in _render(options.fmt, results, options.level):
    _ = sys.stdout.write(f"{line}\n")
  errors: int = sum(o.is_error(options.level) for _, o in results)
  if options.fmt is Format.TEXT and not options.quiet:
    summary: str = f"Found {errors} error(s) and {len(results) - errors} warning(s) in {files} file(s)"
    _ = sys.stdout.write(f"{summary}; fixed {fixed}.\n" if options.fix else f"{summary}.\n")
  return EXIT_ERROR if failed else EXIT_FOUND if errors else EXIT_CLEAN
