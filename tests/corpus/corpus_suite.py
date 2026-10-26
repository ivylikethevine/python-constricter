"""A corpus package's own suite: its checkout, its tests and its type checks, as the corpus runner runs them.

Each package's source is cloned at its pinned tag into `local/corpus-suites/` (`checkout`), installed
there with its test dependencies as its CI installs them (its own `uv.lock` where it has one, its
pins or requirements where it hasn't). It needs `git`, `uv`, a C compiler and Rust (pandas,
SQLAlchemy and pydantic-core are built) and the network, once. `suite_steps` runs its tests
(`tested`), its tests traced (`traced`) and its type checks (`complaints`) as released and after
each of a run's fixes, whose patch it applies to the checkout.

A local variable's annotation is never evaluated at runtime (PEP 526), so the tests catch a fix
that breaks the code itself (a declaration, a dropped comment or annotation, a module's
`__annotations__`), not a wrong type: that's a type checker's job, and the package's own run as its
CI runs them. An error the fixed run has that the released one hasn't is new (of a file's alike
errors, those on a line a fix wrote first); each new one is traced to the fix whose annotation it's
about (`blamed`: the fix on its line, else the nearest one before it in its scope, else the
module's, of a name on its line or in its message), and named by the mechanisms that decided that
fix (`--format=json`'s `kinds`), a guess's marked `(likely)` or `(guess)`. A trace is by line, not
by cause: a certain fix can be blamed for what a guess beside it brought.

A checkout with no settings for Pyright or pyrefly is given empty ones (`_settled`), or the
checkers' servers `--infer-with` starts read this project's, above it.

The tests are traced under `python -m constricter.trace` (this checkout's, which the package's
environment is given the path of), where pytest runs them, `python -c` does (Django's `runtests.py`,
its workers forked, each recording itself), or the suite names a script that does in one process
(`Suite.script`).
"""

import ast
import difflib
import functools
import hashlib
import inspect
import json
import os
import re
import shlex
import shutil
import subprocess  # runs git, uv, the tests, the type checkers and constricter
import tempfile
from collections import Counter
from collections.abc import Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

# pytest's own reports, not a stranger's XML.
from xml.etree import ElementTree as ET  # ruff: ignore[suspicious-xml-etree-import]

from constricter import recording
from constricter.empty import Empty
from constricter.offences import Tier
from tests.corpus import catalog
from tests.corpus.run_config import scrubbed

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"


Suite: TypeAlias = catalog.Suite


class Outcome(NamedTuple):
    """What one test run gave: its summary counts, and the tests that failed or errored."""

    counts: dict[str, int]
    failed: frozenset[str]


class Test(NamedTuple):
    """One test of a run, as pytest's JUnit report has it: its id, outcome, seconds, and why skipped."""

    id: str  # pytest's node id: `tests/test_a.py::TestB::test_c[1]`
    outcome: str  # `passed`, `failed`, `error`, `skipped` or `xfailed`
    seconds: float
    reason: str = ""  # a skipped or expected failure's


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
    likely: bool = False  # a guess `--likely` applies
    imports: tuple[str, ...] = ()  # the import statements it adds


