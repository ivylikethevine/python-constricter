"""Fix a copy of a corpus as a run's `infer-<checker>` step does, then keep what a second pass still fixes.

  local/.venv/bin/python -m scratch.hinted_second_pass CHECKER CORPUS [CORPUS ...]

`--fix --unsafe-fixes --infer-with=CHECKER` at `suffocate` in every scope, on a copy laid out as the
corpus's checkout with its settings and environment (`launch.copied`), then `--diff` with the same:
the count is the `+` lines as the runner's `left` counts them. Each diff, and the first pass's
`--show-fixes` listing, are kept in `local/scratch/hinted-second-pass/`. Outside a sandbox (the
workers' forkserver, the checkers' servers); a suite's checkout is cloned and installed the first
time. Not while a run uses the same checkouts: its tree is taken back to its tag.
"""

import sys
from pathlib import Path

from tests.corpus import catalog, corpus_table, launch, trees
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "hinted-second-pass"


def main() -> int:
    checker, *names = sys.argv[1:]
    options = ["--unsafe-fixes", f"--infer-with={checker}", "--level=suffocate"]
    for name in names:
        tree = trees.found(catalog.load().entries[name])
        where, valid = launch.copied(tree, OUT / "work" / f"{name}-{checker}")
        first = launch.run(DEV, where, ["--fix", "--show-fixes", *options], 0)
        second = launch.run(DEV, where, ["--diff", *options], 0)
        label = f"{name}-{checker}"
        (OUT / f"{label}.fixes.txt").write_text(first.output, encoding="utf-8")
        (OUT / f"{label}.diff").write_text(second.output, encoding="utf-8")
        left = corpus_table.added(second.output)
        print(
            f"{label}: {len(valid)} files, second pass {left} ({first.seconds:.0f}s, {second.seconds:.0f}s)",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
