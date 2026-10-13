# SPDX-License-Identifier: MIT
"""The one way a run starts constricter: every step's check, fix and count goes through `run`.

A version's constricter runs isolated (`python -I -m constricter`) from the place's directory, whose
`pyproject.toml` it reads, with the place's environment as its `VIRTUAL_ENV`, with every scope, on
the place's target. A place is a corpus's own tree, or a copy of it for a fix: the copy keeps the
tree's layout, settings and environment, so a fix sees what a check of the tree did.
"""

import os
import shutil
import subprocess  # runs each version under test
import sys
import tempfile
import threading
import time
from collections.abc import Sequence
from functools import cache
from pathlib import Path
from typing import Final, NamedTuple, cast

from constricter.cli import paths
from tests.corpus import corpus_table
from tests.corpus.run_config import DEV, NAMED
from tests.corpus.trees import Tree

_SETTINGS: Final = ("pyproject.toml", "pyrightconfig.json", "pyrefly.toml")
_INSTALLING: Final = threading.Lock()
_ROOT: Final = Path(__file__).resolve().parents[2]
_PROBE: Final = "def f():\n    a = 1\n"
_FIXED: Final = '"fixed":'  # in `--fix --format=json`'s output, where it says what it fixed


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

    With the checkout's settings (`pyproject.toml`, and the type checkers' own files, which
    `--infer-with` starts them under), so the copy is checked as the tree is.

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
    to.mkdir(parents=True, exist_ok=True)
    name: str
    for name in _SETTINGS if tree.base else ():
        if (cast("Path", tree.base) / name).is_file():
            _ = shutil.copyfile(cast("Path", tree.base) / name, to / name)
    return Place(to, target, tree.environment), valid


def python(version: str) -> str:
    """Find the Python that runs `version`, one caller at a time: a release is installed the first time.

    A version written `NAME=PATH` is the constricter the Python at `PATH` runs (from this checkout's
    root, if it's relative).

    Returns:
      Its path.

    """
    if NAMED in version:  # another checkout's, say: `base=../base/local/.venv/bin/python`
        # A venv's Python as it's named, not the interpreter it links to.
        return os.path.normpath(_ROOT / version.partition(NAMED)[2])
    with _INSTALLING:
        return corpus_table.interpreter(version)


def command(version: str, where: Place, options: Sequence[str], jobs: int) -> list[str]:
    """Write the command `run` runs, from `where`'s directory in `environment(where)`.

    Returns:
      Its words.

    """
    return [
        python(version),
        *("-I", "-W", "ignore", "-m", "constricter"),
        *options,
        "--all-scopes",
        f"--jobs={jobs}",
        os.path.relpath(where.target, where.cwd),
    ]


def environment(where: Place) -> dict[str, str]:
    """Return the environment a constricter runs in at `where`.

    Returns:
      This one, with the place's environment as its `VIRTUAL_ENV`, and this Python's directory on
      the path: `--infer-with`'s type checkers are found beside it.

    """
    path: str = os.pathsep.join((str(Path(sys.executable).parent), os.environ.get("PATH", os.defpath)))
    return {**os.environ, "VIRTUAL_ENV": str(where.environment or sys.prefix), "PATH": path}


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
