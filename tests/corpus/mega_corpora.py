# SPDX-License-Identifier: MIT
"""The super corpora run, on many more packages: what the seven corpora don't stand for.

  local/.venv/bin/python -m tests.corpus.mega_corpora            # everything; a stopped run resumes
  local/.venv/bin/python -m tests.corpus.mega_corpora --fresh    # forget what a stopped run finished
  local/.venv/bin/python -m tests.corpus.mega_corpora --print    # print the section, don't record it
  local/.venv/bin/python -m tests.corpus.mega_corpora NAME ...   # only these packages, printed

The catalog's `mega` set names them (`corpora.toml`, whose head says what each key of an entry is):
its pinned sdist, fetched once into `local/mega-corpora/sources/`, which is the corpus that's checked
and fixed, and its suite, read from its own CI. They're typed applications, `asyncio` code,
pytest-heavy test trees, scientific packages on numpy's types, packages with `TypedDict`s and
overloads of their own, and untyped ones for contrast.

It runs as `tests/corpus/super_corpora.py` does, with the same steps, the suites' tests traced too
where they can be, and writes `## Mega corpora` in docs/RUNS.md. A package with no suite is checked
and fixed alone; one whose suite can't be cloned or installed is too, and the section lists it with
the reason. A suite's commands are its CI's as far as `uv` and pytest can stand for them: what
fails as released fails the same after a fix, and only a difference counts. The packages'
dependencies aren't in this checkout's environment, so `--fix` reads no installed types for them
but numpy's and the corpus group's.
"""

import os
import sys
import tarfile
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple, cast

from tests.corpus import catalog, corpus_sources, super_corpora
from tests.corpus.corpus_sources import Source
from tests.corpus.corpus_suite import Suite
from tests.corpus.corpus_table import Corpus

_ROOT: Final = Path(__file__).resolve().parents[2]
WORK: Final = _ROOT / "local" / "mega-corpora"
_STEP_FLAG: Final = "--step"
# How long a suite's tests may run here (see `corpus_suite`): the longest took 6 minutes a run.
_SECONDS_VARIABLE: Final = "CORPUS_SUITE_SECONDS"
_SECONDS: Final = "900"


class Package(NamedTuple):
    """One package: why it's here, its pinned sdist, its suite if it has one, and what its commands need."""

    why: str
    source: Source
    suite: Suite | None
    environment: dict[str, str]  # set for its steps (see `main`)
    port: str  # the port its tests bind, or ""


def packages() -> dict[str, Package]:
    """Read the catalog's `mega` set.

    Returns:
      Each package, by its name.

    """
    known: catalog.Catalog = catalog.load()
    found: dict[str, Package] = {}
    name: str
    for name in known.sets[catalog.MEGA]:
        entry: catalog.Entry = known.entries[name]
        source: Source = cast("Source", entry.source)
        found[name] = Package(entry.why, source, entry.suite, entry.environment, entry.port)
    return found


PACKAGES: Final = packages()


def corpora() -> list[Corpus]:
    """Fetch each package's sdist (once).

    Returns:
      A corpus for each; one that can't be fetched is left out, with a note on standard error.

    """
    sources: dict[str, Source] = {name: package.source for name, package in PACKAGES.items()}
    found: list[Corpus] = []
    name: str
    for name in PACKAGES:
        try:
            root: Path = corpus_sources.fetch(name, WORK / "sources", sources)
        except (OSError, ValueError, tarfile.TarError) as failure:
            _ = sys.stderr.write(f"{name}: not fetched: {failure}\n")
            continue
        found.append(Corpus(name, sources[name].version, root))
    return found


MEGA: Final = super_corpora.Plan(
    "tests.corpus.mega_corpora",
    "## Mega corpora",
    f"{len(PACKAGES)} more packages, every way (`tests/corpus/mega_corpora.py`):",
    WORK,
    corpora,
    {name: package.suite for name, package in PACKAGES.items() if package.suite is not None},
    ports={name: package.port for name, package in PACKAGES.items() if package.port},
    traced=True,
)


def main(argv: Sequence[str]) -> int:
    """Run as `super_corpora.main` does, on these packages; a step with its package's environment.

    Returns:
      1 if a fix broke anything or a step failed, else 0.

    """
    _ = os.environ.setdefault(_SECONDS_VARIABLE, _SECONDS)
    if argv[:1] == [_STEP_FLAG]:
        os.environ.update(PACKAGES[argv[2]].environment)
    return super_corpora.main(argv, MEGA)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
