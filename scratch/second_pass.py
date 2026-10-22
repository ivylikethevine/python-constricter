"""Fix a copy of each corpus as CI's `ci-fix` run does, then keep what a second pass still fixes.

  local/.venv/bin/python -m scratch.second_pass [CORPUS ...] [--likely | --certain]

`--fix --unsafe-fixes` (or `--likely`, or neither) at `suffocate` in every scope, then `--diff` with
the same: the count is the `+` lines as the runner's `left` counts them, and each diff is kept in
`local/scratch/second-pass/<corpus>.diff`. Outside a sandbox (the workers' forkserver);
`CORPUS_JOBS` sets the workers (every CPU, unset). The standard library and pandas took 5 minutes
together, 8 workers on 8CPU/62GB. CI's pandas is its uninstalled clone, not the installed package
this fixes: for CI's count, run `python -m tests.corpus tests/corpus/runs/ci-fix.toml --only pandas`.
"""

import sys
from pathlib import Path

from tests.corpus import corpus_table

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "second-pass"
TIERS = {"--likely": ["--likely"], "--certain": []}


def main() -> int:
    names = [arg for arg in sys.argv[1:] if not arg.startswith("--")]
    tier = next((TIERS[arg] for arg in sys.argv[1:] if arg in TIERS), ["--unsafe-fixes"])
    args = [*corpus_table.EVERYWHERE, *tier]
    OUT.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    for corpus in corpus_table.corpora():
        if names and corpus.name not in names:
            continue
        root, valid = corpus_table.copied(corpus, "second-pass")
        first = corpus_table._run(python, ["--fix", *args, str(root)])
        broken = sum(not corpus_table.compiles(path) for path in valid)
        diff = corpus_table._run(python, ["--diff", *args, str(root)])
        (OUT / f"{corpus.name.replace(' ', '-')}.diff").write_text(diff, encoding="utf-8")
        fixed = corpus_table.fixed_count(first)
        print(f"{corpus.name}: fixed {fixed}, broken {broken}, second pass {diff.count(chr(10) + '+')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
