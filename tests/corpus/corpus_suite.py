# SPDX-License-Identifier: MIT
"""Run a corpus package's own tests or type checks before and after `--fix`, and `--fix --unsafe-fixes`.

  local/.venv/bin/python tests/corpus/corpus_suite.py                    # every suite's tests
  local/.venv/bin/python tests/corpus/corpus_suite.py NAME ...           # just these
  local/.venv/bin/python tests/corpus/corpus_suite.py --types [NAME ...] # their type checks instead

Each package's source is cloned at its pinned tag into `local/corpus-suites/`, installed there with
its test dependencies as its CI installs them (its own `uv.lock` where it has one, its pins or
requirements where it hasn't), and its tests run three times: as released, after `--fix`, and after
`--fix --unsafe-fixes` (the source reset in between), at `suffocate` with `all-scopes`, as
`tests/corpus/corpus_fix.py` fixes. Each run's outcome is its summary counts and the tests that
failed; the command exits 1 if a fixed run's differs from the released one's. It needs `git`, `uv`,
a C compiler and Rust (pandas, SQLAlchemy and pydantic-core are built) and the network; CI doesn't
run it.

A local variable's annotation is never evaluated at runtime (PEP 526), so these runs catch a fix
that breaks the code itself (a declaration, a dropped comment or annotation, a module's
`__annotations__`), not a wrong type: that's a type checker's job, and `--types` runs each package's
own, as its CI does, the same three times. An error a fixed run has that the released one hasn't
is new; each new one is traced to the fix whose annotation it's about (the fix on its line, else the
nearest one before it in its scope, else the module's, of a name on its line or in its message), and
counted by the mechanisms that decided that fix (`--format=json`'s `kinds`); the command exits 1 if
a fixed run has a new error.
"""

import ast
import difflib
import json
import os
import re
import shlex
import shutil
import subprocess  # runs git, uv, the tests, the type checkers and constricter
import sys
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"


class Suite(NamedTuple):
    """One package's repository, pinned tag and source, and how its CI installs, tests and checks it."""

    repository: str
    tag: str
    source: str  # relative to the checkout
    install: tuple[tuple[str, ...], ...]  # `uv` commands installing it and its tests' dependencies in `.venv`
    tests: tuple[str, ...]  # the command running its tests, the first word from `.venv/bin`
    checks: tuple[tuple[str, ...], ...] = ()  # its CI's type checks, each's first word from `.venv/bin`
    left_out: str = ""  # requirements it can't build here, which `--excludes -` reads


class Outcome(NamedTuple):
    """What one test run gave: its summary counts, and the tests that failed or errored."""

    counts: dict[str, int]
    failed: frozenset[str]


class Complaint(NamedTuple):
    """One type checker error: its file (relative to the checkout), its line, and its message."""

    path: str
    line: int
    message: str


class Fix(NamedTuple):
    """One fix `--format=json` reports: where, the name, its annotation, and what decided it."""

    path: str
    line: int
    name: str
    annotation: str
    kinds: str  # its mechanisms, joined by `+`
    unsafe: bool


WORK: Final = Path(__file__).resolve().parents[2] / "local" / "corpus-suites"
_PYTHON: Final = sys.executable
_VENV: Final = ("venv", "-q", "--allow-existing", "--python", _PYTHON, ".venv")
_PYTEST: Final = "python -m pytest -q -rfE -p no:cacheprovider"


def _words(command: str) -> tuple[str, ...]:
    """Split a command as a shell would.

    Returns:
      Its words.

    """
    return tuple(shlex.split(command))


