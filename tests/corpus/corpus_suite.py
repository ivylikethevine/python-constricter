# SPDX-License-Identifier: MIT
"""Run a corpus package's own tests or type checks before and after `--fix`, and `--fix --unsafe-fixes`.

  local/.venv/bin/python tests/corpus/corpus_suite.py                    # every suite's tests
  local/.venv/bin/python tests/corpus/corpus_suite.py NAME ...           # just these
  local/.venv/bin/python tests/corpus/corpus_suite.py --types [NAME ...] # their type checks instead
  local/.venv/bin/python tests/corpus/corpus_suite.py --types --infer-with basedpyright,ty [NAME ...]

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
is new (of a file's alike errors, those on a line a fix wrote first); each new one is traced to the
fix whose annotation it's about (the fix on its line, else the nearest one before it in its scope,
else the module's, of a name on its line or in its message), and counted by the mechanisms that
decided that fix (`--format=json`'s `kinds`); the command exits 1 if a fixed run has a new error.

`--infer-with CHECKERS` adds a third fixed run, `--fix --unsafe-fixes --infer-with CHECKERS`: the
checkers' servers (on `PATH`, or beside this Python) see the checkout's own environment and settings,
as its type checks do (a checkout with no settings for Pyright or pyrefly is given empty ones, or
their servers read this project's, above it). A hint's fix a later round of `--fix` makes isn't in the
first round's list: an error about one is untraced.
"""

import ast
import difflib
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess  # runs git, uv, the tests, the type checkers and constricter
import sys
import tempfile
from collections import Counter
from collections.abc import Callable, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"


