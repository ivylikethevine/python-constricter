"""Mutation-test `constricter/` with mutmut, on a worktree of HEAD, and keep the mutants its tests survive.

  python3 scratch/mutation.py [--children N] [--only PATTERN ...] [--keep]

Line coverage is held at 100%, so it no longer says which lines run untested; a mutant (an operator
flipped, a constant changed) the unit tests survive does. mutmut 3.8 (`uv run --with`, on
`local/.venv`'s Python) mutates a copy of the checkout at HEAD made under `local/mutation/tree`,
with the tables the build generates copied in, and runs the unit tests (not `tests/corpus`, whose
suites are the corpus runs') for each mutant, `--children` processes at once (default: every CPU
but two). `--only` mutates the files matching each pattern (`constricter/fix/values/*`), for a
first pass. Its forked workers need what the sandbox denies: run it from a shell, or outside the
sandbox. It writes `local/mutation/survivors-<date>.txt` (`mutmut results`); the copy is removed
after unless `--keep`. A full pass is hours of every CPU: no corpus run beside it.
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "local" / "mutation"
TREE = OUT / "tree"
PYTHON = ROOT / "local" / ".venv" / "bin" / "python"
MUTMUT = "mutmut==3.8.0"  # released 2026-09-12
GENERATED = ("constricter/_version.py", "constricter/fix/tables")  # what the build writes, untracked


def config(only: list[str]) -> str:
    """Write mutmut's `setup.cfg` section for the copy."""
    lines = [
        "[mutmut]",
        "source_paths=constricter/",
        "pytest_add_cli_args_test_selection=tests/",
        "pytest_add_cli_args=--ignore=tests/corpus -p no:randomly -q",
        "mutate_only_covered_lines=true",
    ]
    if only:
        lines += ["only_mutate=", *(f"    {pattern}" for pattern in only)]
    return "\n".join(lines) + "\n"


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    print("+", " ".join(command), flush=True)
    return subprocess.run(command, cwd=cwd, check=False, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--children", type=int, default=max(1, (os.cpu_count() or 1) - 2))
    parser.add_argument("--only", nargs="*", default=[])
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if TREE.exists():
        print(f"{TREE} is there already: remove it (`git worktree remove --force {TREE}`) first")
        return 1
    added = run(["git", "worktree", "add", "--detach", str(TREE), "HEAD"], ROOT)
    if added.returncode:
        print(added.stderr)
        return added.returncode
    try:
        for each in GENERATED:
            source, target = ROOT / each, TREE / each
            if source.is_dir():
                shutil.copytree(source, target, dirs_exist_ok=True)
            else:
                shutil.copy2(source, target)
        (TREE / "setup.cfg").write_text(config(args.only), encoding="utf-8")
        uv = ["uv", "run", "--no-project", "--python", str(PYTHON), "--with", MUTMUT, "mutmut"]
        started = datetime.datetime.now()
        mutated = subprocess.run([*uv, "run", "--max-children", str(args.children)], cwd=TREE, check=False)
        print(f"mutmut run: exit {mutated.returncode}, {datetime.datetime.now() - started}")
        results = run([*uv, "results"], TREE)
        out = OUT / f"survivors-{started:%Y-%m-%d-%H%M}.txt"
        out.write_text(results.stdout + results.stderr, encoding="utf-8")
        print(f"{len(results.stdout.splitlines())} lines in {out}")
    finally:
        if not args.keep:
            removed = run(["git", "worktree", "remove", "--force", str(TREE)], ROOT)
            if removed.returncode:
                print(removed.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