_PANDAS: Final = (  # its required, build and test dependencies from its `requirements-dev.txt`
    "meson-python>=0.17.1,<1",
    "meson[ninja]>=1.2.1,<2",
    "cython>=3.1.0,<4",
    "numpy>=2.3.3,<3",
    "versioneer[toml]",
    "python-dateutil>=2.8.2",
    "pytest>=8.3.4,<9",  # 9 errors on 72 of its tests' parametrizations
    "pytest-xdist>=3.6.1",
    "hypothesis>=6.116.0",
    "mypy==1.17.1",  # and its type checkers, as its pre-commit hooks pin them
    "types-python-dateutil",
    "pyright==1.1.404",
)
SUITES: Final = {
    # Its CI's test job and linting job (`pyright pydantic`, its pre-commit typecheck hook); its tests
    # of pydantic-core, its Rust core, which `--fix` doesn't touch, are left out.
    "pydantic": Suite(
        "https://github.com/pydantic/pydantic",
        "v2.13.5",
        "pydantic",
        (
            (
                *_words("sync -q --locked --all-packages --all-extras --group testing-extra --group linting"),
                "--python",
                _PYTHON,
            ),
        ),
        _words(f"{_PYTEST} -p no:pretty --ignore=tests/pydantic_core"),
        (_words("pyright pydantic"),),
    ),
    # Its nox `github-cext-greenlet` session on SQLite (every SQLite driver, its C extensions built)
    # and its `pep484` session (`mypy noxfile.py ./lib/sqlalchemy`, strict for the package).
    "sqlalchemy": Suite(
        "https://github.com/sqlalchemy/sqlalchemy",
        "rel_2_0_54",
        "lib/sqlalchemy",
        (_VENV, _words("pip install -q -e . --group tests --group tests-sqlite-asyncio --group mypy")),
        (
            *_words(f"{_PYTEST} -n 4 -m 'not memory_intensive and not mypy' --db sqlite"),
            *_words("--dbdriver sqlite --dbdriver pysqlite_numeric --dbdriver aiosqlite"),
        ),
        (_words("mypy noxfile.py ./lib/sqlalchemy"),),
    ),
    # Its `runtests.py` on SQLite, in one process: on Linux, Python 3.14 starts processes with
    # `forkserver`, which Django 5.2 can't clone a SQLite test database for. It has no type checker.
    # pylibmc needs libmemcached's headers, and its tests need a memcached server, so they skip anyway.
    "django": Suite(
        "https://github.com/django/django",
        "5.2.17",
        "django",
        (_VENV, _words("pip install -q -e . -r tests/requirements/py3.txt --excludes -")),
        _words("python -Wall tests/runtests.py --parallel=1"),
        left_out="pylibmc",
    ),
    # Its CI's unit tests, `-m "not slow and not network and not single_cpu"` (about 190,000, a few
    # minutes over four workers), with its required dependencies and its tests' from its
    # `requirements-dev.txt` (so the optional ones' tests skip); and its manual pre-commit typing
    # hooks, which its code-checks job runs: mypy and pyright. It's built in place, so its Python
    # files are the checkout's.
    "pandas": Suite(
        "https://github.com/pandas-dev/pandas",
        "v3.0.6",
        "pandas",
        (
            _VENV,
            ("pip", "install", "-q", *_PANDAS),
            _words("pip install -q --no-build-isolation -e ."),
        ),
        _words(f"{_PYTEST} -n 4 --dist=worksteal -m 'not slow and not network and not single_cpu' pandas"),
        (("mypy",), ("pyright",)),
    ),
}
_EVERYWHERE: Final = ("--level=suffocate", "--all-scopes", "--jobs=0")
_INSTALLED: Final = ".venv/corpus-suite-installed"  # written once every install command has succeeded
# pytest's `-rfE` lines, and unittest's (Django's runner's) headers of each failure and error
_FAILED: Final = re.compile(r"^(?:FAILED |ERROR |FAIL: |ERROR: )(\S+(?: \([\w.]+\))?)", re.MULTILINE)
_COUNTS: Final = re.compile(r"(\d+) (passed|failed|skipped|xfailed|xpassed|errors?|warnings?)")
_RAN: Final = re.compile(r"^Ran (\d+) tests?", re.MULTILINE)  # unittest's summary starts here
_UNITTEST: Final = re.compile(r"(failures|errors|skipped|expected failures|unexpected successes)=(\d+)")
# mypy's `path:line: error: message` and pyright's `  /path:line:column - error: message`
_ERROR: Final = re.compile(
    r"^[ \t]*(?P<path>[^:\s][^:\n]*\.pyi?):(?P<line>\d+)(?::\d+)?:? (?:- )?error: (?P<message>.+)$",
    re.MULTILINE,
)
_OTHER_LINE: Final = re.compile(r"\bline \d+")  # a message's reference to another line, which a fix moves
_QUOTED: Final = re.compile(r"""["'`]([A-Za-z_]\w*)["'`]""")
_NAME: Final = re.compile(r"[A-Za-z_]\w*")
_CONSTRICTER: Final = Path(sys.executable).with_name("constricter")
_INSERTED: Final = "insert"  # difflib's opcode for lines only the fixed file has
_MODES: Final = (("--fix", ()), ("--fix --unsafe-fixes", ("--unsafe-fixes",)))


