"""The one way a run starts constricter: every step's check, fix and count goes through `run`.

A version's constricter runs isolated (`python -I -m constricter`) from the place's directory, whose
`pyproject.toml` it reads, with the place's environment as its `VIRTUAL_ENV`, with every scope, on
the place's target. A place is a corpus's own tree, or a copy of it for a fix: the copy keeps the
tree's layout, settings and environment, so a fix sees what a check of the tree did.
"""

import os
import shlex
import shutil
import subprocess  # runs each version under test
import sys
import tempfile
import threading
import time
from collections.abc import Iterator, Sequence
from fnmatch import fnmatch
from functools import cache
from pathlib import Path
from typing import IO, Final, NamedTuple, cast

from constricter.cli import paths
from tests.corpus import checker_settings, corpus_table
from tests.corpus.run_config import DEV, NAMED, ROOT
from tests.corpus.trees import Tree

# In an environment: a directory with its Python alone, for a path (see `_interpreters`).
_INTERPRETERS: Final = "corpus-suite-python"
_PYTHONS: Final = ("python", "python3")
_INSTALLING: Final = threading.Lock()
_PROBE: Final = "def f():\n    a = 1\n"
_FIXED: Final = '"fixed":'  # in `--fix --format=json`'s output, where it says what it fixed
_STUB: Final = ".pyi"


class Place(NamedTuple):
    """Where one constricter runs: its directory, what it checks there, and its environment."""

    cwd: Path
    target: Path
    environment: Path | None = None


class Ran(NamedTuple):
    """What one run gave."""

    output: str
    errors: str
    status: int
    seconds: float


def place(tree: Tree, neutral: Path) -> Place:
    """Place a run on `tree` itself: from its checkout, or from `neutral`, a directory with no settings.

    Returns:
      The place.

    """
    neutral.mkdir(parents=True, exist_ok=True)
    return Place(tree.base or neutral, tree.root, tree.environment)


def copied(tree: Tree, to: Path) -> tuple[Place, list[Path]]:
    """Copy `tree`'s Python files under `to`, fresh, laid out as they are under its checkout.

    With its stubs (`_stubs`), which a check reads for a module beside its source or, for a compiled
    one, alone, and the checkout's settings (`pyproject.toml`, and the type checkers' own files,
    which `--infer-with` starts them under), so the copy is checked as the tree is. A checker the
    copy has no settings for is given empty ones, an sdist's copy too (`checker_settings.own`):
    its root is then the copy, not this project above it.

    Returns:
      The copy's place, and each copied file that compiles.

    """
    shutil.rmtree(to, ignore_errors=True)
    target: Path = to / (tree.root.relative_to(tree.base) if tree.base else tree.root.name)
    valid: list[Path] = []
    source: Path
    for source in paths.python_files([tree.root]):
        copy: Path = target / source.relative_to(tree.root)
        copy.parent.mkdir(parents=True, exist_ok=True)
        _ = shutil.copyfile(source, copy)
        if corpus_table.compiles(copy):
            valid.append(copy)
    for source in _stubs(tree.root):
        copy = target / source.relative_to(tree.root)
        copy.parent.mkdir(parents=True, exist_ok=True)
        _ = shutil.copyfile(source, copy)
    to.mkdir(parents=True, exist_ok=True)
    name: str
    for name in checker_settings.FILES if tree.base else ():
        if (cast("Path", tree.base) / name).is_file():
            _ = shutil.copyfile(cast("Path", tree.base) / name, to / name)
    _ = checker_settings.own(to)
    return Place(to, target, tree.environment), valid


def _stubs(root: Path) -> Iterator[Path]:
    """Find the stubs under `root`, in the directories a check's walk enters (`paths.python_files`).

    Yields:
      Each `.pyi` file.

    """
    directory: str
    inner: list[str]
    names: list[str]
    for directory, inner, names in os.walk(root):
        inner[:] = [name for name in inner if not any(fnmatch(name, glob) for glob in paths.DEFAULT_EXCLUDES)]
        name: str
        for name in names:
            if name.endswith(_STUB):
                yield Path(directory, name)


def python(version: str) -> str:
    """Find the Python that runs `version`, one caller at a time: a release is installed the first time.

    A version written `NAME=PATH` is the constricter the Python at `PATH` runs (from this checkout's
    root, if it's relative).

    Returns:
      Its path.

    """
    if NAMED in version:  # another checkout's, say: `base=../base/local/.venv/bin/python`
        # A venv's Python as it's named, not the interpreter it links to.
        return os.path.normpath(ROOT / version.partition(NAMED)[2])
    with _INSTALLING:
        return corpus_table.interpreter(version)


