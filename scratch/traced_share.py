"""Time one suite's released tests untraced, then traced by `constricter.trace` alone: no witness.

  local/.venv/bin/python -m scratch.traced_share SUITE

A corpus run's `traced` step times the same tests under the witness (`traced.json`'s `seconds`, in
its `traced` table): the witness's share of that run is what's over the seconds this prints for
the trace alone, and the tracer's what that is over the untraced tests'. The suite is installed
first if it isn't (the network, once). Outside a sandbox for a suite whose tests need one.
"""

import os
import sys
import time

from tests.corpus import catalog, corpus_suite


def main(name: str) -> int:
    suite = catalog.load().entry(name).suite
    if suite is None or not corpus_suite.traceable(suite):
        print(f"nothing runs {name}'s tests traced")
        return 1
    root = corpus_suite.checkout(name, suite)
    corpus_suite.reset(root, suite)
    start = time.perf_counter()
    plain = corpus_suite.tested(root, suite, None)
    untraced = time.perf_counter() - start
    print(f"{name} untraced: {untraced:.0f}s: {plain.counts}", flush=True)
    os.environ.pop(corpus_suite.TRACER_VARIABLE, None)  # the tracer itself, not the witness
    start = time.perf_counter()
    ran = corpus_suite.traced(root, suite)
    traced = time.perf_counter() - start
    print(f"{name} traced, no witness: {traced:.0f}s ({traced / untraced:.1f} times): {ran and ran[0]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