class Suite(NamedTuple):
    """One package's repository, pinned tag and source, and how its CI installs, tests and checks it."""

    repository: str
    tag: str
    source: str  # relative to the checkout
    install: tuple[tuple[str, ...], ...]  # `uv` commands installing it and its tests' dependencies in `.venv`
    # The command running its tests, the first word from `.venv/bin`; `_WORKERS` in a word stands for
    # how many processes it's to take (see `workers`).
    tests: tuple[str, ...]
    checks: tuple[tuple[str, ...], ...] = ()  # its CI's type checks, each's first word from `.venv/bin`
    left_out: str = ""  # requirements it can't build here, which `--excludes -` reads
    most: int = 1  # the most processes its tests can keep busy
    worker_memory: float = 1.0  # the gigabytes one of them takes


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
# How many processes constricter takes here: every CPU, unless `CORPUS_JOBS` says; and the most a
# suite's tests may: half the CPUs, unless `CORPUS_SUITE_WORKERS` says (see `super_corpora.py`).
_JOBS: Final = os.environ.get("CORPUS_JOBS", "0")
_MOST_WORKERS: Final = int(os.environ.get("CORPUS_SUITE_WORKERS", "0")) or max(1, (os.cpu_count() or 2) // 2)
_WORKERS: Final = "{workers}"  # in a test command's word: how many processes to take
# How long a suite's tests may run before they're stopped: one waiting on a server no one started
# never ends. Half an hour, unless `CORPUS_SUITE_SECONDS` says.
_TEST_SECONDS: Final = float(os.environ.get("CORPUS_SUITE_SECONDS", "1800"))
_STOPPED: Final = "(stopped:"
_TIMED_OUT: Final = f"ERROR {_STOPPED} it ran too long)"  # read as a failure (see `_FAILED`)
_GIGABYTE: Final = 2**30
_MEMORY_SHARE: Final = 2  # the tests' workers' part of the machine's memory: a half
# Django's `runtests.py` under `fork`: with `forkserver`, Python 3.14's default on Linux, Django 5.2
# can't clone a SQLite test database for each process.
_DJANGO_FORKED: Final = (
    "import multiprocessing, runpy, sys; "
    "multiprocessing.set_start_method('fork'); "
    "sys.argv[0] = 'tests/runtests.py'; "
    "sys.path.insert(0, 'tests'); "
    "runpy.run_path('tests/runtests.py', run_name='__main__')"
)
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
            *_words(f"{_PYTEST} -n {_WORKERS} -m 'not memory_intensive and not mypy' --db sqlite"),
            *_words("--dbdriver sqlite --dbdriver pysqlite_numeric --dbdriver aiosqlite"),
        ),
        (_words("mypy noxfile.py ./lib/sqlalchemy"),),
        most=16,
    ),
    # Its `runtests.py` on SQLite, its processes forked (see `_DJANGO_FORKED`). It has no type checker.
    # pylibmc needs libmemcached's headers, and its tests need a memcached server, so they skip anyway.
    "django": Suite(
        "https://github.com/django/django",
        "5.2.17",
        "django",
        (_VENV, _words("pip install -q -e . -r tests/requirements/py3.txt --excludes -")),
        ("python", "-Wall", "-c", _DJANGO_FORKED, f"--parallel={_WORKERS}"),
        left_out="pylibmc",
        most=16,
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
        (
            *_words(f"{_PYTEST} -n {_WORKERS} --dist=worksteal"),
            *_words("-m 'not slow and not network and not single_cpu' pandas"),
        ),
        (("mypy",), ("pyright",)),
        most=32,
        worker_memory=1.5,
    ),
}
_EVERYWHERE: Final = ("--level=suffocate", "--all-scopes", f"--jobs={_JOBS}")
# Written once every install command has succeeded: a hash of them, so changed ones are run again.
_INSTALLED: Final = ".venv/corpus-suite-installed"
# Each checker's settings file, what an empty one holds, and the `pyproject.toml` sections that stand
# for it: pyrefly reads mypy's or Pyright's where it has none of its own.
_SETTINGS: Final = (
    ("pyrightconfig.json", "{}\n", ("pyright", "basedpyright")),
    ("pyrefly.toml", "", ("pyrefly", "mypy", "pyright")),
)
# pytest's `-rfE` lines, and unittest's (Django's runner's) headers of each failure and error
_FAILED: Final = re.compile(r"^(?:FAILED |ERROR |FAIL: |ERROR: )(\S+(?: \([\w.]+\))?)", re.MULTILINE)
# pytest's summary's counts, but its warnings': those come and go between runs of the same code.
_COUNTS: Final = re.compile(r"(\d+) (passed|failed|skipped|xfailed|xpassed|errors?)")
# pytest's summary line, bare (`-q`) or between `=`s: its counts, before how long it took
_SUMMARY: Final = re.compile(r"^(?:=+ )?((?:\d+ [a-z]+(?: [a-z]+)?(?:, )?)+) in \d[\d.]*s", re.MULTILINE)
_COLOUR: Final = re.compile(r"\x1b\[[0-9;]*m")  # a terminal's colours, which some suites force
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
_EQUAL: Final = "equal"  # and for lines both have
_Fixes: TypeAlias = dict[str, list[Fix]]  # those `--fix` makes, per file
_Mode: TypeAlias = tuple[str, tuple[str, ...]]  # a fixed run's label, and its options beyond `--fix`
MODES: Final[tuple[_Mode, ...]] = (("--fix", ()), ("--fix --unsafe-fixes", ("--unsafe-fixes",)))
_TYPES: Final = "--types"
_INFER_WITH: Final = "--infer-with"


def _environment(cwd: Path) -> dict[str, str]:
    """Return this environment for a command in `cwd`, a checkout or where they're cloned.

    Without this checkout's venv or forced colours (which pytest and the type checkers would print
    into the lines read back); with the checkout's venv activated, if it has one yet (pyright finds
    its packages by it); with an absolute uv cache (this project's `cache-dir` is relative, and uv
    finds this `pyproject.toml` above a checkout without its own `[tool.uv]`); and with a fixed hash
    seed (pytest-xdist's workers must collect the same tests); and with a temporary directory of
    its own.

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
    # Its own temporary files, under a short path (a suite's sockets go there): a suite's leave some
    # no one else can delete, which the next pytest run under the shared directory then trips on.
    temporary: Path = Path(tempfile.gettempdir()) / WORK.name / cwd.name
    temporary.mkdir(parents=True, exist_ok=True)
    environment["TMPDIR"] = str(temporary)
    return environment


def _completed(
    args: Sequence[str],
    cwd: Path,
    given: str = "",
    seconds: float | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command in `cwd`, with `given` as its standard input, for `seconds` at most.

    Returns:
      What it did: its exit status, and its standard output and error; one stopped for taking too
      long, what it had written, then `_TIMED_OUT`.

    """
    try:
        return subprocess.run(
            list(args),
            input=given,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            cwd=cwd,
            env=_environment(cwd),
            timeout=seconds,
        )
    except subprocess.TimeoutExpired as expired:
        written: str | bytes = expired.stdout or ""
        said: str = written if isinstance(written, str) else written.decode("utf-8", "replace")
        return subprocess.CompletedProcess(list(args), 1, f"{said}\n{_TIMED_OUT}\n", "")


