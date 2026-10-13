# SPDX-License-Identifier: MIT
"""A corpus on disk, one tree for every step of a run.

The standard library's directory; a suite's checkout at its pinned tag, whose settings
(`pyproject.toml`) and environment (`.venv`) every constricter the run starts on it reads; or, for a
corpus with no suite, its unpacked sdist's package.
"""

import sysconfig
from pathlib import Path
from typing import NamedTuple

from tests.corpus import corpus_sources, corpus_suite
from tests.corpus.catalog import Entry, Suite


class Tree(NamedTuple):
    """One corpus on disk: what's checked, and where its settings and environment are."""

    name: str
    version: str
    root: Path  # the directory checked
    base: Path | None = None  # a suite's checkout, which `root` is under: its `pyproject.toml` is read
    environment: Path | None = None  # its venv: the installed packages constricter reads types from
    suite: Suite | None = None
    variables: dict[str, str] | None = None  # what the suite's commands need set


def found(entry: Entry, *, install: bool = True) -> Tree:
    """Find a corpus on disk, cloning and installing its suite or fetching its sdist the first time.

    Without `install`, a suite is cloned alone: its source and settings, with no environment to read
    installed packages' types from, and no suite to run.

    Returns:
      Its tree.

    Raises:
      ValueError: the entry has neither a suite nor an sdist, and isn't the standard library.

    """
    if entry.path:
        return Tree(entry.name, "", Path(entry.path).resolve())
    if entry.stdlib:
        return Tree(entry.name, sysconfig.get_python_version(), Path(sysconfig.get_paths()["stdlib"]))
    if entry.suite is not None:
        base: Path = corpus_suite.checkout(
            entry.name,
            entry.suite,
            install=install,
            variables=entry.environment,
        )
        corpus_suite.reset(base, entry.suite)
        source: Path = base / entry.suite.source
        if not install:
            return Tree(entry.name, entry.version, source, base)
        return Tree(entry.name, entry.version, source, base, base / ".venv", entry.suite, entry.environment)
    if entry.source is not None:
        sources: dict[str, corpus_sources.Source] = {entry.name: entry.source}
        return Tree(entry.name, entry.version, corpus_sources.fetch(entry.name, sources=sources))
    message: str = f"{entry.name}: neither a suite nor an sdist"
    raise ValueError(message)