WORK: Final = Path(__file__).resolve().parents[2] / "local" / "corpus-suites"
# The most processes a suite's tests may take: half the CPUs, unless `CORPUS_SUITE_WORKERS` says
# (a run file's `suite-workers`).
_MOST_WORKERS: Final = int(os.environ.get("CORPUS_SUITE_WORKERS", "0")) or max(1, (os.cpu_count() or 2) // 2)
_WORKERS: Final = catalog.WORKERS
# How long a suite's tests may run before they're stopped: one waiting on a server no one started
# never ends. Half an hour, unless `CORPUS_SUITE_SECONDS` says.
_TEST_SECONDS: Final = float(os.environ.get("CORPUS_SUITE_SECONDS", "1800"))
_STOPPED: Final = "(stopped:"
_TIMED_OUT: Final = f"ERROR {_STOPPED} it ran too long)"  # read as a failure (see `_FAILED`)
_GIGABYTE: Final = 2**30
# pytest's JUnit report, a file for each part of a suite's tests: its legacy family names each test's
# file and line, from which the test's node id is written back (see `junit_tests`).
_JUNIT: Final = "--junitxml"
_JUNIT_FAMILY: Final = ("-o", "junit_family=xunit1")
_JUNIT_DIR: Final = ".venv/corpus-suite-junit"  # in a checkout: the parts' reports, written anew each run
_XFAIL: Final = "pytest.xfail"  # the `type` of a skip that's an expected failure
_MEMORY_SHARE: Final = 2  # the tests' workers' part of the machine's memory: a half
SUITES: Final = catalog.load().suites(catalog.ORIGINAL)  # the seven corpora's, as `corpora.toml` has them
# Written once every install command has succeeded: a hash of them, so changed ones are run again.
_INSTALLED: Final = ".venv/corpus-suite-installed"
# Each checker's settings file, what an empty one holds, and the `pyproject.toml` sections that stand
# for it: pyrefly reads mypy's or Pyright's where it has none of its own.
_SETTINGS: Final = (
    ("pyrightconfig.json", "{}\n", ("pyright", "basedpyright")),
    ("pyrefly.toml", "", ("pyrefly", "mypy", "pyright")),
)
_PYRIGHTS: Final = frozenset({"pyright", "basedpyright"})
_PROJECT: Final = frozenset({"-p", "--project"})  # Pyright's option naming its settings
# pytest's `-rfE` lines (the test, then ` - ` and why; a parametrized id may hold a space), and
# unittest's (Django's runner's) headers of each failure and error: not a logged line
# (`ERROR - 2026-10-13 ... - litestar - ...`), nor a captured log record, its level padded to eight
# columns (`ERROR    sphinx.util:logging.py:141 Duplicate target name`, whose line a fix moves), nor
# unittest's summary (`FAILED (failures=2)`).
_FAILED: Final = re.compile(r"^(?:FAILED |ERROR (?![-\s])|FAIL: |ERROR: )(?!\()(.+?)(?= - |$)", re.MULTILINE)
# pytest's summary's counts, but its warnings': those come and go between runs of the same code.
_COUNTS: Final = re.compile(r"(\d+) (passed|failed|skipped|xfailed|xpassed|errors?)")
# pytest's summary line, bare (`-q`) or between `=`s: its counts, before how long it took
_SUMMARY: Final = re.compile(r"^(?:=+ )?((?:\d+ [a-z]+(?: [a-z]+)?(?:, )?)+) in \d[\d.]*s", re.MULTILINE)
# pytest-pretty's, a count to a line under how long it took.
_PRETTY: Final = re.compile(r"^Results \(\d[\d.]*s\):\n((?:[ \t]+\d+ [a-z]+\n?)+)", re.MULTILINE)
_COLOUR: Final = re.compile(r"\x1b\[[0-9;]*m")  # a terminal's colours, which some suites force
_RAN: Final = re.compile(r"^Ran (\d+) tests?", re.MULTILINE)  # unittest's summary starts here
# All of it: how many ran, and after a blank line how they went.
_RAN_SUMMARY: Final = re.compile(r"^(Ran \d+ tests?) in \d[\d.]*s\n+((?:OK|FAILED).*)$", re.MULTILINE)
_UNITTEST: Final = re.compile(r"(failures|errors|skipped|expected failures|unexpected successes)=(\d+)")
# mypy's `path:line: error: message` and pyright's `  /path:line:column - error: message`
_ERROR: Final = re.compile(
    r"^[ \t]*(?P<path>[^:\s][^:\n]*\.pyi?):(?P<line>\d+)(?::\d+)?:? (?:- )?error: (?P<message>.+)$",
    re.MULTILINE,
)
_OTHER_LINE: Final = re.compile(r"\bline \d+")  # a message's reference to another line, which a fix moves
_QUOTED: Final = re.compile(r"""["'`]([A-Za-z_]\w*)["'`]""")
_NAME: Final = re.compile(r"[A-Za-z_]\w*")
_INSERTED: Final = "insert"  # difflib's opcode for lines only the fixed file has
_EQUAL: Final = "equal"  # and for lines both have
_Fixes: TypeAlias = dict[str, list[Fix]]  # those `--fix` makes, per file
# What `constricter.trace` runs for a suite's tests, part by part, what it needs on the path, and
# the interpreter's own options before it (`-Wall`).
_Traceable: TypeAlias = tuple[list[list[str]], list[str], list[str]]
TRACE_FILE: Final = ".venv/corpus-suite-trace.json"  # a checkout's tests' trace: out of its source's way
_PYTHON: Final = "python"
_MODULE: Final = (_PYTHON, "-m")  # how a suite's tests start, where a module runs them
_CODE: Final = "-c"  # and where code does
_PYTEST: Final = (*_MODULE, "pytest")  # and where pytest does
_TRACER: Final = ("constricter.trace", "--output", TRACE_FILE, "--root", ".")
_PART_TRACE: Final = ".venv/corpus-suite-trace-{}.json"  # each part's, where they're traced side by side
# In a checkout: a directory with this checkout's `constricter` alone, for a traced run's path. Not
# this checkout's root, whose `tests` package a suite's own would then share the path with.
_TRACER_PATH: Final = ".venv/corpus-suite-path"
TRACER_VARIABLE: Final = "CORPUS_TRACER"  # set: another module that traces as it does, and where it is


def _environment(cwd: Path) -> dict[str, str]:
    """Return this environment for a command in `cwd`, a checkout or where they're cloned.

    Without this checkout's venv or forced colours (which pytest and the type checkers would print
    into the lines read back); with the checkout's venv activated, if it has one yet (pyright finds
    its packages by it); with an absolute uv cache (this project's `cache-dir` is relative, and uv
    finds this `pyproject.toml` above a checkout without its own `[tool.uv]`); and with a fixed hash
    seed (pytest-xdist's workers must collect the same tests); with a temporary directory of its
    own; without the user's uv settings (an `exclude-newer` there makes a suite's own lockfile
    stale to `uv sync --locked`); and with matplotlib drawing off screen (`Agg`), so a suite's
    plotting tests open no window on the user's display.

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
    _ = environment.setdefault("UV_NO_CONFIG", "1")
    environment["MPLBACKEND"] = "Agg"
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
    more: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command in `cwd`, with `given` as its standard input, for `seconds` at most.

    `more`: environment variables it's given besides.

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
            env=_environment(cwd) | dict(more or {}),
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


def _own(check: Sequence[str]) -> list[str]:
    """Hold Pyright's command to the checkout's settings.

    Run with none named, it reads a `pyrightconfig.json` above the checkout (this project's) before
    the checkout's own `pyproject.toml`.

    Returns:
      The check, with `--project .` where it's Pyright's and names no project.

    """
    named: bool = bool(_PROJECT.intersection(check))
    return [*check, *(("--project", ".") if check[0] in _PYRIGHTS and not named else ())]


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


def checkout(
    name: str,
    suite: Suite,
    apart: str = "",
    *,
    install: bool = True,
    variables: Mapping[str, str] | None = None,
) -> Path:
    """Clone (once) `suite` at its tag and install it and its test dependencies (once for its commands).

    `apart`: names another checkout of it, for what's to run beside its tests (its type checks).
    Without `install`, the clone alone: its source, with no environment. `variables`: what its
    corpus's commands need set, its install's too (a build without its C extensions, say).

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
    if not install:
        return root
    marker: Path = root / _INSTALLED
    wanted: str = hashlib.sha256(repr(suite.install).encode()).hexdigest()
    done: str | None = marker.read_text(encoding="utf-8") if marker.exists() else None
    if done is None or (done and done != wanted):  # an empty one is from before it held the hash
        if suite.submodules:
            _ = _output(["git", "submodule", "update", "-q", "--init", "--depth", "1"], root)
        command: tuple[str, ...]
        for command in suite.install:
            status: int
            output: str
            ran: subprocess.CompletedProcess[str] = _completed(
                [uv, *command],
                root,
                suite.left_out,
                more=variables,
            )
            status, output = ran.returncode, ran.stdout + ran.stderr
            if status:
                message: str = f"{name}: uv {' '.join(command)} failed:\n{output}"
                raise RuntimeError(message)
    if done != wanted:
        _ = marker.write_text(wanted, encoding="utf-8")
    return root


def installed(root: Path) -> str:
    """Hash a checkout's installed environment: its Python's version and every package's.

    A record of its tests is comparable with another's only on a checkout installed the same.

    Returns:
      The hash; of nothing, for a clone with no environment.

    """
    python: Path = root / ".venv" / "bin" / "python"
    if not python.exists():
        return hashlib.sha256(b"").hexdigest()
    uv: str = os.environ.get("UV") or shutil.which("uv") or "uv"
    version: str = _output([str(python), "--version"], root)
    listed: str = _output([uv, "pip", "freeze", "--python", str(python)], root)
    return hashlib.sha256(f"{version}\n{listed}".encode()).hexdigest()


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


def _summary(output: str) -> str:
    """Find pytest's summary in a run's output, or unittest's: the last that reads as one.

    Warnings, or what's on standard error, may come after it.

    Returns:
      Its counts' text; the output's last line if none does.

    """
    found: list[str] = cast("list[str]", _PRETTY.findall(output) or _SUMMARY.findall(output))
    ran: list[tuple[str, str]] = cast("list[tuple[str, str]]", _RAN_SUMMARY.findall(output))
    if ran and not found:
        return ": ".join(ran[-1])
    if found:  # pytest-pretty's counts are a line each
        return ", ".join(line.strip() for line in found[-1].strip().splitlines())
    return output.strip().rsplit("\n", 1)[-1]


def tested(root: Path, suite: Suite, keep: Path | None, data: Path | None) -> Outcome:
    """Run the checkout's tests, writing their output to `keep` and each test's record to `data`.

    Its parts side by side, as many at once as it has workers. Where pytest runs them, each part
    writes a JUnit report, which says exactly which tests failed, and what `data` holds: a line a
    test (see `Test`), unless it's `None`. The output's summary gives the counts either way.

    Returns:
      Their outcome.

    """
    reports: Path = root / _JUNIT_DIR
    shutil.rmtree(reports, ignore_errors=True)
    reports.mkdir(parents=True, exist_ok=True)

    def run(command: list[str]) -> str:
        done: subprocess.CompletedProcess[str] = _completed(_venv(root, command), root, seconds=_TEST_SECONDS)
        return _COLOUR.sub("", done.stdout + done.stderr)

    commands: list[list[str]] = _commands(suite, reports)
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, min(workers(suite), len(commands)))) as pool:  # parts side by side
        outputs: list[str] = list(pool.map(run, commands))
    if keep is not None:
        keep.parent.mkdir(parents=True, exist_ok=True)
        _ = keep.write_text("\n".join(outputs), encoding="utf-8")
    tests: list[Test] = [
        test for report in sorted(reports.glob("*.xml")) for test in junit_tests(report, root)
    ]
    if data is not None and tests:
        data.parent.mkdir(parents=True, exist_ok=True)
        listed: str = "".join(json.dumps(test._asdict()) + "\n" for test in tests)
        _ = data.write_text(scrubbed(listed), encoding="utf-8")
    outcome: Outcome = _added([read(output) for output in outputs])
    if len(list(reports.glob("*.xml"))) != len(commands):  # a part that wrote none: read as text
        return outcome
    return Outcome(outcome.counts, frozenset(test.id for test in tests if test.outcome in _FAILURES))


