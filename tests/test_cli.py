# SPDX-License-Identifier: MIT
"""The `constricter` command: file discovery, `# noqa`, output and exit status."""

import hashlib
import io
import json
import os
import runpy
import sys
import textwrap
import urllib.request
from pathlib import Path
from typing import Final, TypeAlias, cast

import fastjsonschema
import pytest

from constricter.cli import command as cli
from constricter.cli import config, paths

BROKEN: Final = """
def broken(items: list[int]) -> None:
    plain = 1
    other = 2  # noqa: LVA001
    third = 3  # noqa
    fourth = 4  # noqa: E501
    for loop in items:
        pass
    for hushed in items:  # noqa: LVA002
        pass
"""
ONE_CLEAN_FILE: Final = "Found 0 error(s) and 0 warning(s) in 1 file(s).\n"
PLAIN: Final = "local variable 'plain' is not annotated where it's first bound"
FOURTH: Final = "local variable 'fourth' is not annotated where it's first bound"
LOOP: Final = "for/match variable 'loop' is untyped; declare it before the statement"
_Json: TypeAlias = "str | int | float | bool | list[_Json] | dict[str, _Json] | None"
_JsonObject: TypeAlias = dict[str, _Json]
_Sarif: TypeAlias = dict[str, list[dict[str, list[dict[str, _Json]]]]]
# SARIF 2.1.0's JSON schema, from SchemaStore at a pinned commit, fetched once into `local/` (not
# distributed here) and checked against its SHA-256.
SARIF_SCHEMA: Final = Path(__file__).resolve().parents[1] / "local" / "sarif-2.1.0.json"
SARIF_SCHEMA_URL: Final = (
    "https://raw.githubusercontent.com/SchemaStore/schemastore/"
    "2aded6096789c43a722556cf5019464ee747e495/src/schemas/json/sarif-2.1.0.json"
)
SARIF_SCHEMA_SHA256: Final = "c96eb2d311c37b0a38cbd18c52d79a68f778bbd2d831abed7412d9850740f785"
FIXES: Final = "fixes"
RULES_URL: Final = "https://github.com/ivylikethevine/python-constricter#rules"
CLEAN: Final = """
def clean() -> None:
    fine: int = 1
"""


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def test_reports_unsuppressed_offences_and_exits_1(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Unsuppressed offences print with their severity; an error exits 1."""
    broken: Path = _write(tmp_path / "broken.py", BROKEN)
    assert cli.main([str(broken)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out == (
        f"{broken}:3:5: error: LVA001 {PLAIN}\n"
        f"{broken}:6:5: error: LVA001 {FOURTH}\n"
        f"{broken}:7:9: warning: LVA002 {LOOP}\n"
        "Found 2 error(s) and 1 warning(s) in 1 file(s).\n"
    )


@pytest.mark.parametrize(
    ("level", "status", "summary"),
    [
        ("relaxed", cli.EXIT_CLEAN, "Found 0 error(s) and 3 warning(s)"),
        ("0", cli.EXIT_CLEAN, "Found 0 error(s) and 3 warning(s)"),
        ("constrict", cli.EXIT_FOUND, "Found 3 error(s) and 0 warning(s)"),
    ],
)
def test_level_sets_what_is_an_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    level: str,
    status: int,
    summary: str,
) -> None:
    """`--level` decides which codes are errors; warnings alone exit 0."""
    broken: Path = _write(tmp_path / "broken.py", BROKEN)
    assert cli.main([f"--level={level}", str(broken)]) == status
    assert capsys.readouterr().out.splitlines()[-1].startswith(summary)


def test_clean_files_exit_0_and_quiet_drops_the_summary(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A clean file exits 0; `-q` drops the summary."""
    clean: Path = _write(tmp_path / "clean.py", CLEAN)
    assert cli.main([str(clean)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out == ONE_CLEAN_FILE
    assert cli.main(["-q", str(clean)]) == cli.EXIT_CLEAN
    assert not capsys.readouterr().out


def test_directories_skip_hidden_and_tool_dirs_and_honour_exclude(tmp_path: Path) -> None:
    """Directory walks skip hidden and tool directories and `--exclude` globs."""
    name: str
    for name in ("a.py", "pkg/b.py", "pkg/fixtures/c.py", ".venv/d.py", "pkg/__pycache__/e.py", "venv/f.py"):
        _ = _write(tmp_path / name, CLEAN)
    _ = _write(tmp_path / "notes.txt", "")
    found: list[Path] = list(paths.python_files([tmp_path], ["*/fixtures/*"]))
    assert found == [tmp_path / "a.py", tmp_path / "pkg" / "b.py"]
    # A file named explicitly is checked even where a directory walk would skip it.
    assert list(paths.python_files([tmp_path / ".venv" / "d.py"])) == [tmp_path / ".venv" / "d.py"]
    assert not list(paths.python_files([tmp_path / "a.py"], ["a.py"]))


def test_exclude_also_skips_a_directory_by_name(tmp_path: Path) -> None:
    """`--exclude` prunes a directory walk by directory name too, like the built-in skip list."""
    name: str
    for name in ("a.py", "pkg/b.py", "pkg/generated/c.py"):
        _ = _write(tmp_path / name, CLEAN)
    found: list[Path] = list(paths.python_files([tmp_path], ["generated"]))
    assert found == [tmp_path / "a.py", tmp_path / "pkg" / "b.py"]


def test_defaults_to_the_current_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """With no paths it checks the current directory."""
    _ = _write(tmp_path / "clean.py", CLEAN)
    monkeypatch.chdir(tmp_path)
    assert cli.main([]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out == ONE_CLEAN_FILE


def test_unparsable_files_exit_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """An unparsable file is reported on stderr and exits 2; the rest are still checked."""
    bad: Path = _write(tmp_path / "bad.py", "def (:\n")
    broken: Path = _write(tmp_path / "broken.py", BROKEN)
    assert cli.main([str(bad), str(broken)]) == cli.EXIT_ERROR
    out: str
    err: str
    out, err = capsys.readouterr()
    assert err.startswith(f"{bad}: error: ")
    assert out.endswith("Found 2 error(s) and 1 warning(s) in 2 file(s).\n")


def test_runs_as_a_module(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`python -m constricter` runs the command."""
    monkeypatch.setattr(sys, "argv", ["constricter", str(_write(tmp_path / "clean.py", CLEAN))])
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = runpy.run_module("constricter", run_name="__main__")
    assert exit_info.value.code == cli.EXIT_CLEAN
    assert capsys.readouterr().out.startswith("Found 0")


def test_type_comments_flag(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--type-comments` counts `x = 1  # type: int` as annotated."""
    typed: Path = _write(tmp_path / "typed.py", "def f() -> None:\n    x = 1  # type: int\n")
    assert cli.main(["-q", str(typed)]) == cli.EXIT_FOUND
    assert cli.main(["-q", "--type-comments", str(typed)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.count("LVA001") == 1


def test_json_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=json` prints one object per offence."""
    broken: Path = _write(tmp_path / "broken.py", BROKEN)
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
        "fix": {"annotation": "int", "reason": "a literal", "unsafe": False},
    }
    assert [(r["code"], r["severity"]) for r in results] == [
        ("LVA001", "error"),
        ("LVA001", "error"),
        ("LVA002", "warning"),
    ]


def test_github_format_escapes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=github` prints escaped workflow commands, one per offence."""
    odd: Path = _write(
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
    broken: Path = _write(tmp_path / "broken.py", BROKEN)
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
    source: Path = _write(
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


def _pyproject(directory: Path, text: str) -> None:
    _ = (directory / "pyproject.toml").write_text(text, encoding="utf-8", newline="\n")


def test_pyproject_sets_the_defaults(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The nearest `pyproject.toml`'s `[tool.constricter]` sets the defaults; flags still win."""
    _pyproject(
        tmp_path,
        """
[tool.constricter]
level = "constrict"
exclude = ["skipped.py"]
type-comments = true
all-scopes = true
""",
    )
    source: str = (
        "LIMIT = 1\ndef f(items: list[int]) -> None:\n  x = 1  # type: int\n  for y in items:\n    pass\n"
    )
    _ = _write(tmp_path / "pkg" / "checked.py", source)
    _ = _write(tmp_path / "pkg" / "skipped.py", "def f() -> None:\n  z = 1\n")
    monkeypatch.chdir(tmp_path / "pkg")
    assert cli.main(["."]) == cli.EXIT_FOUND
    out: str = capsys.readouterr().out
    assert [(line.split(": ")[1], line.split(": ")[2][:6]) for line in out.splitlines()[:-1]] == [
        ("error", "LVA004"),
        ("error", "LVA002"),
    ]
    assert out.endswith("Found 2 error(s) and 0 warning(s) in 1 file(s).\n")
    assert cli.main(["--level=0", "."]) == cli.EXIT_CLEAN


def test_pyproject_level_can_be_a_number(tmp_path: Path) -> None:
    """`level` takes a number too."""
    _pyproject(tmp_path, "[tool.constricter]\nlevel = 3\n")
    assert config.config_defaults(tmp_path) == {"level": "3"}


def test_no_table_or_no_pyproject_sets_nothing(tmp_path: Path) -> None:
    """A `pyproject.toml` without the table, or none at all, sets no defaults."""
    _pyproject(tmp_path, '[project]\nname = "x"\n')
    assert not config.config_defaults(tmp_path)
    assert not config.config_defaults(Path(tmp_path.anchor))


@pytest.mark.parametrize(
    "text",
    [
        '[tool.constricter]\nlevel = "tight"\n',
        "[tool.constricter]\nlevel = true\n",
        '[tool.constricter]\nexclude = "x"\n',
        "[tool.constricter]\nexclude = [1]\n",
        "[tool.constricter]\nall-scopes = 1\n",
        "[tool.constricter]\ncolour = 1\n",
        "[tool.constricter]\nnesting = 0\n",
        "[tool.constricter]\nnesting = true\n",
        '[tool.constricter]\nselect = "LVA001"\n',
        '[tool.constricter]\nselect = ["XYZ"]\n',
        "[tool.constricter]\njobs = -1\n",
        "[tool.constricter]\nper-path-levels = 1\n",
        '[tool.constricter.per-path-levels]\n"t/*" = "tight"\n',
        "[tool.constricter]\nper-file-ignores = 1\n",
        '[tool.constricter.per-file-ignores]\n"t/*" = ["XYZ"]\n',
        "[tool.constricter]\nnarrower = 1\n",
        '[tool.constricter.narrower]\nUserId = "str"\n',
        "[tool]\nconstricter = 1\n",
        "not toml [",
    ],
)
def test_a_bad_pyproject_exits_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    text: str,
) -> None:
    """An unreadable `pyproject.toml`, or a bad key or value in the table, exits 2."""
    _pyproject(tmp_path, text)
    monkeypatch.chdir(tmp_path)
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main([])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert f"{tmp_path / 'pyproject.toml'}: " in capsys.readouterr().err


def test_fix_adds_the_annotations_values_decide(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--fix` annotates what's certain in place (keeping line endings); `--unsafe-fixes` adds guesses."""
    source: bytes = (
        b"def f() -> None:\r\n  a = 1; b = 'x'\r\n  c = []\r\n  d = 2  # noqa: LVA001\r\n  e = Path()\r\n"
    )
    path: Path = tmp_path / "fixable.py"
    _ = path.write_bytes(source)
    assert cli.main(["--fix", str(path)]) == cli.EXIT_FOUND
    assert path.read_bytes() == source.replace(b"a = 1; b = 'x'", b"a: int = 1; b: str = 'x'")
    out: str = capsys.readouterr().out
    assert out.startswith(f"{path}:3:3: error: LVA001 local variable 'c'")
    assert out.endswith(
        "Found 2 error(s) and 0 warning(s) in 1 file(s); fixed 2; 1 more with --unsafe-fixes.\n",
    )
    assert cli.main(["--fix", "--unsafe-fixes", "-q", str(path)]) == cli.EXIT_FOUND
    assert path.read_bytes().endswith(b"  e: Path = Path()\r\n")
    _ = capsys.readouterr()
    assert cli.main(["--fix", str(path)]) == cli.EXIT_FOUND  # only `c = []` is left, and it can't be fixed
    assert capsys.readouterr().out.endswith("Found 1 error(s) and 0 warning(s) in 1 file(s); fixed 0.\n")
    assert cli.fix_file(path, []) == 0


def test_relaxed_hides_vague_and_nested_annotations(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """LVA005 and LVA006 aren't reported at `relaxed`; `--nesting` sets LVA006's depth."""
    path: Path = _write(tmp_path / "vague.py", "def f() -> None:\n  x: list[list[Any]] = []\n")
    assert cli.main(["-q", "--level=relaxed", str(path)]) == cli.EXIT_CLEAN
    assert not capsys.readouterr().out
    assert cli.main(["-q", "--nesting=2", str(path)]) == cli.EXIT_CLEAN
    assert [line.split(": ")[2][:6] for line in capsys.readouterr().out.splitlines()] == ["LVA005", "LVA006"]


@pytest.mark.parametrize("nesting", ["0", "x", "-1"])
def test_a_bad_nesting_exits_2(nesting: str, capsys: pytest.CaptureFixture[str]) -> None:
    """`--nesting` takes a whole number of at least 1."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main([f"--nesting={nesting}"])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith(f"expected a whole number of at least 1, not {nesting!r}\n")


def test_pyproject_nesting(tmp_path: Path) -> None:
    """`nesting` in `[tool.constricter]` takes a whole number of at least 1."""
    _pyproject(tmp_path, "[tool.constricter]\nnesting = 3\n")
    assert config.config_defaults(tmp_path) == {"nesting": 3}


RDJSON_ERROR: Final = "ERROR"
DEMO_CODES: Final = ("LVA001", "LVA001", "LVA002")
ALL_BASELINED: Final = "Found 0 error(s) and 0 warning(s) in 1 file(s); 3 baselined.\n"
DEMO: Final = "def f(items: list[int]) -> None:\n  a = 1\n  b = []\n  for c in items:\n    pass\n"


@pytest.mark.parametrize("code", ["LVA001", "LVA002", "LVA003", "LVA004", "LVA005", "LVA006"])
def test_explain_prints_each_code(code: str, capsys: pytest.CaptureFixture[str]) -> None:
    """`--explain` prints a code's message, rationale and levels, then exits 0."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main(["--explain", code])
    assert exit_info.value.code == cli.EXIT_CLEAN
    out: str = capsys.readouterr().out
    assert out.startswith(f"{code}: ")
    assert out.rstrip().endswith("suffocate: error")


def test_statistics_counts_each_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--statistics` prints a count per code instead of each offence."""
    path: Path = _write(tmp_path / "demo.py", DEMO)
    assert cli.main(["--statistics", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines() == [
        "    2  LVA001  error",
        "    1  LVA002  warning",
        "Found 2 error(s) and 1 warning(s) in 1 file(s).",
    ]


def test_select_and_ignore(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--select` keeps only matching codes or prefixes; `--ignore` drops them."""
    path: Path = _write(tmp_path / "demo.py", DEMO)
    assert cli.main(["-q", "--select", "lva002", str(path)]) == cli.EXIT_CLEAN
    assert [line.split(": ")[2][:6] for line in capsys.readouterr().out.splitlines()] == ["LVA002"]
    assert cli.main(["-q", "--select", "LVA00", "--ignore", "LVA001,LVA002", str(path)]) == cli.EXIT_CLEAN
    assert not capsys.readouterr().out


def test_pyproject_select_and_ignore(tmp_path: Path) -> None:
    """`select` and `ignore` in `[tool.constricter]` take lists of codes."""
    _pyproject(tmp_path, '[tool.constricter]\nselect = ["LVA001"]\nignore = ["LVA002"]\n')
    assert config.config_defaults(tmp_path) == {"select": ["LVA001"], "ignore": ["LVA002"]}


def test_a_select_matching_no_code_exits_2(capsys: pytest.CaptureFixture[str]) -> None:
    """A code or prefix that matches no code is an error."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main(["--select", "LVA001,XYZ"])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("no code starts with XYZ\n")


def test_diff_prints_the_fixes_and_changes_nothing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--diff` prints what `--fix` would change, exits 1 if anything would, and writes nothing."""
    path: Path = _write(tmp_path / "demo.py", DEMO)
    assert cli.main(["--diff", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out == (
        f"--- {path}\n+++ {path}\n@@ -1,5 +1,6 @@\n"
        " def f(items: list[int]) -> None:\n-  a = 1\n+  a: int = 1\n"
        "   b = []\n+  c: int\n   for c in items:\n     pass\n"
    )
    assert path.read_text(encoding="utf-8") == DEMO
    clean: Path = _write(tmp_path / "clean.py", CLEAN)
    assert cli.main(["--diff", str(clean)]) == cli.EXIT_CLEAN
    assert not capsys.readouterr().out
    bad: Path = _write(tmp_path / "bad.py", "def (:\n")
    assert cli.main(["--diff", str(bad)]) == cli.EXIT_ERROR


def test_fix_and_diff_cant_be_combined(capsys: pytest.CaptureFixture[str]) -> None:
    """`--fix --diff` is an error."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main(["--fix", "--diff"])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith(
        "--fix, --diff, --write-baseline and --coverage can't be combined\n",
    )


def test_per_path_levels(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`per-path-levels` sets the level for files matching a glob; the first match wins."""
    _pyproject(tmp_path, '[tool.constricter.per-path-levels]\n"tests/*" = "relaxed"\n"*.py" = 2\n')
    _ = _write(tmp_path / "tests" / "demo.py", DEMO)
    _ = _write(tmp_path / "src" / "demo.py", DEMO)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["--statistics", "tests"]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.splitlines()[:2] == ["    2  LVA001  warning", "    1  LVA002  warning"]
    assert cli.main(["--statistics", "src"]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.splitlines()[:2] == ["    2  LVA001  error", "    1  LVA002  error"]


@pytest.mark.parametrize("jobs", ["2", "0"])
def test_jobs_check_files_in_parallel_in_order(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    jobs: str,
) -> None:
    """`--jobs` checks files in parallel, and reports them in the same order as one at a time."""
    name: str
    for name in ("a.py", "b.py", "c.py"):
        _ = _write(tmp_path / name, DEMO)
    _ = _write(tmp_path / "bad.py", "def (:\n")
    assert cli.main(["--jobs=1", str(tmp_path)]) == cli.EXIT_ERROR
    serial: tuple[str, str] = capsys.readouterr()
    assert cli.main([f"--jobs={jobs}", str(tmp_path)]) == cli.EXIT_ERROR
    assert capsys.readouterr() == serial


def test_pyproject_jobs_and_per_path_levels(tmp_path: Path) -> None:
    """`jobs` takes 0 and up; `per-path-levels` maps globs to levels."""
    _pyproject(
        tmp_path,
        '[tool.constricter]\njobs = 0\n[tool.constricter.per-path-levels]\n"t/*" = "Strict"\n',
    )
    assert config.config_defaults(tmp_path) == {"jobs": 0, "per_path_levels": {"t/*": "strict"}}


def test_importing_the_main_module_doesnt_run_the_command() -> None:
    """`--jobs` workers import `constricter.__main__`; that mustn't run the command again."""
    assert runpy.run_module("constricter", run_name="__mp_main__")["main"] is cli.main


def test_baseline_reports_only_new_offences(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--write-baseline` records every offence; `--baseline` then reports only ones beyond it."""
    path: Path = _write(tmp_path / "src" / "demo.py", DEMO)
    file: Path = tmp_path / "baseline.json"
    assert cli.main(["--baseline", str(file), "--write-baseline", str(path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out == f"Wrote 3 offence(s) to {file}.\n"
    assert json.loads(file.read_text(encoding="utf-8")) == {
        "version": 1,
        "offences": {"src/demo.py": {"LVA001 a": 1, "LVA001 b": 1, "LVA002 c": 1}},
    }
    assert cli.main(["--baseline", str(file), str(path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out == ALL_BASELINED
    # Lines moving doesn't matter; a new offence, even of a baselined name, does.
    _ = path.write_text("\n\n" + DEMO + "  a = 2\n  e = 3\n", encoding="utf-8", newline="\n")
    monkeypatch.chdir(tmp_path / "src")  # paths are relative to the baseline, not the directory
    assert cli.main(["-q", "--baseline", str(file), "demo.py"]) == cli.EXIT_FOUND
    assert [line.split(": ")[2] for line in capsys.readouterr().out.splitlines()] == [
        "LVA001 local variable 'e' is not annotated where it's first bound",
    ]


def test_baseline_from_pyproject_is_relative_to_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`baseline` in `[tool.constricter]` is a path relative to that pyproject.toml."""
    _pyproject(tmp_path, '[tool.constricter]\nbaseline = "ci/baseline.json"\n')
    (tmp_path / "ci").mkdir()
    _ = _write(tmp_path / "pkg" / "demo.py", DEMO)
    monkeypatch.chdir(tmp_path / "pkg")
    assert cli.main(["--write-baseline", "."]) == cli.EXIT_CLEAN
    assert (tmp_path / "ci" / "baseline.json").is_file()
    _ = capsys.readouterr()
    assert cli.main(["-q", "."]) == cli.EXIT_CLEAN


@pytest.mark.parametrize(
    ("args", "error"),
    [
        (["--write-baseline", "--fix", "--baseline=x.json"], "can't be combined"),
        (["--baseline=missing.json"], "can't read the baseline"),
        (["--baseline=bad.json"], "not a constricter baseline"),
        (["--baseline=counts.json"], "not a constricter baseline"),
    ],
)
def test_baseline_errors_exit_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    args: list[str],
    error: str,
) -> None:
    """A missing or malformed baseline, or `--write-baseline` without a file, exits 2."""
    _ = (tmp_path / "bad.json").write_text('{"version": 2, "offences": {}}', encoding="utf-8")
    _ = (tmp_path / "counts.json").write_text(
        '{"version": 1, "offences": {"a.py": {"LVA001 x": true}}}',
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main(args)
    assert exit_info.value.code == cli.EXIT_ERROR
    assert error in capsys.readouterr().err


def test_the_default_baseline_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without `--baseline`, `constricter-baseline.json` next to pyproject.toml is written and used."""
    _pyproject(tmp_path, '[project]\nname = "x"\n')
    _ = _write(tmp_path / "pkg" / "demo.py", DEMO)
    monkeypatch.chdir(tmp_path / "pkg")
    assert cli.main(["-q", "."]) == cli.EXIT_FOUND  # no baseline yet: everything is reported
    assert cli.main(["--write-baseline", "."]) == cli.EXIT_CLEAN
    assert (tmp_path / "constricter-baseline.json").is_file()
    _ = capsys.readouterr()
    assert cli.main(["."]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.endswith("; 3 baselined.\n")


def test_a_baseline_can_have_comments(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A hand-edited baseline may have comments and trailing commas (JSONC)."""
    path: Path = _write(tmp_path / "demo.py", DEMO)
    file: Path = tmp_path / "baseline.json"
    _ = file.write_text(
        (
            '{\n  "version": 1, // hand-edited\n'
            '  "offences": {"demo.py": {"LVA001 a": 1, "LVA001 b": 1,},},\n}\n'
        ),
        encoding="utf-8",
    )
    assert cli.main(["-q", "--baseline", str(file), str(path)]) == cli.EXIT_CLEAN
    assert [line.split(": ")[2][:6] for line in capsys.readouterr().out.splitlines()] == ["LVA002"]


def test_coverage_reports_the_typed_share(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--coverage` prints each file's and the total typed share; `--format=json` too."""
    demo: Path = _write(tmp_path / "demo.py", DEMO)
    clean: Path = _write(tmp_path / "clean.py", CLEAN)
    assert cli.main(["--coverage", str(tmp_path)]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out == (
        f"{clean}: 1/1 typed (100.0%)\n{demo}: 0/3 typed (0.0%)\nTotal: 1/4 typed (25.0%) in 2 file(s).\n"
    )
    assert cli.main(["--coverage", "--format=json", str(demo)]) == cli.EXIT_CLEAN
    assert json.loads(capsys.readouterr().out) == {
        "typed": 0,
        "total": 3,
        "percent": 0.0,
        "files": [{"path": str(demo), "typed": 0, "total": 3, "percent": 0.0}],
    }


def test_fail_under_sets_the_exit_status(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--fail-under PCT` implies `--coverage`, and exits 1 below PCT; an unparsable file exits 2."""
    _ = _write(tmp_path / "demo.py", DEMO)
    _ = _write(tmp_path / "clean.py", CLEAN)
    assert cli.main(["--fail-under=25", str(tmp_path)]) == cli.EXIT_CLEAN
    assert cli.main(["--fail-under=25.1", str(tmp_path)]) == cli.EXIT_FOUND
    _ = _write(tmp_path / "bad.py", "def (:\n")
    assert cli.main(["--coverage", str(tmp_path)]) == cli.EXIT_ERROR
    assert capsys.readouterr().err.startswith(f"{tmp_path / 'bad.py'}: error: ")


@pytest.mark.parametrize("percent", ["-1", "101", "half"])
def test_a_bad_fail_under_exits_2(percent: str, capsys: pytest.CaptureFixture[str]) -> None:
    """`--fail-under` takes a percentage from 0 to 100."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main([f"--fail-under={percent}"])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith(f"expected a percentage from 0 to 100, not {percent!r}\n")


def _stdin(monkeypatch: pytest.MonkeyPatch, text: str) -> None:
    monkeypatch.setattr(sys, "stdin", io.StringIO(text))


def test_stdin_is_checked_under_its_filename(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`-` reads standard input, reported under `--stdin-filename` (default `-`)."""
    _stdin(monkeypatch, DEMO)
    assert cli.main(["-q", "--stdin-filename", "app.py", "-"]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.startswith("app.py:2:3: error: LVA001 local variable 'a'")
    _stdin(monkeypatch, DEMO)
    assert cli.main(["-q", "-"]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.startswith("-:2:3: error:")


def test_stdin_fix_prints_the_fixed_source(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--fix` on standard input prints the fixed source instead of a report; `--diff` diffs it."""
    _stdin(monkeypatch, DEMO)
    assert cli.main(["--fix", "-"]) == cli.EXIT_FOUND  # `b = []` is left, an error
    assert capsys.readouterr().out == DEMO.replace("  a = 1", "  a: int = 1").replace(
        "  for c",
        "  c: int\n  for c",
    )
    _stdin(monkeypatch, DEMO)
    assert cli.main(["--diff", "--stdin-filename", "app.py", "-"]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.startswith("--- app.py\n+++ app.py\n")


def test_stdin_notebook_and_errors(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A `.ipynb` stdin filename reads a notebook; `-` must be the only path; bad input exits 2."""
    _stdin(monkeypatch, '{"cells": [{"cell_type": "code", "source": "def f() -> None:\\n  x = 1\\n"}]}')
    assert cli.main(["-q", "--stdin-filename", "nb.ipynb", "-"]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.startswith("nb.ipynb:cell 1:2:3: error:")
    _stdin(monkeypatch, "def (:\n")
    assert cli.main(["--coverage", "-"]) == cli.EXIT_ERROR
    assert capsys.readouterr().err.startswith("-: error: ")
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main(["-", "src"])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("`-` (standard input) must be the only path\n")


def test_exit_zero_and_output_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--exit-zero` exits 0 despite errors (not for unreadable files); `--output-file` gets the report."""
    demo: Path = _write(tmp_path / "demo.py", DEMO)
    report: Path = tmp_path / "report.txt"
    assert cli.main(["--exit-zero", "--output-file", str(report), str(demo)]) == cli.EXIT_CLEAN
    assert not capsys.readouterr().out
    assert report.read_text(encoding="utf-8").endswith("Found 2 error(s) and 1 warning(s) in 1 file(s).\n")
    bad: Path = _write(tmp_path / "bad.py", "def (:\n")
    assert cli.main(["--exit-zero", str(bad)]) == cli.EXIT_ERROR


def test_per_file_ignores(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`per-file-ignores` drops codes (or prefixes) for files matching a glob."""
    _pyproject(tmp_path, '[tool.constricter.per-file-ignores]\n"tests/*" = ["LVA001"]\n')
    _ = _write(tmp_path / "tests" / "demo.py", DEMO)
    monkeypatch.chdir(tmp_path)
    assert cli.main(["--statistics", "-q", "tests"]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.split() == ["1", *DEMO_CODES[2:], "warning"]
    assert config.config_defaults(tmp_path) == {"per_file_ignores": {"tests/*": ["LVA001"]}}


def test_gitlab_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=gitlab` is Code Climate JSON with fingerprints unique per offence."""
    demo: Path = _write(tmp_path / "demo.py", DEMO + "  a = 2\n")
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
    demo: Path = _write(tmp_path / "demo.py", DEMO)
    assert cli.main(["--format=junit", str(demo)]) == cli.EXIT_FOUND
    out: str = capsys.readouterr().out
    assert out.startswith(
        "<?xml version='1.0' encoding='utf-8'?>\n<testsuites name=\"constricter\" tests=\"3\"",
    )
    assert f'<testcase name="LVA002 c" classname="{demo}">' in out
    assert out.count("<failure ") == out.count("</testcase>") == len(DEMO_CODES)


def test_rdjson_format(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--format=rdjson` is reviewdog's JSON; a certain fix is a suggestion at the name's end."""
    demo: Path = _write(tmp_path / "demo.py", DEMO)
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
    loop: Path = _write(
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