def _run(args: Sequence[str], cwd: Path, given: str = "") -> tuple[int, str]:
    """Run a command in `cwd`, with `given` as its standard input.

    Returns:
      Its exit status, and its standard output and error, together.

    """
    done: subprocess.CompletedProcess[str] = _completed(args, cwd, given)
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


def _settled(root: Path) -> None:
    """Keep the checkers' servers to checkout `root`'s settings: an empty file of them, where it has none.

    With none in its workspace, Pyright's server reads the nearest above it, and pyrefly takes the
    project above that has some (this one) for the root it resolves imports from. Git is told to
    pass each file over.
    """
    project: Path = root / "pyproject.toml"
    own: str = project.read_text(encoding="utf-8") if project.is_file() else ""
    name: str
    empty: str
    tools: tuple[str, ...]
    for name, empty, tools in _SETTINGS:
        if (root / name).exists() or any(f"[tool.{tool}]" in own for tool in tools):
            continue
        _ = (root / name).write_text(empty, encoding="utf-8")
        stream: IO[str]
        with (root / ".git" / "info" / "exclude").open("a", encoding="utf-8") as stream:
            _ = stream.write(f"/{name}\n")


def checkout(name: str, suite: Suite, apart: str = "") -> Path:
    """Clone (once) `suite` at its tag and install it and its test dependencies (once for its commands).

    `apart`: names another checkout of it, for what's to run beside its tests (its type checks).

    Returns:
      The checkout.

    Raises:
      RuntimeError: an install command failed.

    """
    root: Path = WORK / (f"{name}-{suite.tag}-{apart}" if apart else f"{name}-{suite.tag}")
    uv: str = os.environ.get("UV") or shutil.which("uv") or "uv"
    if not root.is_dir():
        WORK.mkdir(parents=True, exist_ok=True)
        _ = _output(
            ["git", "clone", "-q", "--depth", "1", "--branch", suite.tag, suite.repository, str(root)],
            WORK,
        )
    _settled(root)
    marker: Path = root / _INSTALLED
    wanted: str = hashlib.sha256(repr(suite.install).encode()).hexdigest()
    done: str | None = marker.read_text(encoding="utf-8") if marker.exists() else None
    if done is None or (done and done != wanted):  # an empty one is from before it held the hash
        command: tuple[str, ...]
        for command in suite.install:
            status: int
            output: str
            status, output = _run([uv, *command], root, suite.left_out)
            if status:
                message: str = f"{name}: uv {' '.join(command)} failed:\n{output}"
                raise RuntimeError(message)
    if done != wanted:
        _ = marker.write_text(wanted, encoding="utf-8")
    return root


def workers(suite: Suite) -> int:
    """Size a suite's tests' processes: what it can keep busy, within the CPUs and memory it may take.

    Returns:
      How many.

    """
    try:
        memory: int = os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    except (AttributeError, ValueError, OSError):
        return min(suite.most, _MOST_WORKERS)
    fitting: int = int(memory / _MEMORY_SHARE / _GIGABYTE / suite.worker_memory)
    return max(1, min(suite.most, _MOST_WORKERS, fitting))


def stopped(outcome: Outcome) -> bool:
    """Check whether a test run was stopped for running too long (see `_TEST_SECONDS`).

    Returns:
      Whether it was.

    """
    return _STOPPED in outcome.failed


