# SPDX-License-Identifier: MIT
"""The corpora a run can name: `corpora.toml`, read (its head says what each key is).

Each corpus is an `Entry`: why it's here, its pinned sdist if it has one (`corpus_sources.Source`),
and its suite if it has one (`Suite`: its repository at a pinned tag, and how its CI installs, tests
and type-checks it). Every script that names a corpus, a suite or an sdist reads it from here.
"""

import shlex
import sys
import tomllib
from functools import cache
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast

from tests.corpus import corpus_sources
from tests.corpus.corpus_sources import CATALOG, Source

FULL: Final = "full"  # the set every released version is measured on
SUPER: Final = "super"  # and it with every fast corpus
MEGA: Final = "mega"  # and every corpus
WORKERS: Final = "{workers}"  # in a test command's word: how many processes to take
PYTHON: Final = sys.executable
VENV: Final = ("venv", "-q", "--allow-existing", "--python", PYTHON, ".venv")
PYTEST: Final = ("python", "-m", "pytest", "-q", "-rfE", "-p", "no:cacheprovider")
_PIP: Final = "pip"
_SUITE: Final = "suite"  # an entry's table
_RAW: Final = "!"  # before a test command that isn't pytest's
_MOST: Final = 8  # the most processes a suite is given where its entry doesn't say
_Table: TypeAlias = dict[str, object]  # a table of the catalog, as `tomllib` reads it


class Suite(NamedTuple):
    """One package's repository, pinned tag and source, and how its CI installs, tests and checks it."""

    repository: str
    tag: str
    source: str  # relative to the checkout
    install: tuple[tuple[str, ...], ...]  # `uv` commands installing it and its tests' dependencies in `.venv`
    # The command running its tests, the first word from `.venv/bin`; `WORKERS` in a word stands for
    # how many processes it's to take (see `corpus_suite.workers`).
    tests: tuple[str, ...]
    checks: tuple[tuple[str, ...], ...] = ()  # its CI's type checks, each's first word from `.venv/bin`
    left_out: str = ""  # requirements it can't build here, which `--excludes -` reads
    most: int = 1  # the most processes its tests can keep busy: with `parts`, the parts at once
    worker_memory: float = 1.0  # the gigabytes one of them takes
    submodules: bool = False  # its build needs its repository's submodules (aiohttp's, llhttp)
    # A script and its arguments running its tests in one process, where pytest doesn't run them:
    # what a trace traces, the script's directory on the path as `python` puts it there.
    script: tuple[str, ...] = ()
    # The tests a fix may change the outcome of, each with why: a difference in these alone is no
    # difference (`suite_steps.tests`).
    differs: tuple[tuple[str, str], ...] = ()
    # Its tests' arguments, part by part, each part a process of its own after `tests`, as many at
    # once as it has workers: for tests that hold in one process more than a machine has (celery's,
    # 25 GB).
    parts: tuple[str, ...] = ()


class Entry(NamedTuple):
    """One corpus of the catalog."""

    name: str
    version: str
    why: str
    source: Source | None  # its pinned sdist
    suite: Suite | None
    environment: dict[str, str]  # what its commands need set
    port: str  # the port its tests bind, or ""
    path: str = ""  # a directory a run names itself: no corpus of the catalog
    heavy: bool = False  # its suite's tests hold more memory than a machine has to share: they run alone


def _installing(commands: list[str]) -> tuple[tuple[str, ...], ...]:
    """Read a suite's install commands.

    Returns:
      Each as `uv`'s arguments, after the venv's where the first installs with `uv pip`.

    """
    found: list[tuple[str, ...]] = [VENV] if commands[0].startswith(_PIP) else []
    command: str
    for command in commands:
        kind: str
        rest: list[str]
        kind, *rest = shlex.split(command)
        found.append(
            (_PIP, "install", "-q", *rest) if kind == _PIP else (kind, "-q", *rest, "--python", PYTHON),
        )
    return tuple(found)