def _environment(cwd: Path) -> dict[str, str]:
    """Return this environment for a command in `cwd`, a checkout or where they're cloned.

    Without this checkout's venv or forced colours (which pytest and the type checkers would print
    into the lines read back); with the checkout's venv activated, if it has one yet (pyright finds
    its packages by it); with an absolute uv cache (this project's `cache-dir` is relative, and uv
    finds this `pyproject.toml` above a checkout without its own `[tool.uv]`); and with a fixed hash
    seed (pytest-xdist's workers must collect the same tests).

    Returns:
      The environment.

    """
    environment: dict[str, str] = {
        key: value
        for key, value in os.environ.items()
        if key not in {"UV_PROJECT_ENVIRONMENT", "FORCE_COLOR", "VIRTUAL_ENV"}
    }
    venv: Path = cwd / ".venv"
    if venv.is_dir():
        environment["VIRTUAL_ENV"] = str(venv)
        environment["PATH"] = os.pathsep.join((str(venv / "bin"), environment.get("PATH", os.defpath)))
    _ = environment.setdefault("UV_CACHE_DIR", str(WORK.parent / ".uv-cache"))
    _ = environment.setdefault("PYTHONHASHSEED", "0")
    return environment


def _run(args: Sequence[str], cwd: Path, given: str = "") -> tuple[int, str]:
    """Run a command in `cwd`, with `given` as its standard input.

    Returns:
      Its exit status, and its standard output and error, together.

    """
    done: subprocess.CompletedProcess[str] = subprocess.run(
        list(args),
        input=given,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        cwd=cwd,
        env=_environment(cwd),
    )
    return done.returncode, done.stdout + done.stderr


def _output(args: Sequence[str], cwd: Path) -> str:
    """Run a command in `cwd`.

    Returns:
      Its standard output and error, together.

    """
    return _run(args, cwd)[1]


def _venv(root: Path, command: Sequence[str]) -> list[str]:
    """Take `command`'s first word from the checkout's `.venv/bin`.

    Returns:
      The command.

    """
    return [str(root / ".venv" / "bin" / command[0]), *command[1:]]


def checkout(name: str, suite: Suite) -> Path:
    """Clone (once) `suite` at its tag and install it and its test dependencies (once).

    Returns:
      The checkout.

    Raises:
      RuntimeError: an install command failed.

    """
    root: Path = WORK / f"{name}-{suite.tag}"
    uv: str = os.environ.get("UV") or shutil.which("uv") or "uv"
    if not root.is_dir():
        WORK.mkdir(parents=True, exist_ok=True)
        _ = _output(
            ["git", "clone", "-q", "--depth", "1", "--branch", suite.tag, suite.repository, str(root)],
            WORK,
        )
    if not (root / _INSTALLED).exists():
        command: tuple[str, ...]
        for command in suite.install:
            status: int
            output: str
            status, output = _run([uv, *command], root, suite.left_out)
            if status:
                message: str = f"{name}: uv {' '.join(command)} failed:\n{output}"
                raise RuntimeError(message)
        _ = (root / _INSTALLED).write_text("", encoding="utf-8")
    return root


def tested(root: Path, suite: Suite) -> Outcome:
    """Run the checkout's tests.

    Returns:
      Their outcome.

    """
    output: str = _output(_venv(root, suite.tests), root)
    ran: re.Match[str] | None = _RAN.search(output)
    counts: dict[str, int]
    if ran:
        counts = {"ran": int(ran[1])} | {
            kind: int(n) for kind, n in cast("list[tuple[str, str]]", _UNITTEST.findall(output, ran.end()))
        }
    else:
        summary: str = output.strip().rsplit("\n", 1)[-1]
        counts = {
            kind.rstrip("s") if kind.startswith("error") else kind: int(n)
            for n, kind in cast("list[tuple[str, str]]", _COUNTS.findall(summary))
        }
    return Outcome(counts, frozenset(cast("list[str]", _FAILED.findall(output))))


def fixed(root: Path, suite: Suite, *extra: str) -> str:
    """Reset the checkout's source, then `--fix` it (with `extra` options).

    Returns:
      The size of the change, as `git diff --shortstat` puts it.

    """
    _ = _output(["git", "checkout", "-q", "--", suite.source], root)
    _ = _output([str(_CONSTRICTER), "--fix", *extra, *_EVERYWHERE, "-q", suite.source], root)
    return _output(["git", "diff", "--shortstat"], root).strip()


def complaints(root: Path, suite: Suite) -> list[Complaint]:
    """Run the checkout's type checks.

    Returns:
      Their errors, each file relative to the checkout.

    """
    found: list[Complaint] = []
    check: tuple[str, ...]
    for check in suite.checks:
        match: re.Match[str]
        for match in _ERROR.finditer(_output(_venv(root, check), root)):
            path: Path = Path(match["path"])
            relative: str = str(path.relative_to(root) if path.is_relative_to(root) else path)
            found.append(Complaint(relative, int(match["line"]), match["message"].strip()))
    return found


