# SPDX-License-Identifier: MIT
"""The command's output: text, JSON, GitHub workflow commands, SARIF, and statistics."""

import hashlib
import json
from collections import Counter
from collections.abc import Callable, Iterator, Sequence
from enum import StrEnum
from html import escape
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

from constricter import __version__
from constricter.checker import MESSAGES, Level, Offence

_URL: Final = "https://github.com/ivylikethevine/python-constricter"
_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json]"


class Format(StrEnum):
  """The `--format` choices."""

  TEXT = "text"
  JSON = "json"
  GITHUB = "github"
  SARIF = "sarif"
  GITLAB = "gitlab"
  JUNIT = "junit"
  RDJSON = "rdjson"


class Result(NamedTuple):
  """One reported offence, in its file, at the level that applies to that file."""

  path: Path
  offence: Offence
  level: Level

  @property
  def severity(self) -> str:
    """`error` or `warning`, at the result's level."""
    return "error" if self.offence.is_error(self.level) else "warning"

  @property
  def message(self) -> str:
    """The offence's message; in a notebook, with its cell and line first."""
    o: Offence = self.offence
    return o.message if o.cell is None else f"cell {o.cell}, line {o.line}: {o.message}"


def _github_escape(text: str, *, prop: bool = False) -> str:
  text = text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
  return text.replace(":", "%3A").replace(",", "%2C") if prop else text


def _where(result: Result) -> dict[str, _Json]:
  """Return a SARIF physical location; a notebook's is the file, as its cells have no file lines."""
  where: dict[str, _Json] = {"artifactLocation": {"uri": result.path.as_posix()}}
  if result.offence.cell is None:
    where["region"] = {"startLine": result.offence.line, "startColumn": result.offence.col + 1}
  return where


def _sarif(results: Sequence[Result]) -> dict[str, _Json]:
  rules: list[_Json] = [
    {"id": code, "shortDescription": {"text": message.format(name="`name`")}}
    for code, message in MESSAGES.items()
  ]
  findings: list[_Json] = [
    {
      "ruleId": r.offence.code,
      "level": r.severity,
      "message": {"text": r.message},
      "locations": [{"physicalLocation": _where(r)}],
    }
    for r in results
  ]
  driver: dict[str, _Json] = {
    "name": "constricter",
    "version": __version__,
    "informationUri": _URL,
    "rules": rules,
  }
  return {
    "version": "2.1.0",
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "runs": [{"tool": {"driver": driver}, "results": findings}],
  }


def _text(results: Sequence[Result]) -> Iterator[str]:
  r: Result
  for r in results:
    cell: str = "" if r.offence.cell is None else f"cell {r.offence.cell}:"
    where: str = f"{r.path}:{cell}{r.offence.line}:{r.offence.col + 1}"
    yield f"{where}: {r.severity}: {r.offence.code} {r.offence.message}"


def _json(results: Sequence[Result]) -> Iterator[str]:
  yield json.dumps(
    [
      {
        "path": str(r.path),
        "line": r.offence.line,
        "column": r.offence.col + 1,
        "code": r.offence.code,
        "severity": r.severity,
        "message": r.offence.message,
        "cell": r.offence.cell,
      }
      for r in results
    ],
    indent=2,
  )


def _github(results: Sequence[Result]) -> Iterator[str]:
  r: Result
  for r in results:
    location: str = f"file={_github_escape(str(r.path), prop=True)}"
    if r.offence.cell is None:  # a notebook's cells have no file lines to point at
      location += f",line={r.offence.line},col={r.offence.col + 1}"
    yield f"::{r.severity} {location},title={r.offence.code}::{_github_escape(r.message)}"


