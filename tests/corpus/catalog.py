# SPDX-License-Identifier: MIT
"""The corpora a run can name: `corpora.toml`, read, and each one found on disk as a `Tree`.

A corpus is one tree for every step of a run: the standard library's directory, an unpacked sdist's
package, or a suite's checkout at its pinned tag, whose settings (`pyproject.toml`) and environment
(`.venv`) every constricter the run starts on it reads.
"""

import sysconfig
import tomllib
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from tests.corpus import corpus_sources, corpus_suite

CATALOG: Final = Path(__file__).with_name("corpora.toml")
STDLIB: Final = "stdlib"
SUITE: Final = "suite"
SDIST: Final = "sdist"
_Entry: TypeAlias = dict[str, str]


class Tree(NamedTuple):
    """One corpus on disk: what's checked, and where its settings and environment are."""

    name: str
    version: str
    root: Path  # the directory checked
    base: Path | None = None  # a suite's checkout, which `root` is under: its `pyproject.toml` is read
    environment: Path | None = None  # its venv: the installed packages constricter reads types from


class Catalog(NamedTuple):
    """`corpora.toml`: each corpus's entry, and each set's names."""

    entries: dict[str, _Entry]
    sets: dict[str, list[str]]

    def names(self, include: list[str]) -> list[str]:
        """Expand `include`, a run's corpora: a set's name stands for its corpora.

        Returns:
          The corpora's names, each once, in the order given.

        Raises:
          ValueError: one is neither a corpus nor a set.

        """
        found: dict[str, None] = {}
        name: str
        for name in include:
            if name not in self.sets and name not in self.entries:
                known: str = ", ".join((*self.sets, *self.entries))
                message: str = f"{name!r} is no corpus or set of {CATALOG.name}: {known}"
                raise ValueError(message)
            found.update(dict.fromkeys(self.sets.get(name, [name])))
        return list(found)

    def tree(self, name: str) -> Tree:
        """Find corpus `name` on disk, cloning and installing a suite or fetching an sdist the first time.

        Returns:
          Its tree.

        Raises:
          ValueError: its entry's `kind` is none this knows.

        """
        entry: _Entry = self.entries[name]
        kind: str = entry["kind"]
        if kind == STDLIB:
            return Tree(name, sysconfig.get_python_version(), Path(sysconfig.get_paths()["stdlib"]))
        if kind == SDIST:
            return Tree(name, corpus_sources.SOURCES[name].version, corpus_sources.fetch(name))
        if kind == SUITE:
            suite: corpus_suite.Suite = corpus_suite.SUITES[name]
            base: Path = corpus_suite.checkout(name, suite)
            corpus_suite.reset(base, suite)
            return Tree(name, entry["version"], base / suite.source, base, base / ".venv")
        message: str = f"{name}: kind {kind!r} is none of {STDLIB}, {SUITE}, {SDIST}"
        raise ValueError(message)


def load(path: Path = CATALOG) -> Catalog:
    """Read a catalog.

    Returns:
      It.

    """
    file: IO[bytes]
    with path.open("rb") as file:
        data: dict[str, dict[str, _Entry]] = tomllib.load(file)
    return Catalog(data.get("corpus", {}), cast("dict[str, list[str]]", data.get("sets", {})))
