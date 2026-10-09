# SPDX-License-Identifier: MIT
"""Measure one corpus's annotation coverage with this checkout and a base's constricter.

The Corpus coverage workflow runs it on a pull request, and comments with what it prints:

  local/.venv/bin/python -m tests.corpus.corpus_coverage stdlib --base local/base/local/.venv/bin/python

The corpus is this Python's standard library (`stdlib`) or one of the `corpus` group's packages. For
each side, `head` (this checkout) and `base` (the constricter that `--base`'s Python runs), it
prints as JSON the corpus's bindings typed as released, after `--fix`, and after `--fix
--unsafe-fixes`: each `[typed, total]`, `null` where that fix crashed. Every count is this
checkout's `--coverage` with `all-scopes`, as corpus_table.py counts every version. And under
`timed`, the milliseconds a check of it takes each side in one process: the median of `_RUNS`, the
sides' runs in turn.
"""

import argparse
import importlib
import json
import platform
import statistics
import sys
import sysconfig
from collections.abc import Sequence
from importlib import metadata
from pathlib import Path
from typing import Final, TypeAlias, cast

from tests.corpus.corpus_table import DEV, PACKAGES, Corpus, Typed, check_seconds, coverage, interpreter

_Counts: TypeAlias = dict[str, list[int] | None]  # `[typed, total]` by when, `None` where a fix crashed

_BASE: Final = "base"
_HEAD: Final = "head"
_RUNS: Final = 5  # timed checks a side
_STDLIB: Final = "stdlib"


def _counts(found: tuple[Typed, Typed | None, Typed | None]) -> _Counts:
    """Name each count, as `[typed, total]`.

    Returns:
      Them, by when they were counted.

    """
    released: Typed
    fixed: Typed | None
    guessed: Typed | None
    released, fixed, guessed = found
    return {
        "released": list(released),
        "fixed": None if fixed is None else list(fixed),
        "guessed": None if guessed is None else list(guessed),
    }


def _timed(sides: dict[str, str], root: Path) -> dict[str, int]:
    """Time a check of `root` with each side's Python (`sides`), `_RUNS` times, a run of each in turn.

    Returns:
      Each side's median, in milliseconds.

    """
    taken: dict[str, list[float]] = {side: [] for side in sides}
    for _ in range(_RUNS):
        side: str
        python: str
        for side, python in sides.items():
            taken[side].append(check_seconds(python, root))
    return {side: round(statistics.median(each) * 1000) for side, each in taken.items()}


def _corpus(name: str) -> Corpus:
    """Find the standard library (`stdlib`), or an installed `corpus` package.

    Returns:
      It.

    """
    if name == _STDLIB:
        return Corpus(_STDLIB, platform.python_version(), Path(sysconfig.get_paths()["stdlib"]))
    module_file: str = cast("str", importlib.import_module(name).__file__)
    return Corpus(name, metadata.version(name), Path(module_file).parent)


def main(argv: Sequence[str] | None = None) -> int:
    """Measure the corpus with both constricters, and print the counts.

    Returns:
      0.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="A corpus's annotation coverage, with this checkout and a base's constricter.",
    )
    _ = parser.add_argument("corpus", choices=[_STDLIB, *PACKAGES])
    _ = parser.add_argument("--base", required=True, help="a Python the base's constricter is installed in")
    options: argparse.Namespace = parser.parse_args(argv)
    corpus: Corpus = _corpus(cast("str", options.corpus))
    # Absolute, since each run starts from `WORK`; not resolved, which would leave the venv.
    base: str = str(Path(cast("str", options.base)).absolute())
    result: dict[str, str | _Counts | dict[str, int]] = {
        "corpus": corpus.name,
        "version": corpus.version,
        _HEAD: _counts(coverage(interpreter(DEV), corpus, DEV)),
        _BASE: _counts(coverage(base, corpus, _BASE)),
        "timed": _timed({_HEAD: interpreter(DEV), _BASE: base}, corpus.root),
    }
    _ = sys.stdout.write(f"{json.dumps(result)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
