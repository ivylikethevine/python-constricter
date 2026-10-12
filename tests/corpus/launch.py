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
from typing import Final, NamedTuple

from constricter.cli import paths
from tests.corpus import corpus_table
from tests.corpus.catalog import Tree
from tests.corpus.run_config import DEV

_SETTINGS: str = "pyproject.toml"
_INSTALLING: Final = threading.Lock()
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

    With the checkout's `pyproject.toml`, so the copy is checked under the tree's settings.

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
    if tree.base and (tree.base / _SETTINGS).is_file():
        _ = shutil.copyfile(tree.base / _SETTINGS, to / _SETTINGS)
    return Place(to, target, tree.environment), valid


def _python(version: str) -> str:
    """Find the Python that runs `version`, one caller at a time: a release is installed the first time.

    Returns:
      Its path.

    """
    with _INSTALLING:
        return corpus_table.interpreter(version)


def run(version: str, where: Place, options: Sequence[str], jobs: int) -> Ran:
    """Run `version`'s constricter with `options` on `where`, with every scope and `jobs` processes.

    Returns:
      Its output, its errors, its exit status and the seconds it took.

    """
    start: float = time.perf_counter()
    done: subprocess.CompletedProcess[str] = subprocess.run(
        [
            _python(version),
            *("-I", "-W", "ignore", "-m", "constricter"),
            *options,
            "--all-scopes",
            f"--jobs={jobs}",
            os.path.relpath(where.target, where.cwd),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        cwd=where.cwd,
        env={**os.environ, "VIRTUAL_ENV": str(where.environment or sys.prefix)},
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
