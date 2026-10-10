# SPDX-License-Identifier: MIT
"""The super corpora run, on many more packages: what the seven corpora don't stand for.

  local/.venv/bin/python -m tests.corpus.mega_corpora            # everything; a stopped run resumes
  local/.venv/bin/python -m tests.corpus.mega_corpora --fresh    # forget what a stopped run finished
  local/.venv/bin/python -m tests.corpus.mega_corpora --print    # print the section, don't record it
  local/.venv/bin/python -m tests.corpus.mega_corpora NAME ...   # only these packages, printed

`mega_packages.json` pins each one: its sdist on PyPI's file host (`where`, the directory its hash
names, and `archive`; fetched once into `local/mega-corpora/sources/`, its SHA-256 checked, as
`tests/corpus/corpus_sources.py` fetches Twisted), which is the corpus that's checked and fixed
(`package`, its directory in the sdist); and its `suite`, read from its own CI: the repository and
tag to clone, its `source` there, the `uv` commands installing it (`pip ...` for
`uv pip install`, into a venv made first; `sync ...` for `uv sync`), its `tests` (pytest's
arguments, or a whole command after `!`; `{workers}` stands for its processes), its type
`checks`, and whether its build needs its `submodules`. `alone` says why a package has no suite
here, `environment` what its commands need set,
and `port` the port its tests' own server binds: those of one port run one at a time (httpx's wait
for theirs forever, where another suite has it). They're typed applications, `asyncio` code,
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

import json
import os
import shlex
import sys
import tarfile
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from tests.corpus import corpus_sources, super_corpora
from tests.corpus.corpus_sources import Source
from tests.corpus.corpus_suite import Suite
from tests.corpus.corpus_table import Corpus

_Json: TypeAlias = "str | list[str] | dict[str, _Json]"
_ROOT: Final = Path(__file__).resolve().parents[2]
WORK: Final = _ROOT / "local" / "mega-corpora"
_PINNED: Final = Path(__file__).with_name("mega_packages.json")
_FILES: Final = "https://files.pythonhosted.org/packages"
_PYTHON: Final = sys.executable
_VENV: Final = ("venv", "-q", "--allow-existing", "--python", _PYTHON, ".venv")
_PYTEST: Final = ("python", "-m", "pytest", "-q", "-rfE", "-p", "no:cacheprovider")
_PIP: Final = "pip"
_RAW: Final = "!"  # before a test command that isn't pytest's
_WORKERS: Final = "{workers}"
_MOST: Final = 8  # the most processes a suite here is given: none was sized by a run
_STEP_FLAG: Final = "--step"
# How long a suite's tests may run here (see `corpus_suite`): the longest took 6 minutes a run.
_SECONDS_VARIABLE: Final = "CORPUS_SUITE_SECONDS"
_SECONDS: Final = "900"
_SUITE: Final = "suite"


class Package(NamedTuple):
    """One package: why it's here, its pinned sdist, its suite if it has one, and what its commands need."""

    why: str
    source: Source
    suite: Suite | None
    environment: dict[str, str]  # set for its steps (see `main`)
    port: str  # the port its tests bind, or ""


def _installing(commands: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    """Read a suite's install commands (see the module's docstring).

    Returns:
      Each as `uv`'s arguments, after the venv's where the first installs with `uv pip`.

    """
    found: list[tuple[str, ...]] = [_VENV] if commands[0].startswith(_PIP) else []
    command: str
    for command in commands:
        kind: str
        rest: list[str]
        kind, *rest = shlex.split(command)
        found.append(
            (_PIP, "install", "-q", *rest) if kind == _PIP else (kind, "-q", *rest, "--python", _PYTHON),
        )
    return tuple(found)


def _suite(pinned: dict[str, _Json]) -> Suite:
    """Read a package's suite.

    Returns:
      It.

    """
    tests: str = cast("str", pinned["tests"])
    return Suite(
        cast("str", pinned["repository"]),
        cast("str", pinned["tag"]),
        cast("str", pinned["source"]),
        _installing(cast("list[str]", pinned["install"])),
        tuple(shlex.split(tests.removeprefix(_RAW)))
        if tests.startswith(_RAW)
        else (*_PYTEST, *shlex.split(tests)),
        tuple(tuple(shlex.split(check)) for check in cast("list[str]", pinned["checks"])),
        most=_MOST if _WORKERS in tests else 1,
        submodules=bool(pinned.get("submodules")),
    )


def packages() -> dict[str, Package]:
    """Read `mega_packages.json`.

    Returns:
      Each package, by its name.

    """
    found: dict[str, Package] = {}
    pinned: dict[str, _Json]
    for pinned in cast("list[dict[str, _Json]]", json.loads(_PINNED.read_text(encoding="utf-8"))):
        source: Source = Source(
            cast("str", pinned["version"]),
            f"{_FILES}/{pinned['where']}/{pinned['archive']}",
            cast("str", pinned["sha256"]),
            cast("str", pinned["package"]),
        )
        found[cast("str", pinned["name"])] = Package(
            cast("str", pinned["why"]),
            source,
            _suite(cast("dict[str, _Json]", pinned[_SUITE])) if _SUITE in pinned else None,
            cast("dict[str, str]", pinned.get("environment", {})),
            cast("str", pinned.get("port", "")),
        )
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
