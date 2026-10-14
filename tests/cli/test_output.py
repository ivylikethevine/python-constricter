# SPDX-License-Identifier: MIT
"""The output formats.

`full` (each offence with its source line and a caret under the name), JSON, GitHub annotations,
SARIF, GitLab Code Quality, JUnit and rdjson.
"""

import hashlib
import json
import os
import urllib.request
from pathlib import Path
from typing import Final, TypeAlias, cast

import fastjsonschema
import pytest

from constricter.cli import command as cli
from tests.cli.sources import BROKEN, DEMO, DEMO_CODES, PLAIN, written

_Json: TypeAlias = "str | int | float | bool | list[_Json] | dict[str, _Json] | None"
_JsonObject: TypeAlias = dict[str, _Json]
_Sarif: TypeAlias = dict[str, list[dict[str, list[dict[str, _Json]]]]]
# SARIF 2.1.0's JSON schema, from SchemaStore at a pinned commit, fetched once into `local/` (not
# distributed here) and checked against its SHA-256.
SARIF_SCHEMA: Final = Path(__file__).resolve().parents[2] / "local" / "sarif-2.1.0.json"
SARIF_SCHEMA_URL: Final = (
    "https://raw.githubusercontent.com/SchemaStore/schemastore/"
    "2aded6096789c43a722556cf5019464ee747e495/src/schemas/json/sarif-2.1.0.json"
)
SARIF_SCHEMA_SHA256: Final = "c96eb2d311c37b0a38cbd18c52d79a68f778bbd2d831abed7412d9850740f785"
FIXES: Final = "fixes"
RULES_URL: Final = "https://github.com/ivylikethevine/python-constricter#rules"
RDJSON_ERROR: Final = "ERROR"


