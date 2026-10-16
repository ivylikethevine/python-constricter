# SPDX-License-Identifier: MIT
"""Time a check's second round, where a file is checked again knowing its parameters, against its first.

  local/.venv/bin/python -m scratch.second_round                        # the standard library
  local/.venv/bin/python -m scratch.second_round pandas django pip      # those corpora, one at a time

Checks each corpus at `suffocate` in one process (`--jobs=1`), timing every `checker.checked_tree`
call: a first check, or a second one `_resumed` from where the first ended. A resumed check's time
is split into its rounds (`_resumed`) and what follows them over the whole module (the flow, the
reported offences, what its functions return). Prints each corpus's seconds of first checks and of
second ones, their ratio, and the second rounds' split. Runs in a sandbox (one process).
"""

import argparse
import os
import sys
import time
from collections import defaultdict

from constricter.cli import command
from constricter.rules import checker
from tests.corpus import corpus_table


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpora", nargs="*", default=["standard library"])
    args = parser.parse_args()
    roots = {each.name: each.root for each in corpus_table.corpora()}
    seconds: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)
    state = {"resumed": False}
    checked_tree, resumed = checker.checked_tree, checker._resumed

    def timed_resumed(*a, **k):
        start = time.perf_counter()
        found = resumed(*a, **k)
        if found is not None:
            seconds["rounds"] += time.perf_counter() - start
            state["resumed"] = True
        return found

    def timed_tree(*a, **k):
        state["resumed"] = False
        start = time.perf_counter()
        found = checked_tree(*a, **k)
        kind = "second" if state["resumed"] else "first"
        seconds[kind] += time.perf_counter() - start
        counts[kind] += 1
        return found

    checker._resumed = timed_resumed
    checker.checked_tree = timed_tree
    for name in args.corpora:
        seconds.clear()
        counts.clear()
        start = time.perf_counter()
        with open(os.devnull, "w", encoding="utf-8") as sink:
            stdout, sys.stdout = sys.stdout, sink
            try:
                command.main(["--level=suffocate", "--all-scopes", "--jobs=1", "--exit-zero", "-q", str(roots[name])])
            finally:
                sys.stdout = stdout
        whole = time.perf_counter() - start
        first, second = seconds["first"], seconds["second"]
        print(
            f"{name}: {whole:.1f}s; first checks {first:.1f}s ({counts['first']}), second {second:.2f}s"
            f" ({counts['second']}): {100 * second / first:.0f}% of the first; of the second, its rounds"
            f" {seconds["rounds"]:.2f}s and the rest {second - seconds["rounds"]:.2f}s",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
