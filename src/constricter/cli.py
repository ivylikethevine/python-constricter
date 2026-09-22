# SPDX-License-Identifier: MIT
"""The `constricter` command (see README)."""

import argparse
import json
import re
import sys
from collections.abc import Iterator, Sequence
from enum import StrEnum
from fnmatch import fnmatch
from pathlib import Path
from typing import cast

from constricter import __version__
from constricter.checker import LEVELS, MESSAGES, Level, Offence, check_source

_Result = tuple[Path, Offence]

_SKIPPED_DIRS: frozenset[str] = frozenset(
  {"__pycache__", "node_modules", "venv", "site-packages", "build", "dist"}
)
EXIT_CLEAN = 0
EXIT_FOUND = 1
EXIT_ERROR = 2


class Format(StrEnum):
  """The `--format` choices."""

  TEXT = "text"
  JSON = "json"
  GITHUB = "github"
  SARIF = "sarif"


_NOQA: re.Pattern[str] = re.compile(
  r"#\s*noqa(?::\s*(?P<codes>[A-Z]+[0-9]+(?:[,\s]+[A-Z]+[0-9]+)*))?", re.IGNORECASE
)


def _suppressed(line: str, code: str) -> bool:
  """Return whether `line` has a `# noqa` covering `code`."""
  match_: re.Match[str] | None
  if (match_ := _NOQA.search(line)) is None:
    return False
  codes: str | None = match_.group("codes")
  return codes is None or code in re.split(r"[,\s]+", codes.upper())


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


def check_file(path: Path, *, type_comments: bool = False) -> list[Offence]:
  """Return the offences in `path` that no `# noqa` suppresses."""
  source: str = path.read_text(encoding="utf-8")
  lines: list[str] = source.splitlines()
  return [
    o
    for o in check_source(source, str(path), type_comments=type_comments)
    if not (o.line <= len(lines) and _suppressed(lines[o.line - 1], o.code))
  ]


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
  _ = parser.add_argument("--quiet", "-q", action="store_true", help="don't print the text summary line")
  _ = parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
  return parser


def _check_all(
  paths: Sequence[Path], exclude: Sequence[str], *, type_comments: bool
) -> tuple[list[_Result], int, bool]:
  """Check every file: the results, how many files, and whether any couldn't be checked."""
  results: list[_Result] = []
  files: int = 0
  failed: bool = False
  path: Path
  for path in python_files(paths, exclude):
    files += 1
    try:
      results += [(path, o) for o in check_file(path, type_comments=type_comments)]
    except (OSError, UnicodeDecodeError, SyntaxError) as error:
      _ = sys.stderr.write(f"{path}: error: {error}\n")
      failed = True
  return results, files, failed


def main(argv: Sequence[str] | None = None) -> int:
  """Run the command; return its exit status."""
  args: argparse.Namespace = _parser().parse_args(argv)
  paths: list[Path] = cast("list[Path]", args.paths) or [Path()]
  exclude: list[str] = cast("list[str]", args.exclude)
  level: Level = LEVELS[cast("str", args.level)]
  fmt: Format = cast("Format", args.format)
  type_comments: bool = cast("bool", args.type_comments)
  quiet: bool = cast("bool", args.quiet)

  results: list[_Result]
  files: int
  failed: bool
  results, files, failed = _check_all(paths, exclude, type_comments=type_comments)
  line: str
  for line in _render(fmt, results, level):
    _ = sys.stdout.write(f"{line}\n")
  errors: int = sum(o.is_error(level) for _, o in results)
  if fmt is Format.TEXT and not quiet:
    warnings: int = len(results) - errors
    _ = sys.stdout.write(f"Found {errors} error(s) and {warnings} warning(s) in {files} file(s).\n")
  return EXIT_ERROR if failed else EXIT_FOUND if errors else EXIT_CLEAN