def _gitlab(results: Sequence[Result]) -> Iterator[str]:
  """Yield GitLab's Code Quality report (Code Climate JSON); a fingerprint survives lines moving."""
  seen: Counter[tuple[Path, str, str]] = Counter()
  issues: list[_Json] = []
  r: Result
  for r in results:
    key: tuple[Path, str, str] = (r.path, r.offence.code, r.offence.name)
    seen[key] += 1
    fingerprint: str = hashlib.sha256(
      f"{r.path.as_posix()}:{key[1]}:{key[2]}:{seen[key]}".encode()
    ).hexdigest()
    issues.append(
      {
        "description": f"{r.offence.code} {r.message}",
        "check_name": r.offence.code,
        "fingerprint": fingerprint,
        "severity": "major" if r.offence.is_error(r.level) else "minor",
        "location": {"path": r.path.as_posix(), "lines": {"begin": r.offence.line}},
      }
    )
  yield json.dumps(issues, indent=2)


def _junit(results: Sequence[Result]) -> Iterator[str]:
  """Yield a JUnit XML report: a test suite per file with offences, a failed test case per offence."""
  by_file: dict[Path, list[Result]] = {}
  r: Result
  for r in results:
    by_file.setdefault(r.path, []).append(r)
  yield "<?xml version='1.0' encoding='utf-8'?>"
  yield f'<testsuites name="constricter" tests="{len(results)}" failures="{len(results)}">'
  path: Path
  found: list[Result]
  for path, found in by_file.items():
    yield f'  <testsuite name={_quoted(str(path))} tests="{len(found)}" failures="{len(found)}">'
    for r in found:
      name: str = _quoted(f"{r.offence.code} {r.offence.name}")
      where: str = escape(f"{path}:{r.offence.line}:{r.offence.col + 1}")
      yield f"    <testcase name={name} classname={_quoted(str(path))}>"
      yield f"      <failure message={_quoted(r.message)} type={_quoted(r.severity)}>{where}</failure>"
      yield "    </testcase>"
    yield "  </testsuite>"
  yield "</testsuites>"


def _quoted(text: str) -> str:
  """Return `text` as a double-quoted XML attribute value."""
  return f'"{escape(text, quote=True)}"'


def _rdjson(results: Sequence[Result]) -> Iterator[str]:
  """Yield reviewdog's Diagnostic JSON; a certain fix is a suggestion (columns count UTF-8 bytes)."""
  diagnostics: list[_Json] = []
  r: Result
  for r in results:
    o: Offence = r.offence
    start: dict[str, _Json] = {"line": o.line, "column": o.col + 1}
    diagnostic: dict[str, _Json] = {
      "message": r.message,
      "location": {"path": r.path.as_posix(), "range": {"start": start}},
      "severity": r.severity.upper(),
      "code": {"value": o.code},
    }
    if o.fix and not o.unsafe and o.cell is None:
      end: dict[str, _Json] = {"line": o.line, "column": o.col + len(o.name.encode()) + 1}
      diagnostic["suggestions"] = [{"range": {"start": end, "end": end}, "text": f": {o.fix}"}]
    diagnostics.append(diagnostic)
  yield json.dumps({"source": {"name": "constricter", "url": _URL}, "diagnostics": diagnostics}, indent=2)


_RENDERERS: dict[Format, Callable[[Sequence[Result]], Iterator[str]]] = {
  Format.TEXT: _text,
  Format.JSON: _json,
  Format.GITHUB: _github,
  Format.SARIF: lambda results: iter([json.dumps(_sarif(results), indent=2)]),
  Format.GITLAB: _gitlab,
  Format.JUNIT: _junit,
  Format.RDJSON: _rdjson,
}


def render(fmt: Format, results: Sequence[Result]) -> Iterator[str]:
  """Yield the output lines for `results` in format `fmt`."""
  return _RENDERERS[fmt](results)


def statistics(results: Sequence[Result]) -> Iterator[str]:
  """Yield one line per code and severity: how many, the code, and the severity."""
  key: tuple[str, str]
  count: int
  for key, count in Counter((r.offence.code, r.severity) for r in results).most_common():
    yield f"{count:>5}  {key[0]}  {key[1]}"
