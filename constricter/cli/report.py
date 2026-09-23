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
from constricter.cli.explain import explain
from constricter.fix.fixes import Replacement
from constricter.offences import MESSAGES, Level, Offence

_URL: Final = "https://github.com/ivylikethevine/python-constricter"
_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json]"


class Format(StrEnum):
    """The `--format` choices."""

    TEXT = "text"
    FULL = "full"  # text, with each offence's source line and a caret under the name
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
    source: str = ""  # the offending line, for `--format=full`
    replacements: tuple[Replacement, ...] = ()  # its fix as text edits, for SARIF and rdjson

    @property
    def suggestions(self) -> tuple[Replacement, ...]:
        """Its fix as text edits, if it's certain (not a guess)."""
        return () if self.offence.unsafe else self.replacements

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
    """Locate `result` for SARIF.

    Returns:
      Its physical location; a notebook's is the file, as its cells have no file lines.

    """
    where: dict[str, _Json] = {"artifactLocation": {"uri": result.path.as_posix()}}
    if result.offence.cell is None:
        where["region"] = {"startLine": result.offence.line, "startColumn": _column(result) + 1}
    return where


def _column(result: Result) -> int:
    """Find `result`'s column in characters (its offence's counts UTF-8 bytes, as `ast`'s do).

    Returns:
      It, from 0.

    """
    return len(result.source.encode()[: result.offence.col].decode(errors="ignore"))


def _sarif_result(result: Result) -> dict[str, _Json]:
    """Render one result for SARIF; a certain fix is a SARIF `fix`.

    Returns:
      The result object.

    """
    found: dict[str, _Json] = {
        "ruleId": result.offence.code,
        "level": result.severity,
        "message": {"text": result.message},
        "locations": [{"physicalLocation": _where(result)}],
    }
    edits: tuple[Replacement, ...]
    if edits := result.suggestions:
        change: dict[str, _Json] = {
            "artifactLocation": {"uri": result.path.as_posix()},
            "replacements": [
                {"deletedRegion": _region(edit), "insertedContent": {"text": edit.text}} for edit in edits
            ],
        }
        found["fixes"] = [{"description": {"text": _described(result.offence)}, "artifactChanges": [change]}]
    return found


def _region(edit: Replacement) -> dict[str, _Json]:
    """Place a text edit for SARIF, in characters.

    Returns:
      Its region.

    """
    start: int
    end: int
    start, end = edit.columns
    return {"startLine": edit.line, "startColumn": start + 1, "endLine": edit.line, "endColumn": end + 1}


def _described(offence: Offence) -> str:
    """Say what an offence's fix does.

    Returns:
      A sentence: an annotation added, or a repeated one dropped (its annotation is empty).

    """
    return (
        f"Annotate {offence.name!r} as `{offence.fix}`"
        if offence.fix
        else f"Drop {offence.name!r}'s annotation"
    )


def _sarif(results: Sequence[Result]) -> dict[str, _Json]:
    rules: list[_Json] = [
        {
            "id": code,
            "shortDescription": {"text": message.format(name="`name`", detail="T")},
            "help": {"text": explain(code)},
            "helpUri": f"{_URL}#rules",
        }
        for code, message in MESSAGES.items()
    ]
    driver: dict[str, _Json] = {
        "name": "constricter",
        "version": __version__,
        "informationUri": _URL,
        "rules": rules,
    }
    run: dict[str, _Json] = {
        "tool": {"driver": driver},
        "columnKind": "unicodeCodePoints",
        "results": [_sarif_result(r) for r in results],
    }
    return {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [run],
    }


def _text(results: Sequence[Result]) -> Iterator[str]:
    r: Result
    for r in results:
        cell: str = "" if r.offence.cell is None else f"cell {r.offence.cell}:"
        where: str = f"{r.path}:{cell}{r.offence.line}:{r.offence.col + 1}"
        yield f"{where}: {r.severity}: {r.offence.code} {r.offence.message}"


