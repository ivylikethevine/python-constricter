# SPDX-License-Identifier: MIT
"""Run each corpus package's tests as released and after `--fix --unsafe-fixes` with every `fix-widen` kind.

  local/.venv/bin/python -m scratch.widen_suites [SUITE ...]

Each of the seven corpora's suites (default: all), with that one fixed run (`widen_one.fixed`); it
exits 1 if a fixed run's outcome isn't its released one's. Outside a sandbox.
"""

import sys

from scratch.widen_one import WIDEN, fixed
from tests.corpus import corpus_suite


def main(names: list[str]) -> int:
    same = True
    for name in names or corpus_suite.SUITES:
        suite = corpus_suite.SUITES[name]
        root = corpus_suite.checkout(name, suite)
        corpus_suite.reset(root, suite)
        released = corpus_suite.tested(root, suite, None)
        print(f"{name} {suite.tag}: released: {released.counts}", flush=True)
        change = fixed(root, suite, *WIDEN)
        outcome = corpus_suite.tested(root, suite, None)
        print(f"  widened ({change}): {outcome.counts}: {'same' if outcome == released else 'DIFFERENT'}", flush=True)
        for test in sorted(outcome.failed ^ released.failed):
            print(f"    {'now fails' if test in outcome.failed else 'now passes'}: {test}", flush=True)
        same = same and outcome == released
        corpus_suite.reset(root, suite)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
