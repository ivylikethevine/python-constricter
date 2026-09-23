# SPDX-License-Identifier: MIT
"""Run a corpus package's own test suite before and after `--fix`, and after `--fix --unsafe-fixes`.

  local/.venv/bin/python tests/corpus/corpus_suite.py            # every suite below
  local/.venv/bin/python tests/corpus/corpus_suite.py NAME ...   # just these

Each package's source is cloned at its pinned tag into `local/corpus-suites/`, its locked test
dependencies installed there with `uv sync --locked` (its own `uv.lock`), and its tests run three
times: as released, after `--fix`, and after `--fix --unsafe-fixes` (the source reset in between),
at `suffocate` with `all-scopes`, as `tests/corpus/corpus_fix.py` fixes. Each run's outcome is its
pytest summary counts and the tests that failed; the command exits 1 if a fixed run's differs from
the released one's. It needs `git`, `uv` and the network; CI doesn't run it.

A local variable's annotation is never evaluated at runtime (PEP 526), so these runs catch a fix
that breaks the code itself (a declaration, a dropped comment or annotation, a module's
`__annotations__`), not a wrong type: that's a type checker's job.
"""

import os
import re
import shutil
import subprocess  # runs git, uv, pytest and constricter
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple, cast


class Suite(NamedTuple):
    """One package's repository, the tag the corpus pins, where its source is, and its test group."""

    repository: str
    tag: str
    source: str  # relative to the checkout
    group: str  # the dependency group its `uv.lock` installs for its tests


WORK: Final = Path(__file__).resolve().parents[2] / "local" / "corpus-suites"
# None yet: flask's and fastapi's were run (identical after `--fix`, see docs/RUNS.md) until they left
# the corpus; the remaining corpora's are the roadmap's next.
SUITES: Final[dict[str, Suite]] = {}
_EVERYWHERE: Final = ("--level=suffocate", "--all-scopes", "--jobs=0", "-q")
_FAILED: Final = re.compile(r"^(?:FAILED|ERROR) (\S+)", re.MULTILINE)
_COUNTS: Final = re.compile(r"(\d+) (passed|failed|skipped|xfailed|xpassed|errors?|warnings?)")
_CONSTRICTER: Final = Path(sys.executable).with_name("constricter")
_OUR_ENVIRONMENT: Final = "UV_PROJECT_ENVIRONMENT"  # this checkout's venv; each suite uses its own


class Outcome(NamedTuple):
    """What one test run gave: its summary counts, and the tests that failed or errored."""

    counts: dict[str, int]
    failed: frozenset[str]


def _run(args: Sequence[str], cwd: Path) -> str:
    """Run a command in `cwd`.

    Returns:
      Its standard output and error, together.

    """
    done: subprocess.CompletedProcess[str] = subprocess.run(
        list(args),
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
        cwd=cwd,
        env={key: value for key, value in os.environ.items() if key != _OUR_ENVIRONMENT},
    )
    return done.stdout + done.stderr


def checkout(name: str, suite: Suite) -> Path:
    """Clone (once) `suite` at its tag and install its locked test dependencies.

    Returns:
      The checkout.

    """
    root: Path = WORK / f"{name}-{suite.tag}"
    uv: str = os.environ.get("UV") or shutil.which("uv") or "uv"
    if not root.is_dir():
        WORK.mkdir(parents=True, exist_ok=True)
        _ = _run(
            ["git", "clone", "-q", "--depth", "1", "--branch", suite.tag, suite.repository, str(root)],
            WORK,
        )
    _ = _run([uv, "sync", "-q", "--locked", "--group", suite.group, "--python", sys.executable], root)
    return root


def tested(root: Path) -> Outcome:
    """Run the checkout's tests.

    Returns:
      Their outcome.

    """
    output: str = _run(
        [str(root / ".venv" / "bin" / "python"), "-m", "pytest", "-q", "-rfE", "-p", "no:cacheprovider"],
        root,
    )
    summary: str = output.strip().rsplit("\n", 1)[-1]
    counts: list[tuple[str, str]] = cast("list[tuple[str, str]]", _COUNTS.findall(summary))
    return Outcome(
        {kind.rstrip("s") if kind.startswith("error") else kind: int(n) for n, kind in counts},
        frozenset(cast("list[str]", _FAILED.findall(output))),
    )


def fixed(root: Path, suite: Suite, *extra: str) -> str:
    """Reset the checkout's source, then `--fix` it (with `extra` options).

    Returns:
      The size of the change, as `git diff --shortstat` puts it.

    """
    _ = _run(["git", "checkout", "-q", "--", suite.source], root)
    _ = _run([str(_CONSTRICTER), "--fix", *extra, *_EVERYWHERE, suite.source], root)
    return _run(["git", "diff", "--shortstat"], root).strip()


def main(argv: Sequence[str]) -> int:
    """Run each suite named (default: all) as released, fixed, and fixed with guesses.

    Returns:
      0 if every fixed run's outcome matches its released one, else 1.

    """
    same: bool = True
    name: str
    for name in argv or SUITES:
        suite: Suite = SUITES[name]
        root: Path = checkout(name, suite)
        _ = _run(["git", "checkout", "-q", "--", suite.source], root)
        released: Outcome = tested(root)
        _ = sys.stdout.write(f"{name} {suite.tag}: released: {released.counts}\n")
        label: str
        options: tuple[str, ...]
        test: str
        for label, options in (("--fix", ()), ("--fix --unsafe-fixes", ("--unsafe-fixes",))):
            change: str = fixed(root, suite, *options)
            outcome: Outcome = tested(root)
            verdict: str = "same" if outcome == released else "DIFFERENT"
            _ = sys.stdout.write(f"  {label} ({change}): {outcome.counts}: {verdict}\n")
            for test in sorted(outcome.failed ^ released.failed):
                _ = sys.stdout.write(
                    f"    {'now fails' if test in outcome.failed else 'now passes'}: {test}\n",
                )
            same = same and outcome == released
        _ = _run(["git", "checkout", "-q", "--", suite.source], root)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