_FAILURES: Final = frozenset({"failed", "error"})
_SKIP: Final = "skipped"  # a test's outcome, as `Test` has it


def skips(released: Path, fixed: Path) -> tuple[list[str], list[str]] | None:
    """Name the tests the `fixed` run skipped that the `released` one ran, and the reverse, by their tests.

    Each a run's `data` (see `tested`): a count alone hides which skips moved, as sqlalchemy's do with
    its drivers' order. Only the tests both ran.

    Returns:
      Those skipped anew and those skipped no more, the tests' ids; `None` where either run wrote none.

    """
    then: dict[str, str] | None = _outcomes(released)
    now: dict[str, str] | None = _outcomes(fixed)
    if then is None or now is None:
        return None
    both: set[str] = then.keys() & now.keys()
    skipped: set[str] = {test for test in both if now[test] == _SKIP}
    was: set[str] = {test for test in both if then[test] == _SKIP}
    return sorted(skipped - was), sorted(was - skipped)


def _outcomes(data: Path) -> dict[str, str] | None:
    """Read a run's tests (`tested`'s `data`): each one's outcome, by its id.

    Returns:
      Them; `None` where the run wrote none.

    """
    try:
        text: str = data.read_text(encoding="utf-8")
    except OSError:
        return None
    tests: list[dict[str, str]] = [json.loads(line) for line in text.splitlines() if line]
    return {test["id"]: test["outcome"] for test in tests}


