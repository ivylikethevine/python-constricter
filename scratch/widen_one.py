# SPDX-License-Identifier: MIT
"""Fix one suite's checkout with every `fix-widen` kind, run its tests keeping their output, and keep the diff.

  local/.venv/bin/python -m scratch.widen_one SUITE

Both kept in `local/scratch/widen/`: for a suite `widen_suites` says differs. Outside a sandbox.
"""

import subprocess
import sys
from pathlib import Path

from tests.corpus import corpus_suite

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "widen"
WIDEN = ("--unsafe-fixes", "--fix-widen=all")


def fixed(root: Path, suite: corpus_suite.Suite, *extra: str) -> str:
    """Reset the checkout's source and `--fix` it with `extra`, at `suffocate` with every scope.

    Returns the size of the change, as `git diff --shortstat` puts it.
    """
    corpus_suite.reset(root, suite)
    constricter = str(Path(sys.executable).with_name("constricter"))
    command = [constricter, "--fix", *extra, "--level=suffocate", "--all-scopes", "--jobs=0", suite.source]
    subprocess.run(command, cwd=root, capture_output=True, check=False)
    return subprocess.run(
        ["git", "diff", "--shortstat"], cwd=root, capture_output=True, text=True, check=False
    ).stdout.strip()


def main(name: str) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    suite = corpus_suite.SUITES[name]
    root = corpus_suite.checkout(name, suite)
    change = fixed(root, suite, *WIDEN)
    diff = subprocess.run(["git", "diff"], cwd=root, capture_output=True, text=True, check=False).stdout
    (OUT / f"{name}-suite.diff").write_text(diff, encoding="utf-8")
    outcome = corpus_suite.tested(root, suite, OUT / f"{name}-widened.txt")
    print(name, change, outcome.counts, sorted(outcome.failed)[:20], flush=True)
    corpus_suite.reset(root, suite)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
