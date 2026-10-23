"""Fix a copy of each corpus with every `fix-widen` kind and guesses, then list what a second pass still fixes.

  local/.venv/bin/python -m scratch.widen_pass [CORPUS ...]

Each second pass's diff is kept in `local/scratch/widen/`; its count is the bindings it adds or
changes. Outside a sandbox; about 5 minutes. `CORPUS_JOBS` sets the workers (every CPU, unset).
"""

import re
import sys
from pathlib import Path

from tests.corpus import corpus_table

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "widen"
# A line a second pass adds or changes for a binding: not a file's header, nor an import it adds.
BOUND = re.compile(r"^\+(?!\+\+ )(?!\s*(?:from |import |if TYPE_CHECKING))", re.MULTILINE)
ARGS = ["--level=suffocate", "--all-scopes", corpus_table.JOBS, "--unsafe-fixes", "--fix-widen=all"]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    python = sys.executable
    total = 0
    for corpus in corpus_table.corpora():
        if sys.argv[1:] and corpus.name not in sys.argv[1:]:
            continue
        root, valid = corpus_table.copied(corpus, "widen-guessed")
        first = corpus_table._run(python, ["--fix", *ARGS, str(root)])
        broken = sum(not corpus_table.compiles(path) for path in valid)
        diff = corpus_table._run(python, ["--diff", *ARGS, str(root)])
        name = corpus.name.replace(" ", "-")
        (OUT / f"{name}.diff").write_text(diff, encoding="utf-8")
        left = len(BOUND.findall(diff))
        total += left
        fixed = corpus_table.fixed_count(first)
        print(f"{corpus.name}: fixed {fixed}, broken {broken}, second pass {left}", flush=True)
    print(f"total second pass: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