def _key(complaint: Complaint) -> tuple[str, str]:
    """Identify an error across a fix, which moves lines.

    Returns:
      Its file and message, any line it refers to left out.

    """
    return complaint.path, _OTHER_LINE.sub("line N", complaint.message)


def planned(root: Path, suite: Suite, *extra: str) -> dict[str, list[Fix]]:
    """Reset the checkout's source, and list the fixes `--fix` (with `extra` options) makes in it.

    Returns:
      Them, per file.

    """
    _ = _output(["git", "checkout", "-q", "--", suite.source], root)
    results: list[dict[str, _Json]] = cast(
        "list[dict[str, _Json]]",
        json.loads(_output([str(_CONSTRICTER), "--format=json", *extra, *_EVERYWHERE, suite.source], root)),
    )
    fixes: dict[str, list[Fix]] = {}
    result: dict[str, _Json]
    for result in results:
        fix: dict[str, _Json] | None = cast("dict[str, _Json] | None", result.get("fix"))
        quoted: re.Match[str] | None = re.search(r"'([^']+)'", str(result["message"]))
        if fix and quoted and (extra or not fix["unsafe"]):
            fixes.setdefault(str(result["path"]), []).append(
                Fix(
                    str(result["path"]),
                    cast("int", result["line"]),
                    quoted[1],
                    str(fix["annotation"]),
                    "+".join(cast("list[str]", fix["kinds"])),
                    bool(fix["unsafe"]),
                ),
            )
    return fixes


def _origins(original: list[str], changed: list[str]) -> list[int]:
    """Map each line of a fixed file to the original line it came from (1-based).

    A changed line maps to the line it replaced; an inserted one (a declaration) to the statement
    after it, which it declares a name for.

    Returns:
      The original line of each fixed one, the first at index 1.

    """
    origins: list[int] = [0] * (len(changed) + 1)
    tag: str
    i1: int
    i2: int
    j1: int
    j2: int
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, original, changed, autojunk=False).get_opcodes():
        j: int
        for j in range(j1, j2):
            origins[j + 1] = i1 + 1 if tag == _INSERTED else i1 + 1 + min(j - j1, max(i2 - i1 - 1, 0))
    return origins


def _scopes(source: str) -> list[int]:
    """Map each line of a file to the function, lambda or class it's in.

    Returns:
      The first line of each line's innermost one (0: the module), the first at index 1; all 0 if
      the file doesn't parse.

    """
    scopes: list[int] = [0] * (source.count("\n") + 2)
    try:
        tree: ast.Module = ast.parse(source)
    except SyntaxError:
        return scopes
    node: ast.AST
    for node in ast.walk(tree):  # breadth first: an inner scope overwrites its outer one
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            line: int
            for line in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                scopes[line] = node.lineno
    return scopes


class _Fixed(NamedTuple):
    """A fixed file: its lines, each's original line, and each original line's scope."""

    lines: list[str]
    origins: list[int]
    scopes: list[int]


def _fixed_file(root: Path, path: str) -> _Fixed:
    """Read a fixed file, and map it to its original (`HEAD`'s).

    Returns:
      It.

    """
    original: str = _output(["git", "show", f"HEAD:{path}"], root)
    lines: list[str] = (root / path).read_text("utf-8").splitlines()
    return _Fixed(lines, _origins(original.splitlines(), lines), _scopes(original))


def _blamed(complaint: Complaint, file: _Fixed, fixes: list[Fix]) -> Fix | None:
    """Return the fix a new error is about, if one can be told.

    The fix on its (original) line, preferring one whose name its message quotes; else the nearest
    fix before it in its scope of a name its line or its message has; else the module's last fix of
    such a name (a global it reads).

    Returns:
      The fix, or None.

    """
    origin: int = file.origins[complaint.line] if complaint.line < len(file.origins) else 0
    text: str = file.lines[complaint.line - 1] if complaint.line <= len(file.lines) else ""
    names: set[str] = set(_QUOTED.findall(complaint.message)) | set(_NAME.findall(text))
    here: list[Fix] = sorted(
        (fix for fix in fixes if fix.line == origin),
        key=lambda fix: fix.name not in names,
    )
    if here:
        return here[0]
    scope: int = file.scopes[origin] if origin < len(file.scopes) else -1
    named: list[Fix] = [fix for fix in fixes if fix.name in names and fix.line < len(file.scopes)]
    candidates: list[Fix] = [
        fix for fix in named if fix.line < origin and file.scopes[fix.line] == scope
    ] or [fix for fix in named if not file.scopes[fix.line]]
    return max(candidates, key=lambda fix: fix.line) if candidates else None