def test_full_shows_the_line_and_a_caret_under_the_name(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The caret sits under the name, counted in characters (`col` counts UTF-8 bytes)."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    café = 1\n", encoding="utf-8")
    assert cli.main(["-q", "--format=full", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines() == [
        f"{path}:2:5: error: LVA001 local variable 'café' is not annotated where it's first bound",
        "  |",
        "2 |     café = 1",
        "  |     ^^^^",
        "",
    ]


def test_full_marks_an_annotations_start_with_one_caret(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An offence about an annotation (LVA011) sits at the annotation, not the name: one caret."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    r: tuple[int, int, int, int, int] = t()\n", encoding="utf-8")
    assert cli.main(["-q", "--format=full", "--select=LVA011", str(path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.splitlines()[1:4] == [
        "  |",
        "2 |     r: tuple[int, int, int, int, int] = t()",
        "  |        ^",
    ]


def test_full_places_a_notebooks_offence_in_its_cell(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A notebook's offence shows its cell's line, numbered within the cell."""
    cell: dict[str, str | list[str] | dict[str, str]] = {
        "cell_type": "code",
        "metadata": {},
        "source": ["def f() -> None:\n", "    x = 1\n"],
    }
    path: Path = tmp_path / "demo.ipynb"
    notebook: str = json.dumps({"cells": [cell], "metadata": {}, "nbformat": 4, "nbformat_minor": 5})
    _ = path.write_text(notebook, encoding="utf-8")
    assert cli.main(["-q", "--format=full", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines()[:4] == [
        f"{path}:cell 1:2:5: error: LVA001 local variable 'x' is not annotated where it's first bound",
        "  |",
        "2 |     x = 1",
        "  |     ^",
    ]


def test_full_counts_as_text_for_the_summary(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The summary line (and `--statistics`, `--show-fixes`) treat `full` as text."""
    path: Path = tmp_path / "demo.py"
    _ = path.write_text("def f() -> None:\n    x = 1\n", encoding="utf-8")
    assert cli.main(["--format=full", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines()[-1].startswith("Found 1 error(s)")


def test_json_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=json` prints one object per offence."""
    broken: Path = written(tmp_path / "broken.py", BROKEN)
    assert cli.main(["--format=json", str(broken)]) == cli.EXIT_FOUND
    results: list[dict[str, _Json]] = cast("list[dict[str, _Json]]", json.loads(capsys.readouterr().out))
    assert results[0] == {
        "path": str(broken),
        "line": 3,
        "column": 5,
        "code": "LVA001",
        "severity": "error",
        "message": PLAIN,
        "cell": None,
        "fixed": False,
        "fix": {
            "annotation": "int",
            "reason": "a literal",
            "unsafe": False,
            "likely": False,
            "kinds": ["literal"],
            "imports": [],
        },
    }
    assert [(r["code"], r["severity"]) for r in results] == [
        ("LVA001", "error"),
        ("LVA001", "error"),
        ("LVA002", "warning"),
    ]


def test_github_format_escapes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=github` prints escaped workflow commands, one per offence."""
    odd: Path = written(
        tmp_path / "a,b%c.py",
        "def f(items: list[int]) -> None:\n    x = 1\n    for y in items:\n        pass\n",
    )
    assert cli.main(["--format=github", str(odd)]) == cli.EXIT_FOUND
    escaped: str = str(odd).replace("%", "%25").replace(":", "%3A").replace(",", "%2C")
    assert capsys.readouterr().out == (
        f"::error file={escaped},line=2,col=5,title=LVA001::"
        "local variable 'x' is not annotated where it's first bound\n"
        f"::warning file={escaped},line=3,col=9,title=LVA002::"
        "for/match variable 'y' is untyped; declare it before the statement\n"
    )


def test_sarif_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=sarif` prints a SARIF log with each result's level."""
    broken: Path = written(tmp_path / "broken.py", BROKEN)
    assert cli.main(["--format=sarif", str(broken)]) == cli.EXIT_FOUND
    sarif: _Sarif = cast("_Sarif", json.loads(capsys.readouterr().out))
    results: list[dict[str, _Json]] = sarif["runs"][0]["results"]
    assert [(r["ruleId"], r["level"]) for r in results] == [
        ("LVA001", "error"),
        ("LVA001", "error"),
        ("LVA002", "warning"),
    ]
    assert results[0]["locations"] == [
        {
            "physicalLocation": {
                "artifactLocation": {"uri": broken.as_posix()},
                "region": {"startLine": 3, "startColumn": 5},
            },
        },
    ]


def _sarif_schema() -> bytes:
    """Read the SARIF schema, fetching it the first time; offline, skip (never in CI).

    Returns:
      Its bytes, their SHA-256 checked.

    Raises:
      OSError: it can't be fetched, in CI.

    """
    if not SARIF_SCHEMA.exists():
        SARIF_SCHEMA.parent.mkdir(parents=True, exist_ok=True)
        try:
            _ = urllib.request.urlretrieve(SARIF_SCHEMA_URL, SARIF_SCHEMA)  # a pinned https URL
        except OSError as error:  # URLError is one
            if os.environ.get("CI"):
                raise
            pytest.skip(f"can't fetch the SARIF schema: {error}")
    schema: bytes = SARIF_SCHEMA.read_bytes()
    assert hashlib.sha256(schema).hexdigest() == SARIF_SCHEMA_SHA256
    return schema


def _replacement(result: dict[str, _Json]) -> tuple[_Json, _Json]:
    fixes: list[_JsonObject] = cast("list[_JsonObject]", result[FIXES])
    changes: list[_JsonObject] = cast("list[_JsonObject]", fixes[0]["artifactChanges"])
    replacement: _JsonObject = cast("list[_JsonObject]", changes[0]["replacements"])[0]
    return replacement["deletedRegion"], replacement["insertedContent"]


def test_sarif_links_rules_and_offers_certain_fixes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Each SARIF rule links to its docs; each certain fix is a SARIF fix, and the log is valid."""
    source: Path = written(
        tmp_path / "fixable.py",
        """
        def fixable(items: list[int]) -> None:
            plain = 1
            for loop in items:
                pass
            é = "x"; ü = 2
            guess = Thing()
        """,
    )
    assert cli.main(["--format=sarif", str(source)]) == cli.EXIT_FOUND
    out: str = capsys.readouterr().out
    schema: _JsonObject = cast("_JsonObject", json.loads(_sarif_schema()))
    log: _JsonObject = cast("_JsonObject", json.loads(out))  # a copy: validating fills in defaults
    valid: _JsonObject = cast("_JsonObject", fastjsonschema.validate(schema, log))
    assert valid == log
    sarif: _Sarif = cast("_Sarif", json.loads(out))
    run: _JsonObject = cast("_JsonObject", sarif["runs"][0])
    driver: _JsonObject = cast("_JsonObject", cast("_JsonObject", run["tool"])["driver"])
    rules: list[_JsonObject] = cast("list[_JsonObject]", driver["rules"])
    assert all(rule["helpUri"] == RULES_URL for rule in rules)
    results: list[_JsonObject] = cast("list[_JsonObject]", run["results"])
    assert [_replacement(r) for r in results[:4]] == [
        ({"startLine": 3, "startColumn": 10, "endLine": 3, "endColumn": 10}, {"text": ": int"}),
        ({"startLine": 4, "startColumn": 1, "endLine": 4, "endColumn": 1}, {"text": "    loop: int\n"}),
        # Columns count characters (`columnKind`), where the offence's count UTF-8 bytes.
        ({"startLine": 6, "startColumn": 6, "endLine": 6, "endColumn": 6}, {"text": ": str"}),
        ({"startLine": 6, "startColumn": 15, "endLine": 6, "endColumn": 15}, {"text": ": int"}),
    ]
    assert FIXES not in results[4]  # a guess (`--unsafe-fixes`) isn't offered


def test_gitlab_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=gitlab` is Code Climate JSON with fingerprints unique per offence."""
    demo: Path = written(tmp_path / "demo.py", DEMO + "  a = 2\n")
    assert cli.main(["--format=gitlab", str(demo)]) == cli.EXIT_FOUND
    issues: list[dict[str, _Json]] = cast("list[dict[str, _Json]]", json.loads(capsys.readouterr().out))
    assert [(i["check_name"], i["severity"], i["location"]) for i in issues] == [
        ("LVA001", "major", {"path": demo.as_posix(), "lines": {"begin": 2}}),
        ("LVA001", "major", {"path": demo.as_posix(), "lines": {"begin": 3}}),
        ("LVA002", "minor", {"path": demo.as_posix(), "lines": {"begin": 4}}),
    ]
    assert len({str(i["fingerprint"]) for i in issues}) == len(issues)


def test_junit_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=junit` is a test suite per file, with a failed test case per offence."""
    demo: Path = written(tmp_path / "demo.py", DEMO)
    assert cli.main(["--format=junit", str(demo)]) == cli.EXIT_FOUND
    out: str = capsys.readouterr().out
    assert out.startswith(
        "<?xml version='1.0' encoding='utf-8'?>\n<testsuites name=\"constricter\" tests=\"3\"",
    )
    assert f'<testcase name="LVA002 c" classname="{demo}">' in out
    assert out.count("<failure ") == out.count("</testcase>") == len(DEMO_CODES)


def test_rdjson_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=rdjson` is reviewdog's JSON; a certain fix is a suggestion at the name's end."""
    demo: Path = written(tmp_path / "demo.py", DEMO)
    assert cli.main(["--format=rdjson", str(demo)]) == cli.EXIT_FOUND
    report: dict[str, list[_JsonObject]] = cast(
        "dict[str, list[_JsonObject]]",
        json.loads(capsys.readouterr().out),
    )
    first: dict[str, _Json] = report["diagnostics"][0]
    assert first["severity"] == RDJSON_ERROR
    end: dict[str, int] = {"line": 2, "column": 4}
    assert first["suggestions"] == [{"range": {"start": end, "end": end}, "text": ": int"}]
    assert set(report["diagnostics"][1]) == set(first) - {"suggestions"}  # `b = []` has no fix


def test_rdjson_declares_a_loop_target_on_a_line_of_its_own(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A loop target's suggestion is a declaration before the loop, not `for x: T in ...`."""
    loop: Path = written(
        tmp_path / "loop.py",
        "def f(items: list[str]) -> None:\n    for x in items:\n        pass\n",
    )
    assert cli.main(["--format=rdjson", str(loop)]) == cli.EXIT_CLEAN
    report: dict[str, list[_JsonObject]] = cast(
        "dict[str, list[_JsonObject]]",
        json.loads(capsys.readouterr().out),
    )
    start: dict[str, int] = {"line": 2, "column": 1}
    assert report["diagnostics"][0]["suggestions"] == [
        {"range": {"start": start, "end": start}, "text": "    x: str\n"},
    ]
