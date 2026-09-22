# SPDX-License-Identifier: MIT
"""The command's output: text, JSON, GitHub workflow commands, SARIF, and statistics."""

import json
from collections import Counter
from collections.abc import Iterator, Sequence
from enum import StrEnum
from pathlib import Path
from typing import NamedTuple, TypeAlias

from constricter import __version__
from constricter.checker import MESSAGES, Level, Offence

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json]"


class Format(StrEnum):
  """The `--format` choices."""

  TEXT = "text"
  JSON = "json"
  GITHUB = "github"
  SARIF = "sarif"


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
    "informationUri": "https://github.com/ivylikethevine/python-constricter",
    "rules": rules,
  }
  return {
    "version": "2.1.0",
    "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
    "runs": [{"tool": {"driver": driver}, "results": findings}],
  }


def render(fmt: Format, results: Sequence[Result]) -> Iterator[str]:
  """Yield the output lines for `results` in format `fmt`."""
  r: Result
  if fmt is Format.JSON:
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
  elif fmt is Format.SARIF:
    yield json.dumps(_sarif(results), indent=2)
  elif fmt is Format.GITHUB:
    for r in results:
      location: str = f"file={_github_escape(str(r.path), prop=True)}"
      if r.offence.cell is None:  # a notebook's cells have no file lines to point at
        location += f",line={r.offence.line},col={r.offence.col + 1}"
      yield f"::{r.severity} {location},title={r.offence.code}::{_github_escape(r.message)}"
  else:
    for r in results:
      cell: str = "" if r.offence.cell is None else f"cell {r.offence.cell}:"
      where: str = f"{r.path}:{cell}{r.offence.line}:{r.offence.col + 1}"
      yield f"{where}: {r.severity}: {r.offence.code} {r.offence.message}"


def statistics(results: Sequence[Result]) -> Iterator[str]:
  """Yield one line per code and severity: how many, the code, and the severity."""
  key: tuple[str, str]
  count: int
  for key, count in Counter((r.offence.code, r.severity) for r in results).most_common():
    yield f"{count:>5}  {key[0]}  {key[1]}"