def _suite(pinned: _Table) -> Suite:
    """Read a corpus's `suite` table.

    Returns:
      The suite.

    """
    tests: str = cast("str", pinned["tests"])
    parts: tuple[str, ...] = tuple(cast("list[str]", pinned.get("parts", [])))
    return Suite(
        cast("str", pinned["repository"]),
        cast("str", pinned["tag"]),
        cast("str", pinned["source"]),
        _installing(cast("list[str]", pinned["install"])),
        tuple(shlex.split(tests.removeprefix(_RAW)))
        if tests.startswith(_RAW)
        else (*PYTEST, *shlex.split(tests)),
        tuple(tuple(shlex.split(check)) for check in cast("list[str]", pinned["checks"])),
        cast("str", pinned.get("left-out", "")),
        cast("int", pinned.get("most", len(parts) or (_MOST if WORKERS in tests else 1))),
        cast("float", pinned.get("worker-memory", 1.0)),
        bool(pinned.get("submodules")),
        tuple(shlex.split(cast("str", pinned.get("script", "")))),
        tuple(cast("dict[str, str]", pinned.get("differs", {})).items()),
        parts,
    )


class Catalog(NamedTuple):
    """`corpora.toml`: each corpus's entry, and each set's names."""

    entries: dict[str, Entry]
    sets: dict[str, list[str]]

    def names(self, include: list[str], minus: list[str] | None = None) -> list[str]:
        """Expand `include`, a run's corpora, less `minus`'s: a set stands for its corpora.

        Returns:
          The corpora's names, each once, in the order given.

        """
        gone: dict[str, None] = self._expanded(minus or [], ())
        return [name for name in self._expanded(include, ()) if name not in gone]

    def _expanded(self, names: list[str], within: tuple[str, ...]) -> dict[str, None]:
        """Expand `names`, a set's names standing for its own, inside the sets `within`.

        Returns:
          The corpora's names, each once, in the order given.

        Raises:
          ValueError: one is neither a corpus, a set, nor a directory, or a set names itself.

        """
        found: dict[str, None] = {}
        name: str
        for name in names:
            message: str
            if name in within:
                message = f"the set {name!r} of {CATALOG.name} names itself, by {' > '.join((*within, name))}"
                raise ValueError(message)
            if name in self.sets:
                found.update(self._expanded(self.sets[name], (*within, name)))
            elif name in self.entries or Path(name).is_dir():
                found[name] = None
            else:
                known: str = ", ".join((*self.sets, *self.entries))
                message = f"{name!r} is no directory, and no corpus or set of {CATALOG.name}: {known}"
                raise ValueError(message)
        return found

    def entry(self, name: str) -> Entry:
        """Find the entry of the corpus `name`: the catalog's, or one made for a directory.

        Returns:
          The entry.

        """
        return self.entries.get(name) or Entry(
            Path(name).resolve().name,
            "",
            "",
            None,
            None,
            {},
            "",
            path=name,
        )

    def suites(self, among: str) -> dict[str, Suite]:
        """Find the suites of the set `among`.

        Returns:
          Each by its corpus's name.

        """
        found: dict[str, Suite] = {}
        name: str
        for name in self.names([among]):
            suite: Suite | None
            if (suite := self.entries[name].suite) is not None:
                found[name] = suite
        return found


@cache
def load() -> Catalog:
    """Read `corpora.toml`.

    Returns:
      The catalog.

    """
    file: IO[bytes]
    with CATALOG.open("rb") as file:
        data: _Table = tomllib.load(file)
    sources: dict[str, Source] = corpus_sources.pinned()
    entries: dict[str, Entry] = {}
    name: str
    pinned: _Table
    for name, pinned in cast("dict[str, _Table]", data["corpus"]).items():
        entries[name] = Entry(
            name,
            cast("str", pinned.get("version", "")),
            cast("str", pinned.get("why", "")),
            sources.get(name),
            _suite(cast("_Table", pinned[_SUITE])) if _SUITE in pinned else None,
            cast("dict[str, str]", pinned.get("environment", {})),
            cast("str", pinned.get("port", "")),
            heavy=bool(pinned.get("heavy")),
        )
    return Catalog(entries, cast("dict[str, list[str]]", data["sets"]))
