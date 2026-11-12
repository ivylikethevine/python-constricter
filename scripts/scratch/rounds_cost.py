"""Time `--fix` on a tree by HEAD's code and by the working tree's, and count what a second pass leaves.

  local/.venv/bin/python -m scripts.scratch.fix_diff --source TREE   # first: it writes the two copies of the code
  local/.venv/bin/python -m scripts.scratch.rounds_cost TREE

Each copy of the code (`local/scratch/fix-diff/`) fixes a copy of TREE under `local/scratch/rounds-cost/`
at `suffocate` in every scope, one process, then `--diff` gives the second pass's added lines, the
first ten printed. One run of each, so the seconds are one sample.
"""

import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "local" / "scratch"


def main() -> int:
    source = Path(sys.argv[1]).resolve()
    args = ["--level=suffocate", "--all-scopes", "--exit-zero", "--jobs=1", "-q", source.name]
    for label in ("HEAD", "tree"):
        work = ROOT / "rounds-cost" / label
        shutil.rmtree(work, ignore_errors=True)
        shutil.copytree(source, work / source.name, ignore=shutil.ignore_patterns("__pycache__"))
        env = {"PYTHONPATH": str(ROOT / "fix-diff" / label), "PATH": "/usr/bin:/bin"}
        command = [sys.executable, "-P", "-m", "constricter"]
        start = time.perf_counter()
        subprocess.run([*command, "--fix", *args], cwd=work, env=env, capture_output=True, check=False)
        took = time.perf_counter() - start
        second = subprocess.run(
            [*command, "--diff", *args], cwd=work, env=env, capture_output=True, text=True, check=False
        )
        added = [
            line for line in second.stdout.splitlines() if line.startswith("+") and not line.startswith("+++")
        ]
        print(f"{label}: {took:.1f}s, second pass {len(added)} lines")
        for line in added[:10]:
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