def tested(root: Path, suite: Suite, keep: Path | None) -> Outcome:
    """Run the checkout's tests, writing their output to `keep` unless it's `None`.

    Returns:
      Their outcome.

    """
    command: list[str] = [word.replace(_WORKERS, str(workers(suite))) for word in suite.tests]
    done: subprocess.CompletedProcess[str] = _completed(_venv(root, command), root, seconds=_TEST_SECONDS)
    output: str = _COLOUR.sub("", done.stdout + done.stderr)
    if keep is not None:
        keep.parent.mkdir(parents=True, exist_ok=True)
        _ = keep.write_text(output, encoding="utf-8")
    ran: re.Match[str] | None = _RAN.search(output)
    counts: dict[str, int]
    if ran:
        counts = {"ran": int(ran[1])} | {
            kind: int(n) for kind, n in cast("list[tuple[str, str]]", _UNITTEST.findall(output, ran.end()))
        }
    else:
        # The last line that reads as one: warnings, or what's on standard error, may come after it.
        summaries: list[str] = cast("list[str]", _SUMMARY.findall(output))
        summary: str = summaries[-1] if summaries else output.strip().rsplit("\n", 1)[-1]
        counts = {
            kind.rstrip("s") if kind.startswith("error") else kind: int(n)
            for n, kind in cast("list[tuple[str, str]]", _COUNTS.findall(summary))
        }
    return Outcome(counts, frozenset(cast("list[str]", _FAILED.findall(output))))


def reset(root: Path, suite: Suite) -> None:
    """Take the checkout's source back to its tag's."""
    _ = _output(["git", "checkout", "-q", "--", suite.source], root)


def fixed(root: Path, suite: Suite, *extra: str) -> str:
    """Reset the checkout's source, then `--fix` it (with `extra` options).

    Returns:
      The size of the change, as `git diff --shortstat` puts it.

    """
    reset(root, suite)
    _ = _output([str(_CONSTRICTER), "--fix", *extra, *_EVERYWHERE, "-q", suite.source], root)
    return _output(["git", "diff", "--shortstat"], root).strip()


def complaints(root: Path, suite: Suite) -> list[Complaint]:
    """Run the checkout's type checks, together.

    Returns:
      Their errors, each file relative to the checkout.

    """
    found: list[Complaint] = []
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, len(suite.checks))) as pool:
        checking: list[Future[str]] = [
            pool.submit(_output, _venv(root, check), root) for check in suite.checks
        ]
    checked: Future[str]
    for checked in checking:
        match: re.Match[str]
        for match in _ERROR.finditer(checked.result()):
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


def planned(root: Path, suite: Suite, *extra: str, reset_first: bool = True) -> dict[str, list[Fix]]:
    """Reset the checkout's source (unless told it's as released), and list the fixes `--fix` makes in it.

    With `extra` options.

    Returns:
      Them, per file.

    """
    if reset_first:
        reset(root, suite)
    done: subprocess.CompletedProcess[str] = _completed(
        [str(_CONSTRICTER), "--format=json", *extra, *_EVERYWHERE, suite.source],
        root,
    )
    _ = sys.stdout.write(done.stderr)  # its warnings: a file a checker's server hung on, say
    results: list[dict[str, _Json]] = cast("list[dict[str, _Json]]", json.loads(done.stdout))
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


def _origins(original: list[str], changed: list[str]) -> tuple[list[int], frozenset[int]]:
    """Map each line of a fixed file to the original line it came from (1-based).

    A changed line maps to the line it replaced; an inserted one (a declaration) to the statement
    after it, which it declares a name for.

    Returns:
      The original line of each fixed one, the first at index 1; and the fixed lines a fix changed
      or inserted.

    """
    origins: list[int] = [0] * (len(changed) + 1)
    edited: set[int] = set()
    tag: str
    i1: int
    i2: int
    j1: int
    j2: int
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, original, changed, autojunk=False).get_opcodes():
        j: int
        for j in range(j1, j2):
            origins[j + 1] = i1 + 1 if tag == _INSERTED else i1 + 1 + min(j - j1, max(i2 - i1 - 1, 0))
            if tag != _EQUAL:
                edited.add(j + 1)
    return origins, frozenset(edited)


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
    """A fixed file: its lines, each's original line, those a fix wrote, and each original line's scope."""

    lines: list[str]
    origins: list[int]
    edited: frozenset[int]
    scopes: list[int]