def _full(results: Sequence[Result]) -> Iterator[str]:
    """Render `_text`'s lines, each followed by its source line and a caret under the name.

    Yields:
      The lines: a result's text line, then a gutter numbered with its line, the source, and the
      caret, then a blank line.

    """
    r: Result
    for r in results:
        yield from _text([r])
        source: str = r.source
        # `col` counts UTF-8 bytes, as `ast` does; the caret goes under that many characters.
        start: int = len(source.encode()[: r.offence.col].decode(errors="ignore"))
        width: int = len(r.offence.name) if source[start:].startswith(r.offence.name) else 1
        number: str = str(r.offence.line)
        gutter: str = " " * len(number)
        yield f"{gutter} |"
        yield f"{number} | {source}"
        yield f"{gutter} | {' ' * start}{'^' * width}"
        yield ""


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
                "fix": None
                if r.offence.fix is None
                else {
                    "annotation": r.offence.fix,
                    "reason": r.offence.reason,
                    "unsafe": r.offence.unsafe,
                    "kinds": sorted(r.offence.edit.kinds if r.offence.edit else ()),
                },
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
    """Render GitLab's Code Quality report (Code Climate JSON).

    Yields:
      Its lines; a fingerprint survives lines moving.

    """
    seen: Counter[tuple[Path, str, str]] = Counter()
    issues: list[_Json] = []
    r: Result
    for r in results:
        key: tuple[Path, str, str] = (r.path, r.offence.code, r.offence.name)
        seen[key] += 1
        fingerprint: str = hashlib.sha256(
            f"{r.path.as_posix()}:{key[1]}:{key[2]}:{seen[key]}".encode(),
        ).hexdigest()
        issues.append(
            {
                "description": f"{r.offence.code} {r.message}",
                "check_name": r.offence.code,
                "fingerprint": fingerprint,
                "severity": "major" if r.offence.is_error(r.level) else "minor",
                "location": {"path": r.path.as_posix(), "lines": {"begin": r.offence.line}},
            },
        )
    yield json.dumps(issues, indent=2)


def _junit(results: Sequence[Result]) -> Iterator[str]:
    """Render a JUnit XML report.

    Yields:
      Its lines: a test suite per file with offences, a failed test case per offence.

    """
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
    """Quote `text` for XML.

    Returns:
      It as a double-quoted attribute value.

    """
    return f'"{escape(text, quote=True)}"'


def _rdjson(results: Sequence[Result]) -> Iterator[str]:
    """Render reviewdog's Diagnostic JSON; a certain fix is a suggestion.

    Yields:
      Its lines (columns count UTF-8 bytes).

    """
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
        edits: tuple[Replacement, ...]
        if edits := r.suggestions:
            diagnostic["suggestions"] = [{"range": _byte_range(edit), "text": edit.text} for edit in edits]
        diagnostics.append(diagnostic)
    yield json.dumps({"source": {"name": "constricter", "url": _URL}, "diagnostics": diagnostics}, indent=2)


def _byte_range(edit: Replacement) -> dict[str, _Json]:
    """Place a text edit for rdjson, whose columns count UTF-8 bytes.

    Returns:
      Its range.

    """
    columns: tuple[int, int] = edit.byte_columns
    return {
        "start": {"line": edit.line, "column": columns[0] + 1},
        "end": {"line": edit.line, "column": columns[1] + 1},
    }


_Renderer: TypeAlias = Callable[[Sequence[Result]], Iterator[str]]
_RENDERERS: dict[Format, _Renderer] = {
    Format.TEXT: _text,
    Format.FULL: _full,
    Format.JSON: _json,
    Format.GITHUB: _github,
    Format.SARIF: lambda results: iter([json.dumps(_sarif(results), indent=2)]),
    Format.GITLAB: _gitlab,
    Format.JUNIT: _junit,
    Format.RDJSON: _rdjson,
}


def render(fmt: Format, results: Sequence[Result]) -> Iterator[str]:
    """Render `results` in format `fmt`.

    Returns:
      The output lines.

    """
    return _RENDERERS[fmt](results)


def fix_reasons(results: Sequence[Result]) -> Iterator[str]:
    """List the annotation each fixable result would get, and how its value decided it.

    Yields:
      A line each: where, the name, the annotation and its reason; a guess says it needs
      `--unsafe-fixes`.

    """
    r: Result
    for r in results:
        if r.offence.fix is not None:
            cell: str = "" if r.offence.cell is None else f"cell {r.offence.cell}:"
            where: str = f"{r.path}:{cell}{r.offence.line}:{r.offence.col + 1}"
            guess: str = " (a guess: --unsafe-fixes)" if r.offence.unsafe else ""
            kinds: str = ", ".join(sorted(r.offence.edit.kinds if r.offence.edit else ()))
            written: str = f"`{r.offence.fix}`" if r.offence.fix else "drop its annotation"
            decided: str = f"{written}, from {r.offence.reason} [{kinds}]"
            yield f"{where}: fix {r.offence.name!r}: {decided}{guess}"


def statistics(results: Sequence[Result]) -> Iterator[str]:
    """Count the results per code and severity.

    Yields:
      A line each: how many, the code, and the severity.

    """
    key: tuple[str, str]
    count: int
    for key, count in Counter((r.offence.code, r.severity) for r in results).most_common():
        yield f"{count:>5}  {key[0]}  {key[1]}"