def _commands(suite: Suite, reports: Path | None = None) -> list[list[str]]:
    """Write the commands that run the suite's tests: one, or one for each of its parts.

    `reports`: where each part's JUnit report goes, where pytest runs the tests.

    Returns:
      Each one's words, its processes counted in: one each where its parts are its workers.

    """
    command: list[str] = [
        word.replace(_WORKERS, str(1 if suite.parts else workers(suite))) for word in suite.tests
    ]
    found: list[list[str]] = [[*command, *shlex.split(part)] for part in suite.parts] or [command]
    if reports is None or tuple(command[: len(_PYTEST)]) != _PYTEST:
        return found
    # The report's words before a part's: a part's are read back as its command's last.
    return [
        [*command, f"{_JUNIT}={reports / f'part{index}.xml'}", *_JUNIT_FAMILY, *each[len(command) :]]
        for index, each in enumerate(found)
    ]


def junit_tests(report: Path, ran_in: Path | None = None) -> list[Test]:
    """Read the tests of one part's JUnit report (see `_JUNIT_FAMILY`), run in `ran_in`.

    Returns:
      Each one, in the report's order, its file relative to `ran_in`; none for a report that can't
      be read.

    """
    try:
        root: ET.Element = ET.parse(report).getroot()  # ruff: ignore[suspicious-xml-element-tree-usage]
    except (OSError, ET.ParseError):
        return []
    found: list[Test] = []
    case: ET.Element
    file: str
    inner: str
    for case in root.iter("testcase"):
        file, inner = _located(case.get("file", ""), case.get("classname", ""), ran_in)
        parts: list[str] = [file, *inner.split(".")] if inner else [file]
        child: ET.Element | None = next((each for each in case if each.tag in _OUTCOMES), None)
        outcome: str = _PASSED
        reason: str = ""
        if child is not None:
            outcome = _OUTCOMES[child.tag]
            if child.tag == _SKIP_TAG:
                reason = child.get("message", "") or ""
                outcome = _XFAILED if child.get("type") == _XFAIL else outcome
        found.append(
            Test(
                "::".join([*parts, case.get("name", "")]),
                outcome,
                float(case.get("time", "0") or 0),
                reason,
            ),
        )
    return found


