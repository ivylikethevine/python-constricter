# SPDX-License-Identifier: MIT
"""Run each corpus package's tests as released and after `--fix --unsafe-fixes` with every `fix-widen` kind.

  local/.venv/bin/python -m scratch.widen_suites [SUITE ...]

As `tests/corpus/corpus_suite.py` runs them, with that one fixed run. Outside a sandbox.
"""

import sys

from tests.corpus import corpus_suite

corpus_suite.MODES = (
    ("--fix --unsafe-fixes --fix-widen=all", ("--unsafe-fixes", "--fix-widen=all")),
)

if __name__ == "__main__":
    sys.exit(corpus_suite.main(sys.argv[1:]))
