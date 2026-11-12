"""Fix a copy of one corpus as a run's fix step does, in one process, and keep what a second pass still fixes.

  local/.venv/bin/python -m scratch.second_pass_copy CORPUS [--jobs=N] [OPTION ...]

Each OPTION goes to both passes: `--unsafe-fixes`, `--likely`, `--infer-with=pyrefly` (none: the
certain fixes). The copy is laid out as the corpus's checkout with its settings, stubs and
environment (`launch.copied`), the checkout left as it is (no reset to its tag, so it runs in a
sandbox and beside a run's tests); `--fix --show-fixes` at `suffocate` in every scope, then `--diff`
with the same. Prints the fixes and the second pass's `+` lines as the runner's `left` counts them.
Kept under `local/scratch/second-pass-copy/CORPUS/`: the fixed copy (`work/`), the first pass's
listing (`fixes.txt`) and the second's diff (`second.diff`). One process unless `--jobs` says
otherwise (0: every CPU, outside a sandbox for the workers' forkserver, as a checker's server needs
too). matplotlib's guesses took 2 minutes, 1 worker on 16CPU/60GB.
"""

import sys
from pathlib import Path

from tests.corpus import catalog, corpus_table, launch, trees
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "second-pass-copy"
JOBS = "--jobs="


def main() -> int:
    name, *given = sys.argv[1:]
    jobs = next((int(each.removeprefix(JOBS)) for each in given if each.startswith(JOBS)), 1)
    options = [*(each for each in given if not each.startswith(JOBS)), "--level=suffocate"]
    out = OUT / name.replace(" ", "-")
    tree = trees.found(catalog.load().entries[name], settle=False)
    where, valid = launch.copied(tree, out / "work")
    first = launch.run(DEV, where, ["--fix", "--show-fixes", *options], jobs)
    second = launch.run(DEV, where, ["--diff", *options], jobs)
    (out / "fixes.txt").write_text(first.output + first.errors, encoding="utf-8")
    (out / "second.diff").write_text(second.output + second.errors, encoding="utf-8")
    print(
        f"{name}: {len(valid)} files, fixed {corpus_table.fixed_count(first.output)}, "
        f"second pass {corpus_table.added(second.output)} ({first.seconds:.0f}s, {second.seconds:.0f}s)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