def _located(file: str, classes: str, ran_in: Path | None) -> tuple[str, str]:
    """Split a test's class name into its file, relative to `ran_in`, and the classes after it.

    The class name is the node id's file as a module, then the test's classes, relative to pytest's
    rootdir, which may be above the checkout (`local.corpus-suites.<checkout>.tests.test_a`). The
    report's `file` is the test function's own path: a base class's for a method a test class
    inherits, and kept by pytest's cached rewritten module from wherever it was compiled
    (`../../old/checkout/tests/test_a.py`), so only its last directories are the node id's.

    Returns:
      The file, and the classes' dotted names (empty for a test at a module's top level); `file` or
      the class name, and every class name, where neither `file` nor the checkout's files name the
      class name's module.

    """
    if ran_in is not None:
        base: Path
        for base in ran_in.parents:  # the checkout's own path, where the rootdir is above it
            above: str = f"{ran_in.relative_to(base).as_posix().replace('/', '.')}."
            if classes.startswith(above):
                classes = classes.removeprefix(above)
                break
    suffix: str = ".py" if file.endswith(".py") else ""
    names: list[str] = file.removesuffix(suffix).split("/")
    start: int
    for start in range(len(names)):
        module: str = ".".join(names[start:])
        if classes == module or classes.startswith(f"{module}."):
            return "/".join(names[start:]) + suffix, classes.removeprefix(module).strip(".")
    if ran_in is None:
        return file or classes, classes
    dotted: list[str] = classes.split(".")
    end: int
    for end in range(len(dotted) - 1, 0, -1):  # an inherited method's: the longest start that's a file
        path: str = "/".join(dotted[:end]) + ".py"
        if (ran_in / path).is_file():
            return path, ".".join(dotted[end:])
    return file or classes, classes


_SKIP_TAG: Final = "skipped"  # the report's element for a skip, an expected failure's too
_OUTCOMES: Final = {"failure": "failed", "error": "error", _SKIP_TAG: "skipped"}
_PASSED: Final = "passed"
_XFAILED: Final = "xfailed"