def _fixed_file(root: Path, path: str) -> _Fixed:
    """Read a fixed file, and map it to its original (`HEAD`'s).

    Returns:
      It.

    """
    original: str = _output(["git", "show", f"HEAD:{path}"], root)
    lines: list[str] = (root / path).read_text("utf-8").splitlines()
    return _Fixed(lines, *_origins(original.splitlines(), lines), _scopes(original))


def _file(root: Path, files: dict[str, _Fixed], path: str) -> _Fixed:
    """Read a fixed file (see `_fixed_file`), once: `files` keeps each read.

    Returns:
      It.

    """
    if path not in files:
        files[path] = _fixed_file(root, path)
    return files[path]


def _new(
    root: Path,
    after: list[Complaint],
    added: Counter[tuple[str, str]],
    files: dict[str, _Fixed],
) -> list[Complaint]:
    """Pick the errors of `after` that are new: `added`'s count of each file's alike ones (see `_key`).

    Which of a file's alike errors are new can't be told for sure: those on a line a fix changed or
    inserted first, then the first in the file.

    Returns:
      Them.

    """
    alike: dict[tuple[str, str], list[Complaint]] = {}
    complaint: Complaint
    for complaint in after:
        alike.setdefault(_key(complaint), []).append(complaint)
    new: list[Complaint] = []
    key: tuple[str, str]
    count: int
    for key, count in added.items():
        found: list[Complaint] = alike[key]
        if count < len(found):
            edited: frozenset[int] = _file(root, files, key[0]).edited
            found = [each for each in found if each.line in edited] + [
                each for each in found if each.line not in edited
            ]
        new.extend(found[:count])
    return new


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


class Blamed(NamedTuple):
    """A new error, the fix it's traced to (`None`: untraced), and that fix's mechanisms."""

    complaint: Complaint
    fix: Fix | None
    kind: str  # `fix.kinds`, with ` (guess)` for a guess's; `(untraced)`


class Compared(NamedTuple):
    """What type-checking a fixed checkout gave beside the released one's errors."""

    change: str  # the fix's size, as `git diff --shortstat` puts it
    errors: int
    gone: int
    new: list[Blamed]


def _listed_and_fixed(
    root: Path,
    suite: Suite,
    options: tuple[str, ...],
    unfixed: Path | None,
) -> tuple[dict[str, list[Fix]], str]:
    """List the fixes `--fix` makes with `options` (see `planned`), and make them in checkout `root`.

    Listed on `unfixed` meanwhile, if there's one; else on `root`, first.

    Returns:
      The fixes, and the size of the change.

    """
    if unfixed is None:
        return planned(root, suite, *options), fixed(root, suite, *options)
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(1) as pool:
        listing: Future[_Fixes] = pool.submit(
            planned,
            unfixed,
            suite,
            *options,
            reset_first=False,
        )
        change: str = fixed(root, suite, *options)
    return listing.result(), change


def compared(
    root: Path,
    suite: Suite,
    released: Callable[[], list[Complaint]],
    options: tuple[str, ...],
    unfixed: Path | None = None,
) -> Compared:
    """Fix the checkout's source with `options`, type-check it, and trace what's new since `released`.

    `released` gives the released source's errors, asked for once this checkout's are in: they may
    be found meanwhile, on another checkout. `unfixed`: such a checkout, its source as released,
    where the fixes are listed while this one is fixed.

    Returns:
      The comparison.

    """
    made: tuple[_Fixes, str] = _listed_and_fixed(root, suite, options, unfixed)
    after: list[Complaint] = complaints(root, suite)
    before: Counter[tuple[str, str]] = Counter(_key(complaint) for complaint in released())
    now: Counter[tuple[str, str]] = Counter(_key(complaint) for complaint in after)
    files: dict[str, _Fixed] = {}
    new: list[Blamed] = []
    complaint: Complaint
    for complaint in _new(root, after, now - before, files):
        file: _Fixed = _file(root, files, complaint.path)
        fix: Fix | None = _blamed(complaint, file, made[0].get(complaint.path, []))
        kind: str = "(untraced)" if fix is None else fix.kinds + (" (guess)" if fix.unsafe else "")
        new.append(Blamed(complaint, fix, kind))
    return Compared(made[1], len(after), (before - now).total(), new)