def command(version: str, where: Place, options: Sequence[str], jobs: int) -> list[str]:
    """Write the command `run` runs, from `where`'s directory in `environment(where)`.

    With the run's own options after `options` (see `configure`).

    Returns:
      Its words.

    """
    return [
        python(version),
        *("-I", "-W", "ignore", "-m", "constricter"),
        *options,
        *OPTIONS,
        *(
            ("--no-gitignore",) if version == DEV else ()
        ),  # a suite's checkout is walked whole, as a release walks it
        "--all-scopes",
        f"--jobs={jobs}",
        os.path.relpath(where.target, where.cwd),
    ]


OPTIONS: Final[list[str]] = []  # the run's own options, given to every constricter command (see `configure`)


def configure(options: Sequence[str]) -> None:
    """Give every constricter command of this process's run `options`: a run file's, `--vague 0`."""
    OPTIONS[:] = list(options)


def environment(where: Place) -> dict[str, str]:
    """Return the environment a constricter runs in at `where`.

    Returns:
      This one, with the place's environment as its `VIRTUAL_ENV`, and on the path that
      environment's Python (`_interpreters`), then this Python's directory: `--infer-with`'s type
      checkers are found beside it.

    """
    first: list[str] = [] if where.environment is None else _interpreters(where.environment)
    path: str = os.pathsep.join(
        (*first, str(Path(sys.executable).parent), os.environ.get("PATH", os.defpath)),
    )
    return {**os.environ, "VIRTUAL_ENV": str(where.environment or sys.prefix), "PATH": path}


def _interpreters(prefix: Path) -> list[str]:
    """Make the directory that puts the environment at `prefix`'s Python, and nothing else of it, on a path.

    basedpyright asks the first `python` on the path for its packages, whatever `VIRTUAL_ENV`
    names; the environment's own directory there would put a corpus's type checkers before this
    Python's too.

    Returns:
      The directory, in a list; none for an environment with no Python (one not installed).

    """
    interpreter: Path = prefix / "bin" / _PYTHONS[0]
    if not interpreter.is_file():
        return []
    folder: Path = prefix / _INTERPRETERS
    script: str = f'#!/bin/sh\nexec {shlex.quote(str(interpreter))} "$@"\n'
    name: str
    for name in _PYTHONS:
        if not (folder / name).is_file() or (folder / name).read_text(encoding="utf-8") != script:
            folder.mkdir(parents=True, exist_ok=True)
            # Written whole, then named: another step of the run may be starting it.
            handle: int
            fresh: str
            handle, fresh = tempfile.mkstemp(dir=folder)
            stream: IO[str]
            with os.fdopen(handle, "w", encoding="utf-8") as stream:
                _ = stream.write(script)
            Path(fresh).chmod(0o755)
            _ = Path(fresh).replace(folder / name)
    return [str(folder)]


def run(version: str, where: Place, options: Sequence[str], jobs: int) -> Ran:
    """Run `version`'s constricter with `options` on `where`, with every scope and `jobs` processes.

    Returns:
      Its output, its errors, its exit status and the seconds it took.

    """
    start: float = time.perf_counter()
    done: subprocess.CompletedProcess[str] = subprocess.run(
        command(version, where, options, jobs),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        cwd=where.cwd,
        env=environment(where),
    )
    return Ran(done.stdout, done.stderr, done.returncode, time.perf_counter() - start)


def offered(version: str, *options: str) -> list[str]:
    """Keep the `options` `version`'s constricter has, as its `--help` lists them.

    Returns:
      Them: this checkout's has every one.

    """
    return [option for option in options if version == DEV or option in _helped(version)]


@cache
def _helped(version: str) -> frozenset[str]:
    """Read the words of `version`'s `--help`, once.

    Returns:
      Them.

    """
    done: subprocess.CompletedProcess[str] = subprocess.run(
        [python(version), "-I", "-m", "constricter", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return frozenset(done.stdout.split())


@cache
def lists_fixes(version: str) -> bool:
    """Ask whether `version`'s `--fix --format=json` says which offences it fixed (`fixed`).

    Returns:
      Whether it does: this checkout's does, and a release's by a fix of one line.

    """
    if version == DEV:
        return True
    scratch: str
    with tempfile.TemporaryDirectory() as scratch:
        probe: Path = Path(scratch) / "probe.py"
        _ = probe.write_text(_PROBE, encoding="utf-8")
        options: list[str] = ["--fix", "--show-fixes", "--format=json", "--level=suffocate"]
        ran: Ran = run(version, Place(Path(scratch), probe), options, 1)
    return _FIXED in ran.output