def _added(outcomes: Sequence[Outcome]) -> Outcome:
    """Add up the outcomes of a suite's tests, run part by part.

    Returns:
      Their counts summed, and every test that failed.

    """
    counts: Counter[str] = Counter()
    each: Outcome
    for each in outcomes:
        counts.update(each.counts)
    return Outcome(dict(counts), outcomes[0].failed.union(*(each.failed for each in outcomes)))


def read(output: str) -> Outcome:
    """Read a test run's output, pytest's or unittest's.

    Returns:
      Its summary's counts, and the tests that failed or errored.

    """
    ran: re.Match[str] | None = _RAN.search(output)
    counts: dict[str, int] = (
        {"ran": int(ran[1])}
        | {kind: int(n) for kind, n in cast("list[tuple[str, str]]", _UNITTEST.findall(output, ran.end()))}
        if ran
        else {
            kind.rstrip("s") if kind.startswith("error") else kind: int(n)
            for n, kind in cast("list[tuple[str, str]]", _COUNTS.findall(_summary(output)))
        }
    )
    return Outcome(counts, frozenset(cast("list[str]", _FAILED.findall(output))))


@functools.cache
def parser() -> str:
    """Name the version of what reads a test run's outcome: its output's readers and its JUnit reports'.

    `read`, `_summary`, `_added` and their patterns; `tested`, `junit_tests` and `_located`. A record
    read by another version isn't comparable with one read by this.

    Returns:
      A hash of their source.

    """
    patterns: tuple[re.Pattern[str], ...] = (_FAILED, _COUNTS, _SUMMARY, _PRETTY, _COLOUR, _RAN, _RAN_SUMMARY)
    source: str = "".join(
        inspect.getsource(each) for each in (read, _summary, _added, tested, junit_tests, _located)
    )
    source += "".join(each.pattern for each in (*patterns, _UNITTEST)) + _TIMED_OUT
    return hashlib.sha256(source.encode()).hexdigest()[:12]


def _traceable(suite: Suite) -> _Traceable | None:
    """Find what `constricter.trace` runs for the suite's tests, and what it needs on the path.

    Returns:
      The module and its arguments where pytest runs them, once for each of the suite's parts; or
      the code `python -c` runs and its arguments, after the interpreter's options (Django's
      `runtests.py` on its workers, forked); else the suite's script and its (with the script's
      directory); `None` where none does.

    """
    commands: list[list[str]] = _commands(suite)
    if tuple(commands[0][:2]) == _MODULE:
        return [command[1:] for command in commands], [], []
    first: list[str] = commands[0]
    if first[:1] == [_PYTHON] and _CODE in first:
        at: int = first.index(_CODE)
        if all(word.startswith("-") for word in first[1:at]):
            return [command[at:] for command in commands], [], first[1:at]
    return ([list(suite.script)], [str(Path(suite.script[0]).parent)], []) if suite.script else None


def traceable(suite: Suite) -> bool:
    """Check whether the suite's tests can be traced: pytest runs them, `python -c`, or its script.

    Returns:
      Whether they can.

    """
    return _traceable(suite) is not None


def tracer_path(root: Path) -> Path:
    """Make the directory a traced run of the checkout at `root` finds `constricter` in (`_TRACER_PATH`).

    Returns:
      It: this checkout's `constricter` package, linked, and nothing else.

    """
    path: Path = root / _TRACER_PATH
    link: Path = path / "constricter"
    package: Path = Path(__file__).resolve().parents[2] / "constricter"
    if not link.is_symlink() or link.resolve() != package:
        path.mkdir(parents=True, exist_ok=True)
        link.unlink(missing_ok=True)
        link.symlink_to(package, target_is_directory=True)
    return path