def _report_new(root: Path, new: list[Complaint], fixes: dict[str, list[Fix]]) -> None:
    """Print each new error with the fix it's traced to, and their count per mechanism."""
    per_kind: Counter[str] = Counter()
    lines: list[str] = []
    files: dict[str, _Fixed] = {}
    complaint: Complaint
    for complaint in new:
        if complaint.path not in files:
            files[complaint.path] = _fixed_file(root, complaint.path)
        fix: Fix | None = _blamed(complaint, files[complaint.path], fixes.get(complaint.path, []))
        kind: str = "(untraced)" if fix is None else fix.kinds + (" (guess)" if fix.unsafe else "")
        per_kind[kind] += 1
        what: str = "" if fix is None else f" [{fix.name}: {fix.annotation}, line {fix.line}]"
        lines.append(f"      {kind}: {complaint.path}:{complaint.line}{what}: {complaint.message}\n")
    count: int
    for kind, count in per_kind.most_common():
        _ = sys.stdout.write(f"    {kind}: {count}\n")
    _ = sys.stdout.writelines(sorted(lines))


def _compare_types(
    root: Path,
    suite: Suite,
    released: list[Complaint],
    label: str,
    options: tuple[str, ...],
) -> bool:
    """Fix the checkout's source with `options`, type-check it, and print what's new since `released`.

    Returns:
      Whether nothing is.

    """
    fixes: dict[str, list[Fix]] = planned(root, suite, *options)
    change: str = fixed(root, suite, *options)
    after: list[Complaint] = complaints(root, suite)
    before: Counter[tuple[str, str]] = Counter(_key(complaint) for complaint in released)
    now: Counter[tuple[str, str]] = Counter(_key(complaint) for complaint in after)
    added: Counter[tuple[str, str]] = now - before
    new: list[Complaint] = []
    complaint: Complaint
    for complaint in after:  # which of a file's alike errors are new can't be told: say the first
        if added[_key(complaint)]:
            new.append(complaint)
            added[_key(complaint)] -= 1
    _ = sys.stdout.write(
        f"  {label} ({change}): {len(after)} errors: {len(new)} new, {(before - now).total()} gone\n",
    )
    _report_new(root, new, fixes)
    return not new


def check_types(names: Sequence[str]) -> int:
    """Run each suite's type checks (default: every one's) as released, fixed, and fixed with guesses.

    Returns:
      0 if no fixed run has an error its released one hasn't, else 1.

    """
    clean: bool = True
    name: str
    for name in names or [name for name, suite in SUITES.items() if suite.checks]:
        suite: Suite = SUITES[name]
        root: Path = checkout(name, suite)
        _ = _output(["git", "checkout", "-q", "--", suite.source], root)
        released: list[Complaint] = complaints(root, suite)
        checks: str = "; ".join(" ".join(check) for check in suite.checks)
        _ = sys.stdout.write(f"{name} {suite.tag}: {checks}: released: {len(released)} errors\n")
        label: str
        options: tuple[str, ...]
        for label, options in _MODES:
            clean = _compare_types(root, suite, released, label, options) and clean
        _ = _output(["git", "checkout", "-q", "--", suite.source], root)
    return 0 if clean else 1


def main(argv: Sequence[str]) -> int:
    """Run each suite named (default: all) as released, fixed, and fixed with guesses.

    Returns:
      0 if every fixed run's outcome matches its released one, else 1.

    """
    if argv[:1] == ["--types"]:
        return check_types(argv[1:])
    same: bool = True
    name: str
    for name in argv or SUITES:
        suite: Suite = SUITES[name]
        root: Path = checkout(name, suite)
        _ = _output(["git", "checkout", "-q", "--", suite.source], root)
        released: Outcome = tested(root, suite)
        _ = sys.stdout.write(f"{name} {suite.tag}: released: {released.counts}\n")
        label: str
        options: tuple[str, ...]
        test: str
        for label, options in _MODES:
            change: str = fixed(root, suite, *options)
            outcome: Outcome = tested(root, suite)
            verdict: str = "same" if outcome == released else "DIFFERENT"
            _ = sys.stdout.write(f"  {label} ({change}): {outcome.counts}: {verdict}\n")
            for test in sorted(outcome.failed ^ released.failed):
                _ = sys.stdout.write(
                    f"    {'now fails' if test in outcome.failed else 'now passes'}: {test}\n",
                )
            same = same and outcome == released
        _ = _output(["git", "checkout", "-q", "--", suite.source], root)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
