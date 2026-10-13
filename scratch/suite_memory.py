# SPDX-License-Identifier: MIT
"""Run one suite's released tests once for each set of extra arguments, and say what each run held.

  local/.venv/bin/python -m scratch.suite_memory SUITE                      # its tests as the catalog has them
  local/.venv/bin/python -m scratch.suite_memory SUITE "" "-p no:logging"   # and with each set of arguments
  local/.venv/bin/python -m scratch.suite_memory SUITE "!t/unit/app" ...    # or pytest's own, in place of its

Each run's seconds, CPU seconds, the most memory its process tree held at once (`corpora_cpu`) and
its outcome, a line each; its output kept in `local/scratch/suite-memory/`. The suite is installed
first if it isn't (the network, once). Outside a sandbox.
"""

import shlex
import subprocess
import sys
import time
from pathlib import Path

from tests.corpus import catalog, corpus_suite
from tests.corpus.corpora_cpu import Sampler

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "suite-memory"


def main(name: str, variants: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    suite = catalog.load().entry(name).suite
    if suite is None:
        print(f"{name} has no suite")
        return 1
    root = corpus_suite.checkout(name, suite)
    corpus_suite.reset(root, suite)
    workers = str(corpus_suite.workers(suite))
    sampler = Sampler()
    for at, extra in enumerate(variants or [""]):
        command = [word.replace(catalog.WORKERS, workers) for word in suite.tests] + shlex.split(extra)
        if extra.startswith("!"):
            command = [*catalog.PYTEST, *shlex.split(extra[1:])]
        command[0] = str(root / ".venv" / "bin" / command[0])
        start = time.perf_counter()
        with (OUT / f"{name}-{at}.txt").open("w", encoding="utf-8") as kept:
            ran = subprocess.Popen(command, cwd=root, stdout=kept, stderr=subprocess.STDOUT)
            sampler.watch(ran.pid)
            ran.wait()
        used = sampler.used(ran.pid)
        seconds = time.perf_counter() - start
        last = (
            (OUT / f"{name}-{at}.txt")
            .read_text(encoding="utf-8", errors="replace")
            .strip()
            .rsplit("\n", 1)[-1]
        )
        print(
            f"{name} {extra!r}: {seconds:.0f}s, {used.cpu:.0f} CPU seconds, {used.memory / 2**30:.1f} GB: {last}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