def traced(root: Path, suite: Suite, keep: Path | None = None) -> tuple[str, Outcome] | None:
    """Run the checkout's tests as released under `python -m constricter.trace`, which writes `TRACE_FILE`.

    Or under the module `TRACER_VARIABLE` names, from the directory it names after `os.pathsep`.
    Its parts side by side, as `tested` runs them, each writing a trace of its own; merged, in the
    parts' order. Their output is written to `keep` unless it's `None`.

    Returns:
      The tests' summary and their outcome, or `None` for tests that can't be traced (see
      `traceable`): there's no trace.

    """
    reset(root, suite)
    target: _Traceable | None
    if (target := _traceable(suite)) is None:
        return None
    tracer: list[str] = os.environ.get(TRACER_VARIABLE, _TRACER[0]).split(os.pathsep)  # and its directory
    path: list[str] = [str(tracer_path(root)), *target[1], *tracer[1:]]
    files: list[str] = (
        [TRACE_FILE] if len(target[0]) == 1 else [_PART_TRACE.format(n) for n in range(len(target[0]))]
    )
    (root / TRACE_FILE).unlink(missing_ok=True)

    def run(part: list[str], trace: str) -> tuple[str, recording.Found | None]:
        (root / trace).unlink(missing_ok=True)
        words: list[str] = [tracer[0], _TRACER[1], trace, *_TRACER[3:], *part]
        done: subprocess.CompletedProcess[str] = _completed(
            _venv(root, [_PYTHON, *target[2], *_MODULE[1:], *words]),
            root,
            seconds=_TEST_SECONDS,
            more={"PYTHONPATH": os.pathsep.join(path)},
        )
        found: recording.Found | None = (
            cast("recording.Found", json.loads((root / trace).read_text(encoding="utf-8")))
            if (root / trace).exists()
            else None
        )
        return _COLOUR.sub("", done.stdout + done.stderr), found

    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, min(workers(suite), len(files)))) as pool:  # parts side by side
        ran: list[tuple[str, recording.Found | None]] = list(pool.map(run, target[0], files))
    outputs: list[str] = [output for output, _ in ran]
    traces: list[recording.Found] = [found for _, found in ran if found is not None]
    if len(files) > 1 and traces:  # each part wrote a trace of its own
        recording.write(root / TRACE_FILE, recording.merged(traces))
        trace: str
        for trace in files:
            (root / trace).unlink(missing_ok=True)
    if keep is not None:
        keep.parent.mkdir(parents=True, exist_ok=True)
        _ = keep.write_text("\n".join(outputs), encoding="utf-8")
    outcome: Outcome = _added([read(output) for output in outputs])
    counted: str = ", ".join(f"{count} {kind}" for kind, count in outcome.counts.items())
    return (_summary(outputs[0]) if len(outputs) == 1 else counted), outcome


def reset(root: Path, suite: Suite) -> None:
    """Take the checkout's source back to its tag's."""
    _ = _output(["git", "checkout", "-q", "--", suite.source], root)


def complaints(root: Path, suite: Suite) -> list[Complaint]:
    """Run the checkout's type checks, together.

    Returns:
      Their errors, each file relative to the checkout.

    """
    found: list[Complaint] = []
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max(1, len(suite.checks))) as pool:
        checking: list[Future[str]] = [
            pool.submit(_output, _venv(root, _own(check)), root) for check in suite.checks
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
    kind: str  # `fix.kinds`, with ` (likely)` or ` (guess)` for a guess's; `(untraced)`


class Compared(NamedTuple):
    """What type-checking a fixed checkout gave beside the released one's errors."""

    change: str  # the fix's size, as `git diff --shortstat` puts it
    errors: int
    gone: int
    new: list[Blamed]
    fixes: Mapping[str, Sequence[Fix]] = Empty()  # every fix the run made, per file


def blamed(
    root: Path,
    after: list[Complaint],
    released: list[Complaint],
    made: tuple[_Fixes, str],
) -> Compared:
    """Trace what's new in `after`, the fixed checkout's errors, since `released`, to the fixes `made`.

    `made`: the fixes in the checkout, per file, and the size of their change.

    Returns:
      The comparison.

    """
    before: Counter[tuple[str, str]] = Counter(_key(complaint) for complaint in released)
    now: Counter[tuple[str, str]] = Counter(_key(complaint) for complaint in after)
    files: dict[str, _Fixed] = {}
    new: list[Blamed] = []
    complaint: Complaint
    for complaint in _new(root, after, now - before, files):
        file: _Fixed = _file(root, files, complaint.path)
        fix: Fix | None = _blamed(complaint, file, made[0].get(complaint.path, []))
        tier: Tier = Tier.of(unsafe=bool(fix and fix.unsafe), likely=bool(fix and fix.likely))
        guess: str = "" if tier is Tier.CERTAIN else f" ({tier.value})"
        new.append(Blamed(complaint, fix, "(untraced)" if fix is None else fix.kinds + guess))
    return Compared(made[1], len(after), (before - now).total(), new, made[0])