def _compare_types(
    root: Path,
    suite: Suite,
    released: list[Complaint],
    label: str,
    options: tuple[str, ...],
) -> bool:
    """Fix the checkout's source with `options`, type-check it, and print what's new since `released`.

    Each new error with the fix it's traced to, and their count per mechanism.

    Returns:
      Whether nothing is.

    """
    found: Compared = compared(root, suite, lambda: released, options)
    _ = sys.stdout.write(
        f"  {label} ({found.change}): {found.errors} errors: {len(found.new)} new, {found.gone} gone\n",
    )
    lines: list[str] = []
    each: Blamed
    for each in found.new:
        fix: Fix | None = each.fix
        what: str = "" if fix is None else f" [{fix.name}: {fix.annotation}, line {fix.line}]"
        where: str = f"{each.complaint.path}:{each.complaint.line}"
        lines.append(f"      {each.kind}: {where}{what}: {each.complaint.message}\n")
    kind: str
    count: int
    for kind, count in Counter(each.kind for each in found.new).most_common():
        _ = sys.stdout.write(f"    {kind}: {count}\n")
    _ = sys.stdout.writelines(sorted(lines))
    return not found.new


def check_types(names: Sequence[str], modes: Sequence[_Mode] = MODES) -> int:
    """Run each suite's type checks (default: every one's) as released, then fixed in each of `modes`.

    Returns:
      0 if no fixed run has an error its released one hasn't, else 1.

    """
    clean: bool = True
    name: str
    for name in names or [name for name, suite in SUITES.items() if suite.checks]:
        suite: Suite = SUITES[name]
        root: Path = checkout(name, suite)
        reset(root, suite)
        released: list[Complaint] = complaints(root, suite)
        checks: str = "; ".join(" ".join(check) for check in suite.checks)
        _ = sys.stdout.write(f"{name} {suite.tag}: {checks}: released: {len(released)} errors\n")
        label: str
        options: tuple[str, ...]
        for label, options in modes:
            clean = _compare_types(root, suite, released, label, options) and clean
        reset(root, suite)
    return 0 if clean else 1


def _arguments(argv: Sequence[str]) -> tuple[list[str], list[_Mode]]:
    """Read the options out of the arguments: `--infer-with CHECKERS` adds a fixed run with their hints.

    Returns:
      The other arguments, and the fixed runs to make.

    """
    rest: list[str] = list(argv)
    modes: list[_Mode] = list(MODES)
    if _INFER_WITH in rest:
        at: int = rest.index(_INFER_WITH)
        checkers: str = rest.pop(at + 1)
        _ = rest.pop(at)
        options: tuple[str, ...] = ("--unsafe-fixes", _INFER_WITH, checkers)
        modes.append((f"--fix --unsafe-fixes {_INFER_WITH} {checkers}", options))
    return rest, modes


def main(argv: Sequence[str]) -> int:
    """Run each suite named (default: all) as released, fixed, and fixed with guesses (and hints).

    Returns:
      0 if every fixed run's outcome matches its released one, else 1.

    """
    names: list[str]
    modes: list[_Mode]
    names, modes = _arguments(argv)
    if _TYPES in names:
        names.remove(_TYPES)
        return check_types(names, modes)
    same: bool = True
    name: str
    for name in names or SUITES:
        suite: Suite = SUITES[name]
        root: Path = checkout(name, suite)
        reset(root, suite)
        released: Outcome = tested(root, suite, None)
        _ = sys.stdout.write(f"{name} {suite.tag}: released: {released.counts}\n")
        label: str
        options: tuple[str, ...]
        test: str
        for label, options in modes:
            change: str = fixed(root, suite, *options)
            outcome: Outcome = tested(root, suite, None)
            verdict: str = "same" if outcome == released else "DIFFERENT"
            _ = sys.stdout.write(f"  {label} ({change}): {outcome.counts}: {verdict}\n")
            for test in sorted(outcome.failed ^ released.failed):
                _ = sys.stdout.write(
                    f"    {'now fails' if test in outcome.failed else 'now passes'}: {test}\n",
                )
            same = same and outcome == released
        reset(root, suite)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
